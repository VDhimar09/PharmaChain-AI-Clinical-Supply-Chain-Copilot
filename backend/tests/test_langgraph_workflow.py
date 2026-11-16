from __future__ import annotations

import pytest

from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

from app.ai.intent_engine import IntentEngine
from app.ai.langgraph.nodes import (
    approval_decision_node,
    _parse_approval,
    detect_intent_node,
    initialize_node,
    planning_node,
    response_composition_node,
    route_after_planning,
    route_after_tools,
    route_after_validation,
    tool_execution_node,
)
from app.ai.langgraph.workflow import build_copilot_workflow
from app.ai.planner.execution_plan import ExecutionPlan
from app.ai.response import ResponseComposer
from app.ai.tools.base_tool import BaseTool
from app.ai.tools.tool_registry import ToolRegistry


@pytest.mark.parametrize(
    ("decision", "expected"),
    [
        (True, True),
        (False, False),
        ({"approved": True}, True),
        ({"approved": False}, False),
    ],
)
def test_parse_approval_accepts_explicit_boolean_decisions(
    decision: object,
    expected: bool,
) -> None:
    assert _parse_approval(decision) is expected


@pytest.mark.parametrize(
    "decision",
    ["false", "true", None, 1, {"approved": "false"}],
)
def test_parse_approval_rejects_non_boolean_decisions(decision: object) -> None:
    with pytest.raises(ValueError, match="Approval decision must be a boolean"):
        _parse_approval(decision)


class StubPlanner:
    def __init__(self, tools: list[str] | None = None, fails: bool = False) -> None:
        self.tools = ["inventory"] if tools is None else tools
        self.fails = fails

    def build_plan(self, message: str) -> ExecutionPlan:
        if self.fails:
            raise RuntimeError("planner unavailable")
        plan = ExecutionPlan(user_request=message, tools=self.tools, reasoning="Deterministic plan.")
        return plan


class StubTool(BaseTool):
    def __init__(self, name: str = "inventory", fails: bool = False) -> None:
        self._name = name
        self.fails = fails
        self.calls: list[dict] = []

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return "Test tool"

    def run(self, **kwargs) -> dict:
        self.calls.append(kwargs)
        if self.fails:
            raise RuntimeError("tool unavailable")
        return {"total_available_quantity": 10, "total_inventory_items": 1, "low_stock_products": 0}


def _registry(*tools: StubTool) -> ToolRegistry:
    registry = ToolRegistry()
    for tool in tools:
        registry.register(tool)
    return registry


def _workflow(
    planner: StubPlanner,
    registry: ToolRegistry,
    checkpointer=None,
    tool_context: dict | None = None,
):
    return build_copilot_workflow(
        planner=planner,
        registry=registry,
        composer=ResponseComposer(),
        checkpointer=checkpointer,
        tool_context=tool_context,
    )


def test_initialize_node_resets_workflow_bookkeeping() -> None:
    assert initialize_node({"question": "stock"}) == {
        "executed_tools": [],
        "tool_results": {},
        "tool_execution": [],
        "iteration": 0,
        "validation_errors": [],
        "approval_required": False,
        "approval_status": "NOT_REQUIRED",
        "workflow_status": "RUNNING",
    }


def test_detect_intent_node_uses_existing_intent_engine() -> None:
    assert detect_intent_node({"question": "How much stock is available?"}) == {
        "intent": IntentEngine.INVENTORY
    }


def test_detect_intent_node_routes_blank_question_to_response() -> None:
    result = detect_intent_node({"question": " "})
    assert result["error_message"] == "A question is required."
    assert route_after_validation(result) == "response"


def test_planning_node_reuses_planner_and_captures_errors() -> None:
    success = planning_node({"question": "stock"}, planner=StubPlanner())
    assert success == {"planned_tools": ["inventory"], "plan_reasoning": "Deterministic plan."}

    failure = planning_node({"question": "stock"}, planner=StubPlanner(fails=True))
    assert "Planning failed" in failure["error_message"]
    assert route_after_planning(failure) == "response"


