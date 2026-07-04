from pydantic import BaseModel
from typing import List, Literal


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
