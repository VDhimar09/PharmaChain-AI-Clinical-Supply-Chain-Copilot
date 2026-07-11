"""create system events

Revision ID: 20260711_1500
Revises: 20260711_1400
Create Date: 2026-07-11 15:00:00
"""

from typing import Sequence
from typing import Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "20260711_1500"
down_revision: Union[str, None] = "20260711_1400"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "system_events",
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
            "event_type",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "severity",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "source",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "payload",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "processed",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_system_events_event_type"),
        "system_events",
        ["event_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_system_events_severity"),
        "system_events",
        ["severity"],
        unique=False,
    )
    op.create_index(
        op.f("ix_system_events_source"),
        "system_events",
        ["source"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_system_events_source"),
        table_name="system_events",
    )
    op.drop_index(
        op.f("ix_system_events_severity"),
        table_name="system_events",
    )
    op.drop_index(
        op.f("ix_system_events_event_type"),
        table_name="system_events",
    )
    op.drop_table("system_events")
