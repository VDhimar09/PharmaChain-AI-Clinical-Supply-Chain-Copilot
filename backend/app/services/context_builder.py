"""Bounded, structured context assembly for grounded RAG generation.

Turns ranked `RetrievalResult`s into a deterministic, size-capped block of
text the LLM can be prompted with, while preserving enough metadata per
chunk to resolve citations back to a real document/page after generation.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from app.core.config import settings
from app.core.logging import get_logger
from app.services.retriever_service import RetrievalResult


logger = get_logger("context_builder")


@dataclass(frozen=True)
class ContextItem:
    """A single source included in the LLM prompt context."""

    source_id: str
    document_id: uuid.UUID
    chunk_id: uuid.UUID
    filename: str
    page_number: int
    content: str
    similarity: float


@dataclass(frozen=True)
class BuiltContext:
    """The assembled prompt context plus the items it was built from."""

    items: list[ContextItem]
    text: str


class ContextBuilder:
    """Builds LLM-ready context from retrieved document chunks.

    - Preserves source metadata (chunk id, document id, filename, page,
      similarity) so citations can later be resolved without trusting the
      LLM.
    - Drops duplicate chunks by chunk_id, the chunk's true identity.
    - Assigns stable, deterministic source identifiers (SOURCE_1, SOURCE_2,
      ...) in retrieval-rank order, scoped to a single build() call.
    - Respects a configurable chunk count and character budget so prompt
      size stays bounded regardless of how much evidence is retrieved.
    """

    def __init__(
        self,
        max_chunks: int | None = None,
        max_chars: int | None = None,
    ):
        self.max_chunks = max_chunks or settings.RAG_CONTEXT_MAX_CHUNKS
        self.max_chars = max_chars or settings.RAG_CONTEXT_MAX_CHARS

    def build(self, results: list[RetrievalResult]) -> BuiltContext:
        deduplicated = self._deduplicate(results)[: self.max_chunks]

        items: list[ContextItem] = []
        blocks: list[str] = []
        total_chars = 0

        for index, result in enumerate(deduplicated, start=1):
            source_id = f"SOURCE_{index}"
            block = (
                f"[{source_id}]\n"
                f"Document: {result.filename}\n"
                f"Page: {result.page_number}\n\n"
                f"Content:\n{result.content}\n"
            )

            if items and total_chars + len(block) > self.max_chars:
                logger.info(
                    "Context truncated at %s/%s chunk(s) by character budget "
                    "(max_chars=%s)",
                    len(items),
                    len(deduplicated),
                    self.max_chars,
                )
                break

            items.append(
                ContextItem(
                    source_id=source_id,
                    document_id=result.document_id,
                    chunk_id=result.chunk_id,
                    filename=result.filename,
                    page_number=result.page_number,
                    content=result.content,
                    similarity=result.similarity,
                )
            )
            blocks.append(block)
            total_chars += len(block)

        return BuiltContext(items=items, text="\n".join(blocks))

    def _deduplicate(
        self,
        results: list[RetrievalResult],
    ) -> list[RetrievalResult]:
        # chunk_id is the chunk's true identity, so it is the dedup key -
        # stronger than comparing (document, page, content) tuples.
        seen: set[uuid.UUID] = set()
        deduplicated: list[RetrievalResult] = []

        for result in results:
            if result.chunk_id in seen:
                continue

            seen.add(result.chunk_id)
            deduplicated.append(result)

        return deduplicated
