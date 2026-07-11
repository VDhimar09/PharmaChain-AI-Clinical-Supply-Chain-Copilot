from fastapi import APIRouter
from fastapi import BackgroundTasks
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi import Response
from fastapi import status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    LogoutRequest,
    RefreshTokenRequest,
    TokenResponse,
)
from app.schemas.user import CurrentUserResponse
from app.services.audit_service import AuditService
from app.services.auth_service import AuthService


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate user",
    description="Authenticate using email and password and return JWT access and refresh tokens.",
)
def login(
    request: Request,
    background_tasks: BackgroundTasks,
    payload: LoginRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    try:
        response = AuthService.login(
            db=db,
            email=payload.email,
            password=payload.password,
        )
    except HTTPException as exc:
        if exc.status_code == status.HTTP_401_UNAUTHORIZED:
            AuditService.log(
                action="LOGIN_FAILED",
                resource_type="Authentication",
                status_code=exc.status_code,
                request=request,
                user_email=payload.email.lower(),
                details={
                    "email": payload.email.lower(),
                    "result": "FAILED",
                },
            )
        raise

    AuditService.enqueue_log(
        background_tasks,
        action="LOGIN_SUCCESS",
        resource_type="Authentication",
        status_code=status.HTTP_200_OK,
        request=request,
        user_email=response.user.email,
        resource_id=response.user.id,
        details={
            "email": response.user.email,
            "role": response.user.role,
            "result": "SUCCESS",
        },
    )

    return response


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
    description="Exchange a valid refresh token for a new access token and refresh token.",
)
def refresh_token(
    request: Request,
    background_tasks: BackgroundTasks,
    payload: RefreshTokenRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    response = AuthService.refresh(
        db=db,
        refresh_token=payload.refresh_token,
    )

    AuditService.enqueue_log(
        background_tasks,
        action="TOKEN_REFRESHED",
        resource_type="Authentication",
        status_code=status.HTTP_200_OK,
        request=request,
        user_email=response.user.email,
        resource_id=response.user.id,
        details={
            "email": response.user.email,
            "role": response.user.role,
            "result": "SUCCESS",
        },
    )

    return response


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logout",
    description="Revoke the supplied refresh token.",
)
def logout(
    request: Request,
    background_tasks: BackgroundTasks,
    payload: LogoutRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    AuthService.logout(
        db=db,
        user=current_user,
        refresh_token=payload.refresh_token,
    )

    AuditService.enqueue_log(
        background_tasks,
        action="LOGOUT_SUCCESS",
        resource_type="Authentication",
        status_code=status.HTTP_204_NO_CONTENT,
        request=request,
        user=current_user,
        resource_id=current_user.id,
        details={
            "email": current_user.email,
            "result": "SUCCESS",
        },
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )


@router.get(
    "/me",
    response_model=CurrentUserResponse,
    summary="Current user",
    description="Return the currently authenticated user's profile, role and permissions.",
)
def get_current_user_profile(
    current_user: User = Depends(get_current_user),
) -> CurrentUserResponse:
    return AuthService.get_current_user_profile(
        current_user
    )
