from uuid import UUID
from pydantic import BaseModel


class SupplierCreate(BaseModel):
    name: str
    country: str
    contact_person: str
    email: str
    phone: str
    lead_time_days: int
    reliability_score: float


class SupplierResponse(SupplierCreate):
    id: UUID

    model_config = {
        "from_attributes": True
    }