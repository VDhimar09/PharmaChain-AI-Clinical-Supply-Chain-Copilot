"""Deterministic test doubles shared across the RAG test suite.

Never call a real embedding/LLM provider from unit tests - `FakeEmbeddingProvider`
produces stable, hash-derived vectors so tests are fast, offline, and
reproducible.
"""

from __future__ import annotations

import hashlib
import math

from app.services.embeddings.base_provider import EmbeddingError
from app.services.embeddings.base_provider import EmbeddingProvider
from app.services.llm.base_provider import LLMError
from app.services.llm.base_provider import LLMProvider


def build_minimal_pdf(pages_text: list[str]) -> bytes:
    """Build a tiny, dependency-free, valid single/multi-page PDF.

    Used instead of a fixture binary so tests stay self-contained and the
    expected extracted text is always known up front.
    """

    n_pages = len(pages_text)
    catalog_id = 1
    pages_id = 2
    page_ids = [3 + i for i in range(n_pages)]
    content_ids = [3 + n_pages + i for i in range(n_pages)]
    font_id = 3 + 2 * n_pages

    objects: dict[int, str] = {
        catalog_id: f"<< /Type /Catalog /Pages {pages_id} 0 R >>",
        pages_id: (
            "<< /Type /Pages /Kids ["
            + " ".join(f"{pid} 0 R" for pid in page_ids)
            + f"] /Count {n_pages} >>"
        ),
        font_id: "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    }

    for page_id, content_id in zip(page_ids, content_ids):
        objects[page_id] = (
            f"<< /Type /Page /Parent {pages_id} 0 R "
            f"/Resources << /Font << /F1 {font_id} 0 R >> >> "
            f"/MediaBox [0 0 612 792] /Contents {content_id} 0 R >>"
        )

    for text, content_id in zip(pages_text, content_ids):
        escaped = (
            text.replace("\\", "\\\\")
            .replace("(", "\\(")
            .replace(")", "\\)")
        )
        stream = f"BT /F1 18 Tf 72 700 Td ({escaped}) Tj ET"
        objects[content_id] = (
            f"<< /Length {len(stream)} >>\nstream\n{stream}\nendstream"
        )

    buffer = bytearray(b"%PDF-1.4\n")
    offsets: dict[int, int] = {}

    for object_id in sorted(objects):
        offsets[object_id] = len(buffer)
        buffer += f"{object_id} 0 obj\n".encode("latin-1")
        buffer += objects[object_id].encode("latin-1")
        buffer += b"\nendobj\n"

    xref_offset = len(buffer)
    max_id = max(objects)
    buffer += f"xref\n0 {max_id + 1}\n".encode("latin-1")
    buffer += b"0000000000 65535 f \n"

    for object_id in range(1, max_id + 1):
        buffer += f"{offsets[object_id]:010d} 00000 n \n".encode("latin-1")

    buffer += (
        f"trailer\n<< /Size {max_id + 1} /Root {catalog_id} 0 R >>\n"
        f"startxref\n{xref_offset}\n%%EOF"
    ).encode("latin-1")

    return bytes(buffer)


class FakeEmbeddingProvider(EmbeddingProvider):
    """Deterministic embedding provider for tests.

    The same input text always produces the same unit-length vector, and
    texts that share more words produce vectors with higher cosine
    similarity, which is enough to exercise similarity ranking in tests
    without any network calls.
    """

    def __init__(self, dimension: int = 8, fail_on: set[str] | None = None):
        self._dimension = dimension
        self._fail_on = fail_on or set()

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_one(text) for text in texts]

    def _embed_one(self, text: str) -> list[float]:
        if text in self._fail_on:
            raise EmbeddingError(f"Simulated embedding failure for: {text!r}")

        vector = [0.0] * self._dimension

        for word in text.lower().split():
            digest = hashlib.sha256(word.encode("utf-8")).digest()

            for i in range(self._dimension):
                byte = digest[i % len(digest)]
                vector[i] += (byte / 255.0) * 2 - 1

        magnitude = math.sqrt(sum(component ** 2 for component in vector))

        if magnitude == 0:
            # Degenerate (empty) text: return a fixed non-zero vector so
            # it remains a valid unit vector for cosine similarity.
            vector = [1.0] + [0.0] * (self._dimension - 1)
            magnitude = 1.0

        return [component / magnitude for component in vector]


class FakeLLMProvider(LLMProvider):
    """Deterministic LLM provider for tests - never calls a real model.

    Configure with either a single `response` (returned for every call)
    or a `responses` queue (one per call, in order). Set `fail=True` to
    simulate a provider failure (e.g. timeout/API error) instead.
    """

    def __init__(
        self,
        response: str = "",
        responses: list[str] | None = None,
        fail: bool = False,
        error_message: str = "Simulated LLM failure",
    ):
        self._response = response
        self._responses = list(responses) if responses is not None else None
        self._fail = fail
        self._error_message = error_message
        self.calls: list[dict[str, str]] = []

    def generate(self, *, system_prompt: str, user_prompt: str) -> str:
        self.calls.append(
            {"system_prompt": system_prompt, "user_prompt": user_prompt}
        )

        if self._fail:
            raise LLMError(self._error_message)

        if self._responses is not None:
            return self._responses.pop(0)

        return self._response
