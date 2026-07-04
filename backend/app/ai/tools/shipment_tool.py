from sqlalchemy.orm import Session

from app.ai.tools.base_tool import BaseTool
from app.services.shipment_service import ShipmentService


class ShipmentTool(BaseTool):
    """
    AI Tool for Shipment operations.
    """

    @property
    def name(self) -> str:
        return "shipment"

    @property
    def description(self) -> str:
        return "Provides shipment statistics and summary information."

    def run(self, **kwargs):
        """
        Standard entry point used by the Reasoning Engine.
        """
        db: Session = kwargs["db"]
        return self.get_shipment_summary(db)

    def get_shipment_summary(
        self,
        db: Session
    ):
        return ShipmentService.get_shipment_statistics(db)