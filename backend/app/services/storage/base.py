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
    def store(self, file_bytes: bytes) -> str:
        """Persist bytes and return a server-controlled storage key."""

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
    def generate_download_url(self, storage_key: str) -> str | None:
        """Return a download URL when the storage backend supports one."""
