import uuid
from datetime import date, datetime, timedelta

from sqlalchemy import Integer
from sqlalchemy import Date
from sqlalchemy import DateTime
from sqlalchemy import String
from sqlalchemy import ForeignKey

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base


class Inventory(Base):

    __tablename__ = "inventory"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id")
    )

    zone_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("warehouse_zones.id")
    )

    batch_number: Mapped[str] = mapped_column(
        String(100)
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    reserved_quantity: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    available_quantity: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    expiry_date: Mapped[date] = mapped_column(
        Date
    )

    received_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    product = relationship(
        "Product",
        back_populates="inventory"
    )

    zone = relationship(
        "WarehouseZone",
        back_populates="inventory_items"
    )

    @property
    def product_name(self) -> str:
        return self.product.name if self.product is not None else ""

    @property
    def sku(self) -> str:
        return self.product.sku if self.product is not None else ""

    @property
    def category(self) -> str:
        return self.product.category if self.product is not None else ""

    @property
    def temperature_requirement(self) -> str:
        if self.product is None or self.product.temperature_min is None or self.product.temperature_max is None:
            return "N/A"
        if self.product.temperature_min == self.product.temperature_max:
            return f"{self.product.temperature_min}°C"
        return f"{self.product.temperature_min}–{self.product.temperature_max}°C"

    @property
    def warehouse_zone(self) -> str:
        return self.zone.name if self.zone is not None else ""

    @property
    def status(self) -> str:
        if self.available_quantity <= 100:
            return "Critical"

        if self.expiry_date is not None:
            days_to_expiry = (self.expiry_date - date.today()).days
            if days_to_expiry <= 30:
                return "Expiring Soon"

        if self.available_quantity <= 500:
            return "Low Stock"

        return "In Stock"
