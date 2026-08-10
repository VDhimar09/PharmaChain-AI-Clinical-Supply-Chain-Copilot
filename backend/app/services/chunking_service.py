"""Deterministic, page-aware chunking for the RAG ingestion pipeline."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from app.core.config import settings
from app.services.parsing.base_parser import ParsedPage


@dataclass(frozen=True)
class Chunk:
    """A single chunk ready for embedding and vector storage."""

    document_id: uuid.UUID
    chunk_index: int
    page_number: int
    content: str


class ChunkingService:
    """Splits page-aware parsed text into overlapping, page-scoped chunks.

    Each chunk belongs to exactly one page (chunks never span pages,
    matching `DocumentChunk.page_number` being a single value), splitting
    is word-aware so words are never cut in half, and trailing fragments
    smaller than `min_chunk_size` are merged into the previous chunk
    instead of being emitted on their own.
    """

    def __init__(
        self,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
        min_chunk_size: int | None = None,
    ):
        self.chunk_size = (
            chunk_size
            if chunk_size is not None
            else settings.RAG_CHUNK_SIZE
        )
        self.chunk_overlap = (
            chunk_overlap
            if chunk_overlap is not None
            else settings.RAG_CHUNK_OVERLAP
        )
        self.min_chunk_size = (
            min_chunk_size
            if min_chunk_size is not None
            else settings.RAG_MIN_CHUNK_SIZE
        )

        if self.chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero.")

        if self.chunk_overlap < 0:
            raise ValueError("chunk_overlap cannot be negative.")

        if self.chunk_overlap >= self.chunk_size:
            raise ValueError(
                "chunk_overlap must be smaller than chunk_size."
            )

    def chunk_pages(
        self,
        document_id: uuid.UUID,
        pages: list[ParsedPage],
    ) -> list[Chunk]:
        """Chunk every page of a document into an ordered list of `Chunk`."""

        chunks: list[Chunk] = []
        chunk_index = 0

        for page in pages:
            for chunk_text in self._split_text(page.text):
                chunks.append(
                    Chunk(
                        document_id=document_id,
                        chunk_index=chunk_index,
                        page_number=page.page_number,
                        content=chunk_text,
                    )
                )
                chunk_index += 1

        return chunks

    def _split_text(self, text: str) -> list[str]:
        words = text.split()

        if not words:
            return []

        chunks: list[str] = []
        current_words: list[str] = []
        current_len = 0
        index = 0

        while index < len(words):
            word = words[index]
            added_len = len(word) + (1 if current_words else 0)

            if (
                current_words
                and current_len + added_len > self.chunk_size
            ):
                chunks.append(" ".join(current_words))
                current_words, current_len = self._build_overlap(
                    current_words
                )
                continue

            current_words.append(word)
            current_len += added_len
            index += 1

        if current_words:
            tail = " ".join(current_words)

            if chunks and len(tail) < self.min_chunk_size:
                chunks[-1] = f"{chunks[-1]} {tail}"
            else:
                chunks.append(tail)

        return chunks

    def _build_overlap(
        self,
        words: list[str],
    ) -> tuple[list[str], int]:
        """Return the trailing words (and their length) to seed the next
        chunk with, so consecutive chunks share `chunk_overlap` characters
        of context."""

        overlap_words: list[str] = []
        overlap_len = 0

        for word in reversed(words):
            candidate_len = len(word) + (1 if overlap_words else 0)

            if overlap_len + candidate_len > self.chunk_overlap:
                break

            overlap_words.insert(0, word)
            overlap_len += candidate_len

        return overlap_words, overlap_len
