from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: UUID
    filename: str
    original_filename: str
    mime_type: str
    file_size: int
    checksum: str
    status: str
    failure_reason: str | None = None
    page_count: int | None = None
    uploaded_by: UUID | None = None
    uploaded_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class DocumentDeleteResponse(BaseModel):
    message: str
