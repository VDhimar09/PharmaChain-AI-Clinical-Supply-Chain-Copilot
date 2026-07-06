from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.ai.planner.reasoning_planner import ReasoningPlanner
from app.ai.reasoning.reasoning_engine import ReasoningEngine
from app.ai.response import ResponseComposer
from app.ai.tools.inventory_tool import InventoryTool
from app.ai.tools.procurement_tool import ProcurementTool
from app.ai.tools.shipment_tool import ShipmentTool
from app.ai.tools.tool_registry import ToolRegistry
from app.ai.tools.warehouse_tool import WarehouseTool
from app.services.product_service import ProductService
from app.services.procurement_ai_service import (
    ProcurementAIService,
    ProcurementEvaluationError,
)
from app.services.supplier_service import SupplierService


class ProcurementAnalysisService:
    """
    Orchestrates structured procurement analysis by reusing the
    existing reasoning pipeline and domain services.
    """

    def __init__(self, db: Session):
        self.db = db
        self.procurement_service = ProcurementAIService(db)
        self.response_composer = ResponseComposer()
        self.reasoning_engine = ReasoningEngine(
            planner=ReasoningPlanner(),
            registry=self._build_registry(),
        )

    def analyze(
        self,
        product_id,
        supplier_id,
        requested_quantity: int,
    ) -> dict:
        if requested_quantity <= 0:
            raise ProcurementEvaluationError(
                "Requested quantity must be greater than zero",
                status_code=400,
            )

        product = ProductService.get_product_by_id(
            self.db,
            product_id,
        )
        if not product:
            raise ProcurementEvaluationError(
                "Product not found",
                status_code=404,
            )

        supplier = SupplierService.get_supplier_by_id(
            self.db,
            supplier_id,
        )
        if not supplier:
            raise ProcurementEvaluationError(
                "Supplier not found",
                status_code=404,
            )

        message = (
            "Analyze procurement request for "
            f"{requested_quantity} pallets of {product.name} "
            f"in {datetime.now(UTC).strftime('%B')}."
        )
        current_month = datetime.now(UTC).strftime("%B")

        reasoning_result = self.reasoning_engine.execute(
            message=message,
            db=self.db,
            product_name=product.name,
            pallet_quantity=requested_quantity,
            month=current_month,
        )
        explanation = self.response_composer.compose(
            reasoning_result
        )

        evaluation_context = (
            self.procurement_service.get_evaluation_context(
                product_name=product.name,
                pallet_quantity=requested_quantity,
                month=current_month,
            )
        )

        zone = evaluation_context["zone"]
        incoming_shipments = evaluation_context["incoming_shipments"]
        inventory = evaluation_context["inventory"]
        inventory_units = evaluation_context["inventory_units"]
        supplier_reliability = round(
            float(supplier.reliability_score or 0.0),
            2,
        )

        tool_execution = [
            {
                "tool": self._label_tool(tool_name),
                "status": "SUCCESS",
            }
            for tool_name in reasoning_result["plan"]
        ]

        evidence = {
            "inventory": {
                "available_units": inventory_units,
                "requested_quantity": requested_quantity,
                "safety_stock": product.safety_stock,
                "below_safety_stock": inventory_units <= product.safety_stock,
            },
            "warehouse": {
                "recommended_zone": zone.name,
                "current_occupancy_percent": round(
                    evaluation_context["occupancy"],
                    2,
                ),
                "projected_occupancy_percent": round(
                    evaluation_context["projected_occupancy"],
                    2,
                ),
                "available_capacity_units": max(
                    0,
                    zone.capacity_units - zone.occupied_units,
                ),
            },
            "shipments": {
                "incoming_shipments": len(incoming_shipments),
                "incoming_units": evaluation_context["incoming_total"],
                "conflict_detected": (
                    evaluation_context["incoming_total"] > 0
                ),
            },
            "supplier": {
                "supplier_name": supplier.name,
                "reliability_score": supplier_reliability,
                "lead_time_days": supplier.lead_time_days,
            },
            "cold_chain": {
                "compatible": evaluation_context["temperature_match"],
                "temperature_min": product.temperature_min,
                "temperature_max": product.temperature_max,
                "zone_name": zone.name,
            },
            "procurement": {
                "demand_forecast": self._build_demand_forecast(
                    inventory_units=inventory_units,
                    safety_stock=product.safety_stock,
                    requested_quantity=requested_quantity,
                ),
                "shelf_life_valid": product.shelf_life_days > 0,
                "shelf_life_days": product.shelf_life_days,
            },
        }

        reasoning = self._build_reasoning_steps(
            evaluation_context=evaluation_context,
            evidence=evidence,
        )

        return {
            "request_details": {
                "product_id": product.id,
                "product_name": product.name,
                "supplier_id": supplier.id,
                "supplier_name": supplier.name,
                "requested_quantity": requested_quantity,
                "temperature_min": product.temperature_min,
                "temperature_max": product.temperature_max,
                "safety_stock": product.safety_stock,
                "shelf_life_days": product.shelf_life_days,
            },
            "decision": evaluation_context["decision"],
            "confidence": self._normalize_confidence(
                evaluation_context["confidence"]
            ),
            "tool_execution": tool_execution,
            "reasoning": reasoning,
            "evidence": evidence,
            "recommendation": self._build_recommendation(
                evaluation_context["decision"]
            ),
            "summary": self._build_summary(
                evaluation_context["decision"],
                reasoning,
            ),
            "explanation": explanation,
        }

    def _build_registry(self) -> ToolRegistry:
        registry = ToolRegistry()
        registry.register(InventoryTool())
        registry.register(WarehouseTool())
        registry.register(ShipmentTool())
        registry.register(ProcurementTool())
        return registry

    def _build_reasoning_steps(
        self,
        evaluation_context: dict,
        evidence: dict,
    ) -> list[dict]:
        inventory_status = (
            "PASS"
            if evidence["inventory"]["available_units"] > 0
            else "ATTENTION"
        )
        warehouse_status = (
            "FAIL"
            if evidence["warehouse"]["projected_occupancy_percent"] > 90
            else "PASS"
        )
        cold_chain_status = (
            "PASS"
            if evidence["cold_chain"]["compatible"]
            else "FAIL"
        )
        shipment_status = (
            "ATTENTION"
            if evidence["shipments"]["conflict_detected"]
            else "PASS"
        )
        supplier_status = (
            "PASS"
            if evidence["supplier"]["reliability_score"] >= 0.8
            else "ATTENTION"
        )

        reasoning = [
            {
                "step": "Inventory Check",
                "status": inventory_status,
                "message": (
                    f"{evidence['inventory']['available_units']} units available "
                    f"for requested quantity {evidence['inventory']['requested_quantity']}."
                ),
            },
            {
                "step": "Warehouse Capacity",
                "status": warehouse_status,
                "message": (
                    f"{evidence['warehouse']['recommended_zone']} projects to "
                    f"{evidence['warehouse']['projected_occupancy_percent']}% occupancy."
                ),
            },
            {
                "step": "Cold-Chain Validation",
                "status": cold_chain_status,
                "message": (
                    "Temperature requirements are compatible with the "
                    "recommended storage zone."
                    if evidence["cold_chain"]["compatible"]
                    else "Temperature requirements do not match the recommended storage zone."
                ),
            },
            {
                "step": "Incoming Shipments",
                "status": shipment_status,
                "message": (
                    f"{evidence['shipments']['incoming_shipments']} incoming shipments "
                    f"totalling {evidence['shipments']['incoming_units']} units."
                ),
            },
            {
                "step": "Supplier Reliability",
                "status": supplier_status,
                "message": (
                    f"{evidence['supplier']['supplier_name']} reliability score is "
                    f"{evidence['supplier']['reliability_score']}."
                ),
            },
            {
                "step": "Decision Engine",
                "status": self._decision_status(
                    evaluation_context["decision"]
                ),
                "message": " ".join(evaluation_context["reasoning"]),
            },
        ]

        return reasoning

    def _build_recommendation(self, decision: str) -> str:
        if decision == "APPROVE":
            return "Approve procurement request."
        if decision == "REJECT":
            return "Reject procurement request until blocking constraints are resolved."
        return "Review procurement request before approval."

    def _build_summary(
        self,
        decision: str,
        reasoning: list[dict],
    ) -> str:
        failed_steps = [
            step["step"]
            for step in reasoning
            if step["status"] == "FAIL"
        ]
        attention_steps = [
            step["step"]
            for step in reasoning
            if step["status"] == "ATTENTION"
        ]

        if decision == "APPROVE":
            return "All procurement validation checks passed."
        if failed_steps:
            return (
                "Procurement validation failed for: "
                + ", ".join(failed_steps)
                + "."
            )
        if attention_steps:
            return (
                "Procurement review required due to: "
                + ", ".join(attention_steps)
                + "."
            )
        return "Procurement analysis completed."

    def _build_demand_forecast(
        self,
        inventory_units: int,
        safety_stock: int,
        requested_quantity: int,
    ) -> str:
        projected_units = inventory_units + requested_quantity

        if inventory_units <= safety_stock:
            return "Current inventory is at or below safety stock."
        if projected_units <= safety_stock:
            return "Requested quantity does not recover inventory above safety stock."
        return "Projected inventory remains above safety stock."

    def _label_tool(self, tool_name: str) -> str:
        labels = {
            "inventory": "Inventory Tool",
            "warehouse": "Warehouse Tool",
            "shipment": "Shipment Tool",
            "procurement": "Procurement Tool",
        }
        return labels.get(tool_name, tool_name.title())

    def _normalize_confidence(self, value: float) -> int:
        percentage = value * 100 if value <= 1 else value
        return round(percentage)

    def _decision_status(self, decision: str) -> str:
        if decision == "APPROVE":
            return "PASS"
        if decision == "REJECT":
            return "FAIL"
        return "ATTENTION"
