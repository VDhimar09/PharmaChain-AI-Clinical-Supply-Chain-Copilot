from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db

from app.schemas.procurement_ai import (
    ProcurementAIRequest,
    ProcurementAIResponse
)

from app.services.procurement_ai_service import (
    ProcurementAIService,
    ProcurementEvaluationError
)

router = APIRouter(
    prefix="/api/procurement-ai",
    tags=["Procurement AI"]
)


@router.post(
    "/evaluate",
    response_model=ProcurementAIResponse
)
def evaluate_procurement(
    request: ProcurementAIRequest,
    db: Session = Depends(get_db)
):

    service = ProcurementAIService(db)

    try:
        return service.evaluate_request(
            request.product_name,
            request.pallet_quantity,
            request.month
        )
    except ProcurementEvaluationError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.message
        ) from exc
