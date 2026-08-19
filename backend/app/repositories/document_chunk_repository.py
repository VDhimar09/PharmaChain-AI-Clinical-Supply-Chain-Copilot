import uuid
from dataclasses import dataclass

from sqlalchemy.orm import Session
from sqlalchemy.orm import selectinload

from app.models.document import Document
from app.models.document import DocumentStatus
from app.models.document_chunk import DocumentChunk


@dataclass(frozen=True)
class SimilarChunk:
    """A chunk returned by a vector similarity search, paired with its
    cosine similarity score against the query embedding."""

    chunk: DocumentChunk
    similarity: float


class DocumentChunkRepository:

    @staticmethod
    def bulk_create(
        db: Session,
        chunks: list[DocumentChunk],
    ) -> list[DocumentChunk]:
        if not chunks:
            return []

        db.add_all(chunks)
        db.commit()

        for chunk in chunks:
            db.refresh(chunk)

        return chunks

    @staticmethod
    def get_by_document_id(
        db: Session,
        document_id: uuid.UUID,
    ) -> list[DocumentChunk]:
        return (
            db.query(DocumentChunk)
            .filter(DocumentChunk.document_id == document_id)
            .order_by(DocumentChunk.chunk_index)
            .all()
        )

    @staticmethod
    def delete_by_document_id(
        db: Session,
        document_id: uuid.UUID,
    ) -> None:
        db.query(DocumentChunk).filter(
            DocumentChunk.document_id == document_id
        ).delete(synchronize_session=False)
        db.commit()

    @staticmethod
    def search(
        db: Session,
        query_embedding: list[float],
        top_k: int,
        embedding_profile: str = "openai",
    ) -> list[SimilarChunk]:
        """Return the `top_k` chunks closest to `query_embedding` by
        cosine similarity, restricted to fully ingested documents.

        Threshold filtering is intentionally left to the caller
        (`RetrieverService`) so this repository stays a thin, reusable
        data-access layer.
        """

        embedding_column = (
            DocumentChunk.local_embedding
            if embedding_profile == "local"
            else DocumentChunk.embedding
        )
        distance = embedding_column.cosine_distance(
            query_embedding
        )

        rows = (
            db.query(DocumentChunk, distance.label("distance"))
            .join(Document, DocumentChunk.document_id == Document.id)
            .options(selectinload(DocumentChunk.document))
            .filter(Document.status == DocumentStatus.COMPLETED)
            .filter(DocumentChunk.embedding_profile == embedding_profile)
            .order_by(distance.asc())
            .limit(top_k)
            .all()
        )

        return [
            SimilarChunk(
                chunk=chunk,
                similarity=1 - distance_value,
            )
            for chunk, distance_value in rows
        ]
