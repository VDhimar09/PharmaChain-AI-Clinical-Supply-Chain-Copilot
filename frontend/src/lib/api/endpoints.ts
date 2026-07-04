import { apiClient } from "./client";

export type ShipmentStatus = "In Transit" | "Delivered" | "Delayed" | "Processing";

export type Shipment = {
  id: string;
  shipment_number: string;
  shipment_type: string;
  product_id: string;
  supplier_id: string;
  quantity: number;
  status: ShipmentStatus;
  expected_arrival: string;
  product_name: string;
  supplier_name: string;
};

export const shipmentsApi = {
  list: () => apiClient.get<Shipment[]>("/api/shipments"),
  get: (id: string) => apiClient.get<Shipment>(`/api/shipments/${id}`),
  create: (payload: Omit<Shipment, "id">) => apiClient.post<Shipment>("/api/shipments", payload),
  updateStatus: (id: string, status: ShipmentStatus) => apiClient.patch<Shipment>(`/api/shipments/${id}`, { status }),
};

export type InventoryItem = {
  id: string;
  product_id: string;
  zone_id: string;
  product_name: string;
  sku: string;
  category: string;
  temperature_requirement: string;
  batch_number: string;
  quantity: number;
  available_quantity: number;
  reserved_quantity: number;
  expiry_date: string;
  warehouse_zone: string;
  status: string;
};

export type Product = {
  id: string;
  sku: string;
  name: string;
  category: string;
  temperature_min: number;
  temperature_max: number;
};

export type WarehouseZone = {
  id: string;
  name: string;
  zone_type: string;
  capacity_units: number;
  occupied_units: number;
  temperature_min: number | null;
  temperature_max: number | null;
};

export type WarehouseCapacitySummary = {
  total_capacity: number;
  occupied_capacity: number;
  available_capacity: number;
  occupancy_percentage: number;
};

export const inventoryApi = {
  list: () => apiClient.get<InventoryItem[]>("/api/inventory"),
  get: (id: string) => apiClient.get<InventoryItem>(`/api/inventory/${id}`),
};

export const productsApi = {
  list: () => apiClient.get<Product[]>("/api/products"),
  get: (id: string) => apiClient.get<Product>(`/api/products/${id}`),
};

export const warehouseZonesApi = {
  list: () => apiClient.get<WarehouseZone[]>("/api/warehouse-zones"),
  get: (id: string) => apiClient.get<WarehouseZone>(`/api/warehouse-zones/${id}`),
  capacitySummary: () => apiClient.get<WarehouseCapacitySummary>("/api/warehouse-zones/capacity"),
};

/**
 * Dashboard operational KPIs from backend.
 * Maps to DashboardSummaryResponse in backend.
 */
export type DashboardSummary = {
  total_inventory_units: number;
  available_inventory_units: number;
  reserved_inventory_units: number;
  low_stock_products: number;
  warehouse_occupancy: number;
  warehouse_available_capacity: number;
  incoming_shipments: number;
  outgoing_shipments: number;
  delayed_shipments: number;
  procurement_requests: number;
};

export const dashboardApi = {
  getSummary: () => apiClient.get<DashboardSummary>("/api/dashboard/summary"),
};
