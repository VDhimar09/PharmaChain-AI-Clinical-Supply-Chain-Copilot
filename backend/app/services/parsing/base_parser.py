"""Parser abstraction for turning source documents into page-aware text.

New formats (DOCX, TXT, Markdown, ...) can be supported in the future by
adding another `DocumentParser` implementation - the rest of the RAG
pipeline (chunking, embedding, storage) only depends on this abstraction.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass


class DocumentParsingError(Exception):
    """Raised when a source file cannot be parsed into pages."""


@dataclass(frozen=True)
class ParsedPage:
    """A single page of extracted text.

    `page_number` is 1-indexed to match how humans (and citations) refer
    to pages in a document.
    """

    page_number: int
    text: str


class DocumentParser(ABC):
    """Abstraction over page-aware text extraction for a source format."""

    @abstractmethod
    def supports(self, mime_type: str, filename: str) -> bool:
        """Return True if this parser can handle the given file."""

    @abstractmethod
    def parse(self, file_path: str) -> list[ParsedPage]:
        """Extract text page-by-page from the file at `file_path`.

        Must never silently drop a page: pages with no extractable text
        are still returned with an empty string so page numbering stays
        aligned with the source document.
        """
