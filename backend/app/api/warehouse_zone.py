from typing import List
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, Request
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import require_permission
from app.models.user import User

from app.schemas.warehouse_zone import (
    WarehouseZoneCreate,
    WarehouseZoneResponse
)

from app.services.warehouse_zone_service import (
    WarehouseZoneService
)
from app.services.audit_service import AuditService

router = APIRouter(
    prefix="/api/warehouse-zones",
    tags=["Warehouse Zones"]
)


@router.get(
    "/",
    response_model=List[WarehouseZoneResponse]
)
def get_zones(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("warehouse.read")
    ),
):
    return WarehouseZoneService.get_zones(db)


# ⭐ NEW BUSINESS ENDPOINT
@router.get("/capacity")
def get_capacity_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("warehouse.read")
    ),
):
    return WarehouseZoneService.get_capacity_summary(db)


@router.get(
    "/{zone_id}",
    response_model=WarehouseZoneResponse
)
def get_zone_by_id(
    zone_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("warehouse.read")
    ),
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
    request: Request,
    background_tasks: BackgroundTasks,
    zone: WarehouseZoneCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("warehouse.write")
    ),
):
    created_zone = WarehouseZoneService.create_zone(
        db,
        zone
    )

    zone_data = jsonable_encoder(
        created_zone
    )

    AuditService.enqueue_log(
        background_tasks,
        action="WAREHOUSE_CREATED",
        resource_type="WarehouseZone",
        status_code=200,
        request=request,
        user=current_user,
        resource_id=zone_data.get("id"),
        details={
            "name": zone.name,
            "zone_type": zone.zone_type,
            "capacity_units": zone.capacity_units,
        },
    )

    return created_zone


@router.delete(
    "/{zone_id}"
)
def delete_zone(
    request: Request,
    background_tasks: BackgroundTasks,
    zone_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("warehouse.write")
    ),
):
    WarehouseZoneService.delete_zone(
        db,
        zone_id
    )

    AuditService.enqueue_log(
        background_tasks,
        action="WAREHOUSE_DELETED",
        resource_type="WarehouseZone",
        status_code=200,
        request=request,
        user=current_user,
        resource_id=zone_id,
        details={
            "zone_id": zone_id,
        },
    )

    return {
        "message": "Zone deleted successfully"
    }
