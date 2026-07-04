from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.core.database import get_db

from app.schemas.ai_chat import (
    AIChatRequest,
    AIChatResponse
)

from app.services.ai_chat_service import (
    AIChatService
)

router = APIRouter(
    prefix="/api/chat",
    tags=["AI Chat"]
)


@router.post(
    "/",
    response_model=AIChatResponse
)
def chat(
    request: AIChatRequest,
    db: Session = Depends(get_db)
):
    return AIChatService.chat(
        db,
        request.message
    )