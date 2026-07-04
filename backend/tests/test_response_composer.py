import pytest

from app.ai.exceptions import ResponseCompositionException
from app.ai.response import ResponseComposer


def test_response_composer_formats_procurement_response() -> None:
    composer = ResponseComposer()

    result = {
        "user_request": "Can we receive another shipment of COVID Vaccine A next week?",
        "reasoning": "Procurement decisions require inventory, warehouse capacity, shipment analysis, and procurement policy.",
        "plan": ["inventory", "warehouse", "shipment", "procurement"],
        "tool_results": {
            "inventory": {
                "total_inventory_items": 12,
                "total_quantity": 500,
                "total_available_quantity": 320,
                "low_stock_products": 2,
            },
            "warehouse": {
                "total_capacity": 1000,
                "occupied_capacity": 750,
                "available_capacity": 250,
                "occupancy_percentage": 75.0,
            },
            "shipment": {
                "total_shipments": 14,
                "inbound_shipments": 4,
                "outbound_shipments": 8,
                "delayed_shipments": 1,
            },
            "procurement": {
                "decision": "REVIEW",
                "confidence": 0.9,
                "reason": "Inbound shipments and remaining warehouse capacity should be checked before approval.",
            },
        },
    }

    response = composer.compose(result)

    assert "Recommendation: REVIEW" in response
    assert "Confidence: 90%" in response
    assert "Inventory available: 320 units available" in response
    assert "Warehouse occupancy: 75.0% occupied" in response
    assert "Incoming shipments: 4 inbound shipments" in response
    assert "Procurement decision: REVIEW at 90% confidence" in response
    assert "Plan executed: inventory -> warehouse -> shipment -> procurement" in response


def test_response_composer_raises_response_composition_exception() -> None:
    composer = ResponseComposer()

    with pytest.raises(ResponseCompositionException) as exc_info:
        composer.compose(None)  # type: ignore[arg-type]

    assert "Unable to compose a natural-language response." in str(exc_info.value)
    assert exc_info.value.__cause__ is not None
