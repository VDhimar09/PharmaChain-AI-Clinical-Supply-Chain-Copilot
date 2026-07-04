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

        # -------------------------------------------------
        # Debugging
        # -------------------------------------------------
        print("=" * 60)
        print("Searching for:", normalized_product_name)

        product = self.repo.get_product(
            normalized_product_name
        )

        print("Product found:", product)
        print("=" * 60)

        # -------------------------------------------------

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

        decision = self.agent.evaluate(
            current_occupancy=occupancy,
            projected_occupancy=projected_occupancy,
            temperature_match=temperature_match,
            incoming_conflict=incoming_conflict
        )

        reasoning = (
            fallback_reasoning +
            decision.reasoning
        )

        return {
            "decision": decision.decision,
            "confidence": decision.confidence,
            "reasoning": reasoning,
            "inventory_units": inventory_units,
            "current_occupancy_percent": round(
                occupancy,
                2
            ),
            "projected_occupancy_percent": round(
                projected_occupancy,
                2
            )
        }