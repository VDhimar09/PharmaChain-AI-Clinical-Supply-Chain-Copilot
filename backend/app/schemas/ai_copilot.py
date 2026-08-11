from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.rag import RagCitation
from app.schemas.grounded_copilot import DocumentEvidenceItem


class CopilotChatRequest(BaseModel):
    message: str


class CopilotReasoningStep(BaseModel):
    step: str
    status: str


class CopilotToolExecution(BaseModel):
    tool: str
    status: str
    execution_time_ms: float


class CopilotEvidenceBundle(BaseModel):
    inventory: dict[str, Any] = Field(default_factory=dict)
    warehouse: dict[str, Any] = Field(default_factory=dict)
    shipments: dict[str, Any] = Field(default_factory=dict)
    procurement: dict[str, Any] = Field(default_factory=dict)
    ai_insights: dict[str, Any] = Field(default_factory=dict)


class CopilotChatResponse(BaseModel):
    conversation_id: UUID
    generated_at: datetime
    intent: str
    confidence: int
    tools_used: list[str]
    reasoning: list[CopilotReasoningStep]
    tool_execution: list[CopilotToolExecution]
    evidence: CopilotEvidenceBundle
    recommendations: list[str]
    response: str

    # Phase 3: RAG-grounded Copilot integration. All defaulted so every
    # existing `/api/ai/copilot/chat` caller that only used the
    # operational fields above keeps working unchanged - an
    # operational-only question still gets `evidence_requirement`
    # defaulting to "OPERATIONAL", `grounded=None` (not applicable - the
    # deterministic Copilot response was never LLM-generated), and empty
    # `document_evidence`/`citations`.
    evidence_requirement: str = "OPERATIONAL"
    grounded: bool | None = None
    document_evidence: list[DocumentEvidenceItem] = Field(default_factory=list)
    citations: list[RagCitation] = Field(default_factory=list)
