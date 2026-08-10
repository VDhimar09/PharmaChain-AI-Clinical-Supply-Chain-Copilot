"""Semantic (vector similarity) retrieval over ingested document chunks.

This service returns retrieved evidence only - it does not generate an
LLM answer. That is intentionally out of scope for Phase 1.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import get_logger
from app.repositories.document_chunk_repository import DocumentChunkRepository
from app.services.embeddings.base_provider import EmbeddingProvider


logger = get_logger("retriever_service")


@dataclass(frozen=True)
class RetrievalResult:
    document_id: uuid.UUID
    chunk_id: uuid.UUID
    filename: str
    page_number: int
    content: str
    similarity: float


class RetrieverService:

    def __init__(
        self,
        db: Session,
        embedding_provider: EmbeddingProvider | None = None,
        top_k: int | None = None,
        similarity_threshold: float | None = None,
    ):
        self.db = db
        self._embedding_provider = embedding_provider
        self.top_k = top_k or settings.RAG_SEARCH_TOP_K
        self.similarity_threshold = (
            similarity_threshold
            if similarity_threshold is not None
            else settings.RAG_SIMILARITY_THRESHOLD
        )

    @property
    def embedding_provider(self) -> EmbeddingProvider:
        if self._embedding_provider is None:
            from app.services.embeddings.openai_provider import (
                OpenAIEmbeddingProvider,
            )

            self._embedding_provider = OpenAIEmbeddingProvider()

        return self._embedding_provider

    def search(self, query: str) -> list[RetrievalResult]:
        normalized_query = query.strip()

        if not normalized_query:
            return []

        started_at = time.monotonic()

        query_embedding = self.embedding_provider.embed_text(
            normalized_query
        )

        candidates = DocumentChunkRepository.search(
            self.db,
            query_embedding,
            self.top_k,
        )

        # Top-K narrows candidates first; the similarity threshold then
        # drops anything not actually relevant rather than padding
        # results just to fill out top-K.
        results = [
            RetrievalResult(
                document_id=candidate.chunk.document_id,
                chunk_id=candidate.chunk.id,
                filename=candidate.chunk.document.original_filename,
                page_number=candidate.chunk.page_number,
                content=candidate.chunk.content,
                similarity=candidate.similarity,
            )
            for candidate in candidates
            if candidate.similarity >= self.similarity_threshold
        ]

        elapsed_ms = (time.monotonic() - started_at) * 1000

        logger.info(
            "RAG search returned %s/%s candidate chunk(s) "
            "(top_k=%s, threshold=%.2f) in %.1fms",
            len(results),
            len(candidates),
            self.top_k,
            self.similarity_threshold,
            elapsed_ms,
        )

        return results
