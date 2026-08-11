"""Shared citation resolution (`app.services.citation_resolver`).

This is the single citation-trust boundary reused by both
`RagGenerationService` (see `test_rag_generation_service.py`) and
`GroundedCopilotService` - covered directly here so both call sites can
rely on it without re-testing the same logic twice.
"""

from uuid import uuid4

from app.services.citation_resolver import resolve_citations
from app.services.context_builder import ContextItem


DOC_A = uuid4()
DOC_B = uuid4()


def _item(source_id, document_id, page_number, filename=None):
    return ContextItem(
        source_id=source_id,
        document_id=document_id,
        chunk_id=uuid4(),
        filename=filename or f"{document_id}.pdf",
        page_number=page_number,
        content="content",
        similarity=0.9,
    )


def test_resolve_citations_matches_known_source_ids():
    items = [_item("SOURCE_1", DOC_A, 12, filename="SOP.pdf")]

    citations = resolve_citations("Per SOURCE_1, this is required.", items)

    assert len(citations) == 1
    assert citations[0].document_id == DOC_A
    assert citations[0].filename == "SOP.pdf"
    assert citations[0].page_number == 12


def test_resolve_citations_drops_unknown_source_ids():
    items = [_item("SOURCE_1", DOC_A, 12)]

    citations = resolve_citations("Per SOURCE_1 and SOURCE_99, this is required.", items)

    assert len(citations) == 1
    assert citations[0].page_number == 12


def test_resolve_citations_returns_empty_list_when_answer_has_no_citations():
    items = [_item("SOURCE_1", DOC_A, 12)]

    citations = resolve_citations("A confident answer with no citation.", items)

    assert citations == []


def test_resolve_citations_deduplicates_repeated_references():
    items = [_item("SOURCE_1", DOC_A, 12)]

    citations = resolve_citations("SOURCE_1 ... and again, SOURCE_1.", items)

    assert len(citations) == 1


def test_resolve_citations_supports_multiple_distinct_sources():
    items = [
        _item("SOURCE_1", DOC_A, 12, filename="Cold_Chain_SOP.pdf"),
        _item("SOURCE_2", DOC_B, 7, filename="GDP_Guidelines.pdf"),
    ]

    citations = resolve_citations("Per SOURCE_1 and SOURCE_2.", items)

    filenames = {citation.filename for citation in citations}
    assert filenames == {"Cold_Chain_SOP.pdf", "GDP_Guidelines.pdf"}


def test_resolve_citations_with_no_items_never_fabricates_a_match():
    citations = resolve_citations("Per SOURCE_1.", [])

    assert citations == []
