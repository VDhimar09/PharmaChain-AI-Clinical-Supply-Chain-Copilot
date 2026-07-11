import logging
from collections.abc import Callable
from typing import Any

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.models.system_event import SystemEvent
from app.repositories.system_event_repository import (
    SystemEventRepository,
)


logger = logging.getLogger(__name__)


class EventService:

    MAX_RETRIES = 3

    @staticmethod
    def create_event(
        db: Session,
        *,
        event_type: str,
        severity: str,
        source: str,
        payload: dict[str, Any] | None = None,
    ) -> SystemEvent:
        system_event = SystemEvent(
            event_type=event_type,
            severity=severity,
            source=source,
            payload=EventService._serialize_payload(
                payload
            ),
            processed=False,
        )

        return SystemEventRepository.create(
            db,
            system_event,
        )

    @staticmethod
    def queue_event(
        db: Session,
        *,
        event_type: str,
        severity: str,
        source: str,
        payload: dict[str, Any] | None = None,
    ) -> SystemEvent:
        return EventService.create_event(
            db,
            event_type=event_type,
            severity=severity,
            source=source,
            payload=payload,
        )

    @staticmethod
    def list_events(
        db: Session,
        *,
        processed: bool | None = None,
        limit: int = 100,
    ) -> list[SystemEvent]:
        return SystemEventRepository.list(
            db,
            processed=processed,
            limit=limit,
        )

    @staticmethod
    def process_events(
        db: Session,
        *,
        handler: Callable[[SystemEvent], None],
        limit: int = 100,
    ) -> dict[str, int]:
        processed_count = 0
        failed_count = 0

        events = SystemEventRepository.list(
            db,
            processed=False,
            limit=limit,
        )

        for system_event in events:
            success = EventService._process_with_retry(
                system_event,
                handler,
            )

            if success:
                SystemEventRepository.mark_processed(
                    db,
                    system_event,
                )
                processed_count += 1
            else:
                failed_count += 1

        return {
            "processed": processed_count,
            "failed": failed_count,
            "queued": len(events),
        }

    @staticmethod
    def _process_with_retry(
        system_event: SystemEvent,
        handler: Callable[[SystemEvent], None],
    ) -> bool:
        for attempt in range(
            1,
            EventService.MAX_RETRIES + 1,
        ):
            try:
                handler(system_event)
                return True
            except Exception:
                logger.exception(
                    "Failed to process system event '%s' on attempt %s.",
                    system_event.event_type,
                    attempt,
                )

        return False

    @staticmethod
    def _serialize_payload(
        payload: dict[str, Any] | None
    ) -> dict[str, Any]:
        if payload is None:
            return {}

        encoded = jsonable_encoder(
            payload,
            exclude_none=True,
        )

        if isinstance(encoded, dict):
            return encoded

        return {
            "value": encoded
        }
