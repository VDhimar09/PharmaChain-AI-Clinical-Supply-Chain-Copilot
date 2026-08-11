"""Phase 3.3/3.4: `GroundedCopilotService` orchestration, grounded LLM
synthesis, citation validation, RBAC boundaries, and failure handling.

Offline unit tests - the existing `CopilotOrchestratorService` and RAG
pipeline are stood in with lightweight fakes (`db=None` is safe since
none of these fakes ever touch the database), mirroring the pattern
already used in `test_rag_generation_service.py`.
"""

from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.ai.exceptions import ToolExecutionException
from app.schemas.ai_copilot import (
    CopilotChatResponse,
    CopilotEvidenceBundle,
    CopilotReasoningStep,
    CopilotToolExecution,
)
from app.services.context_builder import ContextBuilder
from app.services.grounded_copilot_service import (
    GroundedCopilotError,
    GroundedCopilotPermissionError,
    GroundedCopilotService,
)
from app.services.rag_generation_service import RagGenerationService
from app.services.retriever_service import RetrievalResult
from tests.fakes import FakeLLMProvider


DOC_A = uuid4()


def _user(permissions: list[str]):
    return SimpleNamespace(
        id=uuid4(),
        role=SimpleNamespace(
            name="Tester",
            permissions=[SimpleNamespace(name=p) for p in permissions],
        ),
    )


def _operational_response(**overrides) -> CopilotChatResponse:
    base = dict(
        conversation_id=uuid4(),
        generated_at=datetime.now(UTC),
        intent="SHIPMENT_STATUS",
        confidence=90,
        tools_used=["Shipment Tool"],
        reasoning=[CopilotReasoningStep(step="Shipment Analysis", status="SUCCESS")],
        tool_execution=[
            CopilotToolExecution(tool="Shipment Tool", status="SUCCESS", execution_time_ms=5.0)
        ],
        evidence=CopilotEvidenceBundle(shipments={"delayed_shipments": 2}),
        recommendations=["Expedite SH-102"],
        response="There are 2 delayed shipments, including SH-102.",
    )
    base.update(overrides)
    return CopilotChatResponse(**base)


class FakeCopilotOrchestrator:
    def __init__(self, response: CopilotChatResponse | dict | None = None, error: Exception | None = None):
        self._response = response
        self._error = error
        self.calls: list[str] = []

    def chat(self, message: str):
        self.calls.append(message)
        if self._error is not None:
            raise self._error
        return self._response


class FakeRetriever:
    def __init__(self, results: list[RetrievalResult] | None = None, error: Exception | None = None):
        self._results = results or []
        self._error = error
        self.calls: list[str] = []

    def search(self, query: str):
        self.calls.append(query)
        if self._error is not None:
            raise self._error
        return self._results


def _retrieval_result(page_number=7, filename="Cold_Chain_SOP.pdf", content="Store between 2C and 8C."):
    return RetrievalResult(
        document_id=DOC_A,
        chunk_id=uuid4(),
        filename=filename,
        page_number=page_number,
        content=content,
        similarity=0.9,
    )


def _service(
    *,
    permissions=("copilot.use", "rag.query"),
    orchestrator=None,
    retriever=None,
    llm_response="",
    llm_fail=False,
):
    llm = FakeLLMProvider(response=llm_response, fail=llm_fail)
    service = GroundedCopilotService(
        db=None,
        current_user=_user(list(permissions)),
        copilot_orchestrator=orchestrator or FakeCopilotOrchestrator(_operational_response()),
        retriever_service=retriever or FakeRetriever(),
        context_builder=ContextBuilder(),
        llm_provider=llm,
    )
    return service, llm


# ---------------------------------------------------------------------------
# OPERATIONAL-only: existing Copilot pipeline, unchanged
# ---------------------------------------------------------------------------


def test_operational_only_question_uses_existing_copilot_pipeline_only():
    orchestrator = FakeCopilotOrchestrator(_operational_response())
    retriever = FakeRetriever()
    service, llm = _service(orchestrator=orchestrator, retriever=retriever)

    result = service.chat("How many delayed shipments do we have?")

    assert result.response == "There are 2 delayed shipments, including SH-102."
    assert result.evidence_requirement == "OPERATIONAL"
    assert result.grounded is None
    assert result.document_evidence == []
    assert result.citations == []
    # No document evidence source was ever touched for an operational-only
    # question - no retrieval, no LLM call.
    assert retriever.calls == []
    assert llm.calls == []


def test_operational_only_accepts_plain_dict_response_for_backward_compatibility():
    # Mirrors how existing tests monkeypatch `CopilotOrchestratorService.chat`
    # to return a plain dict (see test_rbac_integration.py).
    raw = _operational_response().model_dump(mode="json")
    orchestrator = FakeCopilotOrchestrator(raw)
    service, _ = _service(orchestrator=orchestrator)

    result = service.chat("Show me delayed shipments.")

    assert isinstance(result, CopilotChatResponse)
    assert result.response == raw["response"]
    assert result.evidence_requirement == "OPERATIONAL"


