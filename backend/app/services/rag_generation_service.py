"""Grounded RAG generation: retrieval -> bounded context -> LLM -> citations.

This is intentionally independent of the Executive Copilot. It answers
questions using only evidence retrieved from ingested documents, and
refuses to answer - without ever calling the LLM - when no supporting
evidence exists.

Anti-hallucination strategy, in order:
1. No retrieved evidence (including evidence filtered out by
   `RetrieverService`'s similarity threshold - "no evidence" and "weak
   evidence" both surface as an empty result list) -> fixed fallback
   response, no LLM call at all.
2. The LLM is instructed to answer only from the supplied sources and to
   cite them as SOURCE_N.
3. Citations are never trusted from the model's prose. The answer is
   scanned for SOURCE_N references, which are resolved strictly against
   the `ContextItem`s actually built for this request. Unknown or
   fabricated source ids are silently dropped.
4. If, after resolution, zero citations remain (the model answered
   without grounding itself in a real source, or repeated the fallback
   phrase), the response is downgraded to the fixed fallback rather than
   surfaced as a trusted, "grounded" answer.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.services.citation_resolver import Citation
from app.services.citation_resolver import resolve_citations
from app.services.context_builder import ContextBuilder
from app.services.llm.base_provider import LLMError
from app.services.llm.base_provider import LLMProvider
from app.services.retriever_service import RetrieverService


logger = get_logger("rag_generation_service")

FALLBACK_ANSWER = (
    "I couldn't find that information in the uploaded documentation."
)

SYSTEM_PROMPT = (
    "You are PharmaChain's documentation assistant. Answer only using the "
    "SOURCE documentation supplied below the question. Do not use "
    "external or general knowledge. Do not invent procedures, numbers, "
    "policies, or citations. When you rely on a source, reference its "
    "identifier exactly as written, e.g. SOURCE_1. If the supplied "
    "documentation does not support an answer, respond with exactly: "
    f'"{FALLBACK_ANSWER}"'
)


class RagGenerationError(Exception):
    """Raised when a grounded answer could not be generated (e.g. LLM
    failure). Maps to HTTP 503 at the API layer."""


# `Citation` used to be defined directly in this module. It now lives in
# `citation_resolver` so `GroundedCopilotService` can share the exact same
# citation-trust logic instead of a second, competing implementation -
# re-imported above so existing `from app.services.rag_generation_service
# import Citation` call sites keep working unchanged.


@dataclass(frozen=True)
class RagQueryResult:
    answer: str
    grounded: bool
    citations: list[Citation]


class RagGenerationService:

    def __init__(
        self,
        db: Session,
        retriever_service: RetrieverService | None = None,
        context_builder: ContextBuilder | None = None,
        llm_provider: LLMProvider | None = None,
    ):
        self.db = db
        self._retriever_service = retriever_service
        self.context_builder = context_builder or ContextBuilder()
        self._llm_provider = llm_provider

    @property
    def retriever_service(self) -> RetrieverService:
        if self._retriever_service is None:
            self._retriever_service = RetrieverService(self.db)

        return self._retriever_service

    @property
    def llm_provider(self) -> LLMProvider:
        if self._llm_provider is None:
            # Imported lazily so environments without an OpenAI key can
            # still import this module (e.g. to inject a fake provider).
            from app.services.llm.openai_provider import OpenAIChatProvider

            self._llm_provider = OpenAIChatProvider()

        return self._llm_provider

    def query(self, question: str) -> RagQueryResult:
        normalized_question = question.strip()

        if not normalized_question:
            return self._fallback()

        started_at = time.monotonic()

        results = self.retriever_service.search(normalized_question)

        if not results:
            logger.info("RAG query has no supporting evidence; skipping LLM call.")
            return self._fallback()

        context = self.context_builder.build(results)

        if not context.items:
            logger.info("RAG query context is empty after bounding; skipping LLM call.")
            return self._fallback()

        llm_started_at = time.monotonic()

        try:
            raw_answer = self.llm_provider.generate(
                system_prompt=SYSTEM_PROMPT,
                user_prompt=self._build_user_prompt(
                    context.text,
                    normalized_question,
                ),
            )
        except LLMError as exc:
            logger.error(
                "RAG generation failed after retrieving %s chunk(s): %s",
                len(results),
                type(exc).__name__,
            )
            raise RagGenerationError(
                "Failed to generate a grounded answer."
            ) from exc

        llm_elapsed_ms = (time.monotonic() - llm_started_at) * 1000

        answer_text = raw_answer.strip()
        citations = resolve_citations(answer_text, context.items)
        grounded = bool(citations) and not self._is_fallback(answer_text)

        total_elapsed_ms = (time.monotonic() - started_at) * 1000
        logger.info(
            "RAG query completed: retrieved=%s context_chunks=%s "
            "context_chars=%s citations=%s grounded=%s "
            "llm_ms=%.1f total_ms=%.1f",
            len(results),
            len(context.items),
            len(context.text),
            len(citations),
            grounded,
            llm_elapsed_ms,
            total_elapsed_ms,
        )

        if not grounded:
            return self._fallback()

        return RagQueryResult(
            answer=answer_text,
            grounded=True,
            citations=citations,
        )

    def _fallback(self) -> RagQueryResult:
        return RagQueryResult(
            answer=FALLBACK_ANSWER,
            grounded=False,
            citations=[],
        )

    def _is_fallback(self, answer: str) -> bool:
        return FALLBACK_ANSWER.lower() in answer.lower()

    def _build_user_prompt(self, context_text: str, question: str) -> str:
        return (
            f"{context_text}\n\n"
            f"Question: {question}\n\n"
            "Answer using only the sources above, citing every source you "
            "rely on by its identifier (e.g. SOURCE_1)."
        )

