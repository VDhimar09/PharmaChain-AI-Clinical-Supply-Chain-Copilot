from sqlalchemy.orm import Session

from app.models.supplier import Supplier
from app.schemas.supplier import SupplierCreate


class SupplierRepository:

    @staticmethod
    def get_all(db: Session):
        return db.query(Supplier).all()

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