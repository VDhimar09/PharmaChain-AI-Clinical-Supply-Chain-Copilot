import uuid
from datetime import datetime

from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base


class Shipment(Base):

    __tablename__ = "shipments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    shipment_number: Mapped[str] = mapped_column(
        String(100),
        unique=True
    )

    shipment_type: Mapped[str] = mapped_column(
        String(20)
    )
    # INBOUND / OUTBOUND

    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id")
    )

    supplier_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("suppliers.id")
    )

    quantity: Mapped[int] = mapped_column(
        Integer
    )

    status: Mapped[str] = mapped_column(
        String(50)
    )

    expected_arrival: Mapped[datetime] = mapped_column(
        DateTime
    )

    actual_arrival: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=True
    )

    product = relationship(
        "Product",
        back_populates="shipments"
    )

    supplier = relationship(
        "Supplier",
        back_populates="shipments"
    )

    @property
    def product_name(self) -> str:
        return self.product.name if self.product is not None else ""

    @property
    def supplier_name(self) -> str:
        return self.supplier.name if self.supplier is not None else ""
