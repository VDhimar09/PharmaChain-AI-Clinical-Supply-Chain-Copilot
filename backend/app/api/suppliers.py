from typing import List

from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import require_permission
from app.models.user import User

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
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("supplier.read")
    ),
):
    return SupplierService.get_suppliers(db)


@router.post(
    "/",
    response_model=SupplierResponse
)
def create_supplier(
    supplier: SupplierCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("supplier.write")
    ),
):
    return SupplierService.create_supplier(
        db,
        supplier
    )
