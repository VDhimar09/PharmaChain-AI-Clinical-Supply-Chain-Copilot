import uuid

import pytest

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.document import Document
from app.models.document import DocumentStatus
from app.models.document_chunk import DocumentChunk
from app.repositories.document_repository import DocumentRepository
from app.services.retriever_service import RetrieverService
from tests.fakes import FakeEmbeddingProvider


DIMENSION = settings.RAG_EMBEDDING_DIMENSION


@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def provider():
    return FakeEmbeddingProvider(dimension=DIMENSION)


def _make_document(status: str) -> Document:
    return Document(
        filename=f"{uuid.uuid4()}.pdf",
        original_filename="Cold_Chain_SOP.pdf",
        mime_type="application/pdf",
        file_size=1024,
        checksum=uuid.uuid4().hex + uuid.uuid4().hex,
        status=status,
    )


def _add_chunk(db, document, index, content, provider, page_number=1):
    chunk = DocumentChunk(
        document_id=document.id,
        chunk_index=index,
        content=content,
        page_number=page_number,
        embedding=provider.embed_text(content),
    )
    db.add(chunk)
    return chunk


def test_search_returns_most_similar_chunk_first(db, provider):
    document = DocumentRepository.create(db, _make_document(DocumentStatus.COMPLETED))

    try:
        _add_chunk(
            db, document, 0,
            "Cold chain temperature excursion escalation procedure.",
            provider,
        )
        _add_chunk(
            db, document, 1,
            "Quarterly procurement budget review meeting notes.",
            provider,
        )
        db.commit()

        retriever = RetrieverService(
            db,
            embedding_provider=provider,
            top_k=5,
            similarity_threshold=-1.0,
        )
        results = retriever.search("temperature excursion escalation")

        assert len(results) == 2
        assert "excursion" in results[0].content
        assert results[0].similarity >= results[1].similarity
        assert results[0].filename == "Cold_Chain_SOP.pdf"
        assert results[0].document_id == document.id
        assert results[0].page_number == 1
    finally:
        DocumentRepository.delete(db, document)


def test_search_excludes_chunks_from_non_completed_documents(db, provider):
    completed = DocumentRepository.create(db, _make_document(DocumentStatus.COMPLETED))
    processing = DocumentRepository.create(db, _make_document(DocumentStatus.PROCESSING))

    try:
        _add_chunk(
            db, completed, 0,
            "Temperature excursion escalation for completed document.",
            provider,
        )
        _add_chunk(
            db, processing, 0,
            "Temperature excursion escalation for processing document.",
            provider,
        )
        db.commit()

        retriever = RetrieverService(
            db,
            embedding_provider=provider,
            top_k=5,
            similarity_threshold=-1.0,
        )
        results = retriever.search("temperature excursion escalation")

        assert len(results) == 1
        assert results[0].document_id == completed.id
    finally:
        DocumentRepository.delete(db, completed)
        DocumentRepository.delete(db, processing)


def test_search_respects_top_k(db, provider):
    document = DocumentRepository.create(db, _make_document(DocumentStatus.COMPLETED))

    try:
        for i in range(5):
            _add_chunk(db, document, i, f"Cold chain excursion note number {i}.", provider)
        db.commit()

        retriever = RetrieverService(
            db,
            embedding_provider=provider,
            top_k=2,
            similarity_threshold=-1.0,
        )
        results = retriever.search("cold chain excursion note")

        assert len(results) == 2
    finally:
        DocumentRepository.delete(db, document)


def test_search_applies_similarity_threshold(db, provider):
    document = DocumentRepository.create(db, _make_document(DocumentStatus.COMPLETED))

    try:
        _add_chunk(
            db, document, 0,
            "Cold chain temperature excursion escalation procedure.",
            provider,
        )
        _add_chunk(
            db, document, 1,
            "Quarterly procurement budget review meeting notes.",
            provider,
        )
        db.commit()

        retriever = RetrieverService(
            db,
            embedding_provider=provider,
            top_k=5,
            similarity_threshold=0.999,
        )
        results = retriever.search("temperature excursion escalation")

        # An unreachable threshold must not return irrelevant chunks just
        # to pad out top-K.
        assert results == []
    finally:
        DocumentRepository.delete(db, document)


def test_search_with_no_ingested_documents_returns_empty(db, provider):
    retriever = RetrieverService(
        db,
        embedding_provider=provider,
        top_k=5,
        similarity_threshold=0.0,
    )

    results = retriever.search("anything at all")

    assert results == []


def test_search_with_blank_query_returns_empty_without_querying_db(db, provider):
    retriever = RetrieverService(db, embedding_provider=provider)

    assert retriever.search("   ") == []
