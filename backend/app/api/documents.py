from uuid import UUID

from fastapi import APIRouter
from fastapi import BackgroundTasks
from fastapi import Depends
from fastapi import File
from fastapi import HTTPException
from fastapi import Request
from fastapi import UploadFile
from fastapi import status
from fastapi.responses import FileResponse

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import require_permission
from app.models.user import User

from app.schemas.document import (
    DocumentDeleteResponse,
    DocumentDownloadResponse,
    DocumentResponse,
)

from app.services.audit_service import AuditService
from app.services.document_service import (
    DocumentNotFoundError,
    DocumentService,
    DocumentValidationError,
)
from app.services.storage.base import StorageNotFoundError


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


@router.get("/{document_id}/download")
def download_document(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("documents.read")),
):
    """Return a short-lived S3 URL, or stream the private local file."""
    del current_user
    service = DocumentService(db)
    try:
        document = service.get_document(document_id)
        download_url = service.create_download_url(document)
    except DocumentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

    if download_url is not None:
        return DocumentDownloadResponse(download_url=download_url)

    try:
        with service.materialize_document(document) as file_path:
            # A local file has no safe browser-reachable URL. FileResponse is
            # constructed while the context is open; local materialization is
            # the stable original path and therefore remains available.
            return FileResponse(
                path=file_path,
                media_type=document.mime_type,
                filename=document.original_filename,
            )
    except StorageNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stored document was not found.")


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
