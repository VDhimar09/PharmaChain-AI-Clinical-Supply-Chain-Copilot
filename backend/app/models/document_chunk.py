import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import CheckConstraint
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import UniqueConstraint
from sqlalchemy import func
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.core.config import settings
from app.models.base import Base


class DocumentChunk(Base):

    __tablename__ = "document_chunks"

    __table_args__ = (
        UniqueConstraint(
            "document_id",
            "chunk_index",
            name="uq_document_chunks_document_id_chunk_index"
        ),
        CheckConstraint(
            "(embedding_profile = 'openai' AND embedding IS NOT NULL AND local_embedding IS NULL) "
            "OR (embedding_profile = 'local' AND embedding IS NULL AND local_embedding IS NOT NULL)",
            name="ck_document_chunks_embedding_profile",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    chunk_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    page_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True
    )

    # Mapped to the DB column "metadata"; the attribute is renamed to
    # avoid colliding with SQLAlchemy's reserved ``Base.metadata``.
    chunk_metadata: Mapped[dict] = mapped_column(
        "metadata",
        JSONB,
        nullable=False,
        default=dict,
        server_default=text("'{}'::jsonb")
    )

    embedding_profile: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="openai",
        server_default="openai",
        index=True,
    )

    # Existing OpenAI profile, retained at its original 1536 dimensions.
    embedding: Mapped[list[float] | None] = mapped_column(
        Vector(settings.RAG_EMBEDDING_DIMENSION),
        nullable=True
    )

    # Local all-MiniLM-L6-v2 profile. Never compared with the OpenAI column.
    local_embedding: Mapped[list[float] | None] = mapped_column(
        Vector(settings.RAG_LOCAL_EMBEDDING_DIMENSION),
        nullable=True,
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    document = relationship(
        "Document",
        back_populates="chunks"
    )
