from sqlalchemy.orm import Session

from app.models.supplier import Supplier
from app.schemas.supplier import SupplierCreate


class SupplierRepository:

    @staticmethod
    def get_all(db: Session):
        return db.query(Supplier).all()

    @staticmethod
    def has_any(db: Session) -> bool:
        return db.query(Supplier.id).first() is not None

    @staticmethod
    def get_by_id(db: Session, supplier_id):
        return db.query(Supplier).filter(
            Supplier.id == supplier_id
        ).first()

    @staticmethod
    def create(
        db: Session,
        supplier_data: SupplierCreate
    ):
        supplier = Supplier(
            **supplier_data.model_dump()
        )

        db.add(supplier)

        db.commit()

        db.refresh(supplier)

        return supplier
