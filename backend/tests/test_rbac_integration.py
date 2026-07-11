from collections.abc import Callable
from collections.abc import Iterator
from datetime import date
from datetime import datetime
from datetime import timezone
from uuid import uuid4

import pytest
from fastapi import Depends
from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.dependencies.auth import require_permission
from app.main import app
from app.models.permission import Permission
from app.models.role import Role
from app.models.user import User
from app.repositories.role_repository import RoleRepository


UUID_1 = "11111111-1111-1111-1111-111111111111"
UUID_2 = "22222222-2222-2222-2222-222222222222"
NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)

PRODUCT_PAYLOAD = {
    "sku": "SKU-001",
    "name": "Test Product",
    "category": "Vaccines",
    "description": "Temperature sensitive",
    "dosage_form": "Injection",
    "unit_of_measure": "Vial",
    "temperature_min": 2.0,
    "temperature_max": 8.0,
    "shelf_life_days": 180,
    "safety_stock": 50,
    "supplier_id": UUID_1,
}
PRODUCT_RESPONSE = {
    "id": UUID_1,
    **PRODUCT_PAYLOAD,
}

SUPPLIER_PAYLOAD = {
    "name": "Acme Supply",
    "country": "USA",
    "contact_person": "Jane Doe",
    "email": "jane@example.com",
    "phone": "+1-555-1000",
    "lead_time_days": 7,
    "reliability_score": 99.5,
}
SUPPLIER_RESPONSE = {
    "id": UUID_1,
    **SUPPLIER_PAYLOAD,
}

INVENTORY_PAYLOAD = {
    "product_id": UUID_1,
    "zone_id": UUID_2,
    "batch_number": "BATCH-001",
    "quantity": 100,
    "reserved_quantity": 10,
    "available_quantity": 90,
    "expiry_date": "2026-12-31",
}
INVENTORY_RESPONSE = {
    "id": UUID_1,
    "product_id": UUID_1,
    "zone_id": UUID_2,
    "product_name": "Test Product",
    "sku": "SKU-001",
    "category": "Vaccines",
    "temperature_requirement": "2C-8C",
    "batch_number": "BATCH-001",
    "quantity": 100,
    "available_quantity": 90,
    "reserved_quantity": 10,
    "expiry_date": "2026-12-31",
    "warehouse_zone": "Cold Storage",
    "status": "Available",
}

WAREHOUSE_PAYLOAD = {
    "name": "Cold Storage",
    "zone_type": "COLD",
    "capacity_units": 500,
    "occupied_units": 100,
    "temperature_min": 2.0,
    "temperature_max": 8.0,
}
WAREHOUSE_RESPONSE = {
    "id": UUID_1,
    **WAREHOUSE_PAYLOAD,
}

SHIPMENT_PAYLOAD = {
    "shipment_number": "SHP-1001",
    "shipment_type": "INBOUND",
    "product_id": UUID_1,
    "supplier_id": UUID_2,
    "quantity": 240,
    "status": "IN_TRANSIT",
    "expected_arrival": "2026-01-02T00:00:00Z",
}
SHIPMENT_RESPONSE = {
    "id": UUID_1,
    **SHIPMENT_PAYLOAD,
    "product_name": "Test Product",
    "supplier_name": "Acme Supply",
}

PROCUREMENT_PAYLOAD = {
    "product_id": UUID_1,
    "requested_quantity": 100,
    "priority": "HIGH",
    "status": "PENDING",
    "ai_recommendation": "APPROVE",
    "ai_confidence": 0.95,
    "ai_reasoning": "Sufficient capacity",
    "created_by": "system",
}
PROCUREMENT_RESPONSE = {
    "id": UUID_1,
    **PROCUREMENT_PAYLOAD,
    "created_at": NOW.isoformat(),
    "approved_at": None,
}

