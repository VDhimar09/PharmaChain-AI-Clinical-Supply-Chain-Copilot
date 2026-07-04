from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.ai.tools.inventory_tool import InventoryTool
from app.ai.tools.warehouse_tool import WarehouseTool
from app.ai.tools.shipment_tool import ShipmentTool

router = APIRouter(
    prefix="/api/ai",
    tags=["AI Copilot"]
)

inventory_tool = InventoryTool()
warehouse_tool = WarehouseTool()
shipment_tool = ShipmentTool()


@router.get("/inventory-summary")
def inventory_summary(
    db: Session = Depends(get_db)
):
    return inventory_tool.get_inventory_summary(db)


@router.get("/low-stock")
def low_stock(
    db: Session = Depends(get_db)
):
    return inventory_tool.get_low_stock_products(db)


@router.get("/expiring")
def expiring_products(
    db: Session = Depends(get_db)
):
    return inventory_tool.get_expiring_products(db)


@router.get("/warehouse-capacity")
def warehouse_capacity(
    db: Session = Depends(get_db)
):
    return warehouse_tool.get_capacity_summary(db)


@router.get("/shipment-summary")
def shipment_summary(
    db: Session = Depends(get_db)
):
    return shipment_tool.get_shipment_summary(db)