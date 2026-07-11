from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request

from app.dependencies.auth import require_permission
from app.jobs.scheduler import get_scheduler_service
from app.models.user import User
from app.schemas.system_job import (
    SystemJobHealthResponse,
)


router = APIRouter(
    prefix="/api/system/jobs",
    tags=["System Jobs"]
)


@router.get(
    "/",
    response_model=SystemJobHealthResponse
)
def get_system_jobs_health(
    request: Request,
    current_user: User = Depends(
        require_permission("system.monitor")
    ),
) -> SystemJobHealthResponse:
    scheduler_service = getattr(
        request.app.state,
        "scheduler_service",
        None,
    )

    if scheduler_service is None:
        scheduler_service = get_scheduler_service()

    return SystemJobHealthResponse(
        jobs=scheduler_service.get_jobs_health()
    )