def test_operational_only_propagates_tool_failures_unchanged():
    orchestrator = FakeCopilotOrchestrator(error=ToolExecutionException("Tool execution failed for 'shipment'."))
    service, _ = _service(orchestrator=orchestrator)

    with pytest.raises(ToolExecutionException):
        service.chat("How many delayed shipments do we have?")


# ---------------------------------------------------------------------------
# DOCUMENT-only: existing RAG pipeline, unchanged
# ---------------------------------------------------------------------------


def test_document_only_question_uses_rag_pipeline_and_never_touches_copilot():
    orchestrator = FakeCopilotOrchestrator(_operational_response())
    retriever = FakeRetriever(results=[_retrieval_result()])
    service, llm = _service(
        orchestrator=orchestrator,
        retriever=retriever,
        llm_response="Store between 2C and 8C (SOURCE_1).",
    )

    result = service.chat("What does the cold-chain SOP require?")

    assert result.grounded is True
    assert result.evidence_requirement == "DOCUMENT"
    assert result.response == "Store between 2C and 8C (SOURCE_1)."
    assert len(result.citations) == 1
    assert result.citations[0].filename == "Cold_Chain_SOP.pdf"
    assert len(result.document_evidence) == 1
    assert result.tools_used == []
    assert result.evidence == CopilotEvidenceBundle()
    # The deterministic Copilot pipeline is never invoked for a
    # document-only question.
    assert orchestrator.calls == []


def test_document_only_with_no_evidence_returns_fallback_without_llm_call():
    retriever = FakeRetriever(results=[])
    service, llm = _service(retriever=retriever, llm_response="should never be used")

    result = service.chat("What does the cold-chain SOP require?")

    assert result.grounded is False
    assert result.citations == []
    assert result.document_evidence == []
    assert llm.calls == []


def test_document_only_without_rag_query_permission_is_denied():
    retriever = FakeRetriever(results=[_retrieval_result()])
    service, _ = _service(permissions=("copilot.use",), retriever=retriever)

    with pytest.raises(GroundedCopilotPermissionError):
        service.chat("What does the cold-chain SOP require?")

    # `copilot.use` must never silently substitute for `rag.query`.
    assert retriever.calls == []


# ---------------------------------------------------------------------------
# OPERATIONAL_AND_DOCUMENT: combined grounded synthesis
# ---------------------------------------------------------------------------


def test_combined_question_without_rag_query_permission_downgrades_to_operational_only():
    orchestrator = FakeCopilotOrchestrator(_operational_response())
    retriever = FakeRetriever(results=[_retrieval_result()])
    service, llm = _service(
        permissions=("copilot.use",),
        orchestrator=orchestrator,
        retriever=retriever,
    )

    result = service.chat(
        "Why is shipment SH-102 at risk, and what does our cold-chain SOP require?"
    )

    assert result.evidence_requirement == "OPERATIONAL"
    assert result.document_evidence == []
    assert result.citations == []
    # Document evidence must never be fetched on the caller's behalf.
    assert retriever.calls == []
    assert llm.calls == []
    assert orchestrator.calls == ["Why is shipment SH-102 at risk, and what does our cold-chain SOP require?"]


def test_combined_question_with_permission_synthesizes_both_evidence_sources():
    orchestrator = FakeCopilotOrchestrator(_operational_response())
    retriever = FakeRetriever(results=[_retrieval_result()])
    service, llm = _service(
        orchestrator=orchestrator,
        retriever=retriever,
        llm_response=(
            "SH-102 is delayed per current operations, and the cold-chain "
            "SOP (SOURCE_1) requires storage between 2C and 8C."
        ),
    )

    result = service.chat(
        "Why is shipment SH-102 at risk, and what does our cold-chain SOP require?"
    )

    assert result.evidence_requirement == "OPERATIONAL_AND_DOCUMENT"
    assert result.grounded is True
    assert "SOURCE_1" in result.response
    assert len(result.citations) == 1
    assert result.citations[0].filename == "Cold_Chain_SOP.pdf"
    assert len(result.document_evidence) == 1
    # Full chunk-level detail is preserved for the combined path (unlike
    # the document-only path, which only has validated `Citation`s).
    assert result.document_evidence[0].chunk_id is not None
    assert result.document_evidence[0].similarity == pytest.approx(0.9)

    assert len(llm.calls) == 1
    prompt = llm.calls[0]["user_prompt"]
    assert "OPERATIONAL EVIDENCE" in prompt
    assert "DOCUMENT EVIDENCE" in prompt
    assert "delayed_shipments" in prompt
    assert "SOURCE_1" in prompt


