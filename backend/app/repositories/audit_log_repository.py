from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Query
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


class AuditLogRepository:

    @staticmethod
    def create(
        db: Session,
        audit_log: AuditLog
    ) -> AuditLog:
        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)
        return audit_log

    @staticmethod
    def list(
        db: Session,
        *,
        offset: int = 0,
        limit: int = 50
    ) -> list[AuditLog]:
        return (
            db.query(AuditLog)
            .order_by(AuditLog.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    @staticmethod
    def filter(
        db: Session,
        *,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        user_id: UUID | None = None,
        user_email: str | None = None,
        resource_type: str | None = None,
        resource_id: str | None = None,
        action: str | None = None,
        offset: int = 0,
        limit: int = 50
    ) -> tuple[int, list[AuditLog]]:
        query = AuditLogRepository._build_filtered_query(
            db,
            start_date=start_date,
            end_date=end_date,
            user_id=user_id,
            user_email=user_email,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
        )

        total = query.count()

        items = (
            query
            .order_by(AuditLog.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        return total, items

    @staticmethod
    def by_user(
        db: Session,
        *,
        user_id: UUID,
        offset: int = 0,
        limit: int = 50
    ) -> list[AuditLog]:
        return (
            AuditLogRepository._build_filtered_query(
                db,
                user_id=user_id,
            )
            .order_by(AuditLog.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    @staticmethod
    def by_resource(
        db: Session,
        *,
        resource_type: str,
        resource_id: str | None = None,
        offset: int = 0,
        limit: int = 50
    ) -> list[AuditLog]:
        return (
            AuditLogRepository._build_filtered_query(
                db,
                resource_type=resource_type,
                resource_id=resource_id,
            )
            .order_by(AuditLog.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    @staticmethod
    def _build_filtered_query(
        db: Session,
        *,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        user_id: UUID | None = None,
        user_email: str | None = None,
        resource_type: str | None = None,
        resource_id: str | None = None,
        action: str | None = None,
    ) -> Query:
        query = db.query(AuditLog)

        if start_date is not None:
            query = query.filter(
                AuditLog.created_at >= start_date
            )

        if end_date is not None:
            query = query.filter(
                AuditLog.created_at <= end_date
            )

        if user_id is not None:
            query = query.filter(
                AuditLog.user_id == user_id
            )

        if user_email is not None:
            query = query.filter(
                AuditLog.user_email == user_email
            )

        if resource_type is not None:
            query = query.filter(
                AuditLog.resource_type == resource_type
            )

        if resource_id is not None:
            query = query.filter(
                AuditLog.resource_id == resource_id
            )

        if action is not None:
            query = query.filter(
                AuditLog.action == action
            )

        return query
