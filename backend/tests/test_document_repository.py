import uuid

import pytest

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.document import Document
from app.models.document import DocumentStatus
from app.models.document_chunk import DocumentChunk
from app.repositories.document_chunk_repository import DocumentChunkRepository
from app.repositories.document_repository import DocumentRepository


@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


def _make_document(**overrides) -> Document:
    defaults = dict(
        filename=f"{uuid.uuid4()}.pdf",
        original_filename="Warehouse_Policy.pdf",
        mime_type="application/pdf",
        file_size=4096,
        checksum=uuid.uuid4().hex + uuid.uuid4().hex,
    )
    defaults.update(overrides)
    return Document(**defaults)


def test_create_and_get_by_id(db):
    document = DocumentRepository.create(db, _make_document())

    try:
        fetched = DocumentRepository.get_by_id(db, document.id)
        assert fetched is not None
        assert fetched.id == document.id
    finally:
        DocumentRepository.delete(db, document)


def test_get_by_id_returns_none_for_unknown_id(db):
    assert DocumentRepository.get_by_id(db, uuid.uuid4()) is None


def test_get_all_includes_created_document(db):
    document = DocumentRepository.create(db, _make_document())

    try:
        all_documents = DocumentRepository.get_all(db)
        assert any(d.id == document.id for d in all_documents)
    finally:
        DocumentRepository.delete(db, document)


def test_update_status_sets_status_and_failure_reason(db):
    document = DocumentRepository.create(db, _make_document())

    try:
        updated = DocumentRepository.update_status(
            db,
            document,
            DocumentStatus.FAILED,
            failure_reason="Parsing failed.",
        )

        assert updated.status == DocumentStatus.FAILED
        assert updated.failure_reason == "Parsing failed."
    finally:
        DocumentRepository.delete(db, document)


def test_update_status_to_completed_sets_page_count(db):
    document = DocumentRepository.create(db, _make_document())

    try:
        updated = DocumentRepository.update_status(
            db,
            document,
            DocumentStatus.COMPLETED,
            page_count=7,
        )

        assert updated.status == DocumentStatus.COMPLETED
        assert updated.failure_reason is None
        assert updated.page_count == 7
    finally:
        DocumentRepository.delete(db, document)


def test_delete_removes_document(db):
    document = DocumentRepository.create(db, _make_document())
    document_id = document.id

    DocumentRepository.delete(db, document)

    assert DocumentRepository.get_by_id(db, document_id) is None


def test_bulk_create_chunks_and_get_by_document_id(db):
    document = DocumentRepository.create(
        db,
        _make_document(status=DocumentStatus.COMPLETED),
    )

    embedding = [0.1] * settings.RAG_EMBEDDING_DIMENSION
    chunks = [
        DocumentChunk(
            document_id=document.id,
            chunk_index=i,
            content=f"Chunk {i}",
            page_number=1,
            embedding=embedding,
        )
        for i in range(3)
    ]

    try:
        DocumentChunkRepository.bulk_create(db, chunks)

        fetched = DocumentChunkRepository.get_by_document_id(db, document.id)
        assert [c.chunk_index for c in fetched] == [0, 1, 2]
    finally:
        DocumentRepository.delete(db, document)


def test_delete_by_document_id_removes_only_that_documents_chunks(db):
    document_a = DocumentRepository.create(
        db,
        _make_document(status=DocumentStatus.COMPLETED),
    )
    document_b = DocumentRepository.create(
        db,
        _make_document(status=DocumentStatus.COMPLETED),
    )

    embedding = [0.1] * settings.RAG_EMBEDDING_DIMENSION

    try:
        DocumentChunkRepository.bulk_create(
            db,
            [
                DocumentChunk(
                    document_id=document_a.id,
                    chunk_index=0,
                    content="A chunk",
                    page_number=1,
                    embedding=embedding,
                ),
                DocumentChunk(
                    document_id=document_b.id,
                    chunk_index=0,
                    content="B chunk",
                    page_number=1,
                    embedding=embedding,
                ),
            ],
        )

        DocumentChunkRepository.delete_by_document_id(db, document_a.id)

        assert DocumentChunkRepository.get_by_document_id(db, document_a.id) == []
        assert len(DocumentChunkRepository.get_by_document_id(db, document_b.id)) == 1
    finally:
        DocumentRepository.delete(db, document_a)
        DocumentRepository.delete(db, document_b)
