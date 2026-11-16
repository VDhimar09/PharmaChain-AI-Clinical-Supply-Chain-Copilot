"""State contracts for the optional, stateful copilot workflow."""

from typing import Any, Literal, TypedDict


ApprovalStatus = Literal["NOT_REQUIRED", "PENDING", "APPROVED", "REJECTED"]
WorkflowStatus = Literal["RUNNING", "WAITING_FOR_APPROVAL", "COMPLETED", "FAILED"]


class ToolExecutionRecord(TypedDict):
    """Serializable result metadata for a single tool invocation."""

    tool: str
    tool_key: str
    status: Literal["SUCCESS", "FAILED"]
    execution_time_ms: float
    data: dict[str, Any]


class CopilotState(TypedDict, total=False):
    """Information carried through the PharmaChain LangGraph workflow."""

    question: str
    context: dict[str, Any]
    intent: str
    planned_tools: list[str]
    plan_reasoning: str
    executed_tools: list[str]
    tool_results: dict[str, Any]
    tool_execution: list[ToolExecutionRecord]
    iteration: int
    validation_errors: list[str]
    error_message: str
    approval_required: bool
    approval_status: ApprovalStatus
    approval_request: dict[str, Any]
    workflow_status: WorkflowStatus
    composed_response: dict[str, Any]
    final_response: str
