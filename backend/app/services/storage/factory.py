"""Document-storage provider selection."""

from app.core.config import settings
from app.services.storage.base import DocumentStorage
from app.services.storage.base import StorageOperationError
from app.services.storage.local import LocalDocumentStorage
from app.services.storage.s3 import S3DocumentStorage


def get_document_storage(provider: str | None = None) -> DocumentStorage:
    """Create only the configured provider; local mode never touches AWS."""
    selected = (provider or settings.DOCUMENT_STORAGE_PROVIDER).strip().lower()
    if selected == "local":
        return LocalDocumentStorage()
    if selected == "s3":
        return S3DocumentStorage()
    raise StorageOperationError(
        "DOCUMENT_STORAGE_PROVIDER must be either 'local' or 's3'."
    )
