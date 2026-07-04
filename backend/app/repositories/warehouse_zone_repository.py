from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.warehouse_zone import WarehouseZone
from app.schemas.warehouse_zone import WarehouseZoneCreate


class WarehouseZoneRepository:

    @staticmethod
    def get_all(db: Session):
        return db.query(WarehouseZone).all()

    @staticmethod
    def get_by_id(
        db: Session,
        zone_id
    ):
        return db.query(
            WarehouseZone
        ).filter(
            WarehouseZone.id == zone_id
        ).first()

    @staticmethod
    def create(
        db: Session,
        zone_data: WarehouseZoneCreate
    ):
        zone = WarehouseZone(
            **zone_data.model_dump()
        )

        db.add(zone)
        db.commit()
        db.refresh(zone)

        return zone

    @staticmethod
    def delete(
        db: Session,
        zone_id
    ):
        zone = db.query(
            WarehouseZone
        ).filter(
            WarehouseZone.id == zone_id
        ).first()

        if zone:
            db.delete(zone)
            db.commit()

        return zone

    @staticmethod
    def get_capacity_summary(
        db: Session
    ):
        statistics = db.query(
            func.coalesce(
                func.sum(WarehouseZone.capacity_units),
                0
            ).label("total_capacity"),
            func.coalesce(
                func.sum(WarehouseZone.occupied_units),
                0
            ).label("occupied_capacity")
        ).one()

        total_capacity = statistics.total_capacity
        occupied_capacity = statistics.occupied_capacity

        available_capacity = total_capacity - occupied_capacity

        occupancy_percentage = (
            (occupied_capacity / total_capacity) * 100
            if total_capacity > 0
            else 0
        )

        return {
            "total_capacity": total_capacity,
            "occupied_capacity": occupied_capacity,
            "available_capacity": available_capacity,
            "occupancy_percentage": round(
                occupancy_percentage,
                2
            )
        }