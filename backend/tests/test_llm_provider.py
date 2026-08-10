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


def test_openai_provider_requires_api_key():
    with pytest.raises(LLMError):
        OpenAIChatProvider(api_key="")


def test_openai_provider_returns_completion_text(monkeypatch):
    captured_kwargs = {}

    class _FakeMessage:
        def __init__(self, content):
            self.content = content

    class _FakeChoice:
        def __init__(self, content):
            self.message = _FakeMessage(content)

    class _FakeResponse:
        def __init__(self, content):
            self.choices = [_FakeChoice(content)]

    class _FakeCompletionsResource:
        def create(self, **kwargs):
            captured_kwargs.update(kwargs)
            return _FakeResponse("Grounded answer citing SOURCE_1.")

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


def test_openai_provider_wraps_provider_errors(monkeypatch):
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

    provider = OpenAIChatProvider(api_key="fake-key")

    with pytest.raises(LLMError):
        provider.generate(system_prompt="s", user_prompt="u")


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
    class _FakeMessage:
        content = "   "

    class _FakeChoice:
        message = _FakeMessage()

    class _FakeResponse:
        choices = [_FakeChoice()]

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

    provider = OpenAIChatProvider(api_key="fake-key")

    with pytest.raises(LLMError):
        provider.generate(system_prompt="s", user_prompt="u")
