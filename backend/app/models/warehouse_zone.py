import uuid

from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy import Float

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base


class WarehouseZone(Base):

    __tablename__ = "warehouse_zones"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    zone_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    temperature_min: Mapped[float] = mapped_column(
        Float
    )

    temperature_max: Mapped[float] = mapped_column(
        Float
    )

    capacity_units: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    occupied_units: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    inventory_items = relationship(
        "Inventory",
        back_populates="zone"
    )