from uuid import UUID

from pydantic import BaseModel
from pydantic import Field


class RagSearchRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=1,
        max_length=2000,
    )


class RagSearchResultItem(BaseModel):
    document_id: UUID
    filename: str
    page_number: int
    content: str
    similarity: float

    model_config = {
        "from_attributes": True
    }


class RagSearchResponse(BaseModel):
    query: str
    results: list[RagSearchResultItem]
