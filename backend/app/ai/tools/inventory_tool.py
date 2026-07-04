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
        return self.get_inventory_summary(db)

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