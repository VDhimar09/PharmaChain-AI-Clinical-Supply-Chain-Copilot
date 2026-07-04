from pydantic import BaseModel
from uuid import UUID
from datetime import date


class InventoryCreate(BaseModel):
    product_id: UUID
    zone_id: UUID
    batch_number: str
    quantity: int
    reserved_quantity: int
    available_quantity: int
    expiry_date: date


class InventoryResponse(BaseModel):
    id: UUID
    product_id: UUID
    zone_id: UUID
    product_name: str
    sku: str
    category: str
    temperature_requirement: str
    batch_number: str
    quantity: int
    available_quantity: int
    reserved_quantity: int
    expiry_date: date
    warehouse_zone: str
    status: str

    model_config = {
        "from_attributes": True,
    }