from sqlalchemy.orm import Session

from app.repositories.supplier_repository import SupplierRepository
from app.schemas.supplier import SupplierCreate


class SupplierService:

    @staticmethod
    def get_suppliers(
        db: Session
    ):
        return SupplierRepository.get_all(db)

    @staticmethod
    def create_supplier(
        db: Session,
        supplier_data: SupplierCreate
    ):
        return SupplierRepository.create(
            db,
            supplier_data
        )