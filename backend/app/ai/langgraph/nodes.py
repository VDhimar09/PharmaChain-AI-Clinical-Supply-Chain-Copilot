
"""Small, dependency-injected nodes used by the LangGraph workflow."""

from __future__ import annotations

from time import perf_counter
from typing import Any, Literal, Mapping

from langgraph.types import interrupt

from app.ai.intent_engine import IntentEngine
from app.ai.langgraph.state import CopilotState
from app.ai.planner.reasoning_planner import ReasoningPlanner
from app.ai.response import ResponseComposer
from app.ai.tools.tool_registry import ToolRegistry


def initialize_node(state: CopilotState) -> dict[str, Any]:
    """Initialize bookkeeping state for a new workflow execution."""

    return {
        "executed_tools": [],
        "tool_results": {},
        "tool_execution": [],
        "iteration": 0,
        "validation_errors": [],
        "approval_required": False,
        "approval_status": "NOT_REQUIRED",
        "workflow_status": "RUNNING",
    }


def detect_intent_node(state: CopilotState) -> dict[str, Any]:
    """Detect intent using the existing deterministic intent engine."""

    question = state.get("question", "").strip()

    if not question:
        return {
            "validation_errors": ["A question is required."],
            "error_message": "A question is required.",
        }

    return {"intent": IntentEngine.detect(question)}


def planning_node(
    state: CopilotState,
    *,
    planner: ReasoningPlanner,
) -> dict[str, Any]:
    """Build the ordered tool plan through the existing planner."""

    try:
        plan = planner.build_plan(state["question"])

        return {
            "planned_tools": plan.tools,
            "plan_reasoning": plan.reasoning,
        }

    except Exception as exc:
        return _error_update(state, f"Planning failed: {exc}")


def tool_execution_node(
    state: CopilotState,
    *,
    registry: ToolRegistry,
    context: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Execute the planner's tools in order without creating external transactions."""

    results: dict[str, Any] = {}
    executions: list[dict[str, Any]] = []
    executed: list[str] = []

    execution_context = (
        context if context is not None else state.get("context", {})
    )

    for tool_name in state.get("planned_tools", []):
        started_at = perf_counter()

        try:
            tool = registry.get(tool_name)
            result = tool.run(
                message=state["question"],
                **execution_context,
            )

            duration = round(
                (perf_counter() - started_at) * 1000,
                2,
            )

            results[tool_name] = result
            executed.append(tool_name)

            executions.append(
                {
                    "tool": tool.display_name,
                    "tool_key": tool_name,
                    "status": "SUCCESS",
                    "execution_time_ms": duration,
                    "data": result,
                }
            )

        except Exception as exc:
            duration = round(
                (perf_counter() - started_at) * 1000,
                2,
            )

            executions.append(
                {
                    "tool": tool_name.replace("_", " ").title() + " Tool",
                    "tool_key": tool_name,
                    "status": "FAILED",
                    "execution_time_ms": duration,
                    "data": {},
                }
            )

            return {
                "tool_results": results,
                "executed_tools": executed,
                "tool_execution": executions,
                **_error_update(
                    state,
                    f"Tool execution failed for '{tool_name}': {exc}",
                ),
            }

    requires_approval = state.get("intent") == IntentEngine.PROCUREMENT

    return {
        "tool_results": results,
        "executed_tools": executed,
        "tool_execution": executions,
        "approval_required": requires_approval,
        "approval_status": "PENDING" if requires_approval else "NOT_REQUIRED",
        "workflow_status": (
            "WAITING_FOR_APPROVAL" if requires_approval else "RUNNING"
        ),
    }


def approval_decision_node(state: CopilotState) -> dict[str, Any]:
    """Pause for a simulated human procurement approval when required.

    This intentionally approves or rejects only the workflow recommendation.
    It never calls a procurement write API or mutates a procurement request.
    """

    if state.get("intent") != IntentEngine.PROCUREMENT:
        return {
            "approval_required": False,
            "approval_status": "NOT_REQUIRED",
        }

    request = {
        "action": "simulated_procurement_approval",
        "message": (
            "Approve this simulated procurement recommendation? "
            "No transaction will be executed."
        ),
        "tool_results": state.get("tool_results", {}).get("procurement", {}),
    }

    decision = interrupt(request)
    approved = _parse_approval(decision)

    return {
        "approval_required": True,
        "approval_request": request,
        "approval_status": "APPROVED" if approved else "REJECTED",
    }


def response_composition_node(
    state: CopilotState,
    *,
    composer: ResponseComposer,
) -> dict[str, Any]:
    """Compose a response from the same result shape used by the legacy service."""

    if state.get("error_message"):
        response = (
            f"I could not complete this request: {state['error_message']}"
        )

        return {
            "final_response": response,
            "workflow_status": "FAILED",
        }

    result = {
        "user_request": state.get("question", ""),
        "reasoning": state.get("plan_reasoning", ""),
        "plan": state.get("planned_tools", []),
        "tool_results": state.get("tool_results", {}),
        "tool_execution": state.get("tool_execution", []),
    }

    composed = composer.compose_copilot_response(
        intent=state.get("intent", IntentEngine.UNKNOWN),
        result=result,
    )

    response = composed["response"]

    if state.get("approval_status") == "APPROVED":
        response += (
            " Simulated approval was recorded; "
            "no procurement transaction was executed."
        )

    elif state.get("approval_status") == "REJECTED":
        response += (
            " The simulated procurement recommendation was not approved; "
            "no transaction was executed."
        )

    return {
        "composed_response": composed,
        "final_response": response,
        "workflow_status": "COMPLETED",
    }


def route_after_validation(
    state: CopilotState,
) -> Literal["planning", "response"]:
    """Route invalid requests directly to response composition."""

    return "response" if state.get("error_message") else "planning"


def route_after_planning(
    state: CopilotState,
) -> Literal["tools", "response"]:
    """Route failed or empty plans directly to response composition."""

    if state.get("error_message") or not state.get("planned_tools"):
        return "response"

    return "tools"


def route_after_tools(
    state: CopilotState,
) -> Literal["approval", "response"]:
    """Route failed tool executions to response composition."""

    return "response" if state.get("error_message") else "approval"


def _error_update(
    state: CopilotState,
    message: str,
) -> dict[str, Any]:
    """Record a workflow validation or execution error."""

    return {
        "validation_errors": [
            *state.get("validation_errors", []),
            message,
        ],
        "error_message": message,
    }


def _parse_approval(decision: Any) -> bool:
    """Accept only an explicit Boolean approval decision."""

    if isinstance(decision, Mapping):
        decision = decision.get("approved")

    if not isinstance(decision, bool):
        raise ValueError("Approval decision must be a boolean.")

    return decision
