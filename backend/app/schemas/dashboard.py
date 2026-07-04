from pydantic import BaseModel


class DashboardSummary(BaseModel):
    """
    Operational dashboard statistics aggregating KPIs from multiple services.
    
    Inventory metrics:
    - total_inventory_units: Total quantity across all inventory items
    - available_inventory_units: Available (non-reserved) quantity
    - reserved_inventory_units: Quantity reserved for pending orders
    - low_stock_products: Count of products below safety stock
    
    Warehouse metrics:
    - warehouse_occupancy: Percentage of warehouse capacity in use (0-100)
    - warehouse_available_capacity: Available capacity units
    
    Shipment metrics:
    - incoming_shipments: Count of inbound shipments (INBOUND type)
    - outgoing_shipments: Count of outbound shipments (OUTBOUND type)
    - delayed_shipments: Count of shipments with Delayed status
    
    Procurement metrics:
    - procurement_requests: Total count of all procurement requests
    """
    
    total_inventory_units: int
    available_inventory_units: int
    reserved_inventory_units: int
    low_stock_products: int
    warehouse_occupancy: float
    warehouse_available_capacity: int
    incoming_shipments: int
    outgoing_shipments: int
    delayed_shipments: int
    procurement_requests: int