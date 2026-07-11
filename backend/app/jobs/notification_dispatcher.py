import logging

from app.jobs.base import BaseJob
from app.models.system_event import SystemEvent
from app.services.event_service import EventService


logger = logging.getLogger(__name__)


class NotificationDispatcherJob(BaseJob):

    schedule = "* * * * *"

    @property
    def name(self) -> str:
        return "notification_dispatcher"

    @property
    def description(self) -> str:
        return "Dispatch queued system events to notification channels."

    def execute(self) -> dict:
        db = self._get_db()

        try:
            result = EventService.process_events(
                db,
                handler=self._dispatch_to_console,
            )
            return result
        finally:
            db.close()

    def _dispatch_to_console(
        self,
        system_event: SystemEvent
    ) -> None:
        logger.info(
            "Notification dispatched: %s | %s | %s",
            system_event.event_type,
            system_event.severity,
            system_event.payload,
        )
