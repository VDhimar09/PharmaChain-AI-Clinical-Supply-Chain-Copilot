from datetime import date, datetime
from types import SimpleNamespace
from uuid import uuid4

from app.services.ai_insights_service import AIInsightsService


def _inventory_item(
    *,
    name: str,
    sku: str,
    zone_name: str,
    quantity: int,
    available_quantity: int,
    reserved_quantity: int,
    safety_stock: int,
    expiry_date: date,
):
    return SimpleNamespace(
        id=uuid4(),
        product=SimpleNamespace(safety_stock=safety_stock),
        product_name=name,
        sku=sku,
        category="Vaccine",
        warehouse_zone=zone_name,
        quantity=quantity,
        available_quantity=available_quantity,
        reserved_quantity=reserved_quantity,
        expiry_date=expiry_date,
        received_at=datetime(2026, 7, 1, 10, 0, 0),
        status="Critical" if available_quantity <= 100 else "In Stock",
    )


def _zone(*, name: str, zone_type: str, capacity_units: int, occupied_units: int, temperature_max: float):
    return SimpleNamespace(
        id=uuid4(),
        name=name,
        zone_type=zone_type,
        capacity_units=capacity_units,
        occupied_units=occupied_units,
        temperature_min=2.0,
        temperature_max=temperature_max,
    )


def _shipment(*, shipment_number: str, shipment_type: str, status: str, supplier_name: str):
    return SimpleNamespace(
        id=uuid4(),
        shipment_number=shipment_number,
        shipment_type=shipment_type,
        product_name="Vaccine A",
        supplier_name=supplier_name,
        quantity=400,
        status=status,
        expected_arrival=datetime(2026, 7, 3, 10, 0, 0),
    )


def _procurement_request(*, status: str, quantity: int):
    return SimpleNamespace(
        id=uuid4(),
        product=SimpleNamespace(name="Vaccine A"),
        requested_quantity=quantity,
        priority="HIGH",
        status=status,
        ai_recommendation="APPROVE",
        ai_confidence=92.0,
        created_by="ops@pharmachain.ai",
        created_at=datetime(2026, 7, 5, 9, 0, 0),
        approved_at=None,
    )


def test_ai_insights_service_aggregates_operational_data(monkeypatch):
    inventory_items = [
        _inventory_item(
            name="Vaccine A",
            sku="VAC-001",
            zone_name="Cold Zone B",
            quantity=120,
            available_quantity=80,
            reserved_quantity=30,
            safety_stock=100,
            expiry_date=date(2026, 7, 18),
        ),
        _inventory_item(
            name="Therapy B",
            sku="THR-002",
            zone_name="Ambient Zone A",
            quantity=900,
            available_quantity=850,
            reserved_quantity=0,
            safety_stock=200,
            expiry_date=date(2026, 12, 1),
        ),
    ]
    warehouse_zones = [
        _zone(
            name="Cold Zone B",
            zone_type="COLD_CHAIN",
            capacity_units=1000,
            occupied_units=940,
            temperature_max=8.0,
        ),
        _zone(
            name="Ambient Zone A",
            zone_type="AMBIENT",
            capacity_units=800,
            occupied_units=300,
            temperature_max=25.0,
        ),
    ]
    shipments = [
        _shipment(
            shipment_number="SHP-001",
            shipment_type="INBOUND",
            status="Delayed",
            supplier_name="Pfizer",
        ),
        _shipment(
            shipment_number="SHP-002",
            shipment_type="OUTBOUND",
            status="Delivered",
            supplier_name="Sanofi",
        ),
    ]
    procurement_requests = [
        _procurement_request(status="PENDING", quantity=250),
        _procurement_request(status="PENDING", quantity=125),
        _procurement_request(status="APPROVED", quantity=90),
    ]

    monkeypatch.setattr(
        "app.services.ai_insights_service.InventoryService.get_inventory",
        lambda db: inventory_items,
    )
    monkeypatch.setattr(
        "app.services.ai_insights_service.InventoryService.get_low_stock_products",
        lambda db: [inventory_items[0]],
    )
    monkeypatch.setattr(
        "app.services.ai_insights_service.InventoryService.get_expiring_products",
        lambda db, days=60: [inventory_items[0]],
    )
    monkeypatch.setattr(
        "app.services.ai_insights_service.WarehouseZoneService.get_zones",
        lambda db: warehouse_zones,
    )
    monkeypatch.setattr(
        "app.services.ai_insights_service.ShipmentService.get_shipments",
        lambda db: shipments,
    )
    monkeypatch.setattr(
        "app.services.ai_insights_service.ProcurementRequestService.get_procurement_requests",
        lambda db: procurement_requests,
    )
    monkeypatch.setattr(
        "app.services.ai_insights_service.DashboardService.get_summary",
        lambda db: {
            "total_inventory_units": 1020,
            "warehouse_occupancy": 68,
        },
    )

    service = AIInsightsService(db=object())
    result = service.get_insights()

    assert result.executive_summary.inventory_value == 1020
    assert result.executive_summary.pending_procurements == 2
    assert result.inventory.low_stock[0].product_name == "Vaccine A"
    assert result.warehouse.occupancy[0].occupancy_percentage == 94
    assert result.shipments.delayed[0].shipment_number == "SHP-001"
    assert result.procurement.pending[0].status == "PENDING"
    assert any(alert.title == "Warehouse Capacity Pressure" for alert in result.alerts)
    assert any(
        recommendation.title == "Protect Cold-Chain Capacity"
        for recommendation in result.recommendations
    )
    assert result.trend_data.inventory[0].secondary_value == 930
