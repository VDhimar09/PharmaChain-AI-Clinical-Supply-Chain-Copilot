"""Storage adapters for uploaded source documents."""

from app.services.storage.base import DocumentStorage
from app.services.storage.local import LocalDocumentStorage

__all__ = [
    "DocumentStorage",
    "LocalDocumentStorage",
]
