import uuid

import pytest
from sqlalchemy.exc import IntegrityError

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.document import Document
from app.models.document import DocumentStatus
from app.models.document_chunk import DocumentChunk


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
        original_filename="Cold_Chain_SOP.pdf",
        mime_type="application/pdf",
        file_size=2048,
        checksum=uuid.uuid4().hex + uuid.uuid4().hex,
    )
    defaults.update(overrides)
    return Document(**defaults)


def test_document_defaults_are_applied(db):
    document = _make_document()
    db.add(document)
    db.commit()
    db.refresh(document)

    try:
        assert document.id is not None
        assert document.status == DocumentStatus.PENDING
        assert document.failure_reason is None
        assert document.page_count is None
        assert document.uploaded_at is not None
        assert document.updated_at is not None
    finally:
        db.delete(document)
        db.commit()


def test_document_chunk_stores_embedding_and_metadata(db):
    document = _make_document()
    db.add(document)
    db.commit()
    db.refresh(document)

    embedding = [0.1] * settings.RAG_EMBEDDING_DIMENSION
    chunk = DocumentChunk(
        document_id=document.id,
        chunk_index=0,
        content="Store between 2C and 8C.",
        page_number=1,
        chunk_metadata={"section": "storage"},
        embedding=embedding,
    )
    db.add(chunk)
    db.commit()
    db.refresh(chunk)

    try:
        assert chunk.id is not None
        assert len(chunk.embedding) == settings.RAG_EMBEDDING_DIMENSION
        assert chunk.chunk_metadata == {"section": "storage"}
        assert chunk.created_at is not None
    finally:
        db.delete(chunk)
        db.delete(document)
        db.commit()


def test_document_chunk_default_metadata_is_empty_dict(db):
    document = _make_document()
    db.add(document)
    db.commit()
    db.refresh(document)

    chunk = DocumentChunk(
        document_id=document.id,
        chunk_index=0,
        content="No metadata supplied.",
        page_number=1,
        embedding=[0.0] * settings.RAG_EMBEDDING_DIMENSION,
    )
    db.add(chunk)
    db.commit()
    db.refresh(chunk)

    try:
        assert chunk.chunk_metadata == {}
    finally:
        db.delete(chunk)
        db.delete(document)
        db.commit()


def test_duplicate_chunk_index_for_same_document_is_rejected(db):
    document = _make_document()
    db.add(document)
    db.commit()
    db.refresh(document)

    embedding = [0.0] * settings.RAG_EMBEDDING_DIMENSION
    db.add(
        DocumentChunk(
            document_id=document.id,
            chunk_index=0,
            content="First chunk.",
            page_number=1,
            embedding=embedding,
        )
    )
    db.commit()

    db.add(
        DocumentChunk(
            document_id=document.id,
            chunk_index=0,
            content="Duplicate index chunk.",
            page_number=1,
            embedding=embedding,
        )
    )

    try:
        with pytest.raises(IntegrityError):
            db.commit()
    finally:
        db.rollback()
        db.delete(document)
        db.commit()


def test_deleting_document_cascades_to_chunks(db):
    document = _make_document()
    db.add(document)
    db.commit()
    db.refresh(document)

    embedding = [0.0] * settings.RAG_EMBEDDING_DIMENSION
    chunk = DocumentChunk(
        document_id=document.id,
        chunk_index=0,
        content="Will be cascade-deleted.",
        page_number=1,
        embedding=embedding,
    )
    db.add(chunk)
    db.commit()
    chunk_id = chunk.id

    db.delete(document)
    db.commit()

    assert db.get(DocumentChunk, chunk_id) is None
