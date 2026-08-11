"""Shared SOURCE_N citation resolution for grounded LLM answers.

This is the single authoritative place that turns an LLM's raw SOURCE_N
references into validated citations against real retrieved context.
`RagGenerationService` (document-only) and `GroundedCopilotService`
(operational + document) both resolve citations through this module, so
there is exactly one citation-trust boundary in the system - never a
second, competing implementation.

Citations are never trusted from the model's prose. The answer is only
ever scanned for the SOURCE_N token; document id, filename and page
number are always looked up server-side against the `ContextItem`s that
were actually built for the request. Unknown or fabricated source ids
are silently dropped.
"""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass

from app.services.context_builder import ContextItem


SOURCE_ID_PATTERN = re.compile(r"SOURCE_\d+")


@dataclass(frozen=True)
class Citation:
    document_id: uuid.UUID
    filename: str
    page_number: int


def resolve_citations(
    answer: str,
    items: list[ContextItem],
) -> list[Citation]:
    """Resolve SOURCE_N references in an LLM answer against the actual
    retrieved context.

    Unknown/fabricated source ids are dropped rather than trusted, and
    duplicate (document, page) references collapse to a single citation.
    """

    items_by_source_id = {item.source_id: item for item in items}
    resolved: list[Citation] = []
    seen: set[tuple[uuid.UUID, int]] = set()

    for match in SOURCE_ID_PATTERN.finditer(answer):
        item = items_by_source_id.get(match.group(0))

        if item is None:
            # Unknown/fabricated source id - never trusted.
            continue

        key = (item.document_id, item.page_number)

        if key in seen:
            continue

        seen.add(key)
        resolved.append(
            Citation(
                document_id=item.document_id,
                filename=item.filename,
                page_number=item.page_number,
            )
        )

    return resolved
