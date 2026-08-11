"""Phase 3.1: shared evidence contract (`app.schemas.grounded_copilot`).

Focused, offline unit tests - no DB, no LLM - covering operational
evidence, document evidence, and the combined `GroundedEvidence`
container in isolation.
"""

from uuid import uuid4

from app.schemas.ai_copilot import CopilotEvidenceBundle
from app.schemas.grounded_copilot import DocumentEvidenceItem
from app.schemas.grounded_copilot import GroundedEvidence
from app.schemas.grounded_copilot import OperationalEvidenceItem
from app.services.citation_resolver import Citation
from app.services.context_builder import ContextItem


DOC_A = uuid4()
CHUNK_A = uuid4()


# ---------------------------------------------------------------------------
# OperationalEvidenceItem
# ---------------------------------------------------------------------------


def test_operational_evidence_from_bundle_includes_only_non_empty_sections():
    bundle = CopilotEvidenceBundle(
        inventory={"low_stock_products": 3},
        warehouse={},
        shipments={"delayed_shipments": 2},
        procurement={},
        ai_insights={},
    )

    items = OperationalEvidenceItem.from_evidence_bundle(bundle)

    assert [item.tool_key for item in items] == ["inventory", "shipments"]
    assert items[0].tool == "Inventory Tool"
    assert items[0].data == {"low_stock_products": 3}
    assert items[0].status == "SUCCESS"


def test_operational_evidence_from_empty_bundle_is_empty():
    items = OperationalEvidenceItem.from_evidence_bundle(CopilotEvidenceBundle())

    assert items == []


# ---------------------------------------------------------------------------
# DocumentEvidenceItem
# ---------------------------------------------------------------------------


def test_document_evidence_from_context_items_preserves_rag_identity():
    context_item = ContextItem(
        source_id="SOURCE_1",
        document_id=DOC_A,
        chunk_id=CHUNK_A,
        filename="Cold_Chain_SOP.pdf",
        page_number=7,
        content="Store between 2C and 8C.",
        similarity=0.87,
    )

    items = DocumentEvidenceItem.from_context_items([context_item])

    assert len(items) == 1
    item = items[0]
    assert item.source_id == "SOURCE_1"
    assert item.document_id == DOC_A
    assert item.chunk_id == CHUNK_A
    assert item.filename == "Cold_Chain_SOP.pdf"
    assert item.page_number == 7
    assert item.content == "Store between 2C and 8C."
    assert item.similarity == 0.87


def test_document_evidence_from_citations_carries_only_validated_identity():
    citation = Citation(document_id=DOC_A, filename="Cold_Chain_SOP.pdf", page_number=7)

    items = DocumentEvidenceItem.from_citations([citation])

    assert len(items) == 1
    item = items[0]
    assert item.document_id == DOC_A
    assert item.filename == "Cold_Chain_SOP.pdf"
    assert item.page_number == 7
    # A `Citation` (already-validated) carries no chunk-level detail -
    # never fabricate it.
    assert item.chunk_id is None
    assert item.content is None
    assert item.similarity is None
    assert item.source_id is None


# ---------------------------------------------------------------------------
# GroundedEvidence
# ---------------------------------------------------------------------------


def test_grounded_evidence_keeps_operational_and_document_evidence_separate():
    bundle = CopilotEvidenceBundle(shipments={"delayed_shipments": 1})
    context_item = ContextItem(
        source_id="SOURCE_1",
        document_id=DOC_A,
        chunk_id=CHUNK_A,
        filename="Cold_Chain_SOP.pdf",
        page_number=7,
        content="Store between 2C and 8C.",
        similarity=0.87,
    )

    evidence = GroundedEvidence(
        operational_evidence=OperationalEvidenceItem.from_evidence_bundle(bundle),
        document_evidence=DocumentEvidenceItem.from_context_items([context_item]),
    )

    assert len(evidence.operational_evidence) == 1
    assert len(evidence.document_evidence) == 1
    assert evidence.operational_evidence[0].tool_key == "shipments"
    assert evidence.document_evidence[0].filename == "Cold_Chain_SOP.pdf"


def test_grounded_evidence_defaults_to_empty_lists():
    evidence = GroundedEvidence()

    assert evidence.operational_evidence == []
    assert evidence.document_evidence == []


def test_operational_text_renders_bounded_deterministic_block():
    bundle = CopilotEvidenceBundle(shipments={"delayed_shipments": 2})
    evidence = GroundedEvidence(
        operational_evidence=OperationalEvidenceItem.from_evidence_bundle(bundle),
    )

    text = evidence.to_operational_text()

    assert "[Shipment Tool]" in text
    assert "delayed_shipments" in text


def test_operational_text_with_no_evidence_is_explicit_not_silent():
    evidence = GroundedEvidence()

    text = evidence.to_operational_text()

    assert text == "No operational evidence was available."
