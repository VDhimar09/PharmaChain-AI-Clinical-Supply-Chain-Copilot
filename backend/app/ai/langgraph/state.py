from typing import Any, TypedDict


class CopilotState(TypedDict, total=False):
    """Information carried through the PharmaChain LangGraph workflow."""

    question: str
    intent: str
    planned_tools: list[str]
    executed_tools: list[str]
    tool_results: dict[str, Any]
    iteration: int
    validation_errors: list[str]
    final_response: str
