import uuid

import pytest

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.document import Document
from app.models.document import DocumentStatus
from app.repositories.document_chunk_repository import DocumentChunkRepository
from app.repositories.document_repository import DocumentRepository
from app.services.chunking_service import ChunkingService
from app.services.document_service import (
    DocumentNotFoundError,
    DocumentService,
    DocumentValidationError,
)
from tests.fakes import FakeEmbeddingProvider
from tests.fakes import build_minimal_pdf


@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def service(db, tmp_path):
    return DocumentService(
        db,
        embedding_provider=FakeEmbeddingProvider(
            dimension=settings.RAG_EMBEDDING_DIMENSION
        ),
        chunking_service=ChunkingService(
            chunk_size=200,
            chunk_overlap=20,
            min_chunk_size=10,
        ),
        storage_dir=str(tmp_path),
    )


VALID_PDF = build_minimal_pdf(
    [
        "Cold-chain SOP: store vaccines between 2C and 8C at all times.",
        "Escalate any temperature excursion to the duty pharmacist immediately.",
    ]
)


def _cleanup(db, document: Document | None):
    if document is None:
        return
    fresh = DocumentRepository.get_by_id(db, document.id)
    if fresh is not None:
        DocumentRepository.delete(db, fresh)


# ---------------------------------------------------------------------
# Upload validation
# ---------------------------------------------------------------------

def test_rejects_empty_file(service):
    with pytest.raises(DocumentValidationError):
        service.upload_document(
            file_bytes=b"",
            original_filename="empty.pdf",
            mime_type="application/pdf",
            uploaded_by=None,
        )


def test_rejects_oversized_file(service, monkeypatch):
    monkeypatch.setattr(
        "app.services.document_service.settings.RAG_MAX_UPLOAD_SIZE_BYTES",
        10,
    )

    with pytest.raises(DocumentValidationError):
        service.upload_document(
            file_bytes=VALID_PDF,
            original_filename="too_big.pdf",
            mime_type="application/pdf",
            uploaded_by=None,
        )


def test_rejects_path_traversal_filename(service):
    with pytest.raises(DocumentValidationError):
        service.upload_document(
            file_bytes=VALID_PDF,
            original_filename="../../etc/passwd.pdf",
            mime_type="application/pdf",
            uploaded_by=None,
        )


def test_rejects_disallowed_extension(service):
    with pytest.raises(DocumentValidationError):
        service.upload_document(
            file_bytes=VALID_PDF,
            original_filename="report.exe",
            mime_type="application/pdf",
            uploaded_by=None,
        )


def test_rejects_disallowed_mime_type(service):
    with pytest.raises(DocumentValidationError):
        service.upload_document(
            file_bytes=VALID_PDF,
            original_filename="report.pdf",
            mime_type="application/zip",
            uploaded_by=None,
        )


def test_rejects_content_not_matching_pdf_signature(service):
    with pytest.raises(DocumentValidationError):
        service.upload_document(
            file_bytes=b"not actually a pdf, just bytes claiming to be one",
            original_filename="fake.pdf",
            mime_type="application/pdf",
            uploaded_by=None,
        )


# ---------------------------------------------------------------------
# Ingestion
# ---------------------------------------------------------------------

def test_successful_ingestion_marks_document_completed(db, service):
    document = None

    try:
        document = service.upload_document(
            file_bytes=VALID_PDF,
            original_filename="Cold_Chain_SOP.pdf",
            mime_type="application/pdf",
            uploaded_by=None,
        )

        assert document.status == DocumentStatus.COMPLETED
        assert document.failure_reason is None
        assert document.page_count == 2

        chunks = DocumentChunkRepository.get_by_document_id(db, document.id)
        assert len(chunks) > 0
        assert all(chunk.document_id == document.id for chunk in chunks)
        assert {chunk.page_number for chunk in chunks} == {1, 2}
    finally:
        _cleanup(db, document)


def test_ingestion_persists_file_to_storage_dir(service, tmp_path):
    document = None
    try:
        document = service.upload_document(
            file_bytes=VALID_PDF,
            original_filename="Cold_Chain_SOP.pdf",
            mime_type="application/pdf",
            uploaded_by=None,
        )

        stored_path = tmp_path / document.filename
        assert stored_path.exists()
        # Stored filename must never be derived from user input.
        assert document.filename != "Cold_Chain_SOP.pdf"
    finally:
        _cleanup(service.db, document)


def test_embedding_failure_marks_document_failed_and_persists_no_chunks(db, tmp_path):
    page_text = "Cold-chain SOP: store vaccines between 2C and 8C at all times."

    failing_service = DocumentService(
        db,
        embedding_provider=FakeEmbeddingProvider(
            dimension=settings.RAG_EMBEDDING_DIMENSION,
            fail_on={page_text},
        ),
        chunking_service=ChunkingService(
            chunk_size=1000,
            chunk_overlap=0,
            min_chunk_size=10,
        ),
        storage_dir=str(tmp_path),
    )

    # A chunk_size of 1000 keeps the page as a single chunk; embed
    # failure is keyed on the exact chunk text so it reliably triggers.
    pdf_bytes = build_minimal_pdf([page_text])

    document = None
    try:
        document = failing_service.upload_document(
            file_bytes=pdf_bytes,
            original_filename="Broken.pdf",
            mime_type="application/pdf",
            uploaded_by=None,
        )

        assert document.status == DocumentStatus.FAILED
        assert document.failure_reason is not None

        chunks = DocumentChunkRepository.get_by_document_id(db, document.id)
        assert chunks == []
    finally:
        _cleanup(db, document)


def test_ingestion_of_unparseable_pdf_marks_document_failed(service):
    document = None
    try:
        # Passes upload validation (correct signature) but is not a
        # structurally valid PDF, so parsing fails.
        broken_bytes = b"%PDF-1.4\nthis is not a real pdf body"

        document = service.upload_document(
            file_bytes=broken_bytes,
            original_filename="corrupt.pdf",
            mime_type="application/pdf",
            uploaded_by=None,
        )

        assert document.status == DocumentStatus.FAILED
        assert document.failure_reason
    finally:
        _cleanup(service.db, document)


# ---------------------------------------------------------------------
# Listing / deletion
# ---------------------------------------------------------------------

def test_get_documents_includes_uploaded_document(service):
    document = None
    try:
        document = service.upload_document(
            file_bytes=VALID_PDF,
            original_filename="Cold_Chain_SOP.pdf",
            mime_type="application/pdf",
            uploaded_by=None,
        )

        documents = service.get_documents()
        assert any(d.id == document.id for d in documents)
    finally:
        _cleanup(service.db, document)


def test_delete_document_removes_row_chunks_and_file(db, service, tmp_path):
    document = service.upload_document(
        file_bytes=VALID_PDF,
        original_filename="Cold_Chain_SOP.pdf",
        mime_type="application/pdf",
        uploaded_by=None,
    )
    document_id = document.id
    stored_path = tmp_path / document.filename
    assert stored_path.exists()

    service.delete_document(document_id)

    assert DocumentRepository.get_by_id(db, document_id) is None
    assert DocumentChunkRepository.get_by_document_id(db, document_id) == []
    assert not stored_path.exists()


def test_delete_unknown_document_raises_not_found(service):
    with pytest.raises(DocumentNotFoundError):
        service.delete_document(uuid.uuid4())
