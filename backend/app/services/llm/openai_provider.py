import time

from openai import OpenAI
from openai import OpenAIError

from app.core.config import settings
from app.core.logging import get_logger
from app.observability.metrics import record_openai_usage
from app.services.llm.base_provider import LLMError
from app.services.llm.base_provider import LLMProvider


logger = get_logger("llm.openai")


class OpenAIChatProvider(LLMProvider):
    """LLM provider backed by the OpenAI chat completions API.

    Credentials are read exclusively from application configuration
    (`settings.OPENAI_API_KEY`, sourced from the environment) and are
    never logged. Prompt content is never logged either - only lengths
    and timings are.
    """

    def __init__(
        self,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        timeout: float | None = None,
        api_key: str | None = None,
    ):
        self._model = model or settings.RAG_GENERATION_MODEL
        self._temperature = (
            temperature
            if temperature is not None
            else settings.RAG_GENERATION_TEMPERATURE
        )
        self._max_tokens = max_tokens or settings.RAG_GENERATION_MAX_TOKENS
        self._timeout = timeout or settings.RAG_GENERATION_TIMEOUT_SECONDS

        resolved_api_key = api_key or settings.OPENAI_API_KEY

        if not resolved_api_key:
            raise LLMError(
                "OPENAI_API_KEY is not configured."
            )

        self._client = OpenAI(
            api_key=resolved_api_key,
            timeout=self._timeout,
        )

    def generate(self, *, system_prompt: str, user_prompt: str) -> str:
        started_at = time.perf_counter()
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                temperature=self._temperature,
                max_tokens=self._max_tokens,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
        except OpenAIError as exc:
            record_openai_usage(
                operation="chat_completions",
                model=self._model,
                outcome="error",
                duration_seconds=time.perf_counter() - started_at,
            )
            logger.error(
                "OpenAI chat completion request failed: %s",
                type(exc).__name__,
            )
            raise LLMError(
                "Failed to generate a completion via OpenAI."
            ) from exc

        duration_seconds = time.perf_counter() - started_at
        usage = getattr(response, "usage", None)
        input_tokens = getattr(usage, "prompt_tokens", None)
        output_tokens = getattr(usage, "completion_tokens", None)
        choices = getattr(response, "choices", None)
        choice = choices[0] if choices else None
        message = getattr(choice, "message", None)
        content = getattr(message, "content", None)

        if not content or not content.strip():
            record_openai_usage(
                operation="chat_completions",
                model=self._model,
                outcome="invalid_response",
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                duration_seconds=duration_seconds,
            )
            raise LLMError(
                "OpenAI returned an empty completion."
            )

        record_openai_usage(
            operation="chat_completions",
            model=self._model,
            outcome="success",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            duration_seconds=duration_seconds,
        )
        return content
