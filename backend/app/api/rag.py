from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import require_permission
from app.models.user import User

from app.schemas.rag import (
    RagSearchRequest,
    RagSearchResponse,
    RagSearchResultItem,
)

from app.services.retriever_service import RetrieverService


router = APIRouter(
    prefix="/api/rag",
    tags=["RAG"]
)


@router.post(
    "/search",
    response_model=RagSearchResponse
)
def search(
    payload: RagSearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("rag.search")
    ),
):
    """Retrieve semantically relevant document chunks for a query.

    This endpoint returns retrieved evidence only - it does not generate
    an LLM answer.
    """

    results = RetrieverService(db).search(payload.query)

    return RagSearchResponse(
        query=payload.query,
        results=[
            RagSearchResultItem(
                document_id=result.document_id,
                filename=result.filename,
                page_number=result.page_number,
                content=result.content,
                similarity=result.similarity,
            )
            for result in results
        ],
    )
