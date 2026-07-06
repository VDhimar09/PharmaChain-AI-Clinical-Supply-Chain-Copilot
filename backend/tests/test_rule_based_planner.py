from app.ai.intent_engine import IntentEngine
from app.ai.planner.planner_context import PlannerContext
from app.ai.planner.rule_based_planner import RuleBasedPlanner


def test_rule_based_planner_builds_inventory_plan() -> None:
    planner = RuleBasedPlanner()
    context = PlannerContext(
        user_message="How much inventory do we have?",
        detected_intent=IntentEngine.INVENTORY,
        available_tools=("inventory", "warehouse", "shipment", "procurement", "ai_insights"),
    )

    plan = planner.build_plan(context)

    assert plan.tools == ["inventory", "ai_insights"]
    assert plan.reasoning == "Inventory status request."


def test_rule_based_planner_builds_procurement_plan() -> None:
    planner = RuleBasedPlanner()
    context = PlannerContext(
        user_message="Should I reorder stock?",
        detected_intent=IntentEngine.PROCUREMENT,
        available_tools=("inventory", "warehouse", "shipment", "procurement", "ai_insights"),
    )

    plan = planner.build_plan(context)

    assert plan.tools == ["inventory", "warehouse", "shipment", "procurement"]
    assert (
        plan.reasoning
        == "Procurement decisions require inventory, warehouse capacity, "
        "shipment analysis, and procurement policy."
    )


def test_rule_based_planner_returns_empty_plan_for_unknown_intent() -> None:
    planner = RuleBasedPlanner()
    context = PlannerContext(
        user_message="Hello",
        detected_intent=IntentEngine.UNKNOWN,
        available_tools=("inventory", "warehouse", "shipment", "procurement", "ai_insights"),
    )

    plan = planner.build_plan(context)

    assert plan.tools == []
    assert plan.reasoning == "Unable to determine the required tools."


def test_rule_based_planner_builds_executive_summary_plan() -> None:
    planner = RuleBasedPlanner()
    context = PlannerContext(
        user_message="What should I prioritise today?",
        detected_intent=IntentEngine.EXECUTIVE_SUMMARY,
        available_tools=("inventory", "warehouse", "shipment", "procurement", "ai_insights"),
    )

    plan = planner.build_plan(context)

    assert plan.tools == ["inventory", "warehouse", "shipment", "ai_insights"]
    assert plan.reasoning == (
        "Executive summary requires inventory, warehouse, shipment, "
        "and AI insights evidence."
    )
