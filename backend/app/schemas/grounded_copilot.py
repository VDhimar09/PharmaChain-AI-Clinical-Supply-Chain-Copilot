"""Shared evidence contract for the grounded Executive Copilot (Phase 3).

The Executive Copilot answers questions using two kinds of evidence with
different trust semantics:

- Operational evidence: live facts produced by the existing Copilot tools
  (`InventoryTool`, `WarehouseTool`, `ShipmentTool`, `ProcurementTool`,
  `AIInsightsTool`) via `CopilotOrchestratorService`. This is already
  trustworthy - it is deterministic, computed straight from the database.
- Document evidence: chunks retrieved from ingested documents by the RAG
  pipeline (`RetrieverService` / `ContextBuilder`). This is only
  trustworthy once an LLM citation naming a chunk has been validated
  server-side (see `app.services.citation_resolver`).

`GroundedEvidence` keeps the two kinds strictly separated so a grounded
answer can never silently blend a live operational fact with a documented
procedure. Neither container invents a new citation system - both mirror
identity fields already owned elsewhere (`CopilotEvidenceBundle` for
operational evidence, `ContextItem`/`Citation` for document evidence) so
this stays a thin, typed integration boundary rather than a duplicate
source of truth.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any
from uuid import UUID

from pydantic import BaseModel
from pydantic import Field


if TYPE_CHECKING:
    from app.schemas.ai_copilot import CopilotEvidenceBundle
    from app.services.citation_resolver import Citation
    from app.services.context_builder import ContextItem


class OperationalEvidenceItem(BaseModel):
    """One operational tool's contribution to a grounded answer.

    Mirrors the sections already produced by the existing Copilot
    (`CopilotEvidenceBundle`) - this does not execute tools or recompute
    anything, it only carries an already-composed tool result across the
    Copilot/RAG integration boundary.
    """

    tool: str
    tool_key: str
    status: str = "SUCCESS"
    data: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_evidence_bundle(
        cls,
        evidence: "CopilotEvidenceBundle",
    ) -> list["OperationalEvidenceItem"]:
        """Build one item per non-empty section of an existing
        `CopilotEvidenceBundle`. The bundle remains the single source of
        truth for operational tool results - this only reshapes it."""

        sections = (
            ("inventory", "Inventory Tool", evidence.inventory),
            ("warehouse", "Warehouse Tool", evidence.warehouse),
            ("shipments", "Shipment Tool", evidence.shipments),
            ("procurement", "Procurement Tool", evidence.procurement),
            ("ai_insights", "AI Insights Tool", evidence.ai_insights),
        )

        return [
            cls(tool=display_name, tool_key=key, status="SUCCESS", data=dict(data))
            for key, display_name, data in sections
            if data
        ]


class DocumentEvidenceItem(BaseModel):
    """One retrieved document chunk considered as evidence.

    Mirrors `ContextItem` (see `context_builder.py`) - the RAG
    retrieval/citation pipeline remains the single source of truth for
    chunk identity. `chunk_id`/`content`/`similarity`/`source_id` are only
    available when the chunk was retrieved directly (e.g. for combined
    synthesis); they are left unset when this item is reconstructed from
    an already-validated `Citation` instead, since a `Citation` does not
    carry that detail.
    """

    source_id: str | None = None
    document_id: UUID
    chunk_id: UUID | None = None
    filename: str
    page_number: int
    content: str | None = None
    similarity: float | None = None

    @classmethod
    def from_context_items(
        cls,
        items: list["ContextItem"],
    ) -> list["DocumentEvidenceItem"]:
        return [
            cls(
                source_id=item.source_id,
                document_id=item.document_id,
                chunk_id=item.chunk_id,
                filename=item.filename,
                page_number=item.page_number,
                content=item.content,
                similarity=item.similarity,
            )
            for item in items
        ]

    @classmethod
    def from_citations(
        cls,
        citations: list["Citation"],
    ) -> list["DocumentEvidenceItem"]:
        return [
            cls(
                document_id=citation.document_id,
                filename=citation.filename,
                page_number=citation.page_number,
            )
            for citation in citations
        ]


class GroundedEvidence(BaseModel):
    """Evidence collected for a single grounded Copilot answer, kept
    strictly separated by source so operational facts are never conflated
    with documented procedures.

    Conceptually:

        GroundedEvidence
        |-- operational_evidence[]
        `-- document_evidence[]
    """

    operational_evidence: list[OperationalEvidenceItem] = Field(default_factory=list)
    document_evidence: list[DocumentEvidenceItem] = Field(default_factory=list)

    def to_operational_text(self) -> str:
        """Render operational evidence as a bounded, deterministic text
        block suitable for an LLM prompt (see `GroundedCopilotService`)."""

        if not self.operational_evidence:
            return "No operational evidence was available."

        blocks = [
            f"[{item.tool}]\n{json.dumps(item.data, default=str)}"
            for item in self.operational_evidence
        ]
        return "\n\n".join(blocks)
