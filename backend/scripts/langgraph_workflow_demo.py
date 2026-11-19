"""Run PharmaChain's stateful LangGraph workflow without external services.

This script is intentionally self-contained and uses static in-memory tools.
It is suitable for demonstrating the workflow locally without a database,
network access, or real procurement operations.

Run from the backend directory:
    python scripts/langgraph_workflow_demo.py
"""

from __future__ import annotations

import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any
from uuid import uuid4

# Make ``app`` importable when this file is launched directly from scripts/.
BACKEND_DIRECTORY = Path(__file__).resolve().parents[1]
if str(BACKEND_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIRECTORY))

from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

from app.ai.langgraph.workflow import build_copilot_workflow
from app.ai.planner.reasoning_planner import ReasoningPlanner
from app.ai.response import ResponseComposer
from app.ai.tools.base_tool import BaseTool
from app.ai.tools.tool_registry import ToolRegistry


class DemoTool(BaseTool):
    """A deterministic, in-memory replacement for a production tool."""

    def __init__(
        self,
        tool_name: str,
        payload: dict[str, Any],
    ) -> None:
        self._tool_name = tool_name
        self._payload = payload

    @property
    def name(self) -> str:
        return self._tool_name

    @property
    def description(self) -> str:
        return f"Static demonstration data for {self._tool_name}."

    def run(self, **_: Any) -> dict[str, Any]:
        """Return a copy so each workflow run receives independent evidence."""
        return deepcopy(self._payload)


def build_demo_registry() -> ToolRegistry:
    """Register every tool selected by the deterministic planner scenarios."""
    registry = ToolRegistry()

    registry.register(
        DemoTool(
            "inventory",
            {
                "total_available_quantity": 1_240,
                "total_inventory_items": 28,
                "low_stock_products": 2,
            },
        )
    )
    registry.register(
        DemoTool(
            "warehouse",
            {
                "occupancy_percentage": 76,
                "available_capacity": 240,
            },
        )
    )
    registry.register(
        DemoTool(
            "shipment",
            {
                "inbound_shipments": 3,
                "outbound_shipments": 2,
                "delayed_shipments": 0,
            },
        )
    )
    registry.register(
        DemoTool(
            "procurement",
            {
                "decision": "REVIEW",
                "confidence": 0.82,
                "reason": "Stock is low enough to review the proposed replenishment.",
            },
        )
    )
    registry.register(
        DemoTool(
            "ai_insights",
            {
                "confidence": 91,
                "recommendations": [
                    {
                        "title": "Monitor low-stock products",
                        "message": "Review replenishment timing for the two low-stock products.",
                    }
                ],
            },
        )
    )
    return registry


def print_section(title: str) -> None:
    print(f"\n{'=' * 72}\n{title}\n{'=' * 72}")


def main() -> None:
    """Run inventory plus simulated procurement approval and rejection demos."""
    # These are the real workflow collaborators. Only the tool implementations
    # are demo fakes, so no database or external systems are contacted.
    workflow = build_copilot_workflow(
        planner=ReasoningPlanner(),
        registry=build_demo_registry(),
        composer=ResponseComposer(),
        checkpointer=MemorySaver(),
    )

    print_section("1. Inventory workflow")
    inventory_config = {
        "configurable": {
            "thread_id": f"inventory-demo-{uuid4()}",
        }
    }
    inventory_result = workflow.invoke(
        {"question": "How much inventory do we have?"},
        config=inventory_config,
    )
    print(f"Intent: {inventory_result['intent']}")
    print(f"Planned tools: {inventory_result['planned_tools']}")
    print(f"Executed tools: {inventory_result['executed_tools']}")
    print("Final response:")
    print(inventory_result["final_response"])

    print_section("2. Procurement workflow with simulated human approval")
    # A distinct thread ID lets MemorySaver retain this one workflow's pause
    # state until it is resumed below.
    config = {
        "configurable": {
            "thread_id": f"procurement-demo-{uuid4()}",
        }
    }
    paused = workflow.invoke(
        {"question": "Should I reorder 10 pallets of Vaccine A next month?"},
        config=config,
    )

    interrupts = paused.get("__interrupt__", ())
    if not interrupts:
        raise RuntimeError("Expected the procurement workflow to pause for approval.")

    print("Approval request:")
    print(json.dumps(interrupts[0].value, indent=2, default=str))
    print("Checkpoint state:")
    print(json.dumps(workflow.get_state(config).values, indent=2, default=str))

    # This resumes only the simulated workflow decision. DemoTool has no write
    # behaviour and the workflow never sends a procurement transaction.
    completed = workflow.invoke(
        Command(resume={"approved": True}),
        config=config,
    )
    print(f"Final approval status: {completed['approval_status']}")
    print("Final response:")
    print(completed["final_response"])

    print_section("3. Procurement workflow with simulated human rejection")
    # This separate thread isolates the rejection checkpoint from the approval
    # scenario above while using the same deterministic procurement question.
    rejection_config = {
        "configurable": {
            "thread_id": f"procurement-rejection-demo-{uuid4()}",
        }
    }
    rejected_pause = workflow.invoke(
        {"question": "Should I reorder 10 pallets of Vaccine A next month?"},
        config=rejection_config,
    )

    rejection_interrupts = rejected_pause.get("__interrupt__", ())
    if not rejection_interrupts:
        raise RuntimeError("Expected the procurement workflow to pause for rejection.")

    print("Approval request:")
    print(json.dumps(rejection_interrupts[0].value, indent=2, default=str))
    print("Pending checkpoint state:")
    print(
        json.dumps(
            workflow.get_state(rejection_config).values,
            indent=2,
            default=str,
        )
    )

    # Rejecting follows the existing workflow branch. As with approval, this
    # changes only demo state: no procurement transaction or write occurs.
    rejected = workflow.invoke(
        Command(resume={"approved": False}),
        config=rejection_config,
    )
    if rejected["approval_status"] != "REJECTED":
        raise RuntimeError("Expected the simulated procurement decision to be rejected.")

    print(f"Final approval status: {rejected['approval_status']}")
    print("Final response:")
    print(rejected["final_response"])


if __name__ == "__main__":
    main()
