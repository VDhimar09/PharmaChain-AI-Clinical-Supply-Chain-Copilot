from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db

from app.schemas.warehouse_zone import (
    WarehouseZoneCreate,
    WarehouseZoneResponse
)

from app.services.warehouse_zone_service import (
    WarehouseZoneService
)

router = APIRouter(
    prefix="/api/warehouse-zones",
    tags=["Warehouse Zones"]
)


@router.get(
    "/",
    response_model=List[WarehouseZoneResponse]
)
def get_zones(
    db: Session = Depends(get_db)
):
    return WarehouseZoneService.get_zones(db)


# ⭐ NEW BUSINESS ENDPOINT
@router.get("/capacity")
def get_capacity_summary(
    db: Session = Depends(get_db)
):
    return WarehouseZoneService.get_capacity_summary(db)


@router.get(
    "/{zone_id}",
    response_model=WarehouseZoneResponse
)
def get_zone_by_id(
    zone_id: UUID,
    db: Session = Depends(get_db)
):
    return WarehouseZoneService.get_zone_by_id(
        db,
        zone_id
    )


@router.post(
    "/",
    response_model=WarehouseZoneResponse
)
def create_zone(
    zone: WarehouseZoneCreate,
    db: Session = Depends(get_db)
):
    return WarehouseZoneService.create_zone(
        db,
        zone
    )


@router.delete(
    "/{zone_id}"
)
def delete_zone(
    zone_id: UUID,
    db: Session = Depends(get_db)
):
    WarehouseZoneService.delete_zone(
        db,
        zone_id
    )

    return {
        "message": "Zone deleted successfully"
    }