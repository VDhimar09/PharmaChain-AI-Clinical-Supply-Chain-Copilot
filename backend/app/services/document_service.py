"""Document upload validation and RAG ingestion orchestration.

Pipeline: upload validation -> document row -> PDF parsing -> chunking
-> embedding -> vector persistence -> status update. Phase 1 runs this
pipeline synchronously within the request (no Celery/Redis/background
worker exists in this codebase yet), so ingestion completes - or is
marked FAILED - before the upload endpoint responds.
"""

from __future__ import annotations

import hashlib
import time
import uuid
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import get_logger
from app.models.document import Document
from app.models.document import DocumentStatus
from app.models.document_chunk import DocumentChunk
from app.repositories.document_chunk_repository import DocumentChunkRepository
from app.repositories.document_repository import DocumentRepository
from app.services.chunking_service import ChunkingService
from app.services.embeddings.base_provider import EmbeddingError
from app.services.embeddings.base_provider import EmbeddingProvider
from app.services.parsing.base_parser import DocumentParser
from app.services.parsing.base_parser import DocumentParsingError


logger = get_logger("document_service")


class DocumentValidationError(Exception):
    """Raised when an uploaded file fails validation. Maps to HTTP 400."""


class DocumentIngestionError(Exception):
    """Raised internally when a parsed document yields nothing to store."""


class DocumentNotFoundError(Exception):
    """Raised when a document id does not exist. Maps to HTTP 404."""


