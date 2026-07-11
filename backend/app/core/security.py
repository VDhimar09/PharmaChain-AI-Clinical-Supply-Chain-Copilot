from datetime import datetime
from datetime import timedelta
from datetime import timezone
from uuid import uuid4

import jwt
from jwt import InvalidTokenError
from passlib.context import CryptContext

from app.core.config import settings


password_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def hash_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return password_context.verify(password, password_hash)


def create_access_token(*, subject: str, role: str) -> tuple[str, datetime]:
    expires_at = _utc_now() + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    token = _encode_token(
        subject=subject,
        token_type="access",
        expires_at=expires_at,
        extra_claims={"role": role},
    )
    return token, expires_at


def create_refresh_token(*, subject: str) -> tuple[str, str, datetime]:
    expires_at = _utc_now() + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    token_id = str(uuid4())
    token = _encode_token(
        subject=subject,
        token_type="refresh",
        expires_at=expires_at,
        token_id=token_id,
    )
    return token, token_id, expires_at


def decode_token(token: str) -> dict:
    return jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
        issuer=settings.JWT_ISSUER,
    )


def is_invalid_token_error(error: Exception) -> bool:
    return isinstance(error, InvalidTokenError)


def _encode_token(
    *,
    subject: str,
    token_type: str,
    expires_at: datetime,
    token_id: str | None = None,
    extra_claims: dict | None = None,
) -> str:
    issued_at = _utc_now()
    payload = {
        "sub": subject,
        "type": token_type,
        "iss": settings.JWT_ISSUER,
        "iat": int(issued_at.timestamp()),
        "exp": int(expires_at.timestamp()),
    }

    if token_id is not None:
        payload["jti"] = token_id

    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)
