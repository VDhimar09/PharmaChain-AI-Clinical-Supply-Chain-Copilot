from fastapi import APIRouter
from fastapi import BackgroundTasks
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import require_permission
from app.models.user import User

from app.schemas.procurement_ai import (
    ProcurementAIRequest,
    ProcurementAIResponse
)

from app.services.procurement_ai_service import (
    ProcurementAIService,
    ProcurementEvaluationError
)
from app.services.audit_service import AuditService

router = APIRouter(
    prefix="/api/procurement-ai",
    tags=["Procurement AI"]
)


@router.post(
    "/evaluate",
    response_model=ProcurementAIResponse
)
def evaluate_procurement(
    request_context: Request,
    background_tasks: BackgroundTasks,
    request: ProcurementAIRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("ai.access")
    ),
):

    service = ProcurementAIService(db)

    try:
        response = service.evaluate_request(
            request.product_name,
            request.pallet_quantity,
            request.month
        )
        response_data = jsonable_encoder(
            response
        )

        AuditService.enqueue_log(
            background_tasks,
            action="AI_PROCUREMENT_ANALYSIS",
            resource_type="AI",
            status_code=200,
            request=request_context,
            user=current_user,
                details={
                    "product_name": request.product_name,
                    "pallet_quantity": request.pallet_quantity,
                    "month": request.month,
                    "decision": response_data.get("decision"),
                    "risk_level": response_data.get("risk_level"),
                    "response_generated": True,
                },
        )

        return response
    except ProcurementEvaluationError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.message
        ) from exc
