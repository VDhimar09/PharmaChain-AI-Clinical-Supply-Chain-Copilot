import uuid

from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy import Float

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base


class Supplier(Base):

    __tablename__ = "suppliers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    country: Mapped[str] = mapped_column(
        String(100)
    )

    contact_person: Mapped[str] = mapped_column(
        String(255)
    )

    email: Mapped[str] = mapped_column(
        String(255)
    )

    phone: Mapped[str] = mapped_column(
        String(50)
    )

    lead_time_days: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    reliability_score: Mapped[float] = mapped_column(
        Float,
        default=0.0
    )

    products = relationship(
        "Product",
        back_populates="supplier"
    )

    shipments = relationship(
        "Shipment",
        back_populates="supplier"
    )