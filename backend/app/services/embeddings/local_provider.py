"""Local Sentence Transformers embedding provider for development use."""

from __future__ import annotations

from typing import Any

from app.core.config import settings
from app.core.logging import get_logger
from app.services.embeddings.base_provider import EmbeddingError
from app.services.embeddings.base_provider import EmbeddingProvider


logger = get_logger("embeddings.local")


class LocalEmbeddingProvider(EmbeddingProvider):
    """CPU-friendly local embeddings backed by a Sentence Transformers model.

    The model is downloaded by Sentence Transformers on first use to the
    developer's standard Hugging Face cache, never to this repository.
    """

    def __init__(
        self,
        model_name: str | None = None,
        dimension: int | None = None,
        model: Any | None = None,
    ):
        self._model_name = model_name or settings.RAG_LOCAL_EMBEDDING_MODEL
        self._dimension = dimension or settings.RAG_LOCAL_EMBEDDING_DIMENSION

        try:
            if model is None:
                from sentence_transformers import SentenceTransformer

                model = SentenceTransformer(self._model_name, device="cpu")
            self._model = model
            model_dimension = self._model.get_sentence_embedding_dimension()
        except Exception as exc:
            logger.error("Local embedding model initialisation failed: %s", type(exc).__name__)
            raise EmbeddingError("Local embedding model could not be initialised.") from exc

        if model_dimension != self._dimension:
            raise EmbeddingError(
                "Local embedding model dimension does not match the configured local profile."
            )

    @property
    def profile(self) -> str:
        return "local"

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        if any(not isinstance(text, str) or not text.strip() for text in texts):
            raise EmbeddingError("Local embedding input must contain non-empty text.")

        try:
            vectors = self._model.encode(
                texts,
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=False,
            )
        except Exception as exc:
            logger.error("Local embedding generation failed: %s", type(exc).__name__)
            raise EmbeddingError("Failed to generate local embeddings.") from exc

        result = [[float(value) for value in vector] for vector in vectors]
        if any(len(vector) != self._dimension for vector in result):
            raise EmbeddingError("Local embedding model returned an unexpected vector dimension.")

        return result
