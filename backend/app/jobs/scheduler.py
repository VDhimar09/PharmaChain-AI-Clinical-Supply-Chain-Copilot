from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime

from app.jobs.base import BaseJob
from app.jobs.expiry_monitor import ExpiryMonitorJob
from app.jobs.inventory_monitor import InventoryMonitorJob
from app.jobs.notification_dispatcher import (
    NotificationDispatcherJob,
)
from app.jobs.procurement_monitor import ProcurementMonitorJob
from app.jobs.shipment_monitor import ShipmentMonitorJob


logger = logging.getLogger(__name__)


@dataclass
class RegisteredJob:
    job: BaseJob
    trigger: dict


class SchedulerService:

    def __init__(self) -> None:
        try:
            from apscheduler.schedulers.background import (
                BackgroundScheduler,
            )
        except ImportError as exc:
            raise RuntimeError(
                "APScheduler is required for SchedulerService."
            ) from exc

        self._scheduler = BackgroundScheduler()
        self._registered_jobs: dict[str, RegisteredJob] = {}
        self._started = False

    def start(self) -> None:
        if self._started:
            return

        self.register_default_jobs()
        self._scheduler.start()
        self._started = True
        logger.info(
            "Scheduler started with %s jobs.",
            len(self._registered_jobs),
        )

    def shutdown(self) -> None:
        if not self._started:
            return

        self._scheduler.shutdown(
            wait=False
        )
        self._started = False
        logger.info(
            "Scheduler stopped."
        )

    def register_default_jobs(self) -> None:
        if self._registered_jobs:
            return

        self.register_job(
            InventoryMonitorJob(),
            minutes=30,
        )
        self.register_job(
            ShipmentMonitorJob(),
            minutes=15,
        )
        self.register_job(
            ProcurementMonitorJob(),
            hours=1,
        )
        self.register_job(
            ExpiryMonitorJob(),
            days=1,
        )
        self.register_job(
            NotificationDispatcherJob(),
            minutes=1,
        )

    def register_job(
        self,
        job: BaseJob,
        **interval_kwargs,
    ) -> None:
        if job.name in self._registered_jobs:
            return

        scheduler_job = self._scheduler.add_job(
            self._run_job,
            trigger="interval",
            id=job.name,
            name=job.name,
            replace_existing=True,
            kwargs={
                "job_name": job.name
            },
            **interval_kwargs,
        )

        job.next_execution = scheduler_job.next_run_time
        self._registered_jobs[job.name] = RegisteredJob(
            job=job,
            trigger=interval_kwargs,
        )

    def get_jobs_health(self) -> list[dict]:
        jobs_health: list[dict] = []

        for job_name, registered_job in self._registered_jobs.items():
            scheduler_job = self._scheduler.get_job(
                job_name
            )
            registered_job.job.next_execution = (
                scheduler_job.next_run_time
                if scheduler_job is not None
                else None
            )

            jobs_health.append(
                {
                    "name": registered_job.job.name,
                    "description": registered_job.job.description,
                    "schedule": registered_job.job.schedule,
                    "last_execution": registered_job.job.last_execution,
                    "next_execution": registered_job.job.next_execution,
                    "last_duration_ms": registered_job.job.last_duration_ms,
                    "status": registered_job.job.last_status,
                    "retries": registered_job.job.last_attempts,
                }
            )

        return jobs_health

    def is_running(self) -> bool:
        return self._started

    def run_job_now(
        self,
        job_name: str
    ) -> None:
        self._run_job(
            job_name=job_name
        )

    def _run_job(
        self,
        *,
        job_name: str
    ) -> None:
        registered_job = self._registered_jobs.get(
            job_name
        )

        if registered_job is None:
            return

        registered_job.job.run()
        scheduler_job = self._scheduler.get_job(
            job_name
        )

        if scheduler_job is not None:
            registered_job.job.next_execution = (
                scheduler_job.next_run_time
            )


_scheduler_service: SchedulerService | None = None


def get_scheduler_service() -> SchedulerService:
    global _scheduler_service

    if _scheduler_service is None:
        _scheduler_service = SchedulerService()

    return _scheduler_service
