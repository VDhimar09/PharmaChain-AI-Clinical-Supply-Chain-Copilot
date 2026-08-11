"""Phase 3.2: evidence requirement detection
(`app.ai.evidence_requirement`).

Deterministic, offline - no DB, no LLM.
"""

import pytest

from app.ai.evidence_requirement import EvidenceRequirement
from app.ai.evidence_requirement import EvidenceRequirementDetector


@pytest.mark.parametrize(
    "message",
    [
        "How many delayed shipments do we have?",
        "Show me delayed shipments.",
        "What should I prioritise today?",
        "Summarize today's operations.",
        "Hello",
        "Can we receive another shipment of Vaccine A?",
    ],
)
def test_operational_only_questions_do_not_require_document_evidence(message):
    assert EvidenceRequirementDetector.detect(message) == EvidenceRequirement.OPERATIONAL


@pytest.mark.parametrize(
    "message",
    [
        "What does the cold-chain SOP require?",
        "What does our compliance policy say about temperature excursions?",
        "Summarize the GDP guidelines.",
        "What is in the compliance manual?",
    ],
)
def test_document_only_questions_require_only_document_evidence(message):
    assert EvidenceRequirementDetector.detect(message) == EvidenceRequirement.DOCUMENT


@pytest.mark.parametrize(
    "message",
    [
        "Why is shipment SH-102 at risk, and what does our cold-chain SOP require?",
        "What does the cold-chain SOP require, and how many delayed shipments do we have?",
    ],
)
def test_combined_questions_require_both_evidence_sources(message):
    assert (
        EvidenceRequirementDetector.detect(message)
        == EvidenceRequirement.OPERATIONAL_AND_DOCUMENT
    )


def test_detection_is_case_insensitive():
    assert (
        EvidenceRequirementDetector.detect("WHAT DOES THE COLD-CHAIN SOP REQUIRE?")
        == EvidenceRequirement.DOCUMENT
    )


def test_unrecognized_message_defaults_to_operational():
    # Preserves today's behavior: every message currently flows through
    # the deterministic Copilot pipeline, which itself has an "unable to
    # determine tools" fallback - never silently routed to RAG.
    assert (
        EvidenceRequirementDetector.detect("asdkjfh qwoeiur")
        == EvidenceRequirement.OPERATIONAL
    )
