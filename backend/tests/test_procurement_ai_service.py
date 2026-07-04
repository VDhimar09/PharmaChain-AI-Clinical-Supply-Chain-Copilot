from types import SimpleNamespace

from app.services.procurement_ai_service import ProcurementAIService


class StubProcurementRepository:
    def __init__(self, db) -> None:
        self.db = db

    def get_product(self, product_name: str):
        return SimpleNamespace(
            id="product-1",
            name="COVID Vaccine A",
            temperature_min=2.0,
            temperature_max=8.0,
            shelf_life_days=420,
        )

    def get_inventory(self, product_id):
        return SimpleNamespace(
            quantity=120,
            zone_id="zone-1",
        )

    def get_zone(self, zone_id):
        return SimpleNamespace(
            id="zone-1",
            name="Cold Storage B",
            zone_type="Cold Chain",
            temperature_min=2.0,
            temperature_max=8.0,
            capacity_units=1500,
            occupied_units=1080,
        )

    def get_compatible_zone(
        self,
        temperature_min: float,
        temperature_max: float,
    ):
        raise AssertionError(
            "Compatible zone lookup should not run when inventory exists."
        )

    def get_incoming_shipments(self):
        return []


class StubRepositoryWithIncomingShipments(StubProcurementRepository):
    def get_inventory(self, product_id):
        return None

    def get_compatible_zone(
        self,
        temperature_min: float,
        temperature_max: float,
    ):
        return SimpleNamespace(
            id="zone-2",
            name="Ambient Reserve",
            zone_type="Ambient",
            temperature_min=2.0,
            temperature_max=8.0,
            capacity_units=1000,
            occupied_units=700,
        )

    def get_incoming_shipments(self):
        return [
            SimpleNamespace(quantity=50),
            SimpleNamespace(quantity=25),
        ]


def test_procurement_ai_service_returns_extended_response_fields(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        "app.services.procurement_ai_service.ProcurementRepository",
        StubProcurementRepository,
    )

    service = ProcurementAIService(db=object())

    result = service.evaluate_request(
        product_name="COVID Vaccine A",
        pallet_quantity=120,
        month="July",
    )

    assert result == {
        "decision": "APPROVE",
        "confidence": 0.92,
        "reasoning": [
            "Capacity available.",
            "Temperature requirements satisfied.",
        ],
        "inventory_units": 120,
        "risk_level": "LOW",
        "recommended_zone": "Cold Storage B",
        "temperature_fit": "MATCH",
        "badges": [
            "Temperature Fit: Match",
            "Zone Type: Cold Chain",
            "Shelf Life: 14 mo",
            "No Incoming Shipment Conflict",
        ],
        "current_occupancy_percent": 72.0,
        "projected_occupancy_percent": 80.0,
    }


def test_procurement_ai_service_includes_fallback_reasoning_and_review_metadata(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        "app.services.procurement_ai_service.ProcurementRepository",
        StubRepositoryWithIncomingShipments,
    )

    service = ProcurementAIService(db=object())

    result = service.evaluate_request(
        product_name="COVID Vaccine A",
        pallet_quantity=120,
        month="July",
    )

    assert result["decision"] == "REVIEW"
    assert result["confidence"] == 0.75
    assert result["risk_level"] == "MEDIUM"
    assert result["recommended_zone"] == "Ambient Reserve"
    assert result["temperature_fit"] == "MATCH"
    assert result["badges"] == [
        "Temperature Fit: Match",
        "Zone Type: Ambient",
        "Shelf Life: 14 mo",
        "Incoming Shipments Pending",
    ]
    assert (
        "No existing inventory record was found for this product, so the recommendation used a compatible warehouse zone."
        in result["reasoning"]
    )
    assert (
        "Incoming shipments may impact available capacity."
        in result["reasoning"]
    )
