from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class ShipmentCreate(BaseModel):
    shipment_number: str
    shipment_type: str
    product_id: UUID
    supplier_id: UUID
    quantity: int
    status: str
    expected_arrival: datetime


class ShipmentResponse(ShipmentCreate):
    id: UUID
    product_name: str
    supplier_name: str

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "884fe88c-1234-4a1b-8f2a-1234567890ab",
                "shipment_number": "SHP-10231",
                "shipment_type": "INBOUND",
                "product_id": "d7c4b8f2-1234-4a1b-8f2a-1234567890ab",
                "supplier_id": "a1b2c3d4-1234-4a1b-8f2a-1234567890ab",
                "quantity": 2400,
                "status": "IN_TRANSIT",
                "expected_arrival": "2026-08-31T00:00:00",
                "product_name": "COVID Vaccine A",
                "supplier_name": "Pfizer"
            }
        }
    }