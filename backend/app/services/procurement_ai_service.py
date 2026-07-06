from sqlalchemy.orm import Session

from app.ai.procurement_agent import ProcurementAgent
from app.repositories.procurement_repository import ProcurementRepository


class ProcurementEvaluationError(Exception):

    def __init__(self, message: str, status_code: int):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class ProcurementAIService:

    def __init__(self, db: Session):
        self.repo = ProcurementRepository(db)
        self.agent = ProcurementAgent()

    def evaluate_request(
        self,
        product_name: str,
        pallet_quantity: int,
        month: str
    ):
        evaluation = self._prepare_evaluation(
            product_name=product_name,
            pallet_quantity=pallet_quantity,
            month=month,
        )

        decision = self.agent.evaluate(
            current_occupancy=evaluation["occupancy"],
            projected_occupancy=evaluation["projected_occupancy"],
            temperature_match=evaluation["temperature_match"],
            incoming_conflict=evaluation["incoming_conflict"],
        )

        reasoning = (
            evaluation["fallback_reasoning"] +
            decision.reasoning
        )

        risk_level = self._determine_risk_level(
            decision=decision.decision
        )
        temperature_fit = (
            "MATCH" if evaluation["temperature_match"]
            else "MISMATCH"
        )
        badges = self._build_badges(
            temperature_fit=temperature_fit,
            incoming_conflict=evaluation["incoming_conflict"],
            shelf_life_days=evaluation["product"].shelf_life_days,
            zone_type=evaluation["zone"].zone_type,
        )

        return {
            "decision": decision.decision,
            "confidence": decision.confidence,
            "reasoning": reasoning,
            "inventory_units": evaluation["inventory_units"],
            "risk_level": risk_level,
            "recommended_zone": evaluation["zone"].name,
            "temperature_fit": temperature_fit,
            "badges": badges,
            "current_occupancy_percent": round(
                evaluation["occupancy"],
                2
            ),
            "projected_occupancy_percent": round(
                evaluation["projected_occupancy"],
                2
            )
        }

    def get_evaluation_context(
        self,
        product_name: str,
        pallet_quantity: int,
        month: str,
    ):
        evaluation = self._prepare_evaluation(
            product_name=product_name,
            pallet_quantity=pallet_quantity,
            month=month,
        )

        decision = self.agent.evaluate(
            current_occupancy=evaluation["occupancy"],
            projected_occupancy=evaluation["projected_occupancy"],
            temperature_match=evaluation["temperature_match"],
            incoming_conflict=evaluation["incoming_conflict"],
        )

        reasoning = (
            evaluation["fallback_reasoning"] +
            decision.reasoning
        )

        return {
            "product": evaluation["product"],
            "inventory": evaluation["inventory"],
            "zone": evaluation["zone"],
            "incoming_shipments": evaluation["incoming_shipments"],
            "inventory_units": evaluation["inventory_units"],
            "incoming_total": evaluation["incoming_total"],
            "occupancy": evaluation["occupancy"],
            "projected_occupancy": evaluation["projected_occupancy"],
            "temperature_match": evaluation["temperature_match"],
            "decision": decision.decision,
            "confidence": decision.confidence,
            "reasoning": reasoning,
            "month": month,
        }

    def _prepare_evaluation(
        self,
        product_name: str,
        pallet_quantity: int,
        month: str,
    ):
        normalized_product_name = product_name.strip()

        if not normalized_product_name:
            raise ProcurementEvaluationError(
                "Product name is required",
                status_code=400
            )

        if pallet_quantity <= 0:
            raise ProcurementEvaluationError(
                "Pallet quantity must be greater than zero",
                status_code=400
            )

        product = self.repo.get_product(
            normalized_product_name
        )

        if not product:
            raise ProcurementEvaluationError(
                f"Product '{normalized_product_name}' not found",
                status_code=404
            )

        # Find Inventory
        inventory = self.repo.get_inventory(
            product.id
        )

        inventory_units = 0
        fallback_reasoning = []

        if inventory:
            inventory_units = inventory.quantity

            zone = self.repo.get_zone(
                inventory.zone_id
            )
        else:
            zone = self.repo.get_compatible_zone(
                product.temperature_min,
                product.temperature_max
            )

            fallback_reasoning.append(
                "No existing inventory record was found for this product, so the recommendation used a compatible warehouse zone."
            )

        if not zone:
            raise ProcurementEvaluationError(
                "No compatible warehouse zone found for this product",
                status_code=404
            )

        if zone.capacity_units <= 0:
            raise ProcurementEvaluationError(
                "Warehouse zone capacity must be greater than zero",
                status_code=400
            )

        # Incoming Shipments
        incoming_shipments = (
            self.repo.get_incoming_shipments()
        )

        occupancy = (
            zone.occupied_units /
            zone.capacity_units
        ) * 100

        projected_units = (
            zone.occupied_units +
            pallet_quantity
        )

        projected_occupancy = (
            projected_units /
            zone.capacity_units
        ) * 100

        temperature_match = (
            product.temperature_min >= zone.temperature_min
            and
            product.temperature_max <= zone.temperature_max
        )

        incoming_total = sum(
            shipment.quantity
            for shipment in incoming_shipments
        )

        incoming_conflict = incoming_total > 0

        if incoming_total > 0:
            projected_occupancy += (
                incoming_total /
                zone.capacity_units
            ) * 100

        return {
            "inventory_units": inventory_units,
            "product": product,
            "inventory": inventory,
            "zone": zone,
            "incoming_shipments": incoming_shipments,
            "incoming_total": incoming_total,
            "fallback_reasoning": fallback_reasoning,
            "occupancy": occupancy,
            "projected_occupancy": projected_occupancy,
            "temperature_match": temperature_match,
            "incoming_conflict": incoming_conflict,
            "month": month,
        }

    def _determine_risk_level(
        self,
        decision: str,
    ) -> str:
        if decision == "REJECT":
            return "HIGH"

        if decision == "REVIEW":
            return "MEDIUM"

        return "LOW"

    def _build_badges(
        self,
        temperature_fit: str,
        incoming_conflict: bool,
        shelf_life_days: int,
        zone_type: str,
    ) -> list[str]:
        badges = [
            f"Temperature Fit: {temperature_fit.title()}",
            f"Zone Type: {zone_type}",
            f"Shelf Life: {self._format_shelf_life_months(shelf_life_days)}",
        ]

        if incoming_conflict:
            badges.append(
                "Incoming Shipments Pending"
            )
        else:
            badges.append(
                "No Incoming Shipment Conflict"
            )

        return badges

    def _format_shelf_life_months(
        self,
        shelf_life_days: int,
    ) -> str:
        months = max(
            1,
            round(shelf_life_days / 30)
        )
        return f"{months} mo"
