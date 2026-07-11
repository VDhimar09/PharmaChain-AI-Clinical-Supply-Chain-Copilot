"""create audit logs

Revision ID: 20260711_1400
Revises:
Create Date: 2026-07-11 14:00:00
"""

from typing import Sequence
from typing import Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "20260711_1400"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "audit_logs",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        sa.Column(
            "user_email",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "action",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "resource_type",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "resource_id",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "http_method",
            sa.String(length=10),
            nullable=False,
        ),
        sa.Column(
            "endpoint",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "status_code",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "ip_address",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "user_agent",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "details",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_audit_logs_action"),
        "audit_logs",
        ["action"],
        unique=False,
    )
    op.create_index(
        op.f("ix_audit_logs_resource_id"),
        "audit_logs",
        ["resource_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_audit_logs_resource_type"),
        "audit_logs",
        ["resource_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_audit_logs_user_email"),
        "audit_logs",
        ["user_email"],
        unique=False,
    )
    op.create_index(
        op.f("ix_audit_logs_user_id"),
        "audit_logs",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_audit_logs_user_id"),
        table_name="audit_logs",
    )
    op.drop_index(
        op.f("ix_audit_logs_user_email"),
        table_name="audit_logs",
    )
    op.drop_index(
        op.f("ix_audit_logs_resource_type"),
        table_name="audit_logs",
    )
    op.drop_index(
        op.f("ix_audit_logs_resource_id"),
        table_name="audit_logs",
    )
    op.drop_index(
        op.f("ix_audit_logs_action"),
        table_name="audit_logs",
    )
    op.drop_table("audit_logs")
