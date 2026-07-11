import uuid

from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import func
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.models.base import Base


class AuditLog(Base):

    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
        index=True
    )

    user_email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True
    )

    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )

    resource_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )

    resource_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True
    )

    http_method: Mapped[str] = mapped_column(
        String(10),
        nullable=False
    )

    endpoint: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    status_code: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    ip_address: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    user_agent: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    details: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default=text("'{}'::jsonb")
    )

    user = relationship(
        "User",
        back_populates="audit_logs"
    )
