"""Storage adapters for uploaded source documents."""

from app.services.storage.base import DocumentStorage
from app.services.storage.local import LocalDocumentStorage
from app.services.storage.factory import get_document_storage
from app.services.storage.s3 import S3DocumentStorage

__all__ = [
    "DocumentStorage",
    "LocalDocumentStorage",
    "S3DocumentStorage",
    "get_document_storage",
]