def test_tool_execution_node_runs_in_order_with_context() -> None:
    tool = StubTool()
    result = tool_execution_node(
        {"question": "stock", "planned_tools": ["inventory"], "context": {"db": "session"}},
        registry=_registry(tool),
    )
    assert result["executed_tools"] == ["inventory"]
    assert result["tool_results"]["inventory"]["total_available_quantity"] == 10
    assert result["tool_execution"][0]["status"] == "SUCCESS"
    assert tool.calls == [{"message": "stock", "db": "session"}]


def test_tool_execution_node_captures_failure_and_routes_to_response() -> None:
    result = tool_execution_node(
        {"question": "stock", "planned_tools": ["inventory"]}, registry=_registry(StubTool(fails=True))
    )
    assert "Tool execution failed for 'inventory'" in result["error_message"]
    assert result["tool_execution"][0]["status"] == "FAILED"
    assert route_after_tools(result) == "response"


def test_response_composition_node_returns_safe_error_response() -> None:
    result = response_composition_node(
        {"error_message": "planner failed"}, composer=ResponseComposer()
    )
    assert result == {
        "final_response": "I could not complete this request: planner failed",
        "workflow_status": "FAILED",
    }


def test_graph_executes_non_procurement_request() -> None:
    graph = _workflow(StubPlanner(), _registry(StubTool()))
    result = graph.invoke({"question": "How much stock is available?"})

    assert result["intent"] == IntentEngine.INVENTORY
    assert result["executed_tools"] == ["inventory"]
    assert result["approval_status"] == "NOT_REQUIRED"
    assert result["workflow_status"] == "COMPLETED"
    assert "Inventory is tracking" in result["final_response"]


def test_graph_injects_tool_context_without_checkpointing_it() -> None:
    tool = StubTool()
    graph = _workflow(
        StubPlanner(),
        _registry(tool),
        tool_context={"db": "session"},
    )

    graph.invoke({"question": "How much stock is available?"})

    assert tool.calls == [{"message": "How much stock is available?", "db": "session"}]


def test_graph_routes_unknown_plan_to_response_without_tools() -> None:
    graph = _workflow(StubPlanner(tools=[]), _registry())
    result = graph.invoke({"question": "something unclear"})
    assert result["executed_tools"] == []
    assert result["workflow_status"] == "COMPLETED"


def test_procurement_approval_interrupt_can_resume_with_memory_checkpointer() -> None:
    graph = _workflow(StubPlanner(tools=["procurement"]), _registry(StubTool("procurement")), MemorySaver())
    config = {"configurable": {"thread_id": "approval-test"}}

    paused = graph.invoke({"question": "Should I reorder vaccine?"}, config=config)
    assert paused["__interrupt__"]
    assert paused["__interrupt__"][0].value["action"] == "simulated_procurement_approval"
    state = graph.get_state(config).values
    assert state["approval_status"] == "PENDING"
    assert state["workflow_status"] == "WAITING_FOR_APPROVAL"

    resumed = graph.invoke(Command(resume={"approved": True}), config=config)
    assert resumed["approval_status"] == "APPROVED"
    assert resumed["workflow_status"] == "COMPLETED"
    assert "no procurement transaction was executed" in resumed["final_response"]


def test_procurement_approval_rejection_is_simulated() -> None:
    graph = _workflow(StubPlanner(tools=["procurement"]), _registry(StubTool("procurement")), MemorySaver())
    config = {"configurable": {"thread_id": "rejection-test"}}
    graph.invoke({"question": "Should I reorder vaccine?"}, config=config)

    resumed = graph.invoke(Command(resume={"approved": False}), config=config)
    assert resumed["approval_status"] == "REJECTED"
    assert "not approved" in resumed["final_response"]
