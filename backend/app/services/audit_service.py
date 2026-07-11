import logging
from uuid import UUID

from fastapi import BackgroundTasks
from fastapi import Request
from fastapi.encoders import jsonable_encoder

from app.core.database import SessionLocal
from app.models.audit_log import AuditLog
from app.models.user import User
from app.repositories.audit_log_repository import AuditLogRepository


logger = logging.getLogger(__name__)


class AuditService:

    @staticmethod
    def enqueue_log(
        background_tasks: BackgroundTasks,
        **kwargs,
    ) -> None:
        background_tasks.add_task(
            AuditService.log,
            **kwargs,
        )

    @staticmethod
    def log(
        *,
        action: str,
        resource_type: str,
        status_code: int,
        request: Request,
        user: User | None = None,
        user_email: str | None = None,
        resource_id: UUID | str | None = None,
        details: dict | None = None,
    ) -> None:
        db = SessionLocal()

        try:
            audit_log = AuditLog(
                user_id=user.id if user is not None else None,
                user_email=user.email if user is not None else user_email,
                action=action,
                resource_type=resource_type,
                resource_id=str(resource_id) if resource_id is not None else None,
                http_method=request.method,
                endpoint=request.url.path,
                status_code=status_code,
                ip_address=AuditService._get_ip_address(request),
                user_agent=request.headers.get("user-agent"),
                details=AuditService._serialize_details(details),
            )

            AuditLogRepository.create(
                db,
                audit_log,
            )
        except Exception:
            db.rollback()
            logger.exception(
                "Failed to create audit log for action '%s'.",
                action,
            )
        finally:
            db.close()

    @staticmethod
    def _get_ip_address(
        request: Request
    ) -> str | None:
        forwarded_for = request.headers.get(
            "x-forwarded-for"
        )

        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        if request.client is None:
            return None

        return request.client.host

    @staticmethod
    def _serialize_details(
        details: dict | None
    ) -> dict:
        if details is None:
            return {}

        encoded = jsonable_encoder(
            details,
            exclude_none=True,
        )

        if isinstance(encoded, dict):
            return encoded

        return {
            "value": encoded
        }
