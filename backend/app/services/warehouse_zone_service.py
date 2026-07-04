from sqlalchemy.orm import Session

from app.repositories.warehouse_zone_repository import (
    WarehouseZoneRepository
)

from app.schemas.warehouse_zone import (
    WarehouseZoneCreate
)


class WarehouseZoneService:

    @staticmethod
    def get_zones(db: Session):
        return WarehouseZoneRepository.get_all(db)

    @staticmethod
    def get_zone_by_id(
        db: Session,
        zone_id
    ):
        return WarehouseZoneRepository.get_by_id(
            db,
            zone_id
        )

    @staticmethod
    def create_zone(
        db: Session,
        zone_data: WarehouseZoneCreate
    ):
        return WarehouseZoneRepository.create(
            db,
            zone_data
        )

    @staticmethod
    def delete_zone(
        db: Session,
        zone_id
    ):
        return WarehouseZoneRepository.delete(
            db,
            zone_id
        )

    @staticmethod
    def get_capacity_summary(
        db: Session
    ):
        return WarehouseZoneRepository.get_capacity_summary(db)