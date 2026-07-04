from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.core.database import get_db

from app.schemas.shipment import (
    ShipmentCreate,
    ShipmentResponse
)

from app.services.shipment_service import (
    ShipmentService
)

router = APIRouter(
    prefix="/api/shipments",
    tags=["Shipments"]
)


@router.get(
    "/",
    response_model=list[ShipmentResponse]
)
def get_shipments(
    db: Session = Depends(get_db)
):
    return ShipmentService.get_shipments(db)


# ⭐ NEW BUSINESS ENDPOINT
@router.get("/statistics")
def get_shipment_statistics(
    db: Session = Depends(get_db)
):
    return ShipmentService.get_shipment_statistics(db)


@router.post(
    "/",
    response_model=ShipmentResponse
)
def create_shipment(
    shipment: ShipmentCreate,
    db: Session = Depends(get_db)
):
    return ShipmentService.create_shipment(
        db,
        shipment
    )


@router.get(
    "/{shipment_id}",
    response_model=ShipmentResponse
)
def get_shipment(
    shipment_id: UUID,
    db: Session = Depends(get_db)
):
    return ShipmentService.get_shipment_by_id(
        db,
        shipment_id
    )


@router.delete(
    "/{shipment_id}"
)
def delete_shipment(
    shipment_id: UUID,
    db: Session = Depends(get_db)
):
    return ShipmentService.delete_shipment(
        db,
        shipment_id
    )