"""Private AWS S3 implementation of the document storage boundary."""

from __future__ import annotations

import os
import uuid
from contextlib import contextmanager
from pathlib import Path
from pathlib import PurePosixPath
from pathlib import PureWindowsPath
from tempfile import NamedTemporaryFile
from typing import Iterator

import boto3
from botocore.exceptions import BotoCoreError
from botocore.exceptions import ClientError

from app.core.config import settings
from app.services.storage.base import DocumentStorage
from app.services.storage.base import StorageNotFoundError
from app.services.storage.base import StorageOperationError


class S3DocumentStorage(DocumentStorage):
    """Store private document objects in an S3 bucket.

    Credentials are intentionally delegated to boto3's standard credential
    provider chain (including IAM roles); this adapter accepts no credentials.
    """

    def __init__(
        self,
        *,
        bucket: str | None = None,
        region: str | None = None,
        prefix: str | None = None,
        endpoint_url: str | None = None,
        client=None,
    ):
        self.bucket = (bucket if bucket is not None else settings.DOCUMENT_S3_BUCKET or "").strip()
        self.region = region if region is not None else settings.DOCUMENT_S3_REGION
        self.prefix = (prefix if prefix is not None else settings.DOCUMENT_S3_PREFIX).strip("/ ")
        self.endpoint_url = endpoint_url if endpoint_url is not None else settings.DOCUMENT_S3_ENDPOINT_URL

        if not self.bucket:
            raise StorageOperationError("DOCUMENT_S3_BUCKET is required when S3 storage is enabled.")
        if not self.prefix:
            raise StorageOperationError("DOCUMENT_S3_PREFIX must not be empty.")

        self.client = client or boto3.client(
            "s3",
            region_name=self.region or None,
            endpoint_url=self.endpoint_url or None,
        )

    def store(self, file_bytes: bytes, storage_key: str, content_type: str) -> str:
        object_key = self._object_key(storage_key)
        try:
            self.client.put_object(
                Bucket=self.bucket,
                Key=object_key,
                Body=file_bytes,
                ContentType=content_type,
            )
        except (BotoCoreError, ClientError) as exc:
            raise StorageOperationError("Unable to store document in S3.") from exc
        return storage_key

    @contextmanager
    def materialize(self, storage_key: str) -> Iterator[Path]:
        temporary_path: Path | None = None
        try:
            with NamedTemporaryFile(suffix=".pdf", delete=False) as temporary_file:
                temporary_path = Path(temporary_file.name)
            self.client.download_file(self.bucket, self._object_key(storage_key), str(temporary_path))
            yield temporary_path
        except ClientError as exc:
            if self._is_missing_object(exc):
                raise StorageNotFoundError("Stored document was not found.") from exc
            raise StorageOperationError("Unable to materialize document from S3.") from exc
        except BotoCoreError as exc:
            raise StorageOperationError("Unable to materialize document from S3.") from exc
        finally:
            if temporary_path is not None:
                try:
                    os.unlink(temporary_path)
                except FileNotFoundError:
                    pass
                except OSError:
                    # The temporary file has no caller-visible lifecycle after
                    # this context exits; avoid masking the primary error.
                    pass

    def delete(self, storage_key: str) -> None:
        try:
            # S3 DeleteObject is idempotent, which is suitable for cleanup of
            # a database record whose object was already removed.
            self.client.delete_object(Bucket=self.bucket, Key=self._object_key(storage_key))
        except (BotoCoreError, ClientError) as exc:
            raise StorageOperationError("Unable to delete document from S3.") from exc

    def create_download_url(
        self,
        storage_key: str,
        original_filename: str,
        expiry_seconds: int,
    ) -> str:
        try:
            return self.client.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": self.bucket,
                    "Key": self._object_key(storage_key),
                    "ResponseContentDisposition": self._content_disposition(original_filename),
                },
                ExpiresIn=expiry_seconds,
                HttpMethod="GET",
            )
        except (BotoCoreError, ClientError) as exc:
            raise StorageOperationError("Unable to create S3 download URL.") from exc

    def _object_key(self, storage_key: str) -> str:
        self._validate_storage_key(storage_key)
        return f"{self.prefix}/{storage_key}"

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
            parts = stem.split("-")
            if len(parts) != 10:
                raise StorageOperationError("Invalid storage key.") from exc
            try:
                uuid.UUID("-".join(parts[:5]))
                uuid.UUID("-".join(parts[5:]))
            except ValueError as nested_exc:
                raise StorageOperationError("Invalid storage key.") from nested_exc

    @staticmethod
    def _is_missing_object(exc: ClientError) -> bool:
        code = str(exc.response.get("Error", {}).get("Code", ""))
        return code in {"404", "NoSuchKey", "NotFound"}

    @staticmethod
    def _content_disposition(original_filename: str) -> str:
        safe_filename = original_filename.replace('"', "").replace("\r", "").replace("\n", "")
        return f'attachment; filename="{safe_filename}"'
