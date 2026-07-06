from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


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
