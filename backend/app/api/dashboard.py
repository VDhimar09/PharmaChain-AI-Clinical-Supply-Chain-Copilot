from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import require_permission
from app.models.user import User

from app.schemas.dashboard import DashboardSummary
from app.services.dashboard_service import DashboardService


router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard"]
)


@router.get(
    "/summary",
    response_model=DashboardSummary
)
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("insights.view")
    ),
):
    return DashboardService.get_summary(db)
