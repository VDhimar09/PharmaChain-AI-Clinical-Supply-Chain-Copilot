from sqlalchemy.orm import Session

from app.repositories.shipment_repository import (
    ShipmentRepository
)

from app.schemas.shipment import (
    ShipmentCreate
)


class ShipmentService:

    @staticmethod
    def get_shipments(db: Session):
        return ShipmentRepository.get_all(db)

    @staticmethod
    def get_shipment_by_id(
        db: Session,
        shipment_id
    ):
        return ShipmentRepository.get_by_id(
            db,
            shipment_id
        )

    @staticmethod
    def create_shipment(
        db: Session,
        shipment_data: ShipmentCreate
    ):
        return ShipmentRepository.create(
            db,
            shipment_data
        )

    @staticmethod
    def delete_shipment(
        db: Session,
        shipment_id
    ):
        return ShipmentRepository.delete(
            db,
            shipment_id
        )

    @staticmethod
    def get_shipment_statistics(
        db: Session
    ):
        return ShipmentRepository.get_shipment_statistics(db)