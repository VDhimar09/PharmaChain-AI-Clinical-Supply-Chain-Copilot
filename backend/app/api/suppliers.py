from typing import List

from fastapi import BackgroundTasks
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import require_permission
from app.models.user import User

from app.schemas.supplier import (
    SupplierCreate,
    SupplierResponse
)

from app.services.supplier_service import SupplierService
from app.services.audit_service import AuditService


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
    request: Request,
    background_tasks: BackgroundTasks,
    supplier: SupplierCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("supplier.write")
    ),
):
    created_supplier = SupplierService.create_supplier(
        db,
        supplier
    )

    supplier_data = jsonable_encoder(
        created_supplier
    )

    AuditService.enqueue_log(
        background_tasks,
        action="SUPPLIER_CREATED",
        resource_type="Supplier",
        status_code=200,
        request=request,
        user=current_user,
        resource_id=supplier_data.get("id"),
        details={
            "name": supplier.name,
            "country": supplier.country,
            "lead_time_days": supplier.lead_time_days,
        },
    )

    return created_supplier
