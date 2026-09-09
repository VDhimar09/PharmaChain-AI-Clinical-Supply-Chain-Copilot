"""Local filesystem implementation of the document storage boundary."""

from __future__ import annotations

import os
import uuid
from contextlib import contextmanager
from pathlib import Path
from pathlib import PurePosixPath
from pathlib import PureWindowsPath
from tempfile import NamedTemporaryFile
from typing import Iterator

from app.core.config import settings
from app.services.storage.base import DocumentStorage
from app.services.storage.base import StorageNotFoundError
from app.services.storage.base import StorageOperationError


class LocalDocumentStorage(DocumentStorage):
    """Persist documents beneath the configured local storage directory."""

    def __init__(self, storage_dir: str | Path | None = None):
        self.storage_dir = Path(storage_dir or settings.RAG_STORAGE_DIR).resolve()

        try:
            self.storage_dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise StorageOperationError(
                "Unable to initialise local document storage."
            ) from exc

    def store(self, file_bytes: bytes, storage_key: str, content_type: str) -> str:
        """Store bytes under a caller-supplied opaque key, never user input."""
        del content_type
        self._validate_storage_key(storage_key)
        target_path = self._path_for_key(storage_key)
        temporary_path: Path | None = None

        try:
            with NamedTemporaryFile(
                mode="wb",
                dir=self.storage_dir,
                prefix=".upload-",
                suffix=".tmp",
                delete=False,
            ) as temporary_file:
                temporary_path = Path(temporary_file.name)
                temporary_file.write(file_bytes)

            os.replace(temporary_path, target_path)
        except OSError as exc:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)
            raise StorageOperationError(
                "Unable to store document locally."
            ) from exc

        return storage_key

    @contextmanager
    def materialize(self, storage_key: str) -> Iterator[Path]:
        """Yield the local file path; no copy is needed for local storage."""
        path = self._path_for_key(storage_key)

        if not path.is_file():
            raise StorageNotFoundError("Stored document was not found.")

        yield path

    def delete(self, storage_key: str) -> None:
        path = self._path_for_key(storage_key)

        try:
            path.unlink()
        except FileNotFoundError as exc:
            raise StorageNotFoundError("Stored document was not found.") from exc
        except OSError as exc:
            raise StorageOperationError(
                "Unable to delete stored document."
            ) from exc

    def create_download_url(
        self,
        storage_key: str,
        original_filename: str,
        expiry_seconds: int,
    ) -> str | None:
        """Local storage has no externally accessible download URL."""
        del original_filename, expiry_seconds
        self._path_for_key(storage_key)
        return None

    def _path_for_key(self, storage_key: str) -> Path:
        self._validate_storage_key(storage_key)
        candidate = (self.storage_dir / storage_key).resolve()

        if candidate.parent != self.storage_dir:
            raise StorageOperationError("Invalid storage key.")

        return candidate

    @staticmethod
    def _validate_storage_key(storage_key: str) -> None:
        if not storage_key or not isinstance(storage_key, str):
            raise StorageOperationError("Invalid storage key.")

        posix_path = PurePosixPath(storage_key)
        windows_path = PureWindowsPath(storage_key)

        if (
            posix_path.is_absolute()
            or windows_path.is_absolute()
            or len(posix_path.parts) != 1
            or len(windows_path.parts) != 1
            or storage_key != posix_path.name
            or storage_key != windows_path.name
            or not storage_key.lower().endswith(".pdf")
        ):
            raise StorageOperationError("Invalid storage key.")

        stem = storage_key.removesuffix(".pdf")
        try:
            uuid.UUID(stem)
        except ValueError as exc:
            # DocumentService uses this fully opaque, namespace-friendly
            # shape for every provider so storage metadata is portable.
            parts = stem.split("-")
            if len(parts) != 10:
                raise StorageOperationError("Invalid storage key.") from exc
            try:
                uuid.UUID("-".join(parts[:5]))
                uuid.UUID("-".join(parts[5:]))
            except ValueError as nested_exc:
                raise StorageOperationError("Invalid storage key.") from nested_exc
