from datetime import datetime
from datetime import timezone

from app.jobs.base import BaseJob
from app.services.event_service import EventService
from app.services.shipment_service import ShipmentService


class ShipmentMonitorJob(BaseJob):

    schedule = "*/15 * * * *"

    @property
    def name(self) -> str:
        return "shipment_monitor"

    @property
    def description(self) -> str:
        return "Detect delayed and overdue shipments."

    def execute(self) -> dict:
        db = self._get_db()

        try:
            shipments = ShipmentService.get_shipments(
                db
            )
            now = datetime.now(
                timezone.utc
            )

            delayed_shipments = []
            overdue_shipments = []

            for shipment in shipments:
                normalized_status = shipment.status.upper()
                expected_arrival = shipment.expected_arrival

                if expected_arrival.tzinfo is None:
                    expected_arrival = expected_arrival.replace(
                        tzinfo=timezone.utc
                    )

                if normalized_status == "DELAYED":
                    delayed_shipments.append(
                        shipment
                    )

                if (
                    expected_arrival < now
                    and normalized_status != "DELIVERED"
                ):
                    overdue_shipments.append(
                        shipment
                    )

            for shipment in delayed_shipments:
                EventService.queue_event(
                    db,
                    event_type="SHIPMENT_DELAY_DETECTED",
                    severity="HIGH",
                    source=self.name,
                    payload={
                        "shipment_id": shipment.id,
                        "shipment_number": shipment.shipment_number,
                        "status": shipment.status,
                        "expected_arrival": shipment.expected_arrival,
                    },
                )

            for shipment in overdue_shipments:
                EventService.queue_event(
                    db,
                    event_type="SHIPMENT_OVERDUE",
                    severity="HIGH",
                    source=self.name,
                    payload={
                        "shipment_id": shipment.id,
                        "shipment_number": shipment.shipment_number,
                        "status": shipment.status,
                        "expected_arrival": shipment.expected_arrival,
                    },
                )

            return {
                "delayed_count": len(delayed_shipments),
                "overdue_count": len(overdue_shipments),
            }
        finally:
            db.close()
