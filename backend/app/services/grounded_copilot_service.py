"""Grounded Executive Copilot: routes a question to the evidence source(s)
it needs, then synthesizes a single answer.

This is the integration boundary between the existing, deterministic
Executive Copilot (`CopilotOrchestratorService` - unchanged) and the
existing grounded RAG pipeline (`RetrieverService` / `ContextBuilder` /
`RagGenerationService` - unchanged). It does not replace either, does not
duplicate their internals, and does not turn RAG into "just another
Copilot tool" - operational and document evidence keep different trust
semantics all the way through (see `app.schemas.grounded_copilot`).

Routing, by `EvidenceRequirementDetector` output:

    OPERATIONAL              -> existing Copilot pipeline only, response
                                 shape/behavior unchanged.
    DOCUMENT                 -> existing RAG pipeline only
                                 (`RagGenerationService.query`), reused
                                 as-is including its own no-evidence
                                 fallback and citation validation.
    OPERATIONAL_AND_DOCUMENT -> both gathered, then combined via a single
                                 grounded LLM synthesis call that is told
                                 to keep the two evidence kinds separate
                                 and to cite document evidence only.

RBAC: a question that needs document evidence is only allowed to fetch it
if the caller holds `rag.query` - `copilot.use` alone never grants access
to document evidence. See `chat()`.

Failure handling:
    - Operational tool failure (`AIException`) never fabricates
      operational evidence; the combined path degrades to document-only.
    - RAG retrieval failure never fabricates document evidence; the
      combined path degrades to operational-only.
    - If both sources are exhausted, or synthesis genuinely cannot
      produce a grounded answer, `GroundedCopilotError` is raised (maps
      to HTTP 503 at the API layer, mirroring `RagGenerationError`).
    - An LLM answer that does not cite any real, retrieved source is
      never surfaced as a trusted synthesis - it is discarded in favor of
      the deterministic operational answer, exactly like the RAG-only
      pipeline discards ungrounded answers.
"""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy.orm import Session

from app.ai.evidence_requirement import EvidenceRequirement
from app.ai.evidence_requirement import EvidenceRequirementDetector
from app.ai.exceptions import AIException
from app.core.logging import get_logger
from app.dependencies.auth import user_has_permission
from app.models.user import User
from app.schemas.ai_copilot import CopilotChatResponse
from app.schemas.ai_copilot import CopilotEvidenceBundle
from app.schemas.ai_copilot import CopilotReasoningStep
from app.schemas.grounded_copilot import DocumentEvidenceItem
from app.schemas.grounded_copilot import GroundedEvidence
from app.schemas.grounded_copilot import OperationalEvidenceItem
from app.schemas.rag import RagCitation
from app.services.citation_resolver import resolve_citations
from app.services.context_builder import BuiltContext
from app.services.context_builder import ContextBuilder
from app.services.copilot_orchestrator_service import CopilotOrchestratorService
from app.services.llm.base_provider import LLMError
from app.services.llm.base_provider import LLMProvider
from app.services.rag_generation_service import RagGenerationService
from app.services.retriever_service import RetrieverService


logger = get_logger("grounded_copilot_service")

COMBINED_SYSTEM_PROMPT = (
    "You are PharmaChain's Executive Copilot. Answer using two kinds of "
    "evidence supplied below: OPERATIONAL EVIDENCE (live system facts) "
    "and DOCUMENT EVIDENCE (uploaded documentation, each block labeled "
    "SOURCE_N). Use only the evidence supplied - never invent operational "
    "facts, numbers, or policy requirements, and never use outside or "
    "general knowledge. Clearly distinguish current operational state "
    "from documented procedures in your answer. When you rely on a "
    "DOCUMENT EVIDENCE block, cite its identifier exactly as written, "
    "e.g. SOURCE_1. Never cite a SOURCE_N identifier that was not "
    "supplied, and never cite SOURCE_N for an operational fact. If the "
    "supplied document evidence does not support a policy claim, say the "
    "documentation does not cover it instead of guessing."
)


class GroundedCopilotError(Exception):
    """Raised when a grounded Copilot answer could not be produced (e.g.
    LLM failure, or no evidence available from any source). Maps to
    HTTP 503 at the API layer - mirrors `RagGenerationError`."""


class GroundedCopilotPermissionError(Exception):
    """Raised when a question requires document evidence the caller is
    not permitted to retrieve. Maps to HTTP 403 at the API layer."""

    def __init__(self, permission_name: str):
        self.permission_name = permission_name
        super().__init__(f"Permission '{permission_name}' required.")


