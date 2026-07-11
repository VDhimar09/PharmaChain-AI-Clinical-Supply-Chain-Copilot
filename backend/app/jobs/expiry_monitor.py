from app.jobs.base import BaseJob
from app.services.event_service import EventService
from app.services.inventory_service import InventoryService


class ExpiryMonitorJob(BaseJob):

    schedule = "0 0 * * *"
    expiry_windows = (30, 14, 7, 1)

    @property
    def name(self) -> str:
        return "expiry_monitor"

    @property
    def description(self) -> str:
        return "Detect products expiring in 30, 14, 7, and 1 day windows."

    def execute(self) -> dict:
        db = self._get_db()

        try:
            summary: dict[str, int] = {}

            for days in self.expiry_windows:
                expiring_items = InventoryService.get_expiring_products(
                    db,
                    days=days,
                )

                for item in expiring_items:
                    EventService.queue_event(
                        db,
                        event_type="PRODUCT_EXPIRY_ALERT",
                        severity=self._severity_for_days(
                            days
                        ),
                        source=self.name,
                        payload={
                            "inventory_id": item.id,
                            "product_id": item.product_id,
                            "batch_number": item.batch_number,
                            "expiry_date": item.expiry_date,
                            "days_to_expiry": days,
                        },
                    )

                summary[f"expiring_within_{days}_days"] = len(
                    expiring_items
                )

            return summary
        finally:
            db.close()

    def _severity_for_days(
        self,
        days: int
    ) -> str:
        if days <= 1:
            return "CRITICAL"

        if days <= 7:
            return "HIGH"

        if days <= 14:
            return "MEDIUM"

        return "LOW"
