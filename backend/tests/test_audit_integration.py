from collections.abc import Callable
from collections.abc import Iterator
from datetime import datetime
from datetime import timezone
from uuid import uuid4

import pytest
from fastapi import Depends
from fastapi import Request
from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.dependencies.auth import require_permission
from app.main import app
from app.models.audit_log import AuditLog
from app.models.role import Role
from app.models.user import User
from app.repositories.role_repository import RoleRepository
from app.schemas.ai_copilot import CopilotChatResponse
from app.schemas.procurement_ai import ProcurementAIResponse
from app.services.audit_service import AuditService


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

PROCUREMENT_AI_PAYLOAD = {
    "product_name": "Test Product",
    "pallet_quantity": 5,
    "month": "2026-01",
}


@app.patch("/api/test/audit/shipments/{shipment_id}")
def shipment_update_audit_probe(
    shipment_id: str,
    request: Request,
    current_user: User = Depends(
        require_permission("shipment.write")
    ),
):
    AuditService.log(
        action="SHIPMENT_UPDATED",
        resource_type="Shipment",
        status_code=200,
        request=request,
        user=current_user,
        resource_id=shipment_id,
        details={
            "shipment_id": shipment_id,
            "status": "Delivered",
        },
    )

    return {
        "message": "Shipment updated"
    }


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def clear_audit_logs() -> Iterator[None]:
    db = SessionLocal()
    try:
        db.query(AuditLog).delete()
        db.commit()
    finally:
        db.close()

    yield

    db = SessionLocal()
    try:
        db.query(AuditLog).delete()
        db.commit()
    finally:
        db.close()


@pytest.fixture
def user_factory() -> Iterator[Callable[..., tuple[str, str]]]:
    created_user_ids: list[str] = []

    def factory(
        *,
        role_name: str,
    ) -> tuple[str, str]:
        db = SessionLocal()
        try:
            role = RoleRepository.get_by_name(
                db,
                role_name,
            )
            assert role is not None

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
    finally:
        db.close()


def _login_as_bootstrap_admin(
    client: TestClient
) -> dict:
    response = client.post(
        "/api/auth/login",
        json={
            "email": settings.BOOTSTRAP_ADMIN_EMAIL,
            "password": settings.BOOTSTRAP_ADMIN_PASSWORD,
        },
    )

    assert response.status_code == 200
    return response.json()


def _login(
    client: TestClient,
    *,
    email: str,
    password: str,
) -> dict:
    response = client.post(
        "/api/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == 200
    return response.json()


def _auth_headers(
    access_token: str
) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {access_token}"
    }


def _latest_log(
    action: str
) -> AuditLog:
    db = SessionLocal()
    try:
        audit_log = (
            db.query(AuditLog)
            .filter(AuditLog.action == action)
            .order_by(AuditLog.created_at.desc())
            .first()
        )
        assert audit_log is not None
        return audit_log
    finally:
        db.close()


def test_administrator_can_read_audit_logs(
    client: TestClient,
) -> None:
    db = SessionLocal()
    try:
        db.add(
            AuditLog(
                action="LOGIN_SUCCESS",
                resource_type="Authentication",
                http_method="POST",
                endpoint="/api/auth/login",
                status_code=200,
                details={},
            )
        )
        db.commit()
    finally:
        db.close()

    login_payload = _login_as_bootstrap_admin(client)

    response = client.get(
        "/api/audit/",
        headers=_auth_headers(
            login_payload["access_token"]
        ),
    )

    assert response.status_code == 200
    assert response.json()["total"] >= 1


