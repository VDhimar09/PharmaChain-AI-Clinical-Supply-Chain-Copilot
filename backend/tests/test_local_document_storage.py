import uuid

import pytest

from app.services.storage.base import StorageNotFoundError
from app.services.storage.base import StorageOperationError
from app.services.storage.local import LocalDocumentStorage


def test_store_writes_bytes_under_an_opaque_server_controlled_key(tmp_path):
    storage = LocalDocumentStorage(tmp_path)

    storage_key = f"{uuid.uuid4()}-{uuid.uuid4()}.pdf"
    storage.store(b"document bytes", storage_key, "application/pdf")

    assert storage_key.endswith(".pdf")
    assert storage_key != "original-document.pdf"
    assert storage_key.count("-") == 9
    assert (tmp_path / storage_key).read_bytes() == b"document bytes"


def test_materialize_yields_the_stored_local_path(tmp_path):
    storage = LocalDocumentStorage(tmp_path)
    storage_key = f"{uuid.uuid4()}-{uuid.uuid4()}.pdf"
    storage.store(b"document bytes", storage_key, "application/pdf")

    with storage.materialize(storage_key) as path:
        assert path == (tmp_path / storage_key).resolve()
        assert path.read_bytes() == b"document bytes"


def test_delete_removes_stored_document(tmp_path):
    storage = LocalDocumentStorage(tmp_path)
    storage_key = f"{uuid.uuid4()}-{uuid.uuid4()}.pdf"
    storage.store(b"document bytes", storage_key, "application/pdf")

    storage.delete(storage_key)

    assert not (tmp_path / storage_key).exists()


def test_materialize_missing_document_raises_not_found(tmp_path):
    storage = LocalDocumentStorage(tmp_path)
    storage_key = f"{uuid.uuid4()}.pdf"

    with pytest.raises(StorageNotFoundError):
        with storage.materialize(storage_key):
            pass


def test_delete_missing_document_raises_not_found(tmp_path):
    storage = LocalDocumentStorage(tmp_path)
    storage_key = f"{uuid.uuid4()}.pdf"

    with pytest.raises(StorageNotFoundError):
        storage.delete(storage_key)


@pytest.mark.parametrize(
    "storage_key",
    [
        "../../outside.pdf",
        "..\\..\\outside.pdf",
        "/tmp/outside.pdf",
        "C:\\temp\\outside.pdf",
        "not-a-uuid.pdf",
        f"{uuid.uuid4()}.txt",
    ],
)
def test_unsafe_storage_keys_are_rejected(tmp_path, storage_key):
    storage = LocalDocumentStorage(tmp_path)

    with pytest.raises(StorageOperationError):
        with storage.materialize(storage_key):
            pass
