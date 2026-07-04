from sqlalchemy.orm import Session
from sqlalchemy import String
from sqlalchemy import cast
from sqlalchemy import func
from sqlalchemy import or_

from app.models.product import Product
from app.models.inventory import Inventory
from app.models.shipment import Shipment
from app.models.warehouse_zone import WarehouseZone


class ProcurementRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_product(self, product_name: str):
        normalized_name = product_name.strip()

        return (
            self.db.query(Product)
            .filter(
                or_(
                    func.lower(Product.name) ==
                    normalized_name.lower(),
                    func.lower(Product.sku) ==
                    normalized_name.lower(),
                    cast(Product.id, String) ==
                    normalized_name
                )
            )
            .first()
        )

    def get_inventory(self, product_id: int):

        return (
            self.db.query(Inventory)
            .filter(
                Inventory.product_id == product_id
            )
            .first()
        )

    def get_zone(self, zone_id: int):

        return (
            self.db.query(WarehouseZone)
            .filter(
                WarehouseZone.id == zone_id
            )
            .first()
        )

    def get_compatible_zone(
        self,
        temperature_min: float,
        temperature_max: float
    ):

        return (
            self.db.query(WarehouseZone)
            .filter(
                WarehouseZone.temperature_min <=
                temperature_min,
                WarehouseZone.temperature_max >=
                temperature_max,
                WarehouseZone.capacity_units > 0
            )
            .order_by(
                WarehouseZone.occupied_units.asc()
            )
            .first()
        )

    def get_incoming_shipments(self):

        return (
            self.db.query(Shipment)
            .filter(
                Shipment.status == "INCOMING"
            )
            .all()
        )
