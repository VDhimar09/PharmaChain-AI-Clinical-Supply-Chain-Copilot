from typing import List

from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.core.database import get_db

from app.schemas.supplier import (
    SupplierCreate,
    SupplierResponse
)

from app.services.supplier_service import SupplierService


router = APIRouter(
    prefix="/api/suppliers",
    tags=["Suppliers"]
)


@router.get(
    "/",
    response_model=List[SupplierResponse]
)
def get_suppliers(
    db: Session = Depends(get_db)
):
    return SupplierService.get_suppliers(db)


@router.post(
    "/",
    response_model=SupplierResponse
)
def create_supplier(
    supplier: SupplierCreate,
    db: Session = Depends(get_db)
):
    return SupplierService.create_supplier(
        db,
        supplier
    )