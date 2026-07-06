from datetime import date

from sqlalchemy.orm import Session

from app.ai.tools.base_tool import BaseTool
from app.services.inventory_service import InventoryService


class InventoryTool(BaseTool):
    """
    AI Tool for Inventory operations.
    """

    @property
    def name(self) -> str:
        return "inventory"

    @property
    def description(self) -> str:
        return "Provides inventory summary and stock information."

    def run(self, **kwargs):
        """
        Standard entry point used by the Reasoning Engine.
        """
        db: Session = kwargs["db"]
        low_stock_items = self.get_low_stock_products(db)
        expiring_items = self.get_expiring_products(db)

        return {
            **self.get_inventory_summary(db),
            "low_stock_items": [
                {
                    "id": str(item.id),
                    "product_name": item.product_name,
                    "sku": item.sku,
                    "available_quantity": item.available_quantity,
                    "warehouse_zone": item.warehouse_zone,
                    "status": item.status,
                }
                for item in low_stock_items[:5]
            ],
            "expiring_items": [
                {
                    "id": str(item.id),
                    "product_name": item.product_name,
                    "sku": item.sku,
                    "expiry_date": item.expiry_date.isoformat(),
                    "days_to_expiry": (item.expiry_date - date.today()).days,
                    "warehouse_zone": item.warehouse_zone,
                    "status": item.status,
                }
                for item in expiring_items[:5]
            ],
        }

    def get_inventory_summary(
        self,
        db: Session
    ):
        return InventoryService.get_inventory_statistics(db)

    def get_low_stock_products(
        self,
        db: Session
    ):
        return InventoryService.get_low_stock_products(db)

    def get_expiring_products(
        self,
        db: Session
    ):
        return InventoryService.get_expiring_products(db)
