from pydantic import BaseModel
from typing import List, Literal
from uuid import UUID


class ProcurementAIRequest(BaseModel):
    product_name: str
    pallet_quantity: int
    month: str


class ProcurementAIResponse(BaseModel):
    decision: Literal[
        "APPROVE",
        "REJECT",
        "REVIEW"
    ]

    confidence: float

    reasoning: List[str]

    inventory_units: int

    risk_level: Literal[
        "LOW",
        "MEDIUM",
        "HIGH"
    ]

    recommended_zone: str

    temperature_fit: Literal[
        "MATCH",
        "MISMATCH"
    ]

    badges: List[str]

    current_occupancy_percent: float

    projected_occupancy_percent: float


class ProcurementAnalysisRequest(BaseModel):
    product_id: UUID
    supplier_id: UUID
    requested_quantity: int


class ProcurementRequestDetails(BaseModel):
    product_id: UUID
    product_name: str
    supplier_id: UUID
    supplier_name: str
    requested_quantity: int
    temperature_min: float
    temperature_max: float
    safety_stock: int
    shelf_life_days: int


class ToolExecutionItem(BaseModel):
    tool: str
    status: Literal["SUCCESS", "FAILED"]


class ReasoningStep(BaseModel):
    step: str
    status: Literal["PASS", "ATTENTION", "FAIL"]
    message: str


class InventoryEvidence(BaseModel):
    available_units: int
    requested_quantity: int
    safety_stock: int
    below_safety_stock: bool


class WarehouseEvidence(BaseModel):
    recommended_zone: str
    current_occupancy_percent: float
    projected_occupancy_percent: float
    available_capacity_units: int


class ShipmentEvidence(BaseModel):
    incoming_shipments: int
    incoming_units: int
    conflict_detected: bool


class SupplierEvidence(BaseModel):
    supplier_name: str
    reliability_score: float
    lead_time_days: int


class ColdChainEvidence(BaseModel):
    compatible: bool
    temperature_min: float
    temperature_max: float
    zone_name: str


class ProcurementEvidence(BaseModel):
    demand_forecast: str
    shelf_life_valid: bool
    shelf_life_days: int


class ProcurementEvidenceBundle(BaseModel):
    inventory: InventoryEvidence
    warehouse: WarehouseEvidence
    shipments: ShipmentEvidence
    supplier: SupplierEvidence
    cold_chain: ColdChainEvidence
    procurement: ProcurementEvidence


class ProcurementAnalysisResponse(BaseModel):
    request_details: ProcurementRequestDetails
    decision: Literal["APPROVE", "REJECT", "REVIEW"]
    confidence: int
    tool_execution: List[ToolExecutionItem]
    reasoning: List[ReasoningStep]
    evidence: ProcurementEvidenceBundle
    recommendation: str
    summary: str
    explanation: str
