from uuid import UUID

from pydantic import BaseModel


class CurrentUserResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    role: str
    permissions: list[str]

    model_config = {
        "from_attributes": True
    }
