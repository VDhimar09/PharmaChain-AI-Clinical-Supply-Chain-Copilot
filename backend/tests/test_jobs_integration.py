from collections.abc import Callable
from collections.abc import Iterator
from datetime import datetime
from datetime import timedelta
from types import ModuleType
from types import SimpleNamespace
from uuid import uuid4
import sys

import pytest
from fastapi.testclient import TestClient

import app.jobs.scheduler as scheduler_module
from app.core.config import settings
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.main import app
from app.models.system_event import SystemEvent
from app.models.user import User
from app.repositories.role_repository import RoleRepository


class FakeScheduledJob:

    def __init__(
        self,
        *,
        job_id: str,
        kwargs: dict,
        interval_kwargs: dict,
    ) -> None:
        self.id = job_id
        self.kwargs = kwargs
        self.interval_kwargs = interval_kwargs
        self.next_run_time = (
            datetime.utcnow() + timedelta(minutes=1)
        )


class FakeBackgroundScheduler:

    def __init__(self) -> None:
        self.jobs: dict[str, FakeScheduledJob] = {}
        self.running = False

    def add_job(
        self,
        func,
        *,
        trigger: str,
        id: str,
        name: str,
        replace_existing: bool,
        kwargs: dict,
        **interval_kwargs,
    ) -> FakeScheduledJob:
        job = FakeScheduledJob(
            job_id=id,
            kwargs=kwargs,
            interval_kwargs=interval_kwargs,
        )
        self.jobs[id] = job
        return job

    def start(self) -> None:
        self.running = True

    def shutdown(
        self,
        wait: bool = False
    ) -> None:
        self.running = False

    def get_job(
        self,
        job_id: str
    ) -> FakeScheduledJob | None:
        return self.jobs.get(job_id)


@pytest.fixture(autouse=True)
def fake_apscheduler(
    monkeypatch: pytest.MonkeyPatch
) -> Iterator[None]:
    background_module = ModuleType(
        "apscheduler.schedulers.background"
    )
    background_module.BackgroundScheduler = (
        FakeBackgroundScheduler
    )
    schedulers_module = ModuleType(
        "apscheduler.schedulers"
    )
    apscheduler_module = ModuleType(
        "apscheduler"
    )

    monkeypatch.setitem(
        sys.modules,
        "apscheduler",
        apscheduler_module,
    )
    monkeypatch.setitem(
        sys.modules,
        "apscheduler.schedulers",
        schedulers_module,
    )
    monkeypatch.setitem(
        sys.modules,
        "apscheduler.schedulers.background",
        background_module,
    )

    scheduler_module._scheduler_service = None

    yield

    scheduler_module._scheduler_service = None


@pytest.fixture(autouse=True)
def clear_system_events() -> Iterator[None]:
    db = SessionLocal()
    try:
        db.query(SystemEvent).delete()
        db.commit()
    finally:
        db.close()

    yield

    db = SessionLocal()
    try:
        db.query(SystemEvent).delete()
        db.commit()
    finally:
        db.close()


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


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


def _get_job(
    client: TestClient,
    job_name: str,
):
    return client.app.state.scheduler_service._registered_jobs[
        job_name
    ].job


def test_scheduler_starts_and_registers_jobs(
    client: TestClient,
) -> None:
    scheduler_service = client.app.state.scheduler_service

    assert scheduler_service is not None
    assert scheduler_service.is_running() is True

    jobs = scheduler_service.get_jobs_health()
    job_names = {
        job["name"]
        for job in jobs
    }

    assert job_names == {
        "inventory_monitor",
        "shipment_monitor",
        "procurement_monitor",
        "expiry_monitor",
        "notification_dispatcher",
    }


def test_inventory_monitor_runs(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    low_stock_item = SimpleNamespace(
        id=uuid4(),
        product_id=uuid4(),
        batch_number="BATCH-LOW",
        available_quantity=5,
        quantity=10,
        reserved_quantity=0,
    )
    negative_item = SimpleNamespace(
        id=uuid4(),
        product_id=uuid4(),
        batch_number="BATCH-NEG",
        available_quantity=-2,
        quantity=-2,
        reserved_quantity=0,
    )
    monkeypatch.setattr(
        "app.services.inventory_service.InventoryService.get_low_stock_products",
        lambda db: [low_stock_item],
    )
    monkeypatch.setattr(
        "app.services.inventory_service.InventoryService.get_inventory",
        lambda db: [low_stock_item, negative_item],
    )

    client.app.state.scheduler_service.run_job_now(
        "inventory_monitor"
    )

    db = SessionLocal()
    try:
        event_types = {
            event.event_type
            for event in db.query(SystemEvent).all()
        }
    finally:
        db.close()

    assert "INVENTORY_LOW_STOCK" in event_types
    assert "INVENTORY_OUT_OF_STOCK" in event_types
    assert "INVENTORY_NEGATIVE" in event_types


def test_expiry_monitor_runs(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    expiring_item = SimpleNamespace(
        id=uuid4(),
        product_id=uuid4(),
        batch_number="EXP-001",
        expiry_date=datetime.utcnow().date(),
    )
    monkeypatch.setattr(
        "app.services.inventory_service.InventoryService.get_expiring_products",
        lambda db, days=30: [expiring_item],
    )

    client.app.state.scheduler_service.run_job_now(
        "expiry_monitor"
    )

    db = SessionLocal()
    try:
        events = db.query(SystemEvent).all()
    finally:
        db.close()

    assert len(events) == 4
    assert all(
        event.event_type == "PRODUCT_EXPIRY_ALERT"
        for event in events
    )


def test_shipment_monitor_runs(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    delayed_shipment = SimpleNamespace(
        id=uuid4(),
        shipment_number="SHP-001",
        status="Delayed",
        expected_arrival=datetime.utcnow() - timedelta(days=1),
    )
    overdue_shipment = SimpleNamespace(
        id=uuid4(),
        shipment_number="SHP-002",
        status="IN_TRANSIT",
        expected_arrival=datetime.utcnow() - timedelta(days=2),
    )
    monkeypatch.setattr(
        "app.services.shipment_service.ShipmentService.get_shipments",
        lambda db: [delayed_shipment, overdue_shipment],
    )

    client.app.state.scheduler_service.run_job_now(
        "shipment_monitor"
    )

    db = SessionLocal()
    try:
        event_types = [
            event.event_type
            for event in db.query(SystemEvent).all()
        ]
    finally:
        db.close()

    assert "SHIPMENT_DELAY_DETECTED" in event_types
    assert "SHIPMENT_OVERDUE" in event_types


def test_procurement_monitor_runs(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    product = SimpleNamespace(
        id=uuid4(),
        name="Test Product",
        supplier_id=uuid4(),
        safety_stock=50,
    )
    low_stock_item = SimpleNamespace(
        product=product,
        available_quantity=10,
    )
    monkeypatch.setattr(
        "app.services.inventory_service.InventoryService.get_low_stock_products",
        lambda db: [low_stock_item],
    )
    monkeypatch.setattr(
        "app.services.procurement_analysis_service.ProcurementAnalysisService.analyze",
        lambda self, product_id, supplier_id, requested_quantity: {
            "decision": "APPROVE",
            "confidence": 95,
            "recommendation": "Approve procurement request.",
        },
    )

    client.app.state.scheduler_service.run_job_now(
        "procurement_monitor"
    )

    db = SessionLocal()
    try:
        event = (
            db.query(SystemEvent)
            .filter(
                SystemEvent.event_type == "PROCUREMENT_RECOMMENDATION_CREATED"
            )
            .first()
        )
    finally:
        db.close()

    assert event is not None
    assert event.payload["product_name"] == "Test Product"


def test_notification_dispatcher_runs(
    client: TestClient,
) -> None:
    db = SessionLocal()
    try:
        db.add(
            SystemEvent(
                event_type="INVENTORY_LOW_STOCK",
                severity="MEDIUM",
                source="inventory_monitor",
                payload={"inventory_id": str(uuid4())},
                processed=False,
            )
        )
        db.commit()
    finally:
        db.close()

    client.app.state.scheduler_service.run_job_now(
        "notification_dispatcher"
    )

    db = SessionLocal()
    try:
        event = db.query(SystemEvent).first()
    finally:
        db.close()

    assert event is not None
    assert event.processed is True


def test_retry_policy_works(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    job = _get_job(
        client,
        "inventory_monitor",
    )
    attempts = {"count": 0}

    def flaky_execute():
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise RuntimeError("temporary failure")
        return {"ok": True}

    monkeypatch.setattr(
        job,
        "execute",
        flaky_execute,
    )

    client.app.state.scheduler_service.run_job_now(
        "inventory_monitor"
    )

    assert attempts["count"] == 3
    assert job.last_status == "success"
    assert job.last_attempts == 3


def test_job_failures_do_not_stop_scheduler(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    job = _get_job(
        client,
        "shipment_monitor",
    )

    monkeypatch.setattr(
        job,
        "execute",
        lambda: (_ for _ in ()).throw(
            RuntimeError("job failure")
        ),
    )

    client.app.state.scheduler_service.run_job_now(
        "shipment_monitor"
    )

    assert client.app.state.scheduler_service.is_running() is True
    assert job.last_status == "failed"


def test_system_jobs_endpoint_requires_system_monitor(
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
        "/api/system/jobs/",
        headers=_auth_headers(
            login_payload["access_token"]
        ),
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Permission 'system.monitor' required."


def test_administrator_can_read_system_jobs_health(
    client: TestClient,
) -> None:
    login_payload = _login_as_bootstrap_admin(
        client
    )

    response = client.get(
        "/api/system/jobs/",
        headers=_auth_headers(
            login_payload["access_token"]
        ),
    )

    assert response.status_code == 200
    assert len(response.json()["jobs"]) == 5
