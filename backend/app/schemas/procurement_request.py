from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class ProcurementRequestCreate(BaseModel):
    product_id: UUID
    requested_quantity: int
    priority: str
    status: str
    ai_recommendation: str | None = None
    ai_confidence: float | None = None
    ai_reasoning: str | None = None
    created_by: str


class ProcurementRequestResponse(
    ProcurementRequestCreate
):
    id: UUID
    created_at: datetime
    approved_at: datetime | None = None

    class Config:
        from_attributes = True