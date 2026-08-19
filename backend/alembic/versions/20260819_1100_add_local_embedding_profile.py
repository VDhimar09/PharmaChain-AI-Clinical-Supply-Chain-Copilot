"""add local embedding profile storage

Revision ID: 20260819_1100
Revises: 20260810_1000
Create Date: 2026-08-19 11:00:00
"""

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


revision = "20260819_1100"
down_revision = "20260810_1000"
branch_labels = None
depends_on = None

LOCAL_DIMENSION = 384


def upgrade() -> None:
    op.add_column(
        "document_chunks",
        sa.Column("embedding_profile", sa.String(length=32), server_default="openai", nullable=True),
    )
    op.add_column(
        "document_chunks",
        sa.Column("local_embedding", Vector(LOCAL_DIMENSION), nullable=True),
    )
    op.execute("UPDATE document_chunks SET embedding_profile = 'openai' WHERE embedding_profile IS NULL")
    op.alter_column("document_chunks", "embedding_profile", nullable=False, server_default="openai")
    op.alter_column("document_chunks", "embedding", existing_type=Vector(1536), nullable=True)
    op.create_index("ix_document_chunks_embedding_profile", "document_chunks", ["embedding_profile"])
    op.create_check_constraint(
        "ck_document_chunks_embedding_profile",
        "document_chunks",
        "(embedding_profile = 'openai' AND embedding IS NOT NULL AND local_embedding IS NULL) "
        "OR (embedding_profile = 'local' AND embedding IS NULL AND local_embedding IS NOT NULL)",
    )
    op.execute(
        "CREATE INDEX ix_document_chunks_local_embedding ON document_chunks "
        "USING ivfflat (local_embedding vector_cosine_ops) WITH (lists = 100) "
        "WHERE embedding_profile = 'local' AND local_embedding IS NOT NULL"
    )


def downgrade() -> None:
    op.execute("DROP INDEX ix_document_chunks_local_embedding")
    op.drop_constraint("ck_document_chunks_embedding_profile", "document_chunks", type_="check")
    op.drop_index("ix_document_chunks_embedding_profile", table_name="document_chunks")
    op.alter_column("document_chunks", "embedding", existing_type=Vector(1536), nullable=False)
    op.drop_column("document_chunks", "local_embedding")
    op.drop_column("document_chunks", "embedding_profile")
