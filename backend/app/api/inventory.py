from typing import List
from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import require_permission
from app.models.user import User

from app.schemas.inventory import (
    InventoryCreate,
    InventoryResponse
)

from app.services.inventory_service import InventoryService


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
    inventory: InventoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("inventory.write")
    ),
):
    return InventoryService.create_inventory(
        db,
        inventory
    )


@router.delete(
    "/{inventory_id}"
)
def delete_inventory(
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

    return {
        "message": "Inventory deleted successfully"
    }
