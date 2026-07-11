from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.system_event import SystemEvent


class SystemEventRepository:

    @staticmethod
    def create(
        db: Session,
        system_event: SystemEvent
    ) -> SystemEvent:
        db.add(system_event)
        db.commit()
        db.refresh(system_event)
        return system_event

    @staticmethod
    def list(
        db: Session,
        *,
        processed: bool | None = None,
        limit: int = 100
    ) -> list[SystemEvent]:
        query = db.query(SystemEvent)

        if processed is not None:
            query = query.filter(
                SystemEvent.processed == processed
            )

        return (
            query
            .order_by(SystemEvent.created_at.asc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def mark_processed(
        db: Session,
        system_event: SystemEvent
    ) -> SystemEvent:
        system_event.processed = True
        db.commit()
        db.refresh(system_event)
        return system_event
