from types import SimpleNamespace
from uuid import uuid4

from app.models.inventory import Inventory
from app.models.product import Product
from app.models.supplier import Supplier
from app.models.warehouse_zone import WarehouseZone
from app.services.seed_data_service import SeedDataService


class FakeQuery:
    def __init__(self, records) -> None:
        self.records = records
        self.criteria: dict[str, object] = {}

    def filter_by(self, **kwargs):
        self.criteria = kwargs
        return self

    def first(self):
        for record in self.records:
            if all(
                getattr(record, key) == value
                for key, value in self.criteria.items()
            ):
                return record
        return None


class FakeSession:
    def __init__(self) -> None:
        self.data = {
            Supplier: [],
            Product: [],
            WarehouseZone: [],
            Inventory: [],
        }

    def query(self, model):
        return FakeQuery(self.data[model])


def _make_supplier(
    *,
    name: str,
    supplier_id,
) -> SimpleNamespace:
    return SimpleNamespace(
        id=supplier_id,
        name=name,
    )


def _make_zone(
    *,
    name: str,
    zone_id,
) -> SimpleNamespace:
    return SimpleNamespace(
        id=zone_id,
        name=name,
    )


def _install_create_stubs(monkeypatch, db: FakeSession) -> None:
    supplier_counter = {"value": len(db.data[Supplier])}
    product_counter = {"value": len(db.data[Product])}
    zone_counter = {"value": len(db.data[WarehouseZone])}
    inventory_counter = {"value": len(db.data[Inventory])}

    def create_supplier(session, supplier_data):
        supplier_counter["value"] += 1
        supplier = _make_supplier(
            name=supplier_data.name,
            supplier_id=uuid4(),
        )
        session.data[Supplier].append(supplier)
        return supplier

    def create_product(session, product_data):
        product_counter["value"] += 1
        product = SimpleNamespace(
            id=uuid4(),
            sku=product_data.sku,
            supplier_id=product_data.supplier_id,
        )
        session.data[Product].append(product)
        return product

    def create_zone(session, zone_data):
        zone_counter["value"] += 1
        zone = _make_zone(
            name=zone_data.name,
            zone_id=uuid4(),
        )
        session.data[WarehouseZone].append(zone)
        return zone

    def create_inventory(session, inventory_data):
        inventory_counter["value"] += 1
        inventory = SimpleNamespace(
            id=uuid4(),
            product_id=inventory_data.product_id,
            zone_id=inventory_data.zone_id,
            batch_number=inventory_data.batch_number,
        )
        session.data[Inventory].append(inventory)
        return inventory

    monkeypatch.setattr(
        "app.services.seed_data_service.SupplierService.create_supplier",
        create_supplier,
    )
    monkeypatch.setattr(
        "app.services.seed_data_service.ProductService.create_product",
        create_product,
    )
    monkeypatch.setattr(
        "app.services.seed_data_service.WarehouseZoneService.create_zone",
        create_zone,
    )
    monkeypatch.setattr(
        "app.services.seed_data_service.InventoryService.create_inventory",
        create_inventory,
    )


def test_seed_demo_data_does_not_skip_when_unrelated_business_data_exists(
    monkeypatch,
) -> None:
    db = FakeSession()
    db.data[Supplier].append(
        _make_supplier(
            name="Unrelated Supplier",
            supplier_id=uuid4(),
        )
    )
    _install_create_stubs(monkeypatch, db)

    summary = SeedDataService.seed_demo_data(db)

    assert summary == {
        "seeded": True,
        "skipped": False,
        "inserted_suppliers": 5,
        "inserted_products": 5,
        "inserted_warehouse_zones": 6,
        "inserted_inventory": 7,
    }
    assert len(db.data[Supplier]) == 6
    assert len(db.data[Product]) == 5
    assert len(db.data[WarehouseZone]) == 6
    assert len(db.data[Inventory]) == 7


def test_seed_demo_data_backfills_missing_demo_records_and_then_skips(
    monkeypatch,
) -> None:
    db = FakeSession()
    db.data[Supplier].append(
        _make_supplier(
            name="Pfizer",
            supplier_id=uuid4(),
        )
    )
    pfizer_id = db.data[Supplier][0].id
    db.data[Product].append(
        SimpleNamespace(
            id=uuid4(),
            sku="VAC-PFZ-001",
            supplier_id=pfizer_id,
        )
    )
    db.data[WarehouseZone].append(
        _make_zone(
            name="Cold Storage B",
            zone_id=uuid4(),
        )
    )
    zone_id = db.data[WarehouseZone][0].id
    product_id = db.data[Product][0].id
    db.data[Inventory].append(
        SimpleNamespace(
            id=uuid4(),
            product_id=product_id,
            zone_id=zone_id,
            batch_number="PFZ-26A-001",
        )
    )
    _install_create_stubs(monkeypatch, db)

    first_summary = SeedDataService.seed_demo_data(db)
    second_summary = SeedDataService.seed_demo_data(db)

    assert first_summary == {
        "seeded": True,
        "skipped": False,
        "inserted_suppliers": 4,
        "inserted_products": 4,
        "inserted_warehouse_zones": 5,
        "inserted_inventory": 6,
    }
    assert second_summary == {
        "seeded": False,
        "skipped": True,
        "inserted_suppliers": 0,
        "inserted_products": 0,
        "inserted_warehouse_zones": 0,
        "inserted_inventory": 0,
    }
    assert len(db.data[Supplier]) == 5
    assert len(db.data[Product]) == 5
    assert len(db.data[WarehouseZone]) == 6
    assert len(db.data[Inventory]) == 7
