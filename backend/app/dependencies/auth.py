from collections.abc import Callable
from uuid import UUID

from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User
from app.repositories.user_repository import UserRepository

bearer_scheme = HTTPBearer(
    auto_error=False
)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme
    ),
    db: Session = Depends(get_db),
) -> User:
    """
    Validate the JWT access token and return the authenticated user.
    """

    if credentials is None:
        raise _unauthorized(
            "Authentication credentials were not provided."
        )

    token = credentials.credentials

    try:
        payload = decode_token(token)
    except Exception:
        raise _unauthorized(
            "Invalid access token."
        )

    if payload.get("type") != "access":
        raise _unauthorized(
            "Access token required."
        )

    subject = payload.get("sub")

    if subject is None:
        raise _unauthorized(
            "Token subject is missing."
        )

    try:
        user_id = UUID(str(subject))
    except ValueError:
        raise _unauthorized(
            "Invalid token subject."
        )

    user = UserRepository.get_by_id(
        db,
        user_id
    )

    if user is None:
        raise _unauthorized(
            "User not found."
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive."
        )

    return user


def require_role(
    role_name: str,
) -> Callable:
    """
    Require a specific role.

    Example:

        Depends(require_role("Administrator"))
    """

    def dependency(
        current_user: User = Depends(
            get_current_user
        ),
    ) -> User:

        if current_user.role is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User has no assigned role."
            )

        if current_user.role.name != role_name:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"{role_name} role required."
            )

        return current_user

    return dependency


def require_permission(
    permission_name: str,
) -> Callable:
    """
    Require a specific permission.

    Example:

        Depends(require_permission("inventory.read"))
    """

    def dependency(
        current_user: User = Depends(
            get_current_user
        ),
    ) -> User:

        if current_user.role is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User has no assigned role."
            )

        permissions = {
            permission.name
            for permission in (
                current_user.role.permissions or []
            )
        }

        if "system.admin" in permissions:
            return current_user

        if permission_name not in permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission_name}' required."
            )

        return current_user

    return dependency


def require_admin() -> Callable:
    """
    Convenience dependency for administrator-only endpoints.
    """

    return require_role("Administrator")


def _unauthorized(
    detail: str,
) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={
            "WWW-Authenticate": "Bearer"
        },
    )
