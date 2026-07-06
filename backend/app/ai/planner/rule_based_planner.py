"""Deterministic rule-based planning strategy."""

from __future__ import annotations

from app.ai.intent_engine import IntentEngine
from app.ai.planner.execution_plan import ExecutionPlan
from app.ai.planner.planner_context import PlannerContext
from app.ai.planner.planning_strategy import PlanningStrategy


class RuleBasedPlanner(PlanningStrategy):
    """
    Planning strategy that preserves the existing rule-based behavior.

    This class contains the deterministic planning rules that were
    previously embedded directly in ``ReasoningPlanner``.
    """

    def build_plan(self, context: PlannerContext) -> ExecutionPlan:
        """
        Build an execution plan from the detected intent.

        Args:
            context: Structured planning inputs.

        Returns:
            An execution plan with the same behavior as the legacy planner.
        """

        plan = ExecutionPlan(user_request=context.user_message)
        intent = context.detected_intent

        if intent == IntentEngine.EXECUTIVE_SUMMARY:
            plan.add_tool("inventory")
            plan.add_tool("warehouse")
            plan.add_tool("shipment")
            plan.add_tool("ai_insights")
            plan.reasoning = (
                "Executive summary requires inventory, warehouse, shipment, "
                "and AI insights evidence."
            )

        elif intent == IntentEngine.AI_INSIGHTS:
            plan.add_tool("ai_insights")
            plan.reasoning = "AI insights request."

        elif intent == IntentEngine.RISK_SUMMARY:
            plan.add_tool("inventory")
            plan.add_tool("warehouse")
            plan.add_tool("shipment")
            plan.add_tool("ai_insights")
            plan.reasoning = (
                "Risk summary requires operational evidence across inventory, "
                "warehouse, shipments, and AI insights."
            )

        elif intent == IntentEngine.INVENTORY:
            plan.add_tool("inventory")
            plan.add_tool("ai_insights")
            plan.reasoning = "Inventory status request."

        elif intent == IntentEngine.WAREHOUSE:
            plan.add_tool("warehouse")
            plan.add_tool("ai_insights")
            plan.reasoning = "Warehouse status request."

        elif intent == IntentEngine.SHIPMENT:
            plan.add_tool("shipment")
            plan.add_tool("ai_insights")
            plan.reasoning = "Shipment status request."

        elif intent == IntentEngine.PROCUREMENT_STATUS:
            plan.add_tool("ai_insights")
            plan.reasoning = "Procurement status request."

        elif intent == IntentEngine.PROCUREMENT:
            plan.add_tool("inventory")
            plan.add_tool("warehouse")
            plan.add_tool("shipment")
            plan.add_tool("procurement")

            plan.reasoning = (
                "Procurement decisions require inventory, "
                "warehouse capacity, shipment analysis, "
                "and procurement policy."
            )

        else:
            plan.reasoning = "Unable to determine the required tools."

        return plan
