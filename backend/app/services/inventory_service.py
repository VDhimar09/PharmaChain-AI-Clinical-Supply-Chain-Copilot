from sqlalchemy.orm import Session

from app.repositories.inventory_repository import InventoryRepository
from app.schemas.inventory import InventoryCreate


class InventoryService:

    @staticmethod
    def get_inventory(
        db: Session
    ):
        return InventoryRepository.get_all(db)

    @staticmethod
    def get_inventory_by_id(
        db: Session,
        inventory_id
    ):
        return InventoryRepository.get_by_id(
            db,
            inventory_id
        )

    @staticmethod
    def create_inventory(
        db: Session,
        inventory_data: InventoryCreate
    ):
        return InventoryRepository.create(
            db,
            inventory_data
        )

    @staticmethod
    def delete_inventory(
        db: Session,
        inventory_id
    ):
        return InventoryRepository.delete(
            db,
            inventory_id
        )

    @staticmethod
    def get_inventory_statistics(
        db: Session
    ):
        return InventoryRepository.get_inventory_statistics(db)

    @staticmethod
    def get_low_stock_products(
        db: Session
    ):
        return InventoryRepository.get_low_stock_products(db)

    @staticmethod
    def get_expiring_products(
        db: Session
    ):
        return InventoryRepository.get_expiring_products(db)