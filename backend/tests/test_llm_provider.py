import pytest
from openai import APIConnectionError
from openai import APITimeoutError

from app.services.llm.base_provider import LLMError
from app.services.llm.openai_provider import OpenAIChatProvider
from tests.fakes import FakeLLMProvider


def test_fake_provider_returns_configured_response():
    provider = FakeLLMProvider(response="The sky is blue.")

    answer = provider.generate(
        system_prompt="system",
        user_prompt="What color is the sky?",
    )

    assert answer == "The sky is blue."


def test_fake_provider_records_calls():
    provider = FakeLLMProvider(response="answer")

    provider.generate(system_prompt="sys", user_prompt="user question")

    assert provider.calls == [
        {"system_prompt": "sys", "user_prompt": "user question"}
    ]


def test_fake_provider_returns_queued_responses_in_order():
    provider = FakeLLMProvider(responses=["first", "second"])

    assert provider.generate(system_prompt="s", user_prompt="1") == "first"
    assert provider.generate(system_prompt="s", user_prompt="2") == "second"


def test_fake_provider_raises_llm_error_when_configured_to_fail():
    provider = FakeLLMProvider(fail=True, error_message="boom")

    with pytest.raises(LLMError, match="boom"):
        provider.generate(system_prompt="s", user_prompt="u")


def test_openai_provider_requires_api_key(monkeypatch):
    monkeypatch.setattr(
        "app.core.config.settings.OPENAI_API_KEY",
        None,
        raising=False,
    )

    with pytest.raises(LLMError):
        OpenAIChatProvider(api_key="")


def test_openai_provider_returns_completion_text(monkeypatch):
    captured_kwargs = {}
    recorded_usage = []

    class _FakeMessage:
        def __init__(self, content):
            self.content = content

    class _FakeChoice:
        def __init__(self, content):
            self.message = _FakeMessage(content)

    class _FakeUsage:
        prompt_tokens = 14
        completion_tokens = 7

    class _FakeResponse:
        def __init__(self, content, usage=None):
            self.choices = [_FakeChoice(content)]
            self.usage = usage

    class _FakeCompletionsResource:
        def create(self, **kwargs):
            captured_kwargs.update(kwargs)
            return _FakeResponse(
                "Grounded answer citing SOURCE_1.",
                _FakeUsage(),
            )

    class _FakeChatResource:
        def __init__(self):
            self.completions = _FakeCompletionsResource()

    class _FakeOpenAIClient:
        def __init__(self, api_key, timeout):
            self.chat = _FakeChatResource()

    monkeypatch.setattr(
        "app.services.llm.openai_provider.OpenAI",
        _FakeOpenAIClient,
    )
    monkeypatch.setattr(
        "app.services.llm.openai_provider.record_openai_usage",
        lambda **kwargs: recorded_usage.append(kwargs),
    )

    provider = OpenAIChatProvider(
        model="gpt-4o-mini",
        temperature=0.0,
        max_tokens=500,
        api_key="fake-key",
    )

    result = provider.generate(
        system_prompt="Answer only from sources.",
        user_prompt="What is the SOP?",
    )

    assert result == "Grounded answer citing SOURCE_1."
    assert captured_kwargs["model"] == "gpt-4o-mini"
    assert captured_kwargs["temperature"] == 0.0
    assert captured_kwargs["max_tokens"] == 500
    assert captured_kwargs["messages"] == [
        {"role": "system", "content": "Answer only from sources."},
        {"role": "user", "content": "What is the SOP?"},
    ]
    assert len(recorded_usage) == 1
    assert recorded_usage[0]["operation"] == "chat_completions"
    assert recorded_usage[0]["model"] == "gpt-4o-mini"
    assert recorded_usage[0]["outcome"] == "success"
    assert recorded_usage[0]["input_tokens"] == 14
    assert recorded_usage[0]["output_tokens"] == 7
    assert recorded_usage[0]["duration_seconds"] >= 0


