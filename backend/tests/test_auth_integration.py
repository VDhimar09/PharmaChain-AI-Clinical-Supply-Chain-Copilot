from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


def _login_as_bootstrap_admin(client: TestClient) -> dict:
    response = client.post(
        "/api/auth/login",
        json={
            "email": settings.BOOTSTRAP_ADMIN_EMAIL,
            "password": settings.BOOTSTRAP_ADMIN_PASSWORD,
        },
    )

    assert response.status_code == 200
    return response.json()


def test_me_returns_bootstrap_admin_with_valid_access_token(
    client: TestClient,
) -> None:
    login_payload = _login_as_bootstrap_admin(client)
    access_token = login_payload["access_token"]

    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200

    payload = response.json()
    assert payload["email"] == "admin@pharmachain.com"
    assert payload["role"] == "Administrator"
    assert isinstance(payload["permissions"], list)
    assert payload["permissions"]


def test_me_returns_401_without_authorization_header(
    client: TestClient,
) -> None:
    response = client.get("/api/auth/me")

    assert response.status_code == 401


def test_me_returns_401_with_invalid_token(
    client: TestClient,
) -> None:
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401


def test_me_returns_401_with_refresh_token(
    client: TestClient,
) -> None:
    login_payload = _login_as_bootstrap_admin(client)
    refresh_token = login_payload["refresh_token"]

    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {refresh_token}"},
    )

    assert response.status_code == 401
