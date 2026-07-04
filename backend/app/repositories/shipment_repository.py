from sqlalchemy.orm import Session, selectinload
from sqlalchemy import func

from app.models.shipment import Shipment
from app.schemas.shipment import ShipmentCreate


class ShipmentRepository:

    @staticmethod
    def get_all(db: Session):
        return db.query(Shipment).options(
            selectinload(Shipment.product),
            selectinload(Shipment.supplier),
        ).all()

    @staticmethod
    def get_by_id(db: Session, shipment_id):
        return db.query(Shipment).options(
            selectinload(Shipment.product),
            selectinload(Shipment.supplier),
        ).filter(
            Shipment.id == shipment_id
        ).first()

    @staticmethod
    def create(
        db: Session,
        shipment_data: ShipmentCreate
    ):
        shipment = Shipment(
            **shipment_data.model_dump()
        )

        db.add(shipment)
        db.commit()
        db.refresh(shipment)

        return shipment

    @staticmethod
    def delete(
        db: Session,
        shipment_id
    ):
        shipment = db.query(
            Shipment
        ).filter(
            Shipment.id == shipment_id
        ).first()

        if shipment:
            db.delete(shipment)
            db.commit()

        return shipment

    @staticmethod
    def get_shipment_statistics(
        db: Session
    ):
        total_shipments = db.query(
            func.count(Shipment.id)
        ).scalar()

        inbound = db.query(
            func.count(Shipment.id)
        ).filter(
            Shipment.shipment_type == "INBOUND"
        ).scalar()

        outbound = db.query(
            func.count(Shipment.id)
        ).filter(
            Shipment.shipment_type == "OUTBOUND"
        ).scalar()

        delayed = db.query(
            func.count(Shipment.id)
        ).filter(
            Shipment.status == "Delayed"
        ).scalar()

        return {
            "total_shipments": total_shipments or 0,
            "inbound_shipments": inbound or 0,
            "outbound_shipments": outbound or 0,
            "delayed_shipments": delayed or 0
        }