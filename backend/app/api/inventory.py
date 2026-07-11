from typing import List
from uuid import UUID

from fastapi import BackgroundTasks
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import require_permission
from app.models.user import User

from app.schemas.inventory import (
    InventoryCreate,
    InventoryResponse
)

from app.services.inventory_service import InventoryService
from app.services.audit_service import AuditService


router = APIRouter(
    prefix="/api/inventory",
    tags=["Inventory"]
)


@router.get(
    "/",
    response_model=List[InventoryResponse]
)
def get_inventory(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("inventory.read")
    ),
):
    return InventoryService.get_inventory(db)

@router.get("/statistics")
def get_inventory_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("inventory.read")
    ),
):
    return InventoryService.get_inventory_statistics(db)

@router.get("/low-stock")
def get_low_stock_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("inventory.read")
    ),
):
    return InventoryService.get_low_stock_products(db)

@router.get("/expiring")
def get_expiring_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("inventory.read")
    ),
):
    return InventoryService.get_expiring_products(db)

@router.get(
    "/{inventory_id}",
    response_model=InventoryResponse
)
def get_inventory_by_id(
    inventory_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("inventory.read")
    ),
):
    return InventoryService.get_inventory_by_id(
        db,
        inventory_id
    )


@router.post(
    "/",
    response_model=InventoryResponse
)
def create_inventory(
    request: Request,
    background_tasks: BackgroundTasks,
    inventory: InventoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("inventory.write")
    ),
):
    created_inventory = InventoryService.create_inventory(
        db,
        inventory
    )

    inventory_data = jsonable_encoder(
        created_inventory
    )

    AuditService.enqueue_log(
        background_tasks,
        action="INVENTORY_CREATED",
        resource_type="Inventory",
        status_code=200,
        request=request,
        user=current_user,
        resource_id=inventory_data.get("id"),
        details={
            "product_id": inventory.product_id,
            "zone_id": inventory.zone_id,
            "batch_number": inventory.batch_number,
            "quantity": inventory.quantity,
        },
    )

    return created_inventory


@router.delete(
    "/{inventory_id}"
)
def delete_inventory(
    request: Request,
    background_tasks: BackgroundTasks,
    inventory_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("inventory.write")
    ),
):
    InventoryService.delete_inventory(
        db,
        inventory_id
    )

    AuditService.enqueue_log(
        background_tasks,
        action="INVENTORY_DELETED",
        resource_type="Inventory",
        status_code=200,
        request=request,
        user=current_user,
        resource_id=inventory_id,
        details={
            "inventory_id": inventory_id,
        },
    )

    return {
        "message": "Inventory deleted successfully"
    }
