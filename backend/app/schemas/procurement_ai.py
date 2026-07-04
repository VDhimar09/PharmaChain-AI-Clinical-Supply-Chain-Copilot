from pydantic import BaseModel, Field
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

    current_occupancy_percent: float

    projected_occupancy_percent: float