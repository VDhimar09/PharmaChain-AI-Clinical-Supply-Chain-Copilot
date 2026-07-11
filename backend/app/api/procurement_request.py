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

from app.schemas.procurement_request import (
    ProcurementRequestCreate,
    ProcurementRequestResponse
)

from app.services.procurement_request_service import (
    ProcurementRequestService
)
from app.services.audit_service import AuditService

router = APIRouter(
    prefix="/api/procurement-requests",
    tags=["Procurement Requests"]
)


@router.get(
    "/",
    response_model=list[ProcurementRequestResponse]
)
def get_procurement_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("procurement.read")
    ),
):
    return ProcurementRequestService.get_procurement_requests(db)


# ⭐ NEW ENDPOINT
@router.get("/statistics")
def get_procurement_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("procurement.read")
    ),
):
    return ProcurementRequestService.get_procurement_statistics(db)


@router.post(
    "/",
    response_model=ProcurementRequestResponse
)
def create_procurement_request(
    request: Request,
    background_tasks: BackgroundTasks,
    procurement_request: ProcurementRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("procurement.write")
    ),
):
    created_request = ProcurementRequestService.create_procurement_request(
        db,
        procurement_request
    )

    procurement_data = jsonable_encoder(
        created_request
    )

    AuditService.enqueue_log(
        background_tasks,
        action="PROCUREMENT_REQUEST_CREATED",
        resource_type="ProcurementRequest",
        status_code=200,
        request=request,
        user=current_user,
        resource_id=procurement_data.get("id"),
        details={
            "product_id": procurement_request.product_id,
            "requested_quantity": procurement_request.requested_quantity,
            "priority": procurement_request.priority,
            "status": procurement_request.status,
        },
    )

    return created_request


@router.get(
    "/{request_id}",
    response_model=ProcurementRequestResponse
)
def get_procurement_request(
    request_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("procurement.read")
    ),
):
    return ProcurementRequestService.get_procurement_request_by_id(
        db,
        request_id
    )


@router.delete(
    "/{request_id}"
)
def delete_procurement_request(
    request: Request,
    background_tasks: BackgroundTasks,
    request_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("procurement.write")
    ),
):
    deleted_request = ProcurementRequestService.delete_procurement_request(
        db,
        request_id
    )

    AuditService.enqueue_log(
        background_tasks,
        action="PROCUREMENT_REQUEST_DELETED",
        resource_type="ProcurementRequest",
        status_code=200,
        request=request,
        user=current_user,
        resource_id=request_id,
        details={
            "request_id": request_id,
            "deleted": deleted_request is not None,
        },
    )

    return deleted_request
