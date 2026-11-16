from types import SimpleNamespace

import pytest

from app.services.procurement_ai_service import ProcurementEvaluationError
from app.services.procurement_analysis_service import (
    ProcurementAnalysisService,
)


class StubReasoningEngine:
    def execute(self, message: str, **context):
        return {
            "user_request": message,
            "reasoning": "Procurement decisions require structured evidence.",
            "plan": ["inventory", "warehouse", "shipment", "procurement"],
            "tool_results": {
                "inventory": {"total_available_quantity": 120},
                "warehouse": {"occupancy_percentage": 72.0},
                "shipment": {"inbound_shipments": 0},
                "procurement": {
                    "decision": "APPROVE",
                    "confidence": 0.92,
                    "reason": "Capacity available. Temperature requirements satisfied.",
                },
            },
        }


class StubResponseComposer:
    def compose(self, result):
        return "Recommendation: APPROVE"


class StubProcurementAIService:
    def __init__(self, db) -> None:
        self.db = db

    def get_evaluation_context(
        self,
        product_name: str,
        pallet_quantity: int,
        month: str,
    ):
        return {
            "product": SimpleNamespace(
                shelf_life_days=420,
            ),
            "inventory": SimpleNamespace(quantity=120, zone_id="zone-1"),
            "zone": SimpleNamespace(
                name="Cold Storage B",
                capacity_units=1500,
                occupied_units=1080,
                zone_type="Cold Chain",
            ),
            "incoming_shipments": [],
            "inventory_units": 120,
            "incoming_total": 0,
            "occupancy": 72.0,
            "projected_occupancy": 80.0,
            "temperature_match": True,
            "decision": "APPROVE",
            "confidence": 0.92,
            "reasoning": [
                "Capacity available.",
                "Temperature requirements satisfied.",
            ],
            "month": month,
        }


class FailFastReasoningEngine:
    def __init__(self, planner, registry) -> None:
        pass

    def execute(self, message: str, **context):
        raise AssertionError("Reasoning should not run for an invalid request.")


class FailFastResponseComposer:
    def compose(self, result):
        raise AssertionError("Response composition should not run.")


class FailFastProcurementAIService:
    def __init__(self, db) -> None:
        pass

    def get_evaluation_context(
        self,
        product_name: str,
        pallet_quantity: int,
        month: str,
    ):
        raise AssertionError("Procurement evaluation should not run.")


def _fail_if_called(*args, **kwargs):
    raise AssertionError("Downstream lookup should not run.")


def _install_fail_fast_stubs(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.services.procurement_analysis_service.ProductService.get_product_by_id",
        _fail_if_called,
    )
    monkeypatch.setattr(
        "app.services.procurement_analysis_service.SupplierService.get_supplier_by_id",
        _fail_if_called,
    )
    monkeypatch.setattr(
        "app.services.procurement_analysis_service.ProcurementAIService",
        FailFastProcurementAIService,
    )
    monkeypatch.setattr(
        "app.services.procurement_analysis_service.ResponseComposer",
        FailFastResponseComposer,
    )
    monkeypatch.setattr(
        "app.services.procurement_analysis_service.ReasoningEngine",
        FailFastReasoningEngine,
    )


def test_procurement_analysis_service_returns_structured_analysis(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        "app.services.procurement_analysis_service.ProductService.get_product_by_id",
        lambda db, product_id: SimpleNamespace(
            id=product_id,
            name="COVID Vaccine A",
            temperature_min=2.0,
            temperature_max=8.0,
            safety_stock=100,
            shelf_life_days=420,
            supplier_id="supplier-1",
        ),
    )
    monkeypatch.setattr(
        "app.services.procurement_analysis_service.SupplierService.get_supplier_by_id",
        lambda db, supplier_id: SimpleNamespace(
            id=supplier_id,
            name="Pfizer Global Logistics",
            reliability_score=0.95,
            lead_time_days=5,
        ),
    )
    monkeypatch.setattr(
        "app.services.procurement_analysis_service.ProcurementAIService",
        StubProcurementAIService,
    )
    monkeypatch.setattr(
        "app.services.procurement_analysis_service.ResponseComposer",
        lambda: StubResponseComposer(),
    )
    monkeypatch.setattr(
        "app.services.procurement_analysis_service.ReasoningEngine",
        lambda planner, registry: StubReasoningEngine(),
    )

    service = ProcurementAnalysisService(db=object())

    result = service.analyze(
        product_id="product-1",
        supplier_id="supplier-1",
        requested_quantity=120,
    )

    assert result["decision"] == "APPROVE"
    assert result["confidence"] == 92
    assert result["tool_execution"] == [
        {"tool": "Inventory Tool", "status": "SUCCESS"},
        {"tool": "Warehouse Tool", "status": "SUCCESS"},
        {"tool": "Shipment Tool", "status": "SUCCESS"},
        {"tool": "Procurement Tool", "status": "SUCCESS"},
    ]
    assert result["evidence"]["warehouse"]["recommended_zone"] == "Cold Storage B"
    assert result["evidence"]["supplier"]["reliability_score"] == 0.95
    assert result["recommendation"] == "Approve procurement request."
    assert result["summary"] == "All procurement validation checks passed."
    assert result["explanation"] == "Recommendation: APPROVE"


@pytest.mark.parametrize("requested_quantity", [0, -1])
def test_procurement_analysis_service_rejects_non_positive_quantity(
    monkeypatch,
    requested_quantity: int,
) -> None:
    _install_fail_fast_stubs(monkeypatch)
    service = ProcurementAnalysisService(db=object())

    with pytest.raises(ProcurementEvaluationError) as error:
        service.analyze(
            product_id="product-1",
            supplier_id="supplier-1",
            requested_quantity=requested_quantity,
        )

    assert error.value.status_code == 400
    assert error.value.message == "Requested quantity must be greater than zero"


def test_procurement_analysis_service_rejects_missing_product(
    monkeypatch,
) -> None:
    _install_fail_fast_stubs(monkeypatch)
    monkeypatch.setattr(
        "app.services.procurement_analysis_service.ProductService.get_product_by_id",
        lambda db, product_id: None,
    )
    service = ProcurementAnalysisService(db=object())

    with pytest.raises(ProcurementEvaluationError) as error:
        service.analyze(
            product_id="missing-product",
            supplier_id="supplier-1",
            requested_quantity=120,
        )

    assert error.value.status_code == 404
    assert error.value.message == "Product not found"


def test_procurement_analysis_service_rejects_missing_supplier(
    monkeypatch,
) -> None:
    _install_fail_fast_stubs(monkeypatch)
    monkeypatch.setattr(
        "app.services.procurement_analysis_service.ProductService.get_product_by_id",
        lambda db, product_id: SimpleNamespace(
            id=product_id,
            name="COVID Vaccine A",
        ),
    )
    monkeypatch.setattr(
        "app.services.procurement_analysis_service.SupplierService.get_supplier_by_id",
        lambda db, supplier_id: None,
    )
    service = ProcurementAnalysisService(db=object())

    with pytest.raises(ProcurementEvaluationError) as error:
        service.analyze(
            product_id="product-1",
            supplier_id="missing-supplier",
            requested_quantity=120,
        )

    assert error.value.status_code == 404
    assert error.value.message == "Supplier not found"
