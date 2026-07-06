"""Compose professional natural-language responses from structured evidence."""

from __future__ import annotations

from time import perf_counter
from typing import Any, Iterable, Mapping

from app.ai.exceptions import ResponseCompositionException
from app.core.logging import get_logger


logger = get_logger(__name__)


class ResponseComposer:
    """
    Convert structured reasoning evidence into a readable AI response.

    The composer is intentionally pure Python. It does not execute tools,
    access the database, or depend on the web framework.
    """

    def compose(self, result: dict[str, Any]) -> str:
        """
        Build a formatted response from structured reasoning output.

        Args:
            result: Evidence returned by the reasoning engine.

        Returns:
            A professional natural-language response suitable for the chat UI.
        """
        logger.info("Starting response composition.")
        started_at = perf_counter()

        try:
            user_request = self._as_text(
                result.get("user_request"),
                default="No user request provided.",
            )
            logger.info("Composing response for request: %s", user_request)

            reasoning = self._as_text(
                result.get("reasoning"),
                default="No reasoning details were provided.",
            )
            plan = result.get("plan", [])
            tool_results = self._as_mapping(result.get("tool_results"))

            inventory = self._as_mapping(tool_results.get("inventory"))
            warehouse = self._as_mapping(tool_results.get("warehouse"))
            shipment = self._as_mapping(tool_results.get("shipment"))
            procurement = self._as_mapping(tool_results.get("procurement"))

            recommendation = self._get_recommendation(procurement)
            confidence = self._format_confidence(procurement.get("confidence"))

            summary_lines = [
                f"- Inventory available: {self._format_inventory_summary(inventory)}",
                f"- Warehouse occupancy: {self._format_warehouse_summary(warehouse)}",
                f"- Incoming shipments: {self._format_shipment_summary(shipment)}",
                f"- Procurement decision: {self._format_procurement_summary(procurement)}",
            ]

            reasoning_lines = [
                reasoning,
                self._format_plan(plan),
            ]

            procurement_reason = self._as_text(procurement.get("reason"))
            if procurement_reason:
                reasoning_lines.append(procurement_reason)

            sections = [
                f"Recommendation: {recommendation}",
                f"Confidence: {confidence}",
                "",
                "Summary",
                "",
                *summary_lines,
                "",
                "Reasoning",
                "",
                f"User request: {user_request}",
                *[line for line in reasoning_lines if line],
            ]

            response = "\n".join(sections).strip()
            logger.info(
                "Response composition completed duration_ms=%.2f",
                (perf_counter() - started_at) * 1000,
            )
            return response
        except Exception as exc:
            logger.exception("Response composition failed.")
            raise ResponseCompositionException(
                "Unable to compose a natural-language response."
            ) from exc

    def compose_copilot_response(
        self,
        *,
        intent: str,
        result: dict[str, Any],
    ) -> dict[str, Any]:
        try:
            tool_results = self._as_mapping(result.get("tool_results"))
            tool_execution = result.get("tool_execution", [])
            inventory = self._as_mapping(tool_results.get("inventory"))
            warehouse = self._as_mapping(tool_results.get("warehouse"))
            shipment = self._as_mapping(tool_results.get("shipment"))
            procurement = self._as_mapping(tool_results.get("procurement"))
            ai_insights = self._as_mapping(tool_results.get("ai_insights"))

            recommendations = self._extract_recommendations(
                ai_insights=ai_insights,
                procurement=procurement,
            )

            return {
                "confidence": self._copilot_confidence(
                    procurement=procurement,
                    ai_insights=ai_insights,
                    tool_execution=tool_execution,
                ),
                "tools_used": [
                    self._as_text(entry.get("tool"))
                    for entry in tool_execution
                    if self._as_text(entry.get("status")) == "SUCCESS"
                ],
                "reasoning": [
                    {
                        "step": self._humanize_tool_key(
                            self._as_text(entry.get("tool_key"))
                            or self._as_text(entry.get("tool"))
                        ),
                        "status": self._as_text(entry.get("status"), default="SUCCESS"),
                    }
                    for entry in tool_execution
                ],
                "tool_execution": [
                    {
                        "tool": self._as_text(entry.get("tool")),
                        "status": self._as_text(entry.get("status"), default="SUCCESS"),
                        "execution_time_ms": entry.get("execution_time_ms", 0),
                    }
                    for entry in tool_execution
                ],
                "evidence": {
                    "inventory": dict(inventory),
                    "warehouse": dict(warehouse),
                    "shipments": dict(shipment),
                    "procurement": dict(procurement),
                    "ai_insights": dict(ai_insights),
                },
                "recommendations": recommendations,
                "response": self._compose_copilot_text(
                    intent=intent,
                    inventory=inventory,
                    warehouse=warehouse,
                    shipment=shipment,
                    procurement=procurement,
                    ai_insights=ai_insights,
                    recommendations=recommendations,
                ),
            }
        except Exception as exc:
            logger.exception("Copilot response composition failed.")
            raise ResponseCompositionException(
                "Unable to compose a structured copilot response."
            ) from exc

    def _get_recommendation(
        self,
        procurement: Mapping[str, Any],
    ) -> str:
        """Extract the final recommendation from procurement evidence."""

        decision = procurement.get("decision")
        if decision is None:
            return "REVIEW"

        return self._as_text(decision, default="REVIEW").upper()

    def _format_confidence(self, value: Any) -> str:
        """Format numeric confidence values as percentages."""

        if isinstance(value, (int, float)):
            percentage = value * 100 if value <= 1 else value
            return f"{round(percentage)}%"

        text = self._as_text(value)
        return text if text else "N/A"

    def _format_inventory_summary(
        self,
        inventory: Mapping[str, Any],
    ) -> str:
        """Summarize inventory evidence."""

        available = inventory.get("total_available_quantity")
        total = inventory.get("total_quantity")
        low_stock = inventory.get("low_stock_products")
        items = inventory.get("total_inventory_items")

        parts = []
        if available is not None:
            parts.append(f"{available} units available")
        if total is not None:
            parts.append(f"{total} total units")
        if items is not None:
            parts.append(f"{items} inventory items")
        if low_stock is not None:
            parts.append(f"{low_stock} low-stock products")

        return self._join_parts(parts, fallback="No inventory evidence available.")

    def _format_warehouse_summary(
        self,
        warehouse: Mapping[str, Any],
    ) -> str:
        """Summarize warehouse capacity evidence."""

        occupancy = warehouse.get("occupancy_percentage")
        occupied = warehouse.get("occupied_capacity")
        available = warehouse.get("available_capacity")
        total = warehouse.get("total_capacity")

        parts = []
        if occupancy is not None:
            parts.append(f"{occupancy}% occupied")
        if occupied is not None and total is not None:
            parts.append(f"{occupied} of {total} units in use")
        if available is not None:
            parts.append(f"{available} units available")

        return self._join_parts(parts, fallback="No warehouse evidence available.")

    def _format_shipment_summary(
        self,
        shipment: Mapping[str, Any],
    ) -> str:
        """Summarize shipment evidence."""

        inbound = shipment.get("inbound_shipments")
        total = shipment.get("total_shipments")
        delayed = shipment.get("delayed_shipments")
        outbound = shipment.get("outbound_shipments")

        parts = []
        if inbound is not None:
            parts.append(f"{inbound} inbound shipments")
        if outbound is not None:
            parts.append(f"{outbound} outbound shipments")
        if delayed is not None:
            parts.append(f"{delayed} delayed")
        if total is not None:
            parts.append(f"{total} total shipments")

        return self._join_parts(parts, fallback="No shipment evidence available.")

    def _format_procurement_summary(
        self,
        procurement: Mapping[str, Any],
    ) -> str:
        """Summarize procurement evidence."""

        decision = procurement.get("decision")
        if decision is not None:
            decision_text = self._as_text(decision, default="REVIEW").upper()
            confidence = self._format_confidence(procurement.get("confidence"))
            if confidence != "N/A":
                return f"{decision_text} at {confidence} confidence"
            return decision_text

        if procurement:
            return self._format_generic_mapping(procurement)

        return "No procurement evidence available."

    def _format_plan(self, plan: Any) -> str:
        """Render the tool execution plan in prose."""

        if isinstance(plan, Iterable) and not isinstance(plan, (str, bytes, Mapping)):
            ordered_tools = [self._as_text(item) for item in plan if self._as_text(item)]
            if ordered_tools:
                return "Plan executed: " + " -> ".join(ordered_tools)

        return "Plan executed: No tool sequence provided."

    def _compose_copilot_text(
        self,
        *,
        intent: str,
        inventory: Mapping[str, Any],
        warehouse: Mapping[str, Any],
        shipment: Mapping[str, Any],
        procurement: Mapping[str, Any],
        ai_insights: Mapping[str, Any],
        recommendations: list[str],
    ) -> str:
        if intent == "EXECUTIVE_SUMMARY":
            alerts = ai_insights.get("alerts", [])
            alert_count = len(alerts) if isinstance(alerts, list) else 0
            return (
                "Today's highest operational priorities are "
                f"{alert_count} critical alerts, "
                f"{inventory.get('low_stock_products', 0)} low-stock products, "
                f"{shipment.get('delayed_shipments', 0)} delayed shipments, and "
                f"{round(warehouse.get('occupancy_percentage', 0))}% warehouse occupancy. "
                + self._summarize_recommendations(recommendations)
            ).strip()

        if intent == "RISK_SUMMARY":
            return (
                "Current operational risks are concentrated in inventory availability, "
                "shipment delays, and warehouse capacity pressure. "
                + self._summarize_recommendations(recommendations)
            ).strip()

        if intent == "INVENTORY_STATUS":
            return (
                f"Inventory is tracking {inventory.get('total_available_quantity', 0)} available units "
                f"across {inventory.get('total_inventory_items', 0)} items, with "
                f"{inventory.get('low_stock_products', 0)} low-stock products. "
                + self._summarize_recommendations(recommendations)
            ).strip()

        if intent == "WAREHOUSE_STATUS":
            return (
                f"Warehouse capacity is {warehouse.get('occupancy_percentage', 0)}% occupied, "
                f"with {warehouse.get('available_capacity', 0)} units of available space. "
                + self._summarize_recommendations(recommendations)
            ).strip()

        if intent == "SHIPMENT_STATUS":
            return (
                f"There are {shipment.get('inbound_shipments', 0)} inbound shipments, "
                f"{shipment.get('outbound_shipments', 0)} outbound shipments, and "
                f"{shipment.get('delayed_shipments', 0)} delayed shipments. "
                + self._summarize_recommendations(recommendations)
            ).strip()

        if intent == "PROCUREMENT_STATUS":
            pending = self._nested_count(ai_insights, "procurement", "pending")
            approved = self._nested_count(ai_insights, "procurement", "approved")
            rejected = self._nested_count(ai_insights, "procurement", "rejected")
            return (
                f"Procurement currently shows {pending} pending, {approved} approved, and "
                f"{rejected} rejected requests. "
                + self._summarize_recommendations(recommendations)
            ).strip()

        if intent == "AI_INSIGHTS":
            return (
                "The latest AI insights highlight operational recommendations across inventory, "
                "warehouse, shipments, and procurement. "
                + self._summarize_recommendations(recommendations)
            ).strip()

        if intent == "PROCUREMENT":
            return self.compose(
                {
                    "user_request": "",
                    "reasoning": "",
                    "plan": [],
                    "tool_results": {
                        "inventory": inventory,
                        "warehouse": warehouse,
                        "shipment": shipment,
                        "procurement": procurement,
                    },
                }
            )

        return (
            "I could not determine a precise operational intent. "
            + self._summarize_recommendations(recommendations)
        ).strip()

    def _extract_recommendations(
        self,
        *,
        ai_insights: Mapping[str, Any],
        procurement: Mapping[str, Any],
    ) -> list[str]:
        recommendations: list[str] = []
        raw_ai_recommendations = ai_insights.get("recommendations")
        if isinstance(raw_ai_recommendations, list):
            for item in raw_ai_recommendations:
                if isinstance(item, Mapping):
                    title = self._as_text(item.get("title"))
                    message = self._as_text(item.get("message"))
                    recommendations.append(
                        ": ".join(part for part in (title, message) if part)
                    )

        decision = self._as_text(procurement.get("decision"))
        reason = self._as_text(procurement.get("reason"))
        if decision:
            recommendations.append(
                ": ".join(
                    part for part in (f"Procurement decision {decision}", reason) if part
                )
            )

        return recommendations[:6]

    def _copilot_confidence(
        self,
        *,
        procurement: Mapping[str, Any],
        ai_insights: Mapping[str, Any],
        tool_execution: list[Any],
    ) -> int:
        procurement_confidence = procurement.get("confidence")
        if isinstance(procurement_confidence, (int, float)):
            return round(
                procurement_confidence * 100
                if procurement_confidence <= 1
                else procurement_confidence
            )

        ai_confidence = ai_insights.get("confidence")
        if isinstance(ai_confidence, (int, float)):
            return round(ai_confidence)

        successful_tools = sum(
            1
            for entry in tool_execution
            if self._as_text(entry.get("status")) == "SUCCESS"
        )
        return min(99, 72 + successful_tools * 6)

    def _nested_count(self, payload: Mapping[str, Any], *keys: str) -> int:
        current: Any = payload
        for key in keys:
            if isinstance(current, Mapping):
                current = current.get(key)
            else:
                return 0

        return len(current) if isinstance(current, list) else 0

    def _summarize_recommendations(self, recommendations: list[str]) -> str:
        if not recommendations:
            return "No additional AI recommendations are available."
        return "Top recommendation: " + recommendations[0]

    def _humanize_tool_key(self, value: str) -> str:
        if not value:
            return "Tool Execution"
        return value.replace("_", " ").title().replace("Ai ", "AI ") + " Analysis"

    def _format_generic_mapping(
        self,
        value: Mapping[str, Any],
    ) -> str:
        """Flatten a mapping into a concise human-readable string."""

        parts = []
        for key, raw_value in value.items():
            label = key.replace("_", " ")
            parts.append(f"{label}: {self._as_text(raw_value)}")

        return self._join_parts(parts, fallback="No details available.")

    def _join_parts(
        self,
        parts: list[str],
        fallback: str,
    ) -> str:
        """Join non-empty summary parts with commas."""

        filtered_parts = [part for part in parts if part]
        if not filtered_parts:
            return fallback

        return ", ".join(filtered_parts)

    def _as_mapping(self, value: Any) -> Mapping[str, Any]:
        """Return a mapping view when possible."""

        if isinstance(value, Mapping):
            return value
        return {}

    def _as_text(
        self,
        value: Any,
        default: str = "",
    ) -> str:
        """Convert arbitrary values into display-friendly text."""

        if value is None:
            return default

        if isinstance(value, str):
            return value.strip() or default

        if isinstance(value, Mapping):
            return self._format_generic_mapping(value)

        if isinstance(value, Iterable) and not isinstance(value, (str, bytes)):
            items = [self._as_text(item) for item in value]
            items = [item for item in items if item]
            return ", ".join(items) if items else default

        return str(value)
