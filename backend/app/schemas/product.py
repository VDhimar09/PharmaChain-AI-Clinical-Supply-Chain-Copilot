from uuid import UUID
from pydantic import BaseModel


class ProductCreate(BaseModel):
    sku: str
    name: str
    category: str
    description: str
    dosage_form: str
    unit_of_measure: str
    temperature_min: float
    temperature_max: float
    shelf_life_days: int
    safety_stock: int
    supplier_id: UUID


class ProductResponse(ProductCreate):
    id: UUID

    model_config = {
        "from_attributes": True
    }