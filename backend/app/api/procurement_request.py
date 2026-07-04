from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.core.database import get_db

from app.schemas.procurement_request import (
    ProcurementRequestCreate,
    ProcurementRequestResponse
)

from app.services.procurement_request_service import (
    ProcurementRequestService
)

router = APIRouter(
    prefix="/api/procurement-requests",
    tags=["Procurement Requests"]
)


@router.get(
    "/",
    response_model=list[ProcurementRequestResponse]
)
def get_procurement_requests(
    db: Session = Depends(get_db)
):
    return ProcurementRequestService.get_procurement_requests(db)


# ⭐ NEW ENDPOINT
@router.get("/statistics")
def get_procurement_statistics(
    db: Session = Depends(get_db)
):
    return ProcurementRequestService.get_procurement_statistics(db)


@router.post(
    "/",
    response_model=ProcurementRequestResponse
)
def create_procurement_request(
    procurement_request: ProcurementRequestCreate,
    db: Session = Depends(get_db)
):
    return ProcurementRequestService.create_procurement_request(
        db,
        procurement_request
    )


@router.get(
    "/{request_id}",
    response_model=ProcurementRequestResponse
)
def get_procurement_request(
    request_id: UUID,
    db: Session = Depends(get_db)
):
    return ProcurementRequestService.get_procurement_request_by_id(
        db,
        request_id
    )


@router.delete(
    "/{request_id}"
)
def delete_procurement_request(
    request_id: UUID,
    db: Session = Depends(get_db)
):
    return ProcurementRequestService.delete_procurement_request(
        db,
        request_id
    )