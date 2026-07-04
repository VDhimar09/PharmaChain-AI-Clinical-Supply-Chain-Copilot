from pydantic import BaseModel
from uuid import UUID


class WarehouseZoneCreate(BaseModel):
    name: str
    zone_type: str
    capacity_units: int
    occupied_units: int
    temperature_min: float
    temperature_max: float


class WarehouseZoneResponse(WarehouseZoneCreate):
    id: UUID

    class Config:
        from_attributes = True