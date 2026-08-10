import uuid

from sqlalchemy.orm import Session

from app.models.document import Document


class DocumentRepository:

    @staticmethod
    def create(db: Session, document: Document) -> Document:
        db.add(document)
        db.commit()
        db.refresh(document)
        return document

    @staticmethod
    def get_all(db: Session) -> list[Document]:
        return (
            db.query(Document)
            .order_by(Document.uploaded_at.desc())
            .all()
        )

    @staticmethod
    def get_by_id(
        db: Session,
        document_id: uuid.UUID,
    ) -> Document | None:
        return (
            db.query(Document)
            .filter(Document.id == document_id)
            .first()
        )

    @staticmethod
    def get_by_checksum(
        db: Session,
        checksum: str,
    ) -> Document | None:
        return (
            db.query(Document)
            .filter(Document.checksum == checksum)
            .first()
        )

    @staticmethod
    def update_status(
        db: Session,
        document: Document,
        status: str,
        failure_reason: str | None = None,
        page_count: int | None = None,
    ) -> Document:
        document.status = status
        document.failure_reason = failure_reason

        if page_count is not None:
            document.page_count = page_count

        db.add(document)
        db.commit()
        db.refresh(document)
        return document

    @staticmethod
    def delete(db: Session, document: Document) -> None:
        db.delete(document)
        db.commit()
