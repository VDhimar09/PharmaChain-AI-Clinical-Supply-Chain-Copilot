from openai import OpenAI
from openai import OpenAIError

from app.core.config import settings
from app.core.logging import get_logger
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
            logger.error(
                "OpenAI chat completion request failed: %s",
                type(exc).__name__,
            )
            raise LLMError(
                "Failed to generate a completion via OpenAI."
            ) from exc

        choice = response.choices[0] if response.choices else None
        content = choice.message.content if choice and choice.message else None

        if not content or not content.strip():
            raise LLMError(
                "OpenAI returned an empty completion."
            )

        return content
