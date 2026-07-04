from datetime import date, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

from app.models.inventory import Inventory
from app.models.product import Product
from app.schemas.inventory import InventoryCreate


class InventoryRepository:

    @staticmethod
    def get_all(db: Session):
        return db.query(Inventory).options(
            selectinload(Inventory.product),
            selectinload(Inventory.zone),
        ).all()

    @staticmethod
    def get_by_id(
        db: Session,
        inventory_id
    ):
        return db.query(Inventory).options(
            selectinload(Inventory.product),
            selectinload(Inventory.zone),
        ).filter(
            Inventory.id == inventory_id
        ).first()

    @staticmethod
    def create(
        db: Session,
        inventory_data: InventoryCreate
    ):
        inventory = Inventory(
            **inventory_data.model_dump()
        )

        db.add(inventory)

        db.commit()

        db.refresh(inventory)

        return inventory

    @staticmethod
    def delete(
        db: Session,
        inventory_id
    ):
        inventory = db.query(
            Inventory
        ).filter(
            Inventory.id == inventory_id
        ).first()

        if inventory:
            db.delete(inventory)
            db.commit()

        return inventory

    @staticmethod
    def get_low_stock_products(
        db: Session
    ):
        return db.query(
            Inventory
        ).join(
            Inventory.product
        ).filter(
            Inventory.available_quantity <= Product.safety_stock
        ).order_by(
            Inventory.available_quantity.asc(),
            Inventory.expiry_date.asc()
        ).all()

    @staticmethod
    def get_expiring_products(
        db: Session,
        days: int = 30
    ):
        today = date.today()
        expiry_limit = today + timedelta(days=days)

        return db.query(
            Inventory
        ).filter(
            Inventory.expiry_date >= today,
            Inventory.expiry_date <= expiry_limit
        ).order_by(
            Inventory.expiry_date.asc(),
            Inventory.available_quantity.asc()
        ).all()

    @staticmethod
    def get_inventory_statistics(
        db: Session
    ):
        statistics = db.query(
            func.count(Inventory.id).label("total_inventory_items"),
            func.coalesce(
                func.sum(Inventory.quantity),
                0
            ).label("total_quantity"),
            func.coalesce(
                func.sum(Inventory.available_quantity),
                0
            ).label("total_available_quantity"),
            func.coalesce(
                func.sum(Inventory.reserved_quantity),
                0
            ).label("total_reserved_quantity")
        ).one()

        low_stock_count = db.query(
            func.count(Inventory.id)
        ).join(
            Inventory.product
        ).filter(
            Inventory.available_quantity <= Product.safety_stock
        ).scalar()

        return {
            "total_inventory_items": statistics.total_inventory_items,
            "total_quantity": statistics.total_quantity,
            "total_available_quantity": statistics.total_available_quantity,
            "total_reserved_quantity": statistics.total_reserved_quantity,
            "low_stock_products": low_stock_count or 0
        }
