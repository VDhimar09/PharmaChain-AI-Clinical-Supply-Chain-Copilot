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

from app.schemas.shipment import (
    ShipmentCreate,
    ShipmentResponse
)

from app.services.shipment_service import (
    ShipmentService
)
from app.services.audit_service import AuditService

router = APIRouter(
    prefix="/api/shipments",
    tags=["Shipments"]
)


@router.get(
    "/",
    response_model=list[ShipmentResponse]
)
def get_shipments(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("shipment.read")
    ),
):
    return ShipmentService.get_shipments(db)


# ⭐ NEW BUSINESS ENDPOINT
@router.get("/statistics")
def get_shipment_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("shipment.read")
    ),
):
    return ShipmentService.get_shipment_statistics(db)


@router.post(
    "/",
    response_model=ShipmentResponse
)
def create_shipment(
    request: Request,
    background_tasks: BackgroundTasks,
    shipment: ShipmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("shipment.write")
    ),
):
    created_shipment = ShipmentService.create_shipment(
        db,
        shipment
    )

    shipment_data = jsonable_encoder(
        created_shipment
    )

    AuditService.enqueue_log(
        background_tasks,
        action="SHIPMENT_CREATED",
        resource_type="Shipment",
        status_code=200,
        request=request,
        user=current_user,
        resource_id=shipment_data.get("id"),
        details={
            "shipment_number": shipment.shipment_number,
            "shipment_type": shipment.shipment_type,
            "status": shipment.status,
            "quantity": shipment.quantity,
        },
    )

    return created_shipment


@router.get(
    "/{shipment_id}",
    response_model=ShipmentResponse
)
def get_shipment(
    shipment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("shipment.read")
    ),
):
    return ShipmentService.get_shipment_by_id(
        db,
        shipment_id
    )


@router.delete(
    "/{shipment_id}"
)
def delete_shipment(
    request: Request,
    background_tasks: BackgroundTasks,
    shipment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("shipment.write")
    ),
):
    deleted_shipment = ShipmentService.delete_shipment(
        db,
        shipment_id
    )

    AuditService.enqueue_log(
        background_tasks,
        action="SHIPMENT_DELETED",
        resource_type="Shipment",
        status_code=200,
        request=request,
        user=current_user,
        resource_id=shipment_id,
        details={
            "shipment_id": shipment_id,
            "deleted": deleted_shipment is not None,
        },
    )

    return deleted_shipment
