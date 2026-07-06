from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel


class ExecutiveSummary(BaseModel):
    inventory_value: int
    warehouse_utilisation: int
    pending_procurements: int
    critical_alerts: int


class InventoryInsightItem(BaseModel):
    id: UUID
    product_name: str
    sku: str
    category: str
    warehouse_zone: str
    quantity: int
    available_quantity: int
    reserved_quantity: int
    expiry_date: date | None = None
    days_to_expiry: int | None = None
    status: str


class WarehouseInsightItem(BaseModel):
    id: UUID
    name: str
    zone_type: str
    capacity_units: int
    occupied_units: int
    available_capacity: int
    occupancy_percentage: int
    temperature_min: float | None = None
    temperature_max: float | None = None
    status: str


class ShipmentInsightItem(BaseModel):
    id: UUID
    shipment_number: str
    shipment_type: str
    product_name: str
    supplier_name: str
    quantity: int
    status: str
    expected_arrival: datetime
    delay_days: int | None = None


class ProcurementInsightItem(BaseModel):
    id: UUID
    product_name: str
    requested_quantity: int
    priority: str
    status: str
    ai_recommendation: str | None = None
    ai_confidence: float | None = None
    created_by: str
    created_at: datetime
    approved_at: datetime | None = None


class InsightAlert(BaseModel):
    severity: Literal["LOW", "MEDIUM", "HIGH"]
    title: str
    message: str


class InsightRecommendation(BaseModel):
    priority: Literal["LOW", "MEDIUM", "HIGH"]
    title: str
    message: str


class TrendPoint(BaseModel):
    label: str
    value: int
    secondary_value: int | None = None


class InventoryInsights(BaseModel):
    low_stock: list[InventoryInsightItem]
    overstock: list[InventoryInsightItem]
    near_expiry: list[InventoryInsightItem]
    fast_moving: list[InventoryInsightItem]
    slow_moving: list[InventoryInsightItem]


class WarehouseInsights(BaseModel):
    occupancy: list[WarehouseInsightItem]
    cold_chain: list[WarehouseInsightItem]
    available_capacity: list[WarehouseInsightItem]


class ShipmentInsights(BaseModel):
    incoming: list[ShipmentInsightItem]
    outgoing: list[ShipmentInsightItem]
    delayed: list[ShipmentInsightItem]


class ProcurementInsights(BaseModel):
    pending: list[ProcurementInsightItem]
    approved: list[ProcurementInsightItem]
    rejected: list[ProcurementInsightItem]


class TrendData(BaseModel):
    inventory: list[TrendPoint]
    shipments: list[TrendPoint]
    warehouse: list[TrendPoint]


class AIInsightsResponse(BaseModel):
    generated_at: datetime
    confidence: int
    executive_summary: ExecutiveSummary
    inventory: InventoryInsights
    warehouse: WarehouseInsights
    shipments: ShipmentInsights
    procurement: ProcurementInsights
    alerts: list[InsightAlert]
    recommendations: list[InsightRecommendation]
    trend_data: TrendData
