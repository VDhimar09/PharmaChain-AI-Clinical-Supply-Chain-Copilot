import uuid
from datetime import datetime

from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Float
from sqlalchemy import Text
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base


class ProcurementRequest(Base):

    __tablename__ = "procurement_requests"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id")
    )

    requested_quantity: Mapped[int] = mapped_column(
        Integer
    )

    priority: Mapped[str] = mapped_column(
        String(20)
    )

    status: Mapped[str] = mapped_column(
        String(50)
    )

    ai_recommendation: Mapped[str] = mapped_column(
        String(20),
        nullable=True
    )

    ai_confidence: Mapped[float] = mapped_column(
        Float,
        nullable=True
    )

    ai_reasoning: Mapped[str] = mapped_column(
        Text,
        nullable=True
    )

    created_by: Mapped[str] = mapped_column(
        String(255)
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    approved_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=True
    )

    product = relationship(
        "Product",
        back_populates="procurement_requests"
    )