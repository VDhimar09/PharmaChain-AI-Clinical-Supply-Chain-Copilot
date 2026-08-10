from datetime import datetime
from datetime import timezone
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.documents import router as documents_router
from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.services.document_service import (
    DocumentNotFoundError,
    DocumentValidationError,
)
from tests.fakes import build_minimal_pdf


DOCUMENT_ID = uuid4()
NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)

FAKE_DOCUMENT = SimpleNamespace(
    id=DOCUMENT_ID,
    filename="stored-name.pdf",
    original_filename="Cold_Chain_SOP.pdf",
    mime_type="application/pdf",
    file_size=1024,
    checksum="a" * 64,
    status="COMPLETED",
    failure_reason=None,
    page_count=2,
    uploaded_by=None,
    uploaded_at=NOW,
    updated_at=NOW,
)


def _create_app(permissions: list[str]) -> FastAPI:
    app = FastAPI()
    app.include_router(documents_router)
    app.dependency_overrides[get_db] = lambda: SimpleNamespace()
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(
        id=uuid4(),
        email="user@example.com",
        full_name="Test User",
        role=SimpleNamespace(
            name="Tester",
            permissions=[
                SimpleNamespace(name=permission)
                for permission in permissions
            ],
        ),
    )
    return app


@pytest.fixture
def client_factory():
    def factory(permissions: list[str]) -> TestClient:
        return TestClient(_create_app(permissions))

    return factory


def test_list_documents_requires_documents_read_permission(client_factory, monkeypatch):
    monkeypatch.setattr(
        "app.services.document_service.DocumentService.get_documents",
        lambda self: [FAKE_DOCUMENT],
    )

    allowed = client_factory(["documents.read"]).get("/api/documents/")
    denied = client_factory([]).get("/api/documents/")

    assert allowed.status_code == 200
    assert allowed.json()[0]["id"] == str(DOCUMENT_ID)
    assert denied.status_code == 403


def test_upload_requires_documents_upload_permission(client_factory, monkeypatch):
    monkeypatch.setattr(
        "app.services.document_service.DocumentService.upload_document",
        lambda self, **kwargs: FAKE_DOCUMENT,
    )
    pdf_bytes = build_minimal_pdf(["Some SOP content."])
    files = {"file": ("sop.pdf", pdf_bytes, "application/pdf")}

    allowed = client_factory(["documents.upload"]).post(
        "/api/documents/upload", files=files
    )
    denied = client_factory([]).post("/api/documents/upload", files=files)

    assert allowed.status_code == 200
    assert allowed.json()["status"] == "COMPLETED"
    assert denied.status_code == 403


def test_upload_returns_400_on_validation_error(client_factory, monkeypatch):
    def _raise(self, **kwargs):
        raise DocumentValidationError("Unsupported MIME type 'text/plain'.")

    monkeypatch.setattr(
        "app.services.document_service.DocumentService.upload_document",
        _raise,
    )
    files = {"file": ("notes.txt", b"plain text", "text/plain")}

    response = client_factory(["documents.upload"]).post(
        "/api/documents/upload", files=files
    )

    assert response.status_code == 400
    assert "MIME type" in response.json()["detail"]


def test_delete_requires_documents_delete_permission(client_factory, monkeypatch):
    monkeypatch.setattr(
        "app.services.document_service.DocumentService.delete_document",
        lambda self, document_id: None,
    )

    allowed = client_factory(["documents.delete"]).delete(
        f"/api/documents/{DOCUMENT_ID}"
    )
    denied = client_factory([]).delete(f"/api/documents/{DOCUMENT_ID}")

    assert allowed.status_code == 200
    assert denied.status_code == 403


def test_delete_returns_404_when_document_missing(client_factory, monkeypatch):
    def _raise(self, document_id):
        raise DocumentNotFoundError(f"Document '{document_id}' was not found.")

    monkeypatch.setattr(
        "app.services.document_service.DocumentService.delete_document",
        _raise,
    )

    response = client_factory(["documents.delete"]).delete(
        f"/api/documents/{DOCUMENT_ID}"
    )

    assert response.status_code == 404