PROCUREMENT_AI_PAYLOAD = {
    "product_name": "Test Product",
    "pallet_quantity": 5,
    "month": "2026-01",
}
PROCUREMENT_AI_RESPONSE = {
    "decision": "APPROVE",
    "confidence": 0.98,
    "reasoning": ["Capacity available"],
    "inventory_units": 1000,
    "risk_level": "LOW",
    "recommended_zone": "Cold Storage",
    "temperature_fit": "MATCH",
    "badges": ["Cold Chain"],
    "current_occupancy_percent": 50.0,
    "projected_occupancy_percent": 60.0,
}

PROCUREMENT_ANALYSIS_PAYLOAD = {
    "product_id": UUID_1,
    "supplier_id": UUID_2,
    "requested_quantity": 100,
}
PROCUREMENT_ANALYSIS_RESPONSE = {
    "request_details": {
        "product_id": UUID_1,
        "product_name": "Test Product",
        "supplier_id": UUID_2,
        "supplier_name": "Acme Supply",
        "requested_quantity": 100,
        "temperature_min": 2.0,
        "temperature_max": 8.0,
        "safety_stock": 50,
        "shelf_life_days": 180,
    },
    "decision": "APPROVE",
    "confidence": 95,
    "tool_execution": [{"tool": "inventory", "status": "SUCCESS"}],
    "reasoning": [
        {
            "step": "Capacity check",
            "status": "PASS",
            "message": "Warehouse capacity is sufficient.",
        }
    ],
    "evidence": {
        "inventory": {
            "available_units": 1000,
            "requested_quantity": 100,
            "safety_stock": 50,
            "below_safety_stock": False,
        },
        "warehouse": {
            "recommended_zone": "Cold Storage",
            "current_occupancy_percent": 50.0,
            "projected_occupancy_percent": 60.0,
            "available_capacity_units": 200,
        },
        "shipments": {
            "incoming_shipments": 1,
            "incoming_units": 240,
            "conflict_detected": False,
        },
        "supplier": {
            "supplier_name": "Acme Supply",
            "reliability_score": 99.5,
            "lead_time_days": 7,
        },
        "cold_chain": {
            "compatible": True,
            "temperature_min": 2.0,
            "temperature_max": 8.0,
            "zone_name": "Cold Storage",
        },
        "procurement": {
            "demand_forecast": "Stable",
            "shelf_life_valid": True,
            "shelf_life_days": 180,
        },
    },
    "recommendation": "Approve the request.",
    "summary": "Approval recommended.",
    "explanation": "Stock, warehouse, and supplier checks passed.",
}

AI_INSIGHTS_RESPONSE = {
    "generated_at": NOW.isoformat(),
    "confidence": 95,
    "executive_summary": {
        "inventory_value": 100000,
        "warehouse_utilisation": 65,
        "pending_procurements": 4,
        "critical_alerts": 1,
    },
    "inventory": {
        "low_stock": [],
        "overstock": [],
        "near_expiry": [],
        "fast_moving": [],
        "slow_moving": [],
    },
    "warehouse": {
        "occupancy": [],
        "cold_chain": [],
        "available_capacity": [],
    },
    "shipments": {
        "incoming": [],
        "outgoing": [],
        "delayed": [],
    },
    "procurement": {
        "pending": [],
        "approved": [],
        "rejected": [],
    },
    "alerts": [],
    "recommendations": [],
    "trend_data": {
        "inventory": [],
        "shipments": [],
        "warehouse": [],
    },
}

COPILOT_RESPONSE = {
    "conversation_id": UUID_1,
    "generated_at": NOW.isoformat(),
    "intent": "summary",
    "confidence": 90,
    "tools_used": ["inventory"],
    "reasoning": [{"step": "Analyze", "status": "PASS"}],
    "tool_execution": [
        {"tool": "inventory", "status": "SUCCESS", "execution_time_ms": 12.0}
    ],
    "evidence": {
        "inventory": {},
        "warehouse": {},
        "shipments": {},
        "procurement": {},
        "ai_insights": {},
    },
    "recommendations": ["Restock Product A"],
    "response": "Inventory looks healthy overall.",
}


