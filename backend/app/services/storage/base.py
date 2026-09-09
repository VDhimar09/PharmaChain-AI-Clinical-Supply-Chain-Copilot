"""Small storage boundary used by the document ingestion service."""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from contextlib import AbstractContextManager
from pathlib import Path


class StorageError(Exception):
    """Base exception for document-storage failures."""


class StorageNotFoundError(StorageError):
    """Raised when a requested stored document does not exist."""


class StorageOperationError(StorageError):
    """Raised when a storage operation cannot be completed safely."""


class DocumentStorage(ABC):
    """Storage operations required by :class:`DocumentService` only."""

    @abstractmethod
    def store(self, file_bytes: bytes, storage_key: str, content_type: str) -> str:
        """Persist bytes at a server-controlled key and return that key."""

    @abstractmethod
    def materialize(
        self,
        storage_key: str,
    ) -> AbstractContextManager[Path]:
        """Yield a local path suitable for the existing PDF parser."""

    @abstractmethod
    def delete(self, storage_key: str) -> None:
        """Delete a stored document."""

    @abstractmethod
    def create_download_url(
        self,
        storage_key: str,
        original_filename: str,
        expiry_seconds: int,
    ) -> str | None:
        """Return a time-limited download URL when the backend supports it."""
