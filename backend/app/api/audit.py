from datetime import datetime
from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import require_permission
from app.models.user import User
from app.repositories.audit_log_repository import AuditLogRepository
from app.schemas.audit import AuditLogListResponse


router = APIRouter(
    prefix="/api/audit",
    tags=["Audit"]
)


@router.get(
    "/",
    response_model=AuditLogListResponse
)
def get_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    user_id: UUID | None = None,
    user_email: str | None = None,
    resource_type: str | None = None,
    resource_id: str | None = None,
    action: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("audit.read")
    ),
):
    if current_user.role.name != "Administrator":
        user_id = current_user.id
        user_email = current_user.email

    offset = (page - 1) * page_size

    total, items = AuditLogRepository.filter(
        db,
        start_date=start_date,
        end_date=end_date,
        user_id=user_id,
        user_email=user_email,
        resource_type=resource_type,
        resource_id=resource_id,
        action=action,
        offset=offset,
        limit=page_size,
    )

    return AuditLogListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items,
    )
