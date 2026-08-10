from uuid import uuid4

import pytest

from app.services.rag_generation_service import (
    FALLBACK_ANSWER,
    RagGenerationError,
    RagGenerationService,
)
from app.services.retriever_service import RetrievalResult
from tests.fakes import FakeLLMProvider


DOC_A = uuid4()
DOC_B = uuid4()


class _StubRetriever:
    """Stands in for `RetrieverService` - already threshold-filtered."""

    def __init__(self, results):
        self._results = results
        self.queries: list[str] = []

    def search(self, query):
        self.queries.append(query)
        return self._results


def _result(
    document_id,
    page_number,
    content,
    filename=None,
    similarity=0.9,
    chunk_id=None,
):
    return RetrievalResult(
        document_id=document_id,
        chunk_id=chunk_id or uuid4(),
        filename=filename or f"{document_id}.pdf",
        page_number=page_number,
        content=content,
        similarity=similarity,
    )


def _service(results, response="", responses=None, fail=False):
    llm = FakeLLMProvider(response=response, responses=responses, fail=fail)
    retriever = _StubRetriever(results)
    service = RagGenerationService(
        db=None,
        retriever_service=retriever,
        llm_provider=llm,
    )
    return service, llm, retriever


def test_query_with_relevant_evidence_returns_grounded_answer_with_citation():
    results = [
        _result(DOC_A, 12, "Log excursions within one hour.", filename="Cold_Chain_SOP.pdf")
    ]
    service, llm, _ = _service(
        results,
        response="Excursions must be logged within one hour (SOURCE_1).",
    )

    result = service.query("What does the SOP say about temperature excursions?")

    assert result.grounded is True
    assert result.answer == "Excursions must be logged within one hour (SOURCE_1)."
    assert len(result.citations) == 1
    assert result.citations[0].document_id == DOC_A
    assert result.citations[0].filename == "Cold_Chain_SOP.pdf"
    assert result.citations[0].page_number == 12
    assert len(llm.calls) == 1


def test_query_with_no_evidence_returns_fallback_without_calling_llm():
    service, llm, _ = _service(results=[])

    result = service.query("What is the meaning of life?")

    assert result.answer == FALLBACK_ANSWER
    assert result.grounded is False
    assert result.citations == []
    assert llm.calls == []


def test_query_with_weak_evidence_returns_fallback_without_calling_llm():
    # RetrieverService already drops anything below the similarity
    # threshold, so "weak evidence" surfaces identically to "no evidence":
    # an empty result list reaching this service.
    service, llm, _ = _service(results=[])

    result = service.query("completely unrelated nonsense query")

    assert result.grounded is False
    assert result.answer == FALLBACK_ANSWER
    assert llm.calls == []


def test_query_with_blank_question_returns_fallback_without_calling_llm():
    service, llm, retriever = _service(
        results=[_result(DOC_A, 1, "content")],
        response="Answer (SOURCE_1).",
    )

    result = service.query("   ")

    assert result.grounded is False
    assert llm.calls == []
    assert retriever.queries == []


def test_query_resolves_citations_across_multiple_documents():
    results = [
        _result(DOC_A, 12, "cold chain content", filename="Cold_Chain_SOP.pdf"),
        _result(DOC_B, 7, "gdp content", filename="GDP_Guidelines.pdf"),
    ]
    service, _, _ = _service(
        results,
        response="Per SOURCE_1 and SOURCE_2, follow both procedures.",
    )

    result = service.query("What do the SOPs require?")

    assert result.grounded is True
    filenames = {citation.filename for citation in result.citations}
    assert filenames == {"Cold_Chain_SOP.pdf", "GDP_Guidelines.pdf"}


def test_query_resolves_citations_across_multiple_pages_of_same_document():
    results = [
        _result(DOC_A, 3, "page three content", filename="SOP.pdf"),
        _result(DOC_A, 9, "page nine content", filename="SOP.pdf"),
    ]
    service, _, _ = _service(
        results,
        response="See SOURCE_1 and SOURCE_2 for details.",
    )

    result = service.query("What pages cover this?")

    page_numbers = {citation.page_number for citation in result.citations}
    assert page_numbers == {3, 9}


def test_query_deduplicates_citations_from_duplicate_retrieved_chunks():
    duplicate = _result(DOC_A, 12, "same content twice", filename="SOP.pdf")
    service, _, _ = _service(
        results=[duplicate, duplicate],
        response="Answer referencing SOURCE_1.",
    )

    result = service.query("What does the SOP say?")

    assert len(result.citations) == 1


def test_query_ignores_unknown_or_fabricated_source_ids():
    results = [_result(DOC_A, 12, "real content", filename="SOP.pdf")]
    service, _, _ = _service(
        results,
        response="Per SOURCE_1 and also SOURCE_99, this is required.",
    )

    result = service.query("What is required?")

    assert result.grounded is True
    assert len(result.citations) == 1
    assert result.citations[0].page_number == 12


def test_query_answer_without_any_citation_is_downgraded_to_fallback():
    results = [_result(DOC_A, 12, "real content", filename="SOP.pdf")]
    service, _, _ = _service(
        results,
        response="This is a confident-sounding answer with no citation at all.",
    )

    result = service.query("What is required?")

    assert result.grounded is False
    assert result.answer == FALLBACK_ANSWER
    assert result.citations == []


def test_query_answer_repeating_fallback_phrase_is_ungrounded():
    results = [_result(DOC_A, 12, "real content", filename="SOP.pdf")]
    service, _, _ = _service(results, response=FALLBACK_ANSWER)

    result = service.query("What is required?")

    assert result.grounded is False
    assert result.answer == FALLBACK_ANSWER
    assert result.citations == []


def test_query_raises_rag_generation_error_on_llm_failure():
    results = [_result(DOC_A, 12, "real content", filename="SOP.pdf")]
    service, _, _ = _service(results, fail=True)

    with pytest.raises(RagGenerationError):
        service.query("What is required?")


def test_query_passes_bounded_context_to_llm_prompt():
    results = [_result(DOC_A, 12, "Log excursions within one hour.", filename="SOP.pdf")]
    service, llm, _ = _service(results, response="Answer (SOURCE_1).")

    service.query("What does the SOP say?")

    assert len(llm.calls) == 1
    prompt = llm.calls[0]["user_prompt"]
    assert "SOURCE_1" in prompt
    assert "SOP.pdf" in prompt
    assert "Log excursions within one hour." in prompt
    assert "What does the SOP say?" in prompt
