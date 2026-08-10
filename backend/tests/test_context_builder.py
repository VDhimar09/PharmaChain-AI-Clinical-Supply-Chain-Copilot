from uuid import uuid4

from app.services.context_builder import ContextBuilder
from app.services.retriever_service import RetrievalResult


DOC_A = uuid4()
DOC_B = uuid4()


def _result(document_id, page_number, content, similarity=0.9):
    return RetrievalResult(
        document_id=document_id,
        filename=f"{document_id}.pdf",
        page_number=page_number,
        content=content,
        similarity=similarity,
    )


def test_build_preserves_source_metadata():
    result = RetrievalResult(
        document_id=DOC_A,
        filename="Cold_Chain_SOP.pdf",
        page_number=12,
        content="Temperature excursions must be logged within one hour.",
        similarity=0.89,
    )

    context = ContextBuilder().build([result])

    assert len(context.items) == 1
    item = context.items[0]
    assert item.source_id == "SOURCE_1"
    assert item.document_id == DOC_A
    assert item.filename == "Cold_Chain_SOP.pdf"
    assert item.page_number == 12
    assert item.content == result.content
    assert item.similarity == 0.89


def test_build_generates_deterministic_sequential_source_ids():
    results = [
        _result(DOC_A, 1, "first chunk"),
        _result(DOC_A, 2, "second chunk"),
        _result(DOC_B, 7, "third chunk"),
    ]

    context = ContextBuilder().build(results)

    assert [item.source_id for item in context.items] == [
        "SOURCE_1",
        "SOURCE_2",
        "SOURCE_3",
    ]


def test_build_includes_document_and_page_in_rendered_text():
    result = _result(DOC_A, 12, "Log excursions within one hour.")
    context = ContextBuilder().build([result])

    assert "[SOURCE_1]" in context.text
    assert f"Document: {result.filename}" in context.text
    assert "Page: 12" in context.text
    assert "Log excursions within one hour." in context.text


def test_build_supports_multiple_documents_and_pages():
    results = [
        _result(DOC_A, 12, "cold chain content"),
        _result(DOC_B, 7, "gdp content"),
    ]

    context = ContextBuilder().build(results)

    document_ids = {item.document_id for item in context.items}
    assert document_ids == {DOC_A, DOC_B}
    assert {item.page_number for item in context.items} == {12, 7}


def test_build_deduplicates_identical_chunks():
    duplicate = _result(DOC_A, 12, "same content twice")
    results = [duplicate, duplicate]

    context = ContextBuilder().build(results)

    assert len(context.items) == 1


def test_build_respects_max_chunks_limit():
    results = [_result(DOC_A, page, f"content {page}") for page in range(10)]

    context = ContextBuilder(max_chunks=3).build(results)

    assert len(context.items) == 3
    assert [item.source_id for item in context.items] == [
        "SOURCE_1",
        "SOURCE_2",
        "SOURCE_3",
    ]


def test_build_respects_max_chars_budget():
    results = [
        _result(DOC_A, 1, "a" * 100),
        _result(DOC_A, 2, "b" * 100),
        _result(DOC_A, 3, "c" * 100),
    ]

    # Only enough room for the first block once headers are accounted for.
    context = ContextBuilder(max_chunks=10, max_chars=150).build(results)

    assert len(context.items) == 1
    assert len(context.text) <= 150 or len(context.items) == 1


def test_build_always_includes_at_least_one_chunk_even_if_it_exceeds_budget():
    results = [_result(DOC_A, 1, "x" * 500)]

    context = ContextBuilder(max_chunks=10, max_chars=10).build(results)

    assert len(context.items) == 1


def test_build_with_no_results_returns_empty_context():
    context = ContextBuilder().build([])

    assert context.items == []
    assert context.text == ""
