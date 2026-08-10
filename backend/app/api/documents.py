from uuid import UUID

from fastapi import APIRouter
from fastapi import BackgroundTasks
from fastapi import Depends
from fastapi import File
from fastapi import HTTPException
from fastapi import Request
from fastapi import UploadFile
from fastapi import status

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import require_permission
from app.models.user import User

from app.schemas.document import (
    DocumentDeleteResponse,
    DocumentResponse,
)

from app.services.audit_service import AuditService
from app.services.document_service import (
    DocumentNotFoundError,
    DocumentService,
    DocumentValidationError,
)


router = APIRouter(
    prefix="/api/documents",
    tags=["Documents"]
)


@router.post(
    "/upload",
    response_model=DocumentResponse
)
async def upload_document(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("documents.upload")
    ),
):
    file_bytes = await file.read()

    try:
        document = DocumentService(db).upload_document(
            file_bytes=file_bytes,
            original_filename=file.filename or "",
            mime_type=file.content_type or "application/octet-stream",
            uploaded_by=current_user.id,
        )
    except DocumentValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    AuditService.enqueue_log(
        background_tasks,
        action="DOCUMENT_UPLOADED",
        resource_type="Document",
        status_code=200,
        request=request,
        user=current_user,
        resource_id=document.id,
        details={
            "original_filename": document.original_filename,
            "status": document.status,
            "file_size": document.file_size,
        },
    )

    return document


@router.get(
    "/",
    response_model=list[DocumentResponse]
)
def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("documents.read")
    ),
):
    return DocumentService(db).get_documents()


@router.delete(
    "/{document_id}",
    response_model=DocumentDeleteResponse
)
def delete_document(
    document_id: UUID,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("documents.delete")
    ),
):
    try:
        DocumentService(db).delete_document(document_id)
    except DocumentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    AuditService.enqueue_log(
        background_tasks,
        action="DOCUMENT_DELETED",
        resource_type="Document",
        status_code=200,
        request=request,
        user=current_user,
        resource_id=document_id,
    )

    return DocumentDeleteResponse(message="Document deleted.")