class GroundedCopilotService:

    def __init__(
        self,
        db: Session,
        current_user: User,
        copilot_orchestrator: CopilotOrchestratorService | None = None,
        retriever_service: RetrieverService | None = None,
        context_builder: ContextBuilder | None = None,
        rag_generation_service: RagGenerationService | None = None,
        llm_provider: LLMProvider | None = None,
        evidence_detector: type[EvidenceRequirementDetector] = EvidenceRequirementDetector,
    ):
        self.db = db
        self.current_user = current_user
        self._copilot_orchestrator = copilot_orchestrator
        self._retriever_service = retriever_service
        self.context_builder = context_builder or ContextBuilder()
        self._rag_generation_service = rag_generation_service
        self._llm_provider = llm_provider
        self.evidence_detector = evidence_detector

    @property
    def copilot_orchestrator(self) -> CopilotOrchestratorService:
        if self._copilot_orchestrator is None:
            self._copilot_orchestrator = CopilotOrchestratorService(self.db)

        return self._copilot_orchestrator

    @property
    def retriever_service(self) -> RetrieverService:
        if self._retriever_service is None:
            self._retriever_service = RetrieverService(self.db)

        return self._retriever_service

    @property
    def rag_generation_service(self) -> RagGenerationService:
        if self._rag_generation_service is None:
            self._rag_generation_service = RagGenerationService(
                self.db,
                retriever_service=self.retriever_service,
                context_builder=self.context_builder,
                llm_provider=self._llm_provider,
            )

        return self._rag_generation_service

    @property
    def llm_provider(self) -> LLMProvider:
        if self._llm_provider is None:
            # Imported lazily so environments without an OpenAI key can
            # still import this module (e.g. to inject a fake provider).
            from app.services.llm.openai_provider import OpenAIChatProvider

            self._llm_provider = OpenAIChatProvider()

        return self._llm_provider

    def chat(self, message: str) -> CopilotChatResponse:
        requirement = self.evidence_detector.detect(message)
        needs_document = requirement in (
            EvidenceRequirement.DOCUMENT,
            EvidenceRequirement.OPERATIONAL_AND_DOCUMENT,
        )
        has_document_permission = user_has_permission(
            self.current_user, "rag.query"
        )

        if needs_document and not has_document_permission:
            if requirement == EvidenceRequirement.DOCUMENT:
                # The question is document-only and the caller has no
                # document access at all - `copilot.use` must never
                # silently substitute for `rag.query`.
                raise GroundedCopilotPermissionError("rag.query")

            # Combined question, no document access: operational Copilot
            # functionality continues where permitted, document evidence
            # is simply never fetched on the caller's behalf.
            logger.info(
                "Caller lacks 'rag.query'; downgrading combined request "
                "to operational-only evidence."
            )
            requirement = EvidenceRequirement.OPERATIONAL

        if requirement == EvidenceRequirement.OPERATIONAL:
            return self._operational_only(message)

        if requirement == EvidenceRequirement.DOCUMENT:
            return self._document_only(message)

        return self._combined(message)

    # ------------------------------------------------------------------
    # Single-source paths
    # ------------------------------------------------------------------

    def _operational_only(self, message: str) -> CopilotChatResponse:
        """Existing Copilot pipeline, unchanged - including error
        behavior. No LLM call is ever made for an operational-only
        question."""

        response = self._normalize(self.copilot_orchestrator.chat(message))
        return self._finalize(
            response,
            EvidenceRequirement.OPERATIONAL,
            grounded=None,
            document_evidence=[],
            citations=[],
        )

    def _document_only(self, message: str) -> CopilotChatResponse:
        """Existing RAG pipeline, unchanged - including its own
        no-evidence fallback (no LLM call when nothing was retrieved) and
        server-side citation validation."""

        rag_result = self.rag_generation_service.query(message)
        return self._from_rag_result(rag_result, EvidenceRequirement.DOCUMENT)

    # ------------------------------------------------------------------
    # Combined path
    # ------------------------------------------------------------------

    def _combined(self, message: str) -> CopilotChatResponse:
        operational_response = self._try_operational(message)
        context = self._retrieve_document_context(message)

        if operational_response is None and not context.items:
            raise GroundedCopilotError(
                "Unable to gather operational or document evidence for "
                "this request."
            )

        if not context.items:
            # RAG found nothing (or retrieval failed) - the deterministic
            # operational answer stands alone rather than inventing
            # policy evidence that was never retrieved.
            return self._finalize(
                operational_response,
                EvidenceRequirement.OPERATIONAL_AND_DOCUMENT,
                grounded=False,
                document_evidence=[],
                citations=[],
            )

        if operational_response is None:
            # Operational tools failed - do not fabricate operational
            # evidence; fall back to a pure document-grounded answer via
            # the existing RAG pipeline.
            rag_result = self.rag_generation_service.query(message)
            return self._from_rag_result(
                rag_result, EvidenceRequirement.OPERATIONAL_AND_DOCUMENT
            )

        return self._synthesize_combined(message, operational_response, context)

    def _try_operational(self, message: str) -> CopilotChatResponse | None:
        try:
            return self._normalize(self.copilot_orchestrator.chat(message))
        except AIException:
            logger.exception(
                "Operational evidence gathering failed for a grounded "
                "copilot request; continuing with document evidence only."
            )
            return None

    def _retrieve_document_context(self, message: str) -> BuiltContext:
        try:
            results = self.retriever_service.search(message)
        except Exception:
            logger.exception(
                "Document evidence retrieval failed for a grounded "
                "copilot request; continuing with operational evidence "
                "only."
            )
            return BuiltContext(items=[], text="")

        if not results:
            return BuiltContext(items=[], text="")

        return self.context_builder.build(results)

    def _synthesize_combined(
        self,
        message: str,
        operational_response: CopilotChatResponse,
        context: BuiltContext,
    ) -> CopilotChatResponse:
        evidence = GroundedEvidence(
            operational_evidence=OperationalEvidenceItem.from_evidence_bundle(
                operational_response.evidence
            ),
            document_evidence=DocumentEvidenceItem.from_context_items(
                context.items
            ),
        )

        try:
            raw_answer = self.llm_provider.generate(
                system_prompt=COMBINED_SYSTEM_PROMPT,
                user_prompt=self._build_combined_user_prompt(
                    evidence.to_operational_text(),
                    context.text,
                    message,
                ),
            )
        except LLMError as exc:
            logger.error(
                "Grounded copilot synthesis failed after gathering "
                "evidence: %s",
                type(exc).__name__,
            )
            raise GroundedCopilotError(
                "Failed to generate a grounded answer."
            ) from exc

        answer_text = raw_answer.strip()
        citations = resolve_citations(answer_text, context.items)

        if not citations:
            # The model did not ground itself in a real, retrieved
            # source - discard it in favor of the trustworthy
            # deterministic operational answer rather than surfacing an
            # unverified synthesis.
            logger.info(
                "Grounded copilot synthesis produced no valid citations; "
                "falling back to the deterministic operational answer."
            )
            return self._finalize(
                operational_response,
                EvidenceRequirement.OPERATIONAL_AND_DOCUMENT,
                grounded=False,
                document_evidence=DocumentEvidenceItem.from_context_items(
                    context.items
                ),
                citations=[],
            )

        return CopilotChatResponse(
            conversation_id=uuid4(),
            generated_at=datetime.now(UTC),
            intent=operational_response.intent,
            confidence=operational_response.confidence,
            tools_used=operational_response.tools_used,
            reasoning=[
                *operational_response.reasoning,
                CopilotReasoningStep(
                    step="Document Evidence Retrieval",
                    status="SUCCESS",
                ),
            ],
            tool_execution=operational_response.tool_execution,
            evidence=operational_response.evidence,
            recommendations=operational_response.recommendations,
            response=answer_text,
            evidence_requirement=EvidenceRequirement.OPERATIONAL_AND_DOCUMENT,
            grounded=True,
            document_evidence=DocumentEvidenceItem.from_context_items(
                context.items
            ),
            citations=[
                RagCitation(
                    document_id=citation.document_id,
                    filename=citation.filename,
                    page_number=citation.page_number,
                )
                for citation in citations
            ],
        )

    def _build_combined_user_prompt(
        self,
        operational_text: str,
        document_context_text: str,
        question: str,
    ) -> str:
        return (
            "OPERATIONAL EVIDENCE\n\n"
            f"{operational_text}\n\n"
            "DOCUMENT EVIDENCE\n\n"
            f"{document_context_text}\n\n"
            f"Question: {question}\n\n"
            "Answer using the operational evidence and the document "
            "sources above. Cite every document source you rely on by "
            "its identifier (e.g. SOURCE_1). Do not cite SOURCE_N for "
            "operational facts."
        )

    # ------------------------------------------------------------------
    # Response assembly helpers
    # ------------------------------------------------------------------

    def _normalize(self, response) -> CopilotChatResponse:
        """`CopilotOrchestratorService.chat` is typed to return
        `CopilotChatResponse`, but tests (and API compatibility) may
        stand in a plain dict with the same shape - accept either."""

        if isinstance(response, CopilotChatResponse):
            return response

        return CopilotChatResponse(**response)

    def _finalize(
        self,
        response: CopilotChatResponse,
        requirement: str,
        *,
        grounded: bool | None,
        document_evidence: list[DocumentEvidenceItem],
        citations: list[RagCitation],
    ) -> CopilotChatResponse:
        data = response.model_dump()
        data.update(
            evidence_requirement=requirement,
            grounded=grounded,
            document_evidence=document_evidence,
            citations=citations,
        )
        return CopilotChatResponse(**data)

    def _from_rag_result(self, rag_result, requirement: str) -> CopilotChatResponse:
        document_evidence = DocumentEvidenceItem.from_citations(
            rag_result.citations
        )
        citations = [
            RagCitation(
                document_id=citation.document_id,
                filename=citation.filename,
                page_number=citation.page_number,
            )
            for citation in rag_result.citations
        ]

        return CopilotChatResponse(
            conversation_id=uuid4(),
            generated_at=datetime.now(UTC),
            intent="DOCUMENT_QUERY",
            confidence=90 if rag_result.grounded else 0,
            tools_used=[],
            reasoning=[
                CopilotReasoningStep(
                    step="Document Evidence Retrieval",
                    status="SUCCESS" if rag_result.grounded else "NO_EVIDENCE",
                )
            ],
            tool_execution=[],
            evidence=CopilotEvidenceBundle(),
            recommendations=[],
            response=rag_result.answer,
            evidence_requirement=requirement,
            grounded=rag_result.grounded,
            document_evidence=document_evidence,
            citations=citations,
        )
