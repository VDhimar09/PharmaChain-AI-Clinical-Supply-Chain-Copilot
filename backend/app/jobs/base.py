from __future__ import annotations

import logging
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime
from datetime import timezone
from time import perf_counter
from typing import Any

from starlette.requests import Request

from app.core.database import SessionLocal
from app.services.audit_service import AuditService


logger = logging.getLogger(__name__)


@dataclass
class JobExecutionResult:
    status: str
    duration_ms: float
    attempts: int
    payload: dict[str, Any]
    executed_at: datetime


class BaseJob(ABC):

    max_retries = 3
    schedule = "manual"

    def __init__(self) -> None:
        self.last_execution: datetime | None = None
        self.last_duration_ms: float | None = None
        self.last_status: str = "idle"
        self.last_attempts: int = 0
        self.next_execution: datetime | None = None

    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def description(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def execute(
        self
    ) -> dict[str, Any]:
        raise NotImplementedError

    def run(self) -> JobExecutionResult:
        request = self._build_request(
            action="execute"
        )

        AuditService.log(
            action="JOB_STARTED",
            resource_type="Job",
            status_code=200,
            request=request,
            resource_id=self.name,
            details={
                "job_name": self.name,
                "job_description": self.description,
            },
        )

        executed_at = datetime.now(
            timezone.utc
        )
        start_time = perf_counter()
        last_exception: Exception | None = None

        for attempt in range(
            1,
            self.max_retries + 1,
        ):
            try:
                payload = self.execute()
                duration_ms = (
                    perf_counter() - start_time
                ) * 1000

                self.last_execution = executed_at
                self.last_duration_ms = duration_ms
                self.last_status = "success"
                self.last_attempts = attempt

                AuditService.log(
                    action="JOB_COMPLETED",
                    resource_type="Job",
                    status_code=200,
                    request=self._build_request(
                        action="completed"
                    ),
                    resource_id=self.name,
                    details={
                        "job_name": self.name,
                        "attempts": attempt,
                        "duration_ms": round(
                            duration_ms,
                            2,
                        ),
                        "payload": payload,
                    },
                )

                return JobExecutionResult(
                    status="success",
                    duration_ms=duration_ms,
                    attempts=attempt,
                    payload=payload,
                    executed_at=executed_at,
                )
            except Exception as exc:
                last_exception = exc
                logger.exception(
                    "Job '%s' failed on attempt %s.",
                    self.name,
                    attempt,
                )

        duration_ms = (
            perf_counter() - start_time
        ) * 1000

        self.last_execution = executed_at
        self.last_duration_ms = duration_ms
        self.last_status = "failed"
        self.last_attempts = self.max_retries

        AuditService.log(
            action="JOB_FAILED",
            resource_type="Job",
            status_code=500,
            request=self._build_request(
                action="failed"
            ),
            resource_id=self.name,
            details={
                "job_name": self.name,
                "attempts": self.max_retries,
                "duration_ms": round(
                    duration_ms,
                    2,
                ),
                "error": str(last_exception),
            },
        )

        return JobExecutionResult(
            status="failed",
            duration_ms=duration_ms,
            attempts=self.max_retries,
            payload={
                "error": str(last_exception),
            },
            executed_at=executed_at,
        )

    def _get_db(self):
        return SessionLocal()

    def _build_request(
        self,
        *,
        action: str,
    ) -> Request:
        return Request(
            {
                "type": "http",
                "method": "SYSTEM",
                "path": f"/system/jobs/{self.name}/{action}",
                "headers": [],
                "client": ("scheduler", 0),
                "scheme": "http",
                "server": ("scheduler", 80),
                "root_path": "",
                "query_string": b"",
            }
        )
