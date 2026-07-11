from datetime import UTC
from datetime import datetime

from app.services.event_service import EventService
from app.services.inventory_service import InventoryService
from app.services.procurement_analysis_service import (
    ProcurementAnalysisService,
    ProcurementEvaluationError,
)
from app.jobs.base import BaseJob


class ProcurementMonitorJob(BaseJob):

    schedule = "0 * * * *"

    @property
    def name(self) -> str:
        return "procurement_monitor"

    @property
    def description(self) -> str:
        return "Generate procurement recommendations for low-stock products."

    def execute(self) -> dict:
        db = self._get_db()

        try:
            low_stock_items = InventoryService.get_low_stock_products(
                db
            )
            analysis_service = ProcurementAnalysisService(
                db
            )
            recommendations_created = 0

            for item in low_stock_items:
                if item.product is None:
                    continue

                requested_quantity = max(
                    item.product.safety_stock - item.available_quantity,
                    1,
                )

                try:
                    analysis = analysis_service.analyze(
                        product_id=item.product.id,
                        supplier_id=item.product.supplier_id,
                        requested_quantity=requested_quantity,
                    )
                except ProcurementEvaluationError as exc:
                    EventService.queue_event(
                        db,
                        event_type="PROCUREMENT_RECOMMENDATION_FAILED",
                        severity="MEDIUM",
                        source=self.name,
                        payload={
                            "product_id": item.product.id,
                            "requested_quantity": requested_quantity,
                            "error": exc.message,
                        },
                    )
                    continue

                EventService.queue_event(
                    db,
                    event_type="PROCUREMENT_RECOMMENDATION_CREATED",
                    severity="MEDIUM",
                    source=self.name,
                    payload={
                        "product_id": item.product.id,
                        "product_name": item.product.name,
                        "requested_quantity": requested_quantity,
                        "decision": analysis["decision"],
                        "confidence": analysis["confidence"],
                        "recommendation": analysis["recommendation"],
                        "created_at": datetime.now(UTC),
                    },
                )
                recommendations_created += 1

            return {
                "low_stock_products": len(low_stock_items),
                "recommendations_created": recommendations_created,
            }
        finally:
            db.close()