@app.put("/api/test/rbac/procurement-approval")
def procurement_approval_probe(
    current_user: User = Depends(
        require_permission("procurement.approve")
    ),
):
    return {
        "message": "approved"
    }

ADMIN_ENDPOINTS = [
    ("GET", "/api/products/", None, 200),
    ("POST", "/api/products/", PRODUCT_PAYLOAD, 200),
    ("GET", "/api/suppliers/", None, 200),
    ("POST", "/api/suppliers/", SUPPLIER_PAYLOAD, 200),
    ("GET", "/api/inventory/", None, 200),
    ("GET", "/api/inventory/statistics", None, 200),
    ("GET", "/api/inventory/low-stock", None, 200),
    ("GET", "/api/inventory/expiring", None, 200),
    ("GET", f"/api/inventory/{UUID_1}", None, 200),
    ("POST", "/api/inventory/", INVENTORY_PAYLOAD, 200),
    ("DELETE", f"/api/inventory/{UUID_1}", None, 200),
    ("GET", "/api/warehouse-zones/", None, 200),
    ("GET", "/api/warehouse-zones/capacity", None, 200),
    ("GET", f"/api/warehouse-zones/{UUID_1}", None, 200),
    ("POST", "/api/warehouse-zones/", WAREHOUSE_PAYLOAD, 200),
    ("DELETE", f"/api/warehouse-zones/{UUID_1}", None, 200),
    ("GET", "/api/shipments/", None, 200),
    ("GET", "/api/shipments/statistics", None, 200),
    ("POST", "/api/shipments/", SHIPMENT_PAYLOAD, 200),
    ("GET", f"/api/shipments/{UUID_1}", None, 200),
    ("DELETE", f"/api/shipments/{UUID_1}", None, 200),
    ("GET", "/api/procurement-requests/", None, 200),
    ("GET", "/api/procurement-requests/statistics", None, 200),
    ("POST", "/api/procurement-requests/", PROCUREMENT_PAYLOAD, 200),
    ("GET", f"/api/procurement-requests/{UUID_1}", None, 200),
    ("DELETE", f"/api/procurement-requests/{UUID_1}", None, 200),
    ("GET", "/api/dashboard/summary", None, 200),
    ("POST", "/api/procurement-ai/evaluate", PROCUREMENT_AI_PAYLOAD, 200),
    ("GET", "/api/ai/inventory-summary", None, 200),
    ("GET", "/api/ai/low-stock", None, 200),
    ("GET", "/api/ai/expiring", None, 200),
    ("GET", "/api/ai/warehouse-capacity", None, 200),
    ("GET", "/api/ai/shipment-summary", None, 200),
    ("GET", "/api/ai/insights", None, 200),
    ("POST", "/api/ai/copilot/chat", {"message": "Hello"}, 200),
    ("POST", "/api/ai/procurement/analyze", PROCUREMENT_ANALYSIS_PAYLOAD, 200),
    ("POST", "/api/chat/", {"message": "Hello"}, 200),
]


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def user_factory(client: TestClient) -> Iterator[Callable[..., tuple[str, str]]]:
    created_user_ids: list[str] = []
    created_role_ids: list[str] = []

    def factory(
        *,
        role_name: str,
        permissions: list[str] | None = None,
        use_seeded_role: bool = True,
    ) -> tuple[str, str]:
        db = SessionLocal()
        try:
            if use_seeded_role:
                role = RoleRepository.get_by_name(db, role_name)
                assert role is not None
            else:
                role = Role(
                    name=f"{role_name}-{uuid4()}",
                    description=f"{role_name} test role",
                )
                for permission_name in permissions or []:
                    role.permissions.append(
                        Permission(
                            name=permission_name,
                            description=f"{permission_name} test permission",
                        )
                    )
                db.add(role)
                db.flush()
                created_role_ids.append(str(role.id))

            password = "Password123!"
            email = f"{uuid4()}@example.com"
            user = User(
                email=email,
                full_name=f"{role_name} User",
                password_hash=hash_password(password),
                role=role,
                is_active=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            created_user_ids.append(str(user.id))
            return email, password
        finally:
            db.close()

    yield factory

    db = SessionLocal()
    try:
        for user_id in created_user_ids:
            user = db.get(User, user_id)
            if user is not None:
                db.delete(user)
        db.commit()

        for role_id in created_role_ids:
            role = db.get(Role, role_id)
            if role is not None:
                db.delete(role)
        db.commit()
    finally:
        db.close()


def _login(client: TestClient, email: str, password: str) -> dict:
    response = client.post(
        "/api/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == 200
    return response.json()


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _request(
    client: TestClient,
    method: str,
    path: str,
    token: str,
    json_payload: dict | None,
):
    return client.request(
        method,
        path,
        headers=_auth_headers(token),
        json=json_payload,
    )


def _install_service_stubs(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "app.services.product_service.ProductService.get_products",
        lambda db: [],
    )
    monkeypatch.setattr(
        "app.services.product_service.ProductService.create_product",
        lambda db, product: PRODUCT_RESPONSE,
    )
    monkeypatch.setattr(
        "app.services.supplier_service.SupplierService.get_suppliers",
        lambda db: [],
    )
    monkeypatch.setattr(
        "app.services.supplier_service.SupplierService.create_supplier",
        lambda db, supplier: SUPPLIER_RESPONSE,
    )
    monkeypatch.setattr(
        "app.services.inventory_service.InventoryService.get_inventory",
        lambda db: [],
    )
    monkeypatch.setattr(
        "app.services.inventory_service.InventoryService.get_inventory_statistics",
        lambda db: {"total_inventory_units": 100},
    )
    monkeypatch.setattr(
        "app.services.inventory_service.InventoryService.get_low_stock_products",
        lambda db: [],
    )
    monkeypatch.setattr(
        "app.services.inventory_service.InventoryService.get_expiring_products",
        lambda db: [],
    )
    monkeypatch.setattr(
        "app.services.inventory_service.InventoryService.get_inventory_by_id",
        lambda db, inventory_id: INVENTORY_RESPONSE,
    )
    monkeypatch.setattr(
        "app.services.inventory_service.InventoryService.create_inventory",
        lambda db, inventory: INVENTORY_RESPONSE,
    )
    monkeypatch.setattr(
        "app.services.inventory_service.InventoryService.delete_inventory",
        lambda db, inventory_id: None,
    )
    monkeypatch.setattr(
        "app.services.warehouse_zone_service.WarehouseZoneService.get_zones",
        lambda db: [],
    )
    monkeypatch.setattr(
        "app.services.warehouse_zone_service.WarehouseZoneService.get_capacity_summary",
        lambda db: {"total_capacity": 500, "occupied_capacity": 100},
    )
    monkeypatch.setattr(
        "app.services.warehouse_zone_service.WarehouseZoneService.get_zone_by_id",
        lambda db, zone_id: WAREHOUSE_RESPONSE,
    )
    monkeypatch.setattr(
        "app.services.warehouse_zone_service.WarehouseZoneService.create_zone",
        lambda db, zone: WAREHOUSE_RESPONSE,
    )
    monkeypatch.setattr(
        "app.services.warehouse_zone_service.WarehouseZoneService.delete_zone",
        lambda db, zone_id: None,
    )
    monkeypatch.setattr(
        "app.services.shipment_service.ShipmentService.get_shipments",
        lambda db: [],
    )
    monkeypatch.setattr(
        "app.services.shipment_service.ShipmentService.get_shipment_statistics",
        lambda db: {"incoming_shipments": 1},
    )
    monkeypatch.setattr(
        "app.services.shipment_service.ShipmentService.create_shipment",
        lambda db, shipment: SHIPMENT_RESPONSE,
    )
    monkeypatch.setattr(
        "app.services.shipment_service.ShipmentService.get_shipment_by_id",
        lambda db, shipment_id: SHIPMENT_RESPONSE,
    )
    monkeypatch.setattr(
        "app.services.shipment_service.ShipmentService.delete_shipment",
        lambda db, shipment_id: {"message": "Deleted"},
    )
    monkeypatch.setattr(
        "app.services.procurement_request_service.ProcurementRequestService.get_procurement_requests",
        lambda db: [],
    )
    monkeypatch.setattr(
        "app.services.procurement_request_service.ProcurementRequestService.get_procurement_statistics",
        lambda db: {"pending_requests": 1},
    )
    monkeypatch.setattr(
        "app.services.procurement_request_service.ProcurementRequestService.create_procurement_request",
        lambda db, procurement_request: PROCUREMENT_RESPONSE,
    )
    monkeypatch.setattr(
        "app.services.procurement_request_service.ProcurementRequestService.get_procurement_request_by_id",
        lambda db, request_id: PROCUREMENT_RESPONSE,
    )
    monkeypatch.setattr(
        "app.services.procurement_request_service.ProcurementRequestService.delete_procurement_request",
        lambda db, request_id: {"message": "Deleted"},
    )
    monkeypatch.setattr(
        "app.services.dashboard_service.DashboardService.get_summary",
        lambda db: {
            "total_inventory_units": 100,
            "available_inventory_units": 90,
            "reserved_inventory_units": 10,
            "low_stock_products": 1,
            "warehouse_occupancy": 20.0,
            "warehouse_available_capacity": 400,
            "incoming_shipments": 1,
            "outgoing_shipments": 0,
            "delayed_shipments": 0,
            "procurement_requests": 1,
        },
    )
    monkeypatch.setattr(
        "app.services.procurement_ai_service.ProcurementAIService.evaluate_request",
        lambda self, product_name, pallet_quantity, month: PROCUREMENT_AI_RESPONSE,
    )
    monkeypatch.setattr(
        "app.ai.tools.inventory_tool.InventoryTool.get_inventory_summary",
        lambda self, db: {"total_products": 1},
    )
    monkeypatch.setattr(
        "app.ai.tools.inventory_tool.InventoryTool.get_low_stock_products",
        lambda self, db: [],
    )
    monkeypatch.setattr(
        "app.ai.tools.inventory_tool.InventoryTool.get_expiring_products",
        lambda self, db: [],
    )
    monkeypatch.setattr(
        "app.ai.tools.warehouse_tool.WarehouseTool.get_capacity_summary",
        lambda self, db: {"available_capacity": 400},
    )
    monkeypatch.setattr(
        "app.ai.tools.shipment_tool.ShipmentTool.get_shipment_summary",
        lambda self, db: {"total_shipments": 1},
    )
    monkeypatch.setattr(
        "app.services.ai_insights_service.AIInsightsService.get_insights",
        lambda self: AI_INSIGHTS_RESPONSE,
    )
    monkeypatch.setattr(
        "app.services.copilot_orchestrator_service.CopilotOrchestratorService.chat",
        lambda self, message: COPILOT_RESPONSE,
    )
    monkeypatch.setattr(
        "app.services.procurement_analysis_service.ProcurementAnalysisService.analyze",
        lambda self, product_id, supplier_id, requested_quantity: PROCUREMENT_ANALYSIS_RESPONSE,
    )
    monkeypatch.setattr(
        "app.services.ai_chat_service.AIChatService.chat",
        lambda db, message: {"response": "Hello"},
    )


@pytest.mark.parametrize(
    ("method", "path", "json_payload", "expected_status"),
    ADMIN_ENDPOINTS,
)
def test_administrator_has_access_to_all_protected_endpoints(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    method: str,
    path: str,
    json_payload: dict | None,
    expected_status: int,
) -> None:
    _install_service_stubs(monkeypatch)
    login_payload = _login(
        client,
        settings.BOOTSTRAP_ADMIN_EMAIL,
        settings.BOOTSTRAP_ADMIN_PASSWORD,
    )

    response = _request(
        client,
        method,
        path,
        login_payload["access_token"],
        json_payload,
    )

    assert response.status_code == expected_status


@pytest.mark.parametrize(
    ("method", "path", "json_payload"),
    [
        (method, path, json_payload)
        for method, path, json_payload, _expected_status in ADMIN_ENDPOINTS
    ],
)
def test_protected_endpoints_return_403_when_permission_is_missing(
    client: TestClient,
    user_factory: Callable[..., tuple[str, str]],
    method: str,
    path: str,
    json_payload: dict | None,
) -> None:
    email, password = user_factory(
        role_name="No Permissions",
        permissions=[],
        use_seeded_role=False,
    )
    login_payload = _login(client, email, password)

    response = _request(
        client,
        method,
        path,
        login_payload["access_token"],
        json_payload,
    )

    assert response.status_code == 403
    assert response.json()["detail"].startswith("Permission '")


def test_viewer_can_read_products_but_cannot_create_products(
    client: TestClient,
    user_factory: Callable[..., tuple[str, str]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_service_stubs(monkeypatch)
    email, password = user_factory(
        role_name="Viewer",
        use_seeded_role=True,
    )
    login_payload = _login(client, email, password)
    token = login_payload["access_token"]

    read_response = _request(
        client,
        "GET",
        "/api/products/",
        token,
        None,
    )
    write_response = _request(
        client,
        "POST",
        "/api/products/",
        token,
        PRODUCT_PAYLOAD,
    )

    assert read_response.status_code == 200
    assert write_response.status_code == 403


def test_warehouse_manager_can_manage_warehouse_but_not_create_procurement_requests(
    client: TestClient,
    user_factory: Callable[..., tuple[str, str]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_service_stubs(monkeypatch)
    email, password = user_factory(
        role_name="Warehouse Manager",
        use_seeded_role=True,
    )
    login_payload = _login(client, email, password)
    token = login_payload["access_token"]

    warehouse_response = _request(
        client,
        "POST",
        "/api/warehouse-zones/",
        token,
        WAREHOUSE_PAYLOAD,
    )
    procurement_response = _request(
        client,
        "POST",
        "/api/procurement-requests/",
        token,
        PROCUREMENT_PAYLOAD,
    )

    assert warehouse_response.status_code == 200
    assert procurement_response.status_code == 403


def test_procurement_manager_can_create_procurement_requests_but_not_modify_warehouse(
    client: TestClient,
    user_factory: Callable[..., tuple[str, str]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_service_stubs(monkeypatch)
    email, password = user_factory(
        role_name="Procurement Manager",
        use_seeded_role=True,
    )
    login_payload = _login(client, email, password)
    token = login_payload["access_token"]

    procurement_response = _request(
        client,
        "POST",
        "/api/procurement-requests/",
        token,
        PROCUREMENT_PAYLOAD,
    )
    warehouse_response = _request(
        client,
        "POST",
        "/api/warehouse-zones/",
        token,
        WAREHOUSE_PAYLOAD,
    )

    assert procurement_response.status_code == 200
    assert warehouse_response.status_code == 403


@pytest.mark.parametrize(
    ("path", "json_payload"),
    [
        ("/api/procurement-ai/evaluate", PROCUREMENT_AI_PAYLOAD),
        ("/api/ai/procurement/analyze", PROCUREMENT_ANALYSIS_PAYLOAD),
    ],
)
def test_ai_procurement_requires_ai_access_permission(
    client: TestClient,
    user_factory: Callable[..., tuple[str, str]],
    monkeypatch: pytest.MonkeyPatch,
    path: str,
    json_payload: dict,
) -> None:
    _install_service_stubs(monkeypatch)
    allowed_email, allowed_password = user_factory(
        role_name="AI Analyst",
        permissions=["ai.access"],
        use_seeded_role=False,
    )
    denied_email, denied_password = user_factory(
        role_name="No AI Access",
        permissions=[],
        use_seeded_role=False,
    )

    allowed_token = _login(client, allowed_email, allowed_password)["access_token"]
    denied_token = _login(client, denied_email, denied_password)["access_token"]

    allowed_response = _request(
        client,
        "POST",
        path,
        allowed_token,
        json_payload,
    )
    denied_response = _request(
        client,
        "POST",
        path,
        denied_token,
        json_payload,
    )

    assert allowed_response.status_code == 200
    assert denied_response.status_code == 403
    assert denied_response.json()["detail"] == "Permission 'ai.access' required."


def test_ai_insights_requires_insights_permission(
    client: TestClient,
    user_factory: Callable[..., tuple[str, str]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_service_stubs(monkeypatch)
    allowed_email, allowed_password = user_factory(
        role_name="Viewer",
        use_seeded_role=True,
    )
    denied_email, denied_password = user_factory(
        role_name="Warehouse Manager",
        use_seeded_role=True,
    )

    allowed_token = _login(client, allowed_email, allowed_password)["access_token"]
    denied_token = _login(client, denied_email, denied_password)["access_token"]

    allowed_response = _request(
        client,
        "GET",
        "/api/ai/insights",
        allowed_token,
        None,
    )
    denied_response = _request(
        client,
        "GET",
        "/api/ai/insights",
        denied_token,
        None,
    )

    assert allowed_response.status_code == 200
    assert denied_response.status_code == 403


def test_executive_copilot_requires_copilot_permission(
    client: TestClient,
    user_factory: Callable[..., tuple[str, str]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_service_stubs(monkeypatch)
    allowed_email, allowed_password = user_factory(
        role_name="Warehouse Manager",
        use_seeded_role=True,
    )
    denied_email, denied_password = user_factory(
        role_name="Viewer",
        use_seeded_role=True,
    )

    allowed_token = _login(client, allowed_email, allowed_password)["access_token"]
    denied_token = _login(client, denied_email, denied_password)["access_token"]

    allowed_response = _request(
        client,
        "POST",
        "/api/ai/copilot/chat",
        allowed_token,
        {"message": "Summarize inventory"},
    )
    denied_response = _request(
        client,
        "POST",
        "/api/ai/copilot/chat",
        denied_token,
        {"message": "Summarize inventory"},
    )

    assert allowed_response.status_code == 200
    assert denied_response.status_code == 403
    assert denied_response.json()["detail"] == "Permission 'copilot.use' required."


def test_dashboard_summary_requires_insights_view_permission(
    client: TestClient,
    user_factory: Callable[..., tuple[str, str]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_service_stubs(monkeypatch)
    allowed_email, allowed_password = user_factory(
        role_name="Viewer",
        use_seeded_role=True,
    )
    denied_email, denied_password = user_factory(
        role_name="Warehouse Manager",
        use_seeded_role=True,
    )

    allowed_token = _login(client, allowed_email, allowed_password)["access_token"]
    denied_token = _login(client, denied_email, denied_password)["access_token"]

    allowed_response = _request(
        client,
        "GET",
        "/api/dashboard/summary",
        allowed_token,
        None,
    )
    denied_response = _request(
        client,
        "GET",
        "/api/dashboard/summary",
        denied_token,
        None,
    )

    assert allowed_response.status_code == 200
    assert denied_response.status_code == 403
    assert denied_response.json()["detail"] == "Permission 'insights.view' required."


def test_warehouse_manager_cannot_approve_procurement(
    client: TestClient,
    user_factory: Callable[..., tuple[str, str]],
) -> None:
    email, password = user_factory(
        role_name="Warehouse Manager",
        use_seeded_role=True,
    )
    token = _login(client, email, password)["access_token"]

    response = _request(
        client,
        "PUT",
        "/api/test/rbac/procurement-approval",
        token,
        None,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Permission 'procurement.approve' required."


def test_procurement_manager_can_approve_procurement(
    client: TestClient,
    user_factory: Callable[..., tuple[str, str]],
) -> None:
    email, password = user_factory(
        role_name="Procurement Manager",
        use_seeded_role=True,
    )
    token = _login(client, email, password)["access_token"]

    response = _request(
        client,
        "PUT",
        "/api/test/rbac/procurement-approval",
        token,
        None,
    )

    assert response.status_code == 200
