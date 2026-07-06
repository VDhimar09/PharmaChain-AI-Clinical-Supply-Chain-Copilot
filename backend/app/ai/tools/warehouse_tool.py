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
        zones = WarehouseZoneService.get_zones(db)
        return {
            **self.get_capacity_summary(db),
            "zones": [
                {
                    "id": str(zone.id),
                    "name": zone.name,
                    "zone_type": zone.zone_type,
                    "capacity_units": zone.capacity_units,
                    "occupied_units": zone.occupied_units,
                    "occupancy_percentage": round(
                        (zone.occupied_units / zone.capacity_units) * 100
                    ) if zone.capacity_units > 0 else 0,
                }
                for zone in zones[:8]
            ],
        }

    def get_capacity_summary(
        self,
        db: Session
    ):
        return WarehouseZoneService.get_capacity_summary(db)