def test_openai_provider_records_success_without_usage(monkeypatch):
    recorded_usage = []

    class _FakeMessage:
        content = "Grounded answer."

    class _FakeChoice:
        message = _FakeMessage()

    class _FakeResponse:
        choices = [_FakeChoice()]

    class _FakeCompletionsResource:
        def create(self, **kwargs):
            return _FakeResponse()

    class _FakeChatResource:
        completions = _FakeCompletionsResource()

    class _FakeOpenAIClient:
        def __init__(self, api_key, timeout):
            self.chat = _FakeChatResource()

    monkeypatch.setattr(
        "app.services.llm.openai_provider.OpenAI",
        _FakeOpenAIClient,
    )
    monkeypatch.setattr(
        "app.services.llm.openai_provider.record_openai_usage",
        lambda **kwargs: recorded_usage.append(kwargs),
    )

    provider = OpenAIChatProvider(api_key="fake-key")

    assert provider.generate(system_prompt="s", user_prompt="u") == "Grounded answer."
    assert recorded_usage[0]["outcome"] == "success"
    assert recorded_usage[0]["input_tokens"] is None
    assert recorded_usage[0]["output_tokens"] is None
    assert recorded_usage[0]["duration_seconds"] >= 0


def test_openai_provider_wraps_provider_errors(monkeypatch):
    recorded_usage = []
    class _FailingCompletionsResource:
        def create(self, **kwargs):
            raise APIConnectionError(request=None)

    class _FakeChatResource:
        def __init__(self):
            self.completions = _FailingCompletionsResource()

    class _FakeOpenAIClient:
        def __init__(self, api_key, timeout):
            self.chat = _FakeChatResource()

    monkeypatch.setattr(
        "app.services.llm.openai_provider.OpenAI",
        _FakeOpenAIClient,
    )
    monkeypatch.setattr(
        "app.services.llm.openai_provider.record_openai_usage",
        lambda **kwargs: recorded_usage.append(kwargs),
    )

    provider = OpenAIChatProvider(api_key="fake-key")

    with pytest.raises(LLMError):
        provider.generate(system_prompt="s", user_prompt="u")

    assert recorded_usage[0]["operation"] == "chat_completions"
    assert recorded_usage[0]["model"] == provider._model
    assert recorded_usage[0]["outcome"] == "error"
    assert "input_tokens" not in recorded_usage[0]
    assert "output_tokens" not in recorded_usage[0]
    assert recorded_usage[0]["duration_seconds"] >= 0


def test_openai_provider_wraps_timeout_errors(monkeypatch):
    class _TimingOutCompletionsResource:
        def create(self, **kwargs):
            raise APITimeoutError(request=None)

    class _FakeChatResource:
        def __init__(self):
            self.completions = _TimingOutCompletionsResource()

    class _FakeOpenAIClient:
        def __init__(self, api_key, timeout):
            self.chat = _FakeChatResource()

    monkeypatch.setattr(
        "app.services.llm.openai_provider.OpenAI",
        _FakeOpenAIClient,
    )

    provider = OpenAIChatProvider(api_key="fake-key", timeout=1.0)

    with pytest.raises(LLMError):
        provider.generate(system_prompt="s", user_prompt="u")


def test_openai_provider_rejects_empty_completion(monkeypatch):
    recorded_usage = []
    class _FakeMessage:
        content = "   "

    class _FakeChoice:
        message = _FakeMessage()

    class _FakeUsage:
        prompt_tokens = 9
        completion_tokens = 2

    class _FakeResponse:
        choices = [_FakeChoice()]
        usage = _FakeUsage()

    class _EmptyCompletionsResource:
        def create(self, **kwargs):
            return _FakeResponse()

    class _FakeChatResource:
        def __init__(self):
            self.completions = _EmptyCompletionsResource()

    class _FakeOpenAIClient:
        def __init__(self, api_key, timeout):
            self.chat = _FakeChatResource()

    monkeypatch.setattr(
        "app.services.llm.openai_provider.OpenAI",
        _FakeOpenAIClient,
    )
    monkeypatch.setattr(
        "app.services.llm.openai_provider.record_openai_usage",
        lambda **kwargs: recorded_usage.append(kwargs),
    )

    provider = OpenAIChatProvider(api_key="fake-key")

    with pytest.raises(LLMError):
        provider.generate(system_prompt="s", user_prompt="u")

    assert recorded_usage[0]["operation"] == "chat_completions"
    assert recorded_usage[0]["model"] == provider._model
    assert recorded_usage[0]["outcome"] == "invalid_response"
    assert recorded_usage[0]["input_tokens"] == 9
    assert recorded_usage[0]["output_tokens"] == 2
    assert recorded_usage[0]["duration_seconds"] >= 0
