from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    id: UUID
    created_at: datetime
    user_id: UUID | None
    user_email: str | None
    action: str
    resource_type: str
    resource_id: str | None
    http_method: str
    endpoint: str
    status_code: int
    ip_address: str | None
    user_agent: str | None
    details: dict[str, Any]

    model_config = {
        "from_attributes": True
    }


class AuditLogListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[AuditLogResponse]
