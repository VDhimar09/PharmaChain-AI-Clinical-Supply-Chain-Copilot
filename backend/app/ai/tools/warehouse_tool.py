from sqlalchemy.orm import Session

from app.ai.tools.base_tool import BaseTool
from app.services.warehouse_zone_service import WarehouseZoneService


class WarehouseTool(BaseTool):
    """
    AI Tool for Warehouse operations.
    """

    @property
    def name(self) -> str:
        return "warehouse"

    @property
    def description(self) -> str:
        return "Provides warehouse capacity and occupancy information."

    def run(self, **kwargs):
        """
        Standard entry point used by the Reasoning Engine.
        """
        db: Session = kwargs["db"]
        return self.get_capacity_summary(db)

    def get_capacity_summary(
        self,
        db: Session
    ):
        return WarehouseZoneService.get_capacity_summary(db)