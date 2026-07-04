from app.ai.tools.procurement_tool import ProcurementTool


def test_procurement_tool_delegates_to_service_and_normalizes_response(
    monkeypatch,
) -> None:
    db = object()
    captured: dict = {}

    class StubProcurementAIService:
        def __init__(self, session) -> None:
            captured["db"] = session

        def evaluate_request(
            self,
            product_name: str,
            pallet_quantity: int,
            month: str,
        ) -> dict:
            captured["request"] = {
                "product_name": product_name,
                "pallet_quantity": pallet_quantity,
                "month": month,
            }
            return {
                "decision": "APPROVE",
                "confidence": 0.92,
                "reasoning": [
                    "Capacity available.",
                    "Temperature requirements satisfied.",
                ],
                "inventory_units": 120,
                "current_occupancy_percent": 72.5,
                "projected_occupancy_percent": 81.0,
            }

    monkeypatch.setattr(
        "app.ai.tools.procurement_tool.ProcurementAIService",
        StubProcurementAIService,
    )

    result = ProcurementTool().run(
        db=db,
        product_name="COVID Vaccine A",
        pallet_quantity=12,
        month="July",
    )

    assert captured["db"] is db
    assert captured["request"] == {
        "product_name": "COVID Vaccine A",
        "pallet_quantity": 12,
        "month": "July",
    }
    assert result["decision"] == "APPROVE"
    assert result["confidence"] == 0.92
    assert result["reasoning"] == [
        "Capacity available.",
        "Temperature requirements satisfied.",
    ]
    assert (
        result["reason"]
        == "Capacity available. Temperature requirements satisfied."
    )


def test_procurement_tool_extracts_request_fields_from_message(
    monkeypatch,
) -> None:
    captured: dict = {}

    class StubProcurementAIService:
        def __init__(self, session) -> None:
            captured["db"] = session

        def evaluate_request(
            self,
            product_name: str,
            pallet_quantity: int,
            month: str,
        ) -> dict:
            captured["request"] = {
                "product_name": product_name,
                "pallet_quantity": pallet_quantity,
                "month": month,
            }
            return {
                "decision": "REVIEW",
                "confidence": 0.75,
                "reasoning": [
                    "Incoming shipments may impact available capacity.",
                ],
                "inventory_units": 80,
                "current_occupancy_percent": 76.0,
                "projected_occupancy_percent": 88.0,
            }

    monkeypatch.setattr(
        "app.ai.tools.procurement_tool.ProcurementAIService",
        StubProcurementAIService,
    )

    ProcurementTool().run(
        db=object(),
        message="Can we receive 12 pallets of COVID Vaccine A next week?",
    )

    assert captured["request"] == {
        "product_name": "COVID Vaccine A",
        "pallet_quantity": 12,
        "month": "next week",
    }
