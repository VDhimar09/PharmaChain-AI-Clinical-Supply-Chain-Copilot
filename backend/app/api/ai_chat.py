from fastapi import APIRouter
from fastapi import BackgroundTasks
from fastapi import Depends
from fastapi import Request

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import require_permission
from app.models.user import User

from app.schemas.ai_chat import (
    AIChatRequest,
    AIChatResponse
)

from app.services.ai_chat_service import (
    AIChatService
)
from app.services.audit_service import AuditService

router = APIRouter(
    prefix="/api/chat",
    tags=["AI Chat"]
)


@router.post(
    "/",
    response_model=AIChatResponse
)
def chat(
    request_context: Request,
    background_tasks: BackgroundTasks,
    request: AIChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("copilot.use")
    ),
):
    response = AIChatService.chat(
        db,
        request.message
    )

    AuditService.enqueue_log(
        background_tasks,
        action="COPILOT_CHAT",
        resource_type="AI",
        status_code=200,
        request=request_context,
        user=current_user,
        details={
            "prompt": request.message,
            "response_generated": True,
        },
    )

    return response
