from datetime import datetime
from datetime import timezone
from hashlib import sha256
from uuid import UUID

from fastapi import HTTPException
from fastapi import status
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.core.security import create_refresh_token
from app.core.security import decode_token
from app.core.security import verify_password
from app.models.permission import Permission  # noqa: F401
from app.models.refresh_token import RefreshToken
from app.models.role import Role  # noqa: F401
from app.models.user import User
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenResponse
from app.schemas.user import CurrentUserResponse


class AuthService:

    @staticmethod
    def login(
        db: Session,
        *,
        email: str,
        password: str
    ) -> TokenResponse:
        user = UserRepository.get_by_email(
            db,
            email.lower()
        )

        if user is None or not verify_password(
            password,
            user.password_hash
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password."
            )

        AuthService._ensure_active_user(user)

        return AuthService._issue_tokens(
            db,
            user
        )

    @staticmethod
    def refresh(
        db: Session,
        *,
        refresh_token: str
    ) -> TokenResponse:
        payload = AuthService._decode_token(
            refresh_token,
            expected_type="refresh"
        )

        token_hash = AuthService._hash_token(refresh_token)
        stored_token = RefreshTokenRepository.get_by_hash(
            db,
            token_hash
        )

        if stored_token is None:
            raise AuthService._unauthorized("Refresh token not recognized.")

        if stored_token.token_id != payload.get("jti"):
            raise AuthService._unauthorized("Refresh token does not match.")

        if stored_token.revoked_at is not None:
            raise AuthService._unauthorized("Refresh token has been revoked.")

        if stored_token.expires_at <= AuthService._utc_now():
            raise AuthService._unauthorized("Refresh token has expired.")

        user = UserRepository.get_by_id(
            db,
            UUID(str(payload["sub"]))
        )

        if user is None:
            raise AuthService._unauthorized("User does not exist.")

        AuthService._ensure_active_user(user)

        stored_token.last_used_at = AuthService._utc_now()
        RefreshTokenRepository.revoke(
            db,
            stored_token,
            revoked_at=AuthService._utc_now()
        )

        return AuthService._issue_tokens(
            db,
            user
        )

    @staticmethod
    def logout(
        db: Session,
        *,
        user: User,
        refresh_token: str
    ) -> None:
        payload = AuthService._decode_token(
            refresh_token,
            expected_type="refresh"
        )

        if str(user.id) != str(payload["sub"]):
            raise AuthService._unauthorized(
                "Refresh token does not belong to the current user."
            )

        stored_token = RefreshTokenRepository.get_by_hash(
            db,
            AuthService._hash_token(refresh_token)
        )

        if stored_token is None:
            raise AuthService._unauthorized("Refresh token not recognized.")

        if stored_token.revoked_at is None:
            RefreshTokenRepository.revoke(
                db,
                stored_token,
                revoked_at=AuthService._utc_now()
            )

        db.commit()

    @staticmethod
    def get_current_user_profile(user: User) -> CurrentUserResponse:
        return CurrentUserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=user.role.name,
            permissions=sorted(
                permission.name
                for permission in user.role.permissions
            )
        )

    @staticmethod
    def _issue_tokens(
        db: Session,
        user: User
    ) -> TokenResponse:
        access_token, access_expires_at = create_access_token(
            subject=str(user.id),
            role=user.role.name,
        )
        refresh_token, refresh_token_id, refresh_expires_at = create_refresh_token(
            subject=str(user.id)
        )

        RefreshTokenRepository.create(
            db,
            RefreshToken(
                token_id=refresh_token_id,
                token_hash=AuthService._hash_token(refresh_token),
                user_id=user.id,
                expires_at=refresh_expires_at,
            )
        )

        db.commit()

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=int(
                (access_expires_at - AuthService._utc_now()).total_seconds()
            ),
            refresh_expires_in=int(
                (refresh_expires_at - AuthService._utc_now()).total_seconds()
            ),
            user=AuthService.get_current_user_profile(user),
        )

    @staticmethod
    def _hash_token(token: str) -> str:
        return sha256(token.encode("utf-8")).hexdigest()

    @staticmethod
    def _decode_token(
        token: str,
        *,
        expected_type: str
    ) -> dict:
        try:
            payload = decode_token(token)
        except Exception:
            raise AuthService._unauthorized("Invalid token.")

        if payload.get("type") != expected_type:
            raise AuthService._unauthorized(
                f"Expected a {expected_type} token."
            )

        if "sub" not in payload:
            raise AuthService._unauthorized("Token subject is missing.")

        return payload

    @staticmethod
    def _ensure_active_user(user: User) -> None:
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive."
            )

    @staticmethod
    def _unauthorized(message: str) -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message,
            headers={"WWW-Authenticate": "Bearer"},
        )

    @staticmethod
    def _utc_now() -> datetime:
        return datetime.now(timezone.utc)
