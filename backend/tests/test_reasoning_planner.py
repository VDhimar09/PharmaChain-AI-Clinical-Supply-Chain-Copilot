import pytest

from app.ai.exceptions import PlanningException
from app.ai.intent_engine import IntentEngine
from app.ai.planner.execution_plan import ExecutionPlan
from app.ai.planner.planner_context import PlannerContext
from app.ai.planner.planning_strategy import PlanningStrategy
from app.ai.planner.reasoning_planner import ReasoningPlanner


class StubPlanningStrategy(PlanningStrategy):
    def __init__(self) -> None:
        self.last_context: PlannerContext | None = None

    def build_plan(self, context: PlannerContext) -> ExecutionPlan:
        self.last_context = context
        plan = ExecutionPlan(user_request=context.user_message)
        plan.add_tool("inventory")
        plan.reasoning = "Inventory request."
        return plan


class FailingPlanningStrategy(PlanningStrategy):
    def build_plan(self, context: PlannerContext) -> ExecutionPlan:
        raise RuntimeError("planner failed")


def test_reasoning_planner_builds_context_and_delegates() -> None:
    strategy = StubPlanningStrategy()
    planner = ReasoningPlanner(
        strategy=strategy,
        available_tools=("inventory", "warehouse"),
    )

    plan = planner.build_plan("How much inventory do we have?")

    assert plan.tools == ["inventory"]
    assert strategy.last_context is not None
    assert strategy.last_context.user_message == "How much inventory do we have?"
    assert strategy.last_context.detected_intent == IntentEngine.INVENTORY
    assert strategy.last_context.available_tools == ("inventory", "warehouse")


def test_reasoning_planner_raises_planning_exception() -> None:
    planner = ReasoningPlanner(strategy=FailingPlanningStrategy())

    with pytest.raises(PlanningException) as exc_info:
        planner.build_plan("Should I reorder stock?")

    assert "Unable to build an execution plan." in str(exc_info.value)
    assert isinstance(exc_info.value.__cause__, RuntimeError)