class DocumentService:

    def __init__(
        self,
        db: Session,
        embedding_provider: EmbeddingProvider | None = None,
        parser: DocumentParser | None = None,
        chunking_service: ChunkingService | None = None,
        storage_dir: str | None = None,
    ):
        self.db = db
        self._embedding_provider = embedding_provider
        self._parser = parser
        self.chunking_service = chunking_service or ChunkingService()
        self.storage_dir = Path(storage_dir or settings.RAG_STORAGE_DIR)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    @property
    def embedding_provider(self) -> EmbeddingProvider:
        if self._embedding_provider is None:
            # Imported lazily so environments without an OpenAI key can
            # still import this module (e.g. to inject a fake provider).
            from app.services.embeddings.openai_provider import (
                OpenAIEmbeddingProvider,
            )

            self._embedding_provider = OpenAIEmbeddingProvider()

        return self._embedding_provider

    @property
    def parser(self) -> DocumentParser:
        if self._parser is None:
            from app.services.parsing.pdf_parser import PyPdfDocumentParser

            self._parser = PyPdfDocumentParser()

        return self._parser

    # ------------------------------------------------------------------
    # Upload + ingestion
    # ------------------------------------------------------------------

    def upload_document(
        self,
        *,
        file_bytes: bytes,
        original_filename: str,
        mime_type: str,
        uploaded_by: uuid.UUID | None,
    ) -> Document:
        self._validate_upload(file_bytes, original_filename, mime_type)

        checksum = hashlib.sha256(file_bytes).hexdigest()

        # The stored filename is always server-generated - never derived
        # from user input - to rule out path traversal or unsafe storage.
        stored_filename = f"{uuid.uuid4()}.pdf"
        file_path = self.storage_dir / stored_filename
        file_path.write_bytes(file_bytes)

        document = Document(
            filename=stored_filename,
            original_filename=original_filename,
            mime_type=mime_type,
            file_size=len(file_bytes),
            checksum=checksum,
            status=DocumentStatus.PENDING,
            uploaded_by=uploaded_by,
        )
        document = DocumentRepository.create(self.db, document)

        self._ingest(document, file_path)

        return document

    def get_documents(self) -> list[Document]:
        return DocumentRepository.get_all(self.db)

    def delete_document(self, document_id: uuid.UUID) -> None:
        document = DocumentRepository.get_by_id(self.db, document_id)

        if document is None:
            raise DocumentNotFoundError(
                f"Document '{document_id}' was not found."
            )

        file_path = self.storage_dir / document.filename

        # Chunks are removed via the model's cascade relationship / the
        # FK's ON DELETE CASCADE.
        DocumentRepository.delete(self.db, document)

        if file_path.exists():
            file_path.unlink(missing_ok=True)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _ingest(self, document: Document, file_path: Path) -> None:
        started_at = time.monotonic()

        try:
            DocumentRepository.update_status(
                self.db,
                document,
                DocumentStatus.PROCESSING,
            )

            parse_started_at = time.monotonic()
            pages = self.parser.parse(str(file_path))
            parse_elapsed_ms = (time.monotonic() - parse_started_at) * 1000

            chunks = self.chunking_service.chunk_pages(document.id, pages)

            if not chunks:
                raise DocumentIngestionError(
                    "No extractable text was found in the document."
                )

            embed_started_at = time.monotonic()
            embeddings = self.embedding_provider.embed_texts(
                [chunk.content for chunk in chunks]
            )
            embed_elapsed_ms = (time.monotonic() - embed_started_at) * 1000

            chunk_rows = [
                DocumentChunk(
                    document_id=document.id,
                    chunk_index=chunk.chunk_index,
                    content=chunk.content,
                    page_number=chunk.page_number,
                    chunk_metadata={},
                    embedding=embedding,
                )
                for chunk, embedding in zip(chunks, embeddings)
            ]
            DocumentChunkRepository.bulk_create(self.db, chunk_rows)

            DocumentRepository.update_status(
                self.db,
                document,
                DocumentStatus.COMPLETED,
                page_count=len(pages),
            )

            total_elapsed_ms = (time.monotonic() - started_at) * 1000

            logger.info(
                "Document %s ingested: pages=%s chunks=%s "
                "parse_ms=%.1f embed_ms=%.1f total_ms=%.1f",
                document.id,
                len(pages),
                len(chunks),
                parse_elapsed_ms,
                embed_elapsed_ms,
                total_elapsed_ms,
            )

        except (
            DocumentParsingError,
            EmbeddingError,
            DocumentIngestionError,
        ) as exc:
            self._mark_failed(document, str(exc))

        except Exception:
            logger.exception(
                "Unexpected error during ingestion of document %s",
                document.id,
            )
            self._mark_failed(
                document,
                "An unexpected error occurred while processing the document.",
            )

    def _mark_failed(self, document: Document, reason: str) -> None:
        self.db.rollback()
        DocumentChunkRepository.delete_by_document_id(self.db, document.id)
        DocumentRepository.update_status(
            self.db,
            document,
            DocumentStatus.FAILED,
            failure_reason=reason[:1000],
        )
        logger.warning(
            "Document ingestion failed for %s: %s",
            document.id,
            reason,
        )

    def _validate_upload(
        self,
        file_bytes: bytes,
        original_filename: str,
        mime_type: str,
    ) -> None:
        if not file_bytes:
            raise DocumentValidationError("Uploaded file is empty.")

        if len(file_bytes) > settings.RAG_MAX_UPLOAD_SIZE_BYTES:
            raise DocumentValidationError(
                "File exceeds the maximum allowed size of "
                f"{settings.RAG_MAX_UPLOAD_SIZE_BYTES} bytes."
            )

        if not original_filename or not original_filename.strip():
            raise DocumentValidationError("Filename is required.")

        safe_name = Path(original_filename).name

        if safe_name != original_filename or ".." in original_filename:
            raise DocumentValidationError(
                "Filename contains invalid path characters."
            )

        allowed_extensions = tuple(
            extension.strip().lower()
            for extension in settings.RAG_ALLOWED_EXTENSIONS.split(",")
        )

        if not safe_name.lower().endswith(allowed_extensions):
            raise DocumentValidationError(
                "Unsupported file extension. Allowed: "
                f"{settings.RAG_ALLOWED_EXTENSIONS}"
            )

        allowed_mime_types = {
            allowed.strip().lower()
            for allowed in settings.RAG_ALLOWED_MIME_TYPES.split(",")
        }

        if mime_type.lower() not in allowed_mime_types:
            raise DocumentValidationError(
                f"Unsupported MIME type '{mime_type}'."
            )

        if not file_bytes.startswith(b"%PDF-"):
            raise DocumentValidationError(
                "File content does not match a valid PDF signature."
            )
