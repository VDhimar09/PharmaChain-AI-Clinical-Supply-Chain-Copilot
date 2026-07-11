from types import SimpleNamespace
from datetime import timedelta
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.core.security import hash_password
from app.models.user import User
from app.services.auth_service import AuthService


def _user() -> User:
    permissions = [
        SimpleNamespace(name="inventory.read"),
        SimpleNamespace(name="ai.access"),
    ]
    role = SimpleNamespace(
        name="Viewer",
        permissions=permissions,
    )
    return SimpleNamespace(
        id=uuid4(),
        email="viewer@pharmachain.com",
        full_name="Viewer User",
        password_hash=hash_password("Password123!"),
        is_active=True,
        role=role,
    )


def test_login_returns_token_response(monkeypatch):
    user = _user()
    created_tokens = []

    monkeypatch.setattr(
        "app.services.auth_service.UserRepository.get_by_email",
        lambda db, email: user,
    )
    monkeypatch.setattr(
        "app.services.auth_service.RefreshTokenRepository.create",
        lambda db, refresh_token: created_tokens.append(refresh_token),
    )

    db = SimpleNamespace(commit=lambda: None)
    response = AuthService.login(
        db,
        email=user.email,
        password="Password123!",
    )

    assert response.user.email == user.email
    assert response.user.role == "Viewer"
    assert response.token_type == "bearer"
    assert response.access_token
    assert response.refresh_token
    assert len(created_tokens) == 1


def test_login_rejects_invalid_password(monkeypatch):
    user = _user()

    monkeypatch.setattr(
        "app.services.auth_service.UserRepository.get_by_email",
        lambda db, email: user,
    )

    with pytest.raises(HTTPException) as error:
        AuthService.login(
            SimpleNamespace(),
            email=user.email,
            password="WrongPassword123!",
        )

    assert error.value.status_code == 401


def test_refresh_rotates_stored_refresh_token(monkeypatch):
    user = _user()
    issued = []
    revoked = []

    monkeypatch.setattr(
        "app.services.auth_service.RefreshTokenRepository.create",
        lambda db, refresh_token: None,
    )

    initial_response = AuthService._issue_tokens(
        SimpleNamespace(commit=lambda: None),
        user,
    )

    stored_token = SimpleNamespace(
        token_id=AuthService._decode_token(
            initial_response.refresh_token,
            expected_type="refresh",
        )["jti"],
        token_hash=AuthService._hash_token(initial_response.refresh_token),
        revoked_at=None,
        expires_at=AuthService._utc_now() + timedelta(days=30),
        last_used_at=None,
    )

    monkeypatch.setattr(
        "app.services.auth_service.RefreshTokenRepository.get_by_hash",
        lambda db, token_hash: stored_token,
    )
    monkeypatch.setattr(
        "app.services.auth_service.UserRepository.get_by_id",
        lambda db, user_id: user,
    )
    monkeypatch.setattr(
        "app.services.auth_service.RefreshTokenRepository.revoke",
        lambda db, refresh_token, revoked_at: revoked.append(revoked_at),
    )
    monkeypatch.setattr(
        "app.services.auth_service.RefreshTokenRepository.create",
        lambda db, refresh_token: issued.append(refresh_token),
    )

    db = SimpleNamespace(commit=lambda: None)
    response = AuthService.refresh(
        db,
        refresh_token=initial_response.refresh_token,
    )

    assert response.refresh_token != initial_response.refresh_token
    assert len(issued) == 1
    assert len(revoked) == 1


def test_logout_revokes_refresh_token(monkeypatch):
    user = _user()

    monkeypatch.setattr(
        "app.services.auth_service.RefreshTokenRepository.create",
        lambda db, refresh_token: None,
    )

    token_response = AuthService._issue_tokens(
        SimpleNamespace(commit=lambda: None),
        user,
    )

    stored_token = SimpleNamespace(
        revoked_at=None,
    )
    revoked = []

    monkeypatch.setattr(
        "app.services.auth_service.RefreshTokenRepository.get_by_hash",
        lambda db, token_hash: stored_token,
    )
    monkeypatch.setattr(
        "app.services.auth_service.RefreshTokenRepository.revoke",
        lambda db, refresh_token, revoked_at: revoked.append(revoked_at),
    )

    db = SimpleNamespace(commit=lambda: None)
    AuthService.logout(
        db,
        user=user,
        refresh_token=token_response.refresh_token,
    )

    assert len(revoked) == 1
