"""Deterministic detection of which evidence source(s) a Copilot question
requires: live operational data, uploaded documentation, or both.

This is intentionally separate from `IntentEngine`, which classifies
*which operational tools* a question needs (inventory, shipment, ...).
`EvidenceRequirementDetector` classifies a different, orthogonal axis -
*where the evidence to answer the question should come from* - and reuses
`IntentEngine` read-only as a signal, never replacing or duplicating it.

Kept deterministic (keyword-based) rather than an LLM classifier, matching
the rest of the reasoning/planning layer's style (`IntentEngine`,
`RuleBasedPlanner`).
"""

from __future__ import annotations

from app.ai.intent_engine import IntentEngine


class EvidenceRequirement:
    OPERATIONAL = "OPERATIONAL"
    DOCUMENT = "DOCUMENT"
    OPERATIONAL_AND_DOCUMENT = "OPERATIONAL_AND_DOCUMENT"


class EvidenceRequirementDetector:
    """Detects whether a question needs operational evidence, document
    evidence, or both.

    Examples:
        "How many delayed shipments do we have?" -> OPERATIONAL
        "What does the cold-chain SOP require?" -> DOCUMENT
        "Why is SH-102 at risk and what does the cold-chain SOP require?"
            -> OPERATIONAL_AND_DOCUMENT
    """

    _DOCUMENT_KEYWORDS = (
        "sop",
        "sops",
        "policy",
        "policies",
        "procedure",
        "procedures",
        "documentation",
        "document",
        "documents",
        "pdf",
        "guideline",
        "guidelines",
        "compliance",
        "regulation",
        "regulations",
        "manual",
        "protocol",
        "protocols",
    )

    @classmethod
    def detect(cls, message: str) -> str:
        text = message.lower().strip()

        mentions_documents = any(
            keyword in text for keyword in cls._DOCUMENT_KEYWORDS
        )

        if not mentions_documents:
            return EvidenceRequirement.OPERATIONAL

        mentions_operational_topic = (
            IntentEngine.detect(message) != IntentEngine.UNKNOWN
        )

        if mentions_operational_topic:
            return EvidenceRequirement.OPERATIONAL_AND_DOCUMENT

        return EvidenceRequirement.DOCUMENT
