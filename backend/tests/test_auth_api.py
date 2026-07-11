from types import SimpleNamespace
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.auth import router as auth_router
from app.dependencies.auth import get_current_user
from app.core.database import get_db


def _create_test_app() -> FastAPI:
    app = FastAPI()
    app.include_router(auth_router)
    app.dependency_overrides[get_db] = lambda: SimpleNamespace()
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(
        id=uuid4(),
        email="admin@pharmachain.com",
        full_name="Admin User",
        role=SimpleNamespace(
            name="Administrator",
            permissions=[SimpleNamespace(name="system.admin")]
        ),
    )
    return app


def test_login_endpoint_returns_tokens(monkeypatch):
    app = _create_test_app()
    client = TestClient(app)

    monkeypatch.setattr(
        "app.api.auth.AuthService.login",
        lambda db, email, password: {
            "access_token": "access",
            "refresh_token": "refresh",
            "token_type": "bearer",
            "expires_in": 900,
            "refresh_expires_in": 604800,
            "user": {
                "id": str(uuid4()),
                "email": email,
                "full_name": "Admin User",
                "role": "Administrator",
                "permissions": ["system.admin"],
            },
        },
    )

    response = client.post(
        "/api/auth/login",
        json={
            "email": "admin@pharmachain.com",
            "password": "Password123!",
        },
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"


def test_me_endpoint_returns_current_user(monkeypatch):
    app = _create_test_app()
    client = TestClient(app)

    monkeypatch.setattr(
        "app.api.auth.AuthService.get_current_user_profile",
        lambda user: {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.name,
            "permissions": ["system.admin"],
        },
    )

    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer access"},
    )

    assert response.status_code == 200
    assert response.json()["role"] == "Administrator"