def test_combined_synthesis_without_valid_citation_falls_back_to_operational_answer():
    orchestrator = FakeCopilotOrchestrator(_operational_response())
    retriever = FakeRetriever(results=[_retrieval_result()])
    service, llm = _service(
        orchestrator=orchestrator,
        retriever=retriever,
        llm_response="A confident-sounding answer with no real citation.",
    )

    result = service.chat(
        "Why is shipment SH-102 at risk, and what does our cold-chain SOP require?"
    )

    assert result.grounded is False
    assert result.citations == []
    # The deterministic operational answer is trusted over an ungrounded
    # LLM synthesis.
    assert result.response == "There are 2 delayed shipments, including SH-102."


def test_combined_with_fabricated_source_id_is_rejected():
    orchestrator = FakeCopilotOrchestrator(_operational_response())
    retriever = FakeRetriever(results=[_retrieval_result()])
    service, llm = _service(
        orchestrator=orchestrator,
        retriever=retriever,
        llm_response="Per SOURCE_1 and also fabricated SOURCE_999, this is required.",
    )

    result = service.chat(
        "Why is shipment SH-102 at risk, and what does our cold-chain SOP require?"
    )

    assert result.grounded is True
    assert len(result.citations) == 1
    assert result.citations[0].filename == "Cold_Chain_SOP.pdf"


def test_combined_with_no_document_evidence_returns_operational_answer_without_llm_call():
    orchestrator = FakeCopilotOrchestrator(_operational_response())
    retriever = FakeRetriever(results=[])
    service, llm = _service(orchestrator=orchestrator, retriever=retriever)

    result = service.chat(
        "Why is shipment SH-102 at risk, and what does our cold-chain SOP require?"
    )

    assert result.grounded is False
    assert result.document_evidence == []
    assert result.response == "There are 2 delayed shipments, including SH-102."
    assert llm.calls == []


def test_combined_with_operational_failure_falls_back_to_document_only_answer():
    orchestrator = FakeCopilotOrchestrator(
        error=ToolExecutionException("Tool execution failed for 'shipment'.")
    )
    retriever = FakeRetriever(results=[_retrieval_result()])
    service, llm = _service(
        orchestrator=orchestrator,
        retriever=retriever,
        llm_response="Store between 2C and 8C (SOURCE_1).",
    )

    result = service.chat(
        "Why is shipment SH-102 at risk, and what does our cold-chain SOP require?"
    )

    assert result.grounded is True
    assert result.tools_used == []
    assert result.intent == "DOCUMENT_QUERY"
    assert len(result.citations) == 1


def test_combined_with_both_sources_unavailable_raises_grounded_copilot_error():
    orchestrator = FakeCopilotOrchestrator(
        error=ToolExecutionException("Tool execution failed for 'shipment'.")
    )
    retriever = FakeRetriever(results=[])
    service, _ = _service(orchestrator=orchestrator, retriever=retriever)

    with pytest.raises(GroundedCopilotError):
        service.chat(
            "Why is shipment SH-102 at risk, and what does our cold-chain SOP require?"
        )


def test_combined_llm_failure_raises_grounded_copilot_error():
    orchestrator = FakeCopilotOrchestrator(_operational_response())
    retriever = FakeRetriever(results=[_retrieval_result()])
    service, _ = _service(orchestrator=orchestrator, retriever=retriever, llm_fail=True)

    with pytest.raises(GroundedCopilotError):
        service.chat(
            "Why is shipment SH-102 at risk, and what does our cold-chain SOP require?"
        )


def test_document_retrieval_failure_degrades_combined_to_operational_only():
    orchestrator = FakeCopilotOrchestrator(_operational_response())
    retriever = FakeRetriever(error=RuntimeError("embedding provider unavailable"))
    service, llm = _service(orchestrator=orchestrator, retriever=retriever)

    result = service.chat(
        "Why is shipment SH-102 at risk, and what does our cold-chain SOP require?"
    )

    assert result.grounded is False
    assert result.document_evidence == []
    assert result.response == "There are 2 delayed shipments, including SH-102."
    assert llm.calls == []


# ---------------------------------------------------------------------------
# RagGenerationService reuse sanity check
# ---------------------------------------------------------------------------


def test_document_only_reuses_rag_generation_service_when_injected():
    retriever = FakeRetriever(results=[_retrieval_result()])
    llm = FakeLLMProvider(response="Store between 2C and 8C (SOURCE_1).")
    rag_service = RagGenerationService(db=None, retriever_service=retriever, llm_provider=llm)

    service = GroundedCopilotService(
        db=None,
        current_user=_user(["copilot.use", "rag.query"]),
        rag_generation_service=rag_service,
    )

    result = service.chat("What does the cold-chain SOP require?")

    assert result.grounded is True
    assert len(llm.calls) == 1
