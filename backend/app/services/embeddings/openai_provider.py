import time

from openai import OpenAI
from openai import OpenAIError

from app.core.config import settings
from app.core.logging import get_logger
from app.observability.metrics import record_openai_usage
from app.services.embeddings.base_provider import EmbeddingError
from app.services.embeddings.base_provider import EmbeddingProvider


logger = get_logger("embeddings.openai")

# The OpenAI embeddings endpoint accepts multiple inputs per request; keep
# batches modest to bound request size and memory.
_BATCH_SIZE = 100


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """Embedding provider backed by the OpenAI embeddings API.

    Credentials are read exclusively from application configuration
    (`settings.OPENAI_API_KEY`, sourced from the environment) and are
    never logged.
    """

    def __init__(
        self,
        model: str | None = None,
        dimension: int | None = None,
        api_key: str | None = None,
    ):
        self._model = model or settings.RAG_EMBEDDING_MODEL
        self._dimension = dimension or settings.RAG_EMBEDDING_DIMENSION

        resolved_api_key = api_key or settings.OPENAI_API_KEY

        if not resolved_api_key:
            raise EmbeddingError(
                "OPENAI_API_KEY is not configured."
            )

        self._client = OpenAI(api_key=resolved_api_key)

    @property
    def profile(self) -> str:
        return "openai"

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        embeddings: list[list[float]] = []

        for start in range(0, len(texts), _BATCH_SIZE):
            batch = texts[start:start + _BATCH_SIZE]
            embeddings.extend(self._embed_batch(batch))

        return embeddings

    def _embed_batch(self, batch: list[str]) -> list[list[float]]:
        started_at = time.perf_counter()
        try:
            response = self._client.embeddings.create(
                model=self._model,
                input=batch,
                dimensions=self._dimension,
            )
        except OpenAIError as exc:
            record_openai_usage(
                operation="embeddings",
                model=self._model,
                outcome="error",
                duration_seconds=time.perf_counter() - started_at,
            )
            logger.error(
                "OpenAI embedding request failed for a batch of %s text(s): %s",
                len(batch),
                type(exc).__name__,
            )
            raise EmbeddingError(
                "Failed to generate embeddings via OpenAI."
            ) from exc

        duration_seconds = time.perf_counter() - started_at
        ordered = sorted(response.data, key=lambda item: item.index)
        usage = getattr(response, "usage", None)
        record_openai_usage(
            operation="embeddings",
            model=self._model,
            outcome="success",
            input_tokens=getattr(usage, "prompt_tokens", None),
            output_tokens=None,
            duration_seconds=duration_seconds,
        )
        return [item.embedding for item in ordered]
