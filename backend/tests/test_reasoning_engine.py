import pytest

from app.ai.exceptions import ToolExecutionException
from app.ai.planner.execution_plan import ExecutionPlan
from app.ai.reasoning.reasoning_engine import ReasoningEngine
from app.ai.tools.base_tool import BaseTool
from app.ai.tools.tool_registry import ToolRegistry


class StubPlanner:
    def build_plan(self, message: str) -> ExecutionPlan:
        plan = ExecutionPlan(user_request=message)
        plan.add_tool("inventory")
        plan.add_tool("shipment")
        plan.reasoning = "Procurement decisions require evidence."
        return plan


class SuccessfulTool(BaseTool):
    def __init__(self, tool_name: str, payload: dict) -> None:
        self._tool_name = tool_name
        self.payload = payload
        self.calls: list[dict] = []

    @property
    def name(self) -> str:
        return self._tool_name

    @property
    def description(self) -> str:
        return f"{self._tool_name} tool"

    def run(self, *args, **kwargs) -> dict:
        self.calls.append(kwargs)
        return self.payload


class FailingTool(SuccessfulTool):
    def run(self, *args, **kwargs) -> dict:
        raise RuntimeError("tool failed")


def test_reasoning_engine_executes_tools_in_plan_order() -> None:
    registry = ToolRegistry()
    inventory_tool = SuccessfulTool("inventory", {"available": 10})
    shipment_tool = SuccessfulTool("shipment", {"incoming": 2})
    registry.register(inventory_tool)
    registry.register(shipment_tool)

    engine = ReasoningEngine(planner=StubPlanner(), registry=registry)
    db_context = object()

    result = engine.execute("Can we receive another shipment?", db=db_context)

    assert result["user_request"] == "Can we receive another shipment?"
    assert result["plan"] == ["inventory", "shipment"]
    assert result["tool_results"]["inventory"] == {"available": 10}
    assert result["tool_results"]["shipment"] == {"incoming": 2}
    assert inventory_tool.calls == [
        {"message": "Can we receive another shipment?", "db": db_context}
    ]
    assert shipment_tool.calls == [
        {"message": "Can we receive another shipment?", "db": db_context}
    ]


def test_reasoning_engine_raises_tool_execution_exception() -> None:
    registry = ToolRegistry()
    registry.register(FailingTool("inventory", {}))

    engine = ReasoningEngine(planner=StubPlanner(), registry=registry)

    with pytest.raises(ToolExecutionException) as exc_info:
        engine.execute("How much inventory do we have?", db=object())

    assert "Tool execution failed for 'inventory'." in str(exc_info.value)
    assert isinstance(exc_info.value.__cause__, RuntimeError)
