from datetime import datetime

from pydantic import BaseModel


class SystemJobStatusResponse(BaseModel):
    name: str
    description: str
    schedule: str
    last_execution: datetime | None
    next_execution: datetime | None
    last_duration_ms: float | None
    status: str
    retries: int


class SystemJobHealthResponse(BaseModel):
    jobs: list[SystemJobStatusResponse]
