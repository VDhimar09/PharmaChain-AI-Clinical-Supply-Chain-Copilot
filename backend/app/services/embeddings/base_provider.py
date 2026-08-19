"""Embedding provider abstraction.

The rest of the RAG pipeline (chunking output -> vector storage ->
retrieval) depends only on this interface, never on a concrete embedding
vendor. Swapping providers (OpenAI, Azure OpenAI, a local model, ...)
means adding another implementation here.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod


class EmbeddingError(Exception):
    """Raised when embedding generation fails."""


class EmbeddingProvider(ABC):

    @property
    def profile(self) -> str:
        """Storage profile used to keep incompatible vector spaces apart."""

        return "openai"

    @property
    @abstractmethod
    def dimension(self) -> int:
        """The fixed vector width this provider produces."""

    @abstractmethod
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of texts, preserving input order.

        Implementations must raise `EmbeddingError` (not a
        provider-specific exception) on failure, and must never include
        credentials in any raised message or log line.
        """

    def embed_text(self, text: str) -> list[float]:
        """Convenience wrapper for embedding a single text."""

        return self.embed_texts([text])[0]
