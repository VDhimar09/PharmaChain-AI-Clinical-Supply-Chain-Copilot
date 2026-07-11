from datetime import date

from app.jobs.base import BaseJob
from app.services.event_service import EventService
from app.services.inventory_service import InventoryService


class InventoryMonitorJob(BaseJob):

    schedule = "*/30 * * * *"

    @property
    def name(self) -> str:
        return "inventory_monitor"

    @property
    def description(self) -> str:
        return "Detect low stock, out of stock, and negative inventory."

    def execute(self) -> dict:
        db = self._get_db()

        try:
            low_stock_items = InventoryService.get_low_stock_products(
                db
            )
            inventory_items = InventoryService.get_inventory(
                db
            )

            out_of_stock_items = [
                item
                for item in inventory_items
                if item.available_quantity <= 0
            ]
            negative_inventory_items = [
                item
                for item in inventory_items
                if item.quantity < 0
                or item.available_quantity < 0
                or item.reserved_quantity < 0
            ]

            for item in low_stock_items:
                EventService.queue_event(
                    db,
                    event_type="INVENTORY_LOW_STOCK",
                    severity="MEDIUM",
                    source=self.name,
                    payload={
                        "inventory_id": item.id,
                        "product_id": item.product_id,
                        "batch_number": item.batch_number,
                        "available_quantity": item.available_quantity,
                        "detected_on": date.today(),
                    },
                )

            for item in out_of_stock_items:
                EventService.queue_event(
                    db,
                    event_type="INVENTORY_OUT_OF_STOCK",
                    severity="HIGH",
                    source=self.name,
                    payload={
                        "inventory_id": item.id,
                        "product_id": item.product_id,
                        "batch_number": item.batch_number,
                        "available_quantity": item.available_quantity,
                        "detected_on": date.today(),
                    },
                )

            for item in negative_inventory_items:
                EventService.queue_event(
                    db,
                    event_type="INVENTORY_NEGATIVE",
                    severity="CRITICAL",
                    source=self.name,
                    payload={
                        "inventory_id": item.id,
                        "product_id": item.product_id,
                        "batch_number": item.batch_number,
                        "quantity": item.quantity,
                        "available_quantity": item.available_quantity,
                        "reserved_quantity": item.reserved_quantity,
                        "detected_on": date.today(),
                    },
                )

            return {
                "low_stock_count": len(low_stock_items),
                "out_of_stock_count": len(out_of_stock_items),
                "negative_inventory_count": len(negative_inventory_items),
            }
        finally:
            db.close()