def test_viewer_receives_403_for_audit_logs(
    client: TestClient,
    user_factory: Callable[..., tuple[str, str]],
) -> None:
    email, password = user_factory(
        role_name="Viewer"
    )
    login_payload = _login(
        client,
        email=email,
        password=password,
    )

    response = client.get(
        "/api/audit/",
        headers=_auth_headers(
            login_payload["access_token"]
        ),
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Permission 'audit.read' required."


def test_login_creates_audit_entry(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/auth/login",
        json={
            "email": settings.BOOTSTRAP_ADMIN_EMAIL,
            "password": settings.BOOTSTRAP_ADMIN_PASSWORD,
        },
    )

    assert response.status_code == 200

    audit_log = _latest_log(
        "LOGIN_SUCCESS"
    )

    assert audit_log.user_email == settings.BOOTSTRAP_ADMIN_EMAIL
    assert audit_log.resource_type == "Authentication"
    assert audit_log.endpoint == "/api/auth/login"
    assert audit_log.status_code == 200
    assert audit_log.created_at is not None


def test_logout_creates_audit_entry(
    client: TestClient,
) -> None:
    login_payload = _login_as_bootstrap_admin(
        client
    )

    response = client.post(
        "/api/auth/logout",
        headers=_auth_headers(
            login_payload["access_token"]
        ),
        json={
            "refresh_token": login_payload["refresh_token"]
        },
    )

    assert response.status_code == 204

    audit_log = _latest_log(
        "LOGOUT_SUCCESS"
    )

    assert audit_log.user_email == settings.BOOTSTRAP_ADMIN_EMAIL
    assert audit_log.resource_type == "Authentication"
    assert audit_log.endpoint == "/api/auth/logout"
    assert audit_log.status_code == 204
    assert audit_log.created_at is not None


def test_product_create_creates_audit_entry(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "app.services.product_service.ProductService.create_product",
        lambda db, product: {
            "id": UUID_1,
            **PRODUCT_PAYLOAD,
        },
    )
    login_payload = _login_as_bootstrap_admin(
        client
    )

    response = client.post(
        "/api/products/",
        headers=_auth_headers(
            login_payload["access_token"]
        ),
        json=PRODUCT_PAYLOAD,
    )

    assert response.status_code == 200

    audit_log = _latest_log(
        "PRODUCT_CREATED"
    )

    assert audit_log.user_email == settings.BOOTSTRAP_ADMIN_EMAIL
    assert audit_log.resource_type == "Product"
    assert audit_log.resource_id == UUID_1
    assert audit_log.endpoint == "/api/products/"
    assert audit_log.details["sku"] == PRODUCT_PAYLOAD["sku"]


def test_shipment_update_creates_audit_entry(
    client: TestClient,
) -> None:
    login_payload = _login_as_bootstrap_admin(
        client
    )

    response = client.patch(
        f"/api/test/audit/shipments/{UUID_1}",
        headers=_auth_headers(
            login_payload["access_token"]
        ),
    )

    assert response.status_code == 200

    audit_log = _latest_log(
        "SHIPMENT_UPDATED"
    )

    assert audit_log.user_email == settings.BOOTSTRAP_ADMIN_EMAIL
    assert audit_log.resource_type == "Shipment"
    assert audit_log.resource_id == UUID_1
    assert audit_log.endpoint == f"/api/test/audit/shipments/{UUID_1}"
    assert audit_log.details["status"] == "Delivered"


def test_procurement_create_creates_audit_entry(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "app.services.procurement_request_service.ProcurementRequestService.create_procurement_request",
        lambda db, procurement_request: {
            "id": UUID_1,
            **PROCUREMENT_PAYLOAD,
            "created_at": NOW.isoformat(),
            "approved_at": None,
        },
    )
    login_payload = _login_as_bootstrap_admin(
        client
    )

    response = client.post(
        "/api/procurement-requests/",
        headers=_auth_headers(
            login_payload["access_token"]
        ),
        json=PROCUREMENT_PAYLOAD,
    )

    assert response.status_code == 200

    audit_log = _latest_log(
        "PROCUREMENT_REQUEST_CREATED"
    )

    assert audit_log.user_email == settings.BOOTSTRAP_ADMIN_EMAIL
    assert audit_log.resource_type == "ProcurementRequest"
    assert audit_log.resource_id == UUID_1
    assert audit_log.endpoint == "/api/procurement-requests/"
    assert audit_log.details["requested_quantity"] == PROCUREMENT_PAYLOAD["requested_quantity"]


def test_ai_procurement_creates_audit_entry(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "app.services.procurement_ai_service.ProcurementAIService.evaluate_request",
        lambda self, product_name, pallet_quantity, month: ProcurementAIResponse(
            decision="APPROVE",
            confidence=0.98,
            reasoning=["Capacity available"],
            inventory_units=1000,
            risk_level="LOW",
            recommended_zone="Cold Storage",
            temperature_fit="MATCH",
            badges=["Cold Chain"],
            current_occupancy_percent=50.0,
            projected_occupancy_percent=60.0,
        ),
    )
    login_payload = _login_as_bootstrap_admin(
        client
    )

    response = client.post(
        "/api/procurement-ai/evaluate",
        headers=_auth_headers(
            login_payload["access_token"]
        ),
        json=PROCUREMENT_AI_PAYLOAD,
    )

    assert response.status_code == 200

    audit_log = _latest_log(
        "AI_PROCUREMENT_ANALYSIS"
    )

    assert audit_log.user_email == settings.BOOTSTRAP_ADMIN_EMAIL
    assert audit_log.resource_type == "AI"
    assert audit_log.endpoint == "/api/procurement-ai/evaluate"
    assert audit_log.details["product_name"] == PROCUREMENT_AI_PAYLOAD["product_name"]
    assert audit_log.details["response_generated"] is True


def test_copilot_chat_creates_audit_entry(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "app.services.copilot_orchestrator_service.CopilotOrchestratorService.chat",
        lambda self, message: CopilotChatResponse(
            conversation_id=UUID_1,
            generated_at=NOW,
            intent="summary",
            confidence=90,
            tools_used=["inventory"],
            reasoning=[{
                "step": "Analyze",
                "status": "PASS",
            }],
            tool_execution=[{
                "tool": "inventory",
                "status": "SUCCESS",
                "execution_time_ms": 12.0,
            }],
            evidence={
                "inventory": {},
                "warehouse": {},
                "shipments": {},
                "procurement": {},
                "ai_insights": {},
            },
            recommendations=["Restock Product A"],
            response="Inventory looks healthy overall.",
        ),
    )
    login_payload = _login_as_bootstrap_admin(
        client
    )

    response = client.post(
        "/api/ai/copilot/chat",
        headers=_auth_headers(
            login_payload["access_token"]
        ),
        json={
            "message": "Summarize inventory"
        },
    )

    assert response.status_code == 200

    audit_log = _latest_log(
        "COPILOT_CHAT"
    )

    assert audit_log.user_email == settings.BOOTSTRAP_ADMIN_EMAIL
    assert audit_log.resource_type == "AI"
    assert audit_log.endpoint == "/api/ai/copilot/chat"
    assert audit_log.details["prompt"] == "Summarize inventory"
    assert audit_log.details["response_generated"] is True
