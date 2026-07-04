from sqlalchemy.orm import Session

from app.services.inventory_service import InventoryService
from app.services.warehouse_zone_service import WarehouseZoneService
from app.services.shipment_service import ShipmentService
from app.services.procurement_request_service import ProcurementRequestService


class DashboardService:
    """
    Dashboard aggregation service - acts as an orchestrator for operational KPIs.
    
    Follows Clean Architecture principles:
    - Does NOT perform direct database queries
    - Reuses existing service layer to avoid logic duplication
    - Aggregates results from specialized services into a unified dashboard response
    
    Services leveraged:
    - InventoryService: Inventory statistics (quantities, low stock)
    - WarehouseZoneService: Warehouse capacity and occupancy
    - ShipmentService: Shipment statistics (inbound, outbound, delayed)
    - ProcurementRequestService: Procurement request counts
    """

    @staticmethod
    def get_summary(db: Session):
        """
        Aggregates operational KPIs from all services.
        
        Args:
            db: SQLAlchemy session
            
        Returns:
            Dictionary with operational dashboard metrics
        """
        
        # Fetch statistics from each service
        inventory_stats = InventoryService.get_inventory_statistics(db)
        warehouse_stats = WarehouseZoneService.get_capacity_summary(db)
        shipment_stats = ShipmentService.get_shipment_statistics(db)
        procurement_stats = ProcurementRequestService.get_procurement_statistics(db)
        
        # Aggregate into unified dashboard response
        return {
            # Inventory metrics
            "total_inventory_units": inventory_stats["total_quantity"],
            "available_inventory_units": inventory_stats["total_available_quantity"],
            "reserved_inventory_units": inventory_stats["total_reserved_quantity"],
            "low_stock_products": inventory_stats["low_stock_products"],
            
            # Warehouse metrics
            "warehouse_occupancy": warehouse_stats["occupancy_percentage"],
            "warehouse_available_capacity": warehouse_stats["available_capacity"],
            
            # Shipment metrics
            "incoming_shipments": shipment_stats["inbound_shipments"],
            "outgoing_shipments": shipment_stats["outbound_shipments"],
            "delayed_shipments": shipment_stats["delayed_shipments"],
            
            # Procurement metrics
            "procurement_requests": procurement_stats["total_requests"],
        }