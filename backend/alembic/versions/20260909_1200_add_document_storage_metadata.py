"""add document storage backend metadata

Revision ID: 20260909_1200
Revises: 20260819_1100
Create Date: 2026-09-09 12:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260909_1200"
down_revision = "20260819_1100"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "documents",
        sa.Column("storage_backend", sa.String(length=20), server_default="local", nullable=True),
    )
    op.add_column(
        "documents",
        sa.Column("storage_key", sa.String(length=512), nullable=True),
    )
    # Existing rows were stored beneath RAG_STORAGE_DIR using filename.
    op.execute("UPDATE documents SET storage_backend = 'local' WHERE storage_backend IS NULL")
    op.execute("UPDATE documents SET storage_key = filename WHERE storage_key IS NULL")
    op.alter_column("documents", "storage_backend", nullable=False, server_default="local")
    op.alter_column("documents", "storage_key", nullable=False)


def downgrade() -> None:
    op.drop_column("documents", "storage_key")
    op.drop_column("documents", "storage_backend")
