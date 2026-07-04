import uuid

from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy import Float
from sqlalchemy import Text
from sqlalchemy import ForeignKey

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base


class Product(Base):

    __tablename__ = "products"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    sku: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    category: Mapped[str] = mapped_column(
        String(100)
    )

    description: Mapped[str] = mapped_column(
        Text
    )

    dosage_form: Mapped[str] = mapped_column(
        String(100)
    )

    unit_of_measure: Mapped[str] = mapped_column(
        String(50)
    )

    temperature_min: Mapped[float] = mapped_column(
        Float
    )

    temperature_max: Mapped[float] = mapped_column(
        Float
    )

    shelf_life_days: Mapped[int] = mapped_column(
        Integer
    )

    safety_stock: Mapped[int] = mapped_column(
        Integer
    )

    supplier_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("suppliers.id")
    )

    supplier = relationship(
        "Supplier",
        back_populates="products"
    )

    inventory = relationship(
        "Inventory",
        back_populates="product"
    )

    shipments = relationship(
        "Shipment",
        back_populates="product"
    )

    procurement_requests = relationship(
        "ProcurementRequest",
        back_populates="product"
    )

    inventory = relationship(
    "Inventory",
    back_populates="product"
)
    
    procurement_requests = relationship(
    "ProcurementRequest",
    back_populates="product"
)
    
    shipments = relationship(
    "Shipment",
    back_populates="product"
)