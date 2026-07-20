import logging
from datetime import date, timedelta
from typing import Any

from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.supplier import Supplier
from app.models.warehouse_zone import WarehouseZone
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.supplier_repository import SupplierRepository
from app.repositories.warehouse_zone_repository import (
    WarehouseZoneRepository,
)
from app.schemas.inventory import InventoryCreate
from app.schemas.product import ProductCreate
from app.schemas.supplier import SupplierCreate
from app.schemas.warehouse_zone import WarehouseZoneCreate
from app.services.inventory_service import InventoryService
from app.services.product_service import ProductService
from app.services.supplier_service import SupplierService
from app.services.warehouse_zone_service import (
    WarehouseZoneService,
)


logger = logging.getLogger(__name__)


class SeedDataService:

    @staticmethod
    def seed_demo_data(db: Session) -> dict[str, Any]:
        if SeedDataService._business_data_exists(db):
            summary = SeedDataService._build_summary(
                inserted_suppliers=0,
                inserted_products=0,
                inserted_warehouse_zones=0,
                inserted_inventory=0,
                skipped=True,
            )
            logger.info(
                "SeedDataService skipped business data seeding because "
                "existing data was detected: %s",
                summary,
            )
            return summary

        suppliers = SeedDataService._seed_suppliers(db)
        products = SeedDataService._seed_products(db, suppliers)
        warehouse_zones = SeedDataService._seed_warehouse_zones(db)
        inserted_inventory = SeedDataService._seed_inventory(
            db,
            products,
            warehouse_zones,
        )

        summary = SeedDataService._build_summary(
            inserted_suppliers=len(suppliers),
            inserted_products=len(products),
            inserted_warehouse_zones=len(warehouse_zones),
            inserted_inventory=inserted_inventory,
            skipped=False,
        )
        logger.info("SeedDataService inserted demo business data: %s", summary)
        return summary

    @staticmethod
    def _business_data_exists(db: Session) -> bool:
        return any(
            (
                SupplierRepository.has_any(db),
                ProductRepository.has_any(db),
                WarehouseZoneRepository.has_any(db),
                InventoryRepository.has_any(db),
            )
        )

    @staticmethod
    def _seed_suppliers(db: Session) -> dict[str, Supplier]:
        suppliers_by_name: dict[str, Supplier] = {}

        for supplier_data in SeedDataService._supplier_payloads():
            supplier = SupplierService.create_supplier(
                db,
                supplier_data,
            )
            suppliers_by_name[supplier.name] = supplier

        return suppliers_by_name

    @staticmethod
    def _seed_products(
        db: Session,
        suppliers_by_name: dict[str, Supplier],
    ) -> dict[str, Product]:
        products_by_sku: dict[str, Product] = {}

        for product_data in SeedDataService._product_payloads(suppliers_by_name):
            product = ProductService.create_product(
                db,
                product_data,
            )
            products_by_sku[product.sku] = product

        return products_by_sku

    @staticmethod
    def _seed_warehouse_zones(
        db: Session,
    ) -> dict[str, WarehouseZone]:
        zones_by_name: dict[str, WarehouseZone] = {}

        for zone_data in SeedDataService._warehouse_zone_payloads():
            zone = WarehouseZoneService.create_zone(
                db,
                zone_data,
            )
            zones_by_name[zone.name] = zone

        return zones_by_name

    @staticmethod
    def _seed_inventory(
        db: Session,
        products_by_sku: dict[str, Product],
        zones_by_name: dict[str, WarehouseZone],
    ) -> int:
        inserted_count = 0

        for inventory_data in SeedDataService._inventory_payloads(
            products_by_sku,
            zones_by_name,
        ):
            InventoryService.create_inventory(
                db,
                inventory_data,
            )
            inserted_count += 1

        return inserted_count

    @staticmethod
    def _supplier_payloads() -> list[SupplierCreate]:
        return [
            SupplierCreate(
                name="Pfizer",
                country="United States",
                contact_person="Laura Bennett",
                email="laura.bennett@pfizer-demo.com",
                phone="+1-212-555-0148",
                lead_time_days=5,
                reliability_score=0.98,
            ),
            SupplierCreate(
                name="Moderna",
                country="United States",
                contact_person="Daniel Foster",
                email="daniel.foster@moderna-demo.com",
                phone="+1-617-555-0186",
                lead_time_days=6,
                reliability_score=0.97,
            ),
            SupplierCreate(
                name="AstraZeneca",
                country="United Kingdom",
                contact_person="Hannah Clarke",
                email="hannah.clarke@astrazeneca-demo.com",
                phone="+44-20-5550-0182",
                lead_time_days=8,
                reliability_score=0.95,
            ),
            SupplierCreate(
                name="Roche",
                country="Switzerland",
                contact_person="Marc Dubois",
                email="marc.dubois@roche-demo.com",
                phone="+41-61-555-0114",
                lead_time_days=9,
                reliability_score=0.96,
            ),
            SupplierCreate(
                name="Novartis",
                country="Switzerland",
                contact_person="Sophie Keller",
                email="sophie.keller@novartis-demo.com",
                phone="+41-61-555-0173",
                lead_time_days=7,
                reliability_score=0.94,
            ),
        ]

    @staticmethod
    def _product_payloads(
        suppliers_by_name: dict[str, Supplier],
    ) -> list[ProductCreate]:
        return [
            ProductCreate(
                sku="VAC-PFZ-001",
                name="COVID Vaccine A",
                category="Vaccine",
                description="mRNA COVID-19 vaccine for frozen cold-chain distribution.",
                dosage_form="Injection",
                unit_of_measure="vials",
                temperature_min=-80.0,
                temperature_max=-60.0,
                shelf_life_days=270,
                safety_stock=1200,
                supplier_id=suppliers_by_name["Pfizer"].id,
            ),
            ProductCreate(
                sku="VAC-MOD-002",
                name="COVID Vaccine B",
                category="Vaccine",
                description="mRNA COVID-19 vaccine for standard frozen storage and site replenishment.",
                dosage_form="Injection",
                unit_of_measure="vials",
                temperature_min=-25.0,
                temperature_max=-15.0,
                shelf_life_days=240,
                safety_stock=900,
                supplier_id=suppliers_by_name["Moderna"].id,
            ),
            ProductCreate(
                sku="VAC-AZ-014",
                name="Influenza Quadrivalent",
                category="Vaccine",
                description="Seasonal influenza vaccine maintained in refrigerated cold-chain lanes.",
                dosage_form="Prefilled syringe",
                unit_of_measure="syringes",
                temperature_min=2.0,
                temperature_max=8.0,
                shelf_life_days=365,
                safety_stock=600,
                supplier_id=suppliers_by_name["AstraZeneca"].id,
            ),
            ProductCreate(
                sku="MED-NOV-031",
                name="Insulin Glargine",
                category="Medicine",
                description="Long-acting insulin for controlled refrigerated distribution.",
                dosage_form="Cartridge",
                unit_of_measure="pens",
                temperature_min=2.0,
                temperature_max=8.0,
                shelf_life_days=730,
                safety_stock=450,
                supplier_id=suppliers_by_name["Novartis"].id,
            ),
            ProductCreate(
                sku="CLT-ROC-022",
                name="Trial Biologic BIO-22",
                category="Clinical Trial",
                description="Investigational biologic requiring ultra-low storage for phase II trial kits.",
                dosage_form="Lyophilised vial",
                unit_of_measure="kits",
                temperature_min=-80.0,
                temperature_max=-60.0,
                shelf_life_days=180,
                safety_stock=150,
                supplier_id=suppliers_by_name["Roche"].id,
            ),
        ]

    @staticmethod
    def _warehouse_zone_payloads() -> list[WarehouseZoneCreate]:
        return [
            WarehouseZoneCreate(
                name="Cold Storage A",
                zone_type="Cold Chain",
                capacity_units=1800,
                occupied_units=1120,
                temperature_min=2.0,
                temperature_max=8.0,
            ),
            WarehouseZoneCreate(
                name="Cold Storage B",
                zone_type="Cold Chain",
                capacity_units=2200,
                occupied_units=1580,
                temperature_min=-80.0,
                temperature_max=-60.0,
            ),
            WarehouseZoneCreate(
                name="Ambient Storage",
                zone_type="Ambient",
                capacity_units=2600,
                occupied_units=720,
                temperature_min=15.0,
                temperature_max=25.0,
            ),
            WarehouseZoneCreate(
                name="Controlled Drugs",
                zone_type="Secure",
                capacity_units=900,
                occupied_units=260,
                temperature_min=-25.0,
                temperature_max=-15.0,
            ),
            WarehouseZoneCreate(
                name="Receiving",
                zone_type="Inbound",
                capacity_units=700,
                occupied_units=140,
                temperature_min=2.0,
                temperature_max=8.0,
            ),
            WarehouseZoneCreate(
                name="Dispatch",
                zone_type="Outbound",
                capacity_units=700,
                occupied_units=110,
                temperature_min=2.0,
                temperature_max=8.0,
            ),
        ]

    @staticmethod
    def _inventory_payloads(
        products_by_sku: dict[str, Product],
        zones_by_name: dict[str, WarehouseZone],
    ) -> list[InventoryCreate]:
        today = date.today()

        return [
            InventoryCreate(
                product_id=products_by_sku["VAC-PFZ-001"].id,
                zone_id=zones_by_name["Cold Storage B"].id,
                batch_number="PFZ-26A-001",
                quantity=2400,
                reserved_quantity=420,
                available_quantity=1980,
                expiry_date=today + timedelta(days=180),
            ),
            InventoryCreate(
                product_id=products_by_sku["VAC-AZ-014"].id,
                zone_id=zones_by_name["Dispatch"].id,
                batch_number="AZ-26Q-109",
                quantity=360,
                reserved_quantity=360,
                available_quantity=0,
                expiry_date=today + timedelta(days=165),
            ),
            InventoryCreate(
                product_id=products_by_sku["VAC-MOD-002"].id,
                zone_id=zones_by_name["Controlled Drugs"].id,
                batch_number="MOD-26B-014",
                quantity=1850,
                reserved_quantity=240,
                available_quantity=1610,
                expiry_date=today + timedelta(days=150),
            ),
            InventoryCreate(
                product_id=products_by_sku["VAC-AZ-014"].id,
                zone_id=zones_by_name["Cold Storage A"].id,
                batch_number="AZ-26Q-102",
                quantity=980,
                reserved_quantity=180,
                available_quantity=800,
                expiry_date=today + timedelta(days=120),
            ),
            InventoryCreate(
                product_id=products_by_sku["MED-NOV-031"].id,
                zone_id=zones_by_name["Cold Storage A"].id,
                batch_number="NOV-IG-2611",
                quantity=620,
                reserved_quantity=110,
                available_quantity=510,
                expiry_date=today + timedelta(days=320),
            ),
            InventoryCreate(
                product_id=products_by_sku["CLT-ROC-022"].id,
                zone_id=zones_by_name["Cold Storage B"].id,
                batch_number="ROC-BIO22-071",
                quantity=210,
                reserved_quantity=64,
                available_quantity=146,
                expiry_date=today + timedelta(days=75),
            ),
            InventoryCreate(
                product_id=products_by_sku["VAC-AZ-014"].id,
                zone_id=zones_by_name["Receiving"].id,
                batch_number="AZ-26Q-110",
                quantity=300,
                reserved_quantity=0,
                available_quantity=300,
                expiry_date=today + timedelta(days=210),
            ),
        ]

    @staticmethod
    def _build_summary(
        *,
        inserted_suppliers: int,
        inserted_products: int,
        inserted_warehouse_zones: int,
        inserted_inventory: int,
        skipped: bool,
    ) -> dict[str, Any]:
        return {
            "seeded": not skipped,
            "skipped": skipped,
            "inserted_suppliers": inserted_suppliers,
            "inserted_products": inserted_products,
            "inserted_warehouse_zones": inserted_warehouse_zones,
            "inserted_inventory": inserted_inventory,
        }
