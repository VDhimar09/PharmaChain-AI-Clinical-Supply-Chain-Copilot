from app.ai.langgraph.state import CopilotState


def initialize_node(state: CopilotState) -> dict:
    """Initialize bookkeeping state for a new workflow execution."""

    return {
        "executed_tools": [],
        "tool_results": {},
        "iteration": 0,
        "validation_errors": [],
    }
