from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import require_permission
from app.models.user import User

from app.schemas.rag import (
    RagCitation,
    RagQueryRequest,
    RagQueryResponse,
    RagSearchRequest,
    RagSearchResponse,
    RagSearchResultItem,
)

from app.services.rag_generation_service import (
    RagGenerationError,
    RagGenerationService,
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


@router.post(
    "/query",
    response_model=RagQueryResponse
)
def query(
    payload: RagQueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("rag.query")
    ),
):
    """Answer a question with an LLM, grounded strictly in retrieved
    document evidence.

    No supporting evidence retrieved -> the LLM is never called and a
    fixed "not found" response is returned. Citations are always resolved
    server-side against the documents actually retrieved for this
    request - never trusted from the model's output.
    """

    try:
        result = RagGenerationService(db).query(payload.query)
    except RagGenerationError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI generation is temporarily unavailable. Please try again.",
        )

    return RagQueryResponse(
        answer=result.answer,
        grounded=result.grounded,
        citations=[
            RagCitation(
                document_id=citation.document_id,
                filename=citation.filename,
                page_number=citation.page_number,
            )
            for citation in result.citations
        ],
    )
