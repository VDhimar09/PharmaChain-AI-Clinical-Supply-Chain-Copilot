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
        shipments = ShipmentService.get_shipments(db)
        return {
            **self.get_shipment_summary(db),
            "delayed_shipments_list": [
                {
                    "id": str(shipment.id),
                    "shipment_number": shipment.shipment_number,
                    "product_name": shipment.product_name,
                    "supplier_name": shipment.supplier_name,
                    "status": shipment.status,
                }
                for shipment in shipments
                if shipment.status.lower() == "delayed"
            ][:5],
        }

    def get_shipment_summary(
        self,
        db: Session
    ):
        return ShipmentService.get_shipment_statistics(db)
