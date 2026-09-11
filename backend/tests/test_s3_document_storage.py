import uuid
from pathlib import Path
from unittest.mock import Mock

import pytest
from botocore.exceptions import BotoCoreError
from botocore.exceptions import ClientError

from app.services.storage.base import StorageNotFoundError
from pydantic import ValidationError
from app.core.config import Settings
from app.services.storage.base import StorageOperationError
from app.services.storage.factory import get_document_storage
from app.services.storage.local import LocalDocumentStorage
from app.services.storage.s3 import S3DocumentStorage


def _storage(client: Mock) -> S3DocumentStorage:
    return S3DocumentStorage(bucket="private-documents", region="eu-west-2", prefix="documents", client=client)


def _storage_key() -> str:
    return f"{uuid.uuid4()}-{uuid.uuid4()}.pdf"


def test_store_uses_private_bucket_opaque_key_and_content_type():
    client = Mock()
    storage = _storage(client)
    storage_key = _storage_key()

    assert storage.store(b"pdf", storage_key, "application/pdf") == storage_key
    client.put_object.assert_called_once_with(Bucket="private-documents", Key=f"documents/{storage_key}", Body=b"pdf", ContentType="application/pdf")


def test_materialize_downloads_then_removes_temporary_file():
    client = Mock()
    storage_key = _storage_key()
    def download(bucket, key, destination):
        assert bucket == "private-documents"
        assert key == f"documents/{storage_key}"
        Path(destination).write_bytes(b"pdf")
    client.download_file.side_effect = download

    with _storage(client).materialize(storage_key) as path:
        assert path.read_bytes() == b"pdf"
        temporary_path = path
    assert not temporary_path.exists()


def test_materialize_missing_object_raises_not_found():
    client = Mock()
    client.download_file.side_effect = ClientError({"Error": {"Code": "NoSuchKey"}}, "GetObject")
    with pytest.raises(StorageNotFoundError):
        with _storage(client).materialize(_storage_key()):
            pass


def test_delete_and_presigned_download_url():
    client = Mock()
    client.generate_presigned_url.return_value = "https://example.test/signed"
    storage = _storage(client)
    storage_key = _storage_key()

    storage.delete(storage_key)
    url = storage.create_download_url(storage_key, "Cold Chain.pdf", 300)

    client.delete_object.assert_called_once_with(Bucket="private-documents", Key=f"documents/{storage_key}")
    assert url == "https://example.test/signed"
    assert client.generate_presigned_url.call_args.kwargs["ExpiresIn"] == 300
    assert client.generate_presigned_url.call_args.kwargs["Params"]["ResponseContentDisposition"] == 'attachment; filename="Cold Chain.pdf"'


@pytest.mark.parametrize(
    "storage_key",
    [
        "report.pdf",
        "../outside.pdf",
        "..\\outside.pdf",
        "/tmp/document.pdf",
        "C:\\temp\\document.pdf",
    ],
)
def test_rejects_invalid_s3_storage_keys(storage_key):
    storage = _storage(Mock())

    with pytest.raises(StorageOperationError):
        storage.store(b"pdf", storage_key, "application/pdf")


def test_accepts_service_generated_s3_storage_key():
    client = Mock()
    storage = _storage(client)
    storage_key = _storage_key()

    assert storage.store(b"pdf", storage_key, "application/pdf") == storage_key


def test_s3_delete_errors_are_wrapped():
    client = Mock()
    client.delete_object.side_effect = ClientError({"Error": {"Code": "AccessDenied"}}, "DeleteObject")

    with pytest.raises(StorageOperationError, match="delete document"):
        _storage(client).delete(_storage_key())


def test_s3_presigned_url_errors_are_wrapped():
    client = Mock()
    client.generate_presigned_url.side_effect = ClientError({"Error": {"Code": "AccessDenied"}}, "GetObject")

    with pytest.raises(StorageOperationError, match="download URL"):
        _storage(client).create_download_url(_storage_key(), "Cold Chain.pdf", 300)


def test_s3_store_botocore_errors_are_wrapped():
    client = Mock()
    client.put_object.side_effect = BotoCoreError(error_msg="connection failed")

    with pytest.raises(StorageOperationError, match="store document"):
        _storage(client).store(b"pdf", _storage_key(), "application/pdf")


def test_s3_materialize_botocore_errors_are_wrapped():
    client = Mock()
    client.download_file.side_effect = BotoCoreError(error_msg="connection failed")

    with pytest.raises(StorageOperationError, match="materialize document"):
        with _storage(client).materialize(_storage_key()):
            pass


def test_s3_delete_botocore_errors_are_wrapped():
    client = Mock()
    client.delete_object.side_effect = BotoCoreError(error_msg="connection failed")

    with pytest.raises(StorageOperationError, match="delete document"):
        _storage(client).delete(_storage_key())


def test_s3_presigned_url_botocore_errors_are_wrapped():
    client = Mock()
    client.generate_presigned_url.side_effect = BotoCoreError(error_msg="connection failed")

    with pytest.raises(StorageOperationError, match="download URL"):
        _storage(client).create_download_url(_storage_key(), "Cold Chain.pdf", 300)


def test_s3_client_receives_region_and_endpoint_url(monkeypatch):
    client = Mock()
    boto3_client = Mock(return_value=client)
    monkeypatch.setattr("app.services.storage.s3.boto3.client", boto3_client)

    storage = S3DocumentStorage(
        bucket="private-documents",
        region="eu-west-2",
        prefix="documents",
        endpoint_url="https://s3.example.test",
    )

    assert storage.client is client
    boto3_client.assert_called_once_with(
        "s3",
        region_name="eu-west-2",
        endpoint_url="https://s3.example.test",
    )


def test_s3_rejects_empty_prefix():
    with pytest.raises(StorageOperationError, match="DOCUMENT_S3_PREFIX"):
        S3DocumentStorage(bucket="private-documents", prefix="", client=Mock())


def test_s3_sanitizes_presigned_filename():
    client = Mock()
    client.generate_presigned_url.return_value = "https://example.test/signed"

    _storage(client).create_download_url(
        _storage_key(), 'Cold "Chain"\r\nSOP.pdf', 300
    )

    disposition = client.generate_presigned_url.call_args.kwargs["Params"][
        "ResponseContentDisposition"
    ]
    assert disposition == 'attachment; filename="Cold ChainSOP.pdf"'


def test_s3_requires_bucket_and_factory_keeps_local_default(monkeypatch):
    with pytest.raises(StorageOperationError, match="DOCUMENT_S3_BUCKET"):
        S3DocumentStorage(bucket="", client=Mock())
    monkeypatch.setattr("app.services.storage.factory.settings.DOCUMENT_STORAGE_PROVIDER", "local")
    assert isinstance(get_document_storage(), LocalDocumentStorage)

def test_factory_selects_s3_without_creating_an_aws_client(monkeypatch):
    expected = object()
    monkeypatch.setattr("app.services.storage.factory.S3DocumentStorage", lambda: expected)
    monkeypatch.setattr("app.services.storage.factory.settings.DOCUMENT_STORAGE_PROVIDER", "s3")

    assert get_document_storage() is expected

def test_presigned_url_expiry_must_be_positive():
    with pytest.raises(ValidationError):
        Settings(
            DATABASE_URL="postgresql://example",
            DOCUMENT_S3_PRESIGNED_URL_EXPIRES_SECONDS=0,
        )


def test_factory_rejects_unknown_provider():
    with pytest.raises(StorageOperationError, match="local.*s3"):
        get_document_storage("not-a-provider")
