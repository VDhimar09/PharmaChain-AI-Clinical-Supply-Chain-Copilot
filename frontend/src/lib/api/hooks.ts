import { useMutation, useQuery, UseMutationOptions, UseQueryOptions } from "@tanstack/react-query";
import {
  shipmentsApi,
  Shipment,
  ShipmentStatus,
  dashboardApi,
  DashboardSummary,
  inventoryApi,
  InventoryItem,
  productsApi,
  Product,
  warehouseZonesApi,
  WarehouseZone,
  WarehouseCapacitySummary,
} from "./endpoints";

export function useShipments(options?: UseQueryOptions<Shipment[], Error>) {
  return useQuery<Shipment[], Error>({
    queryKey: ["shipments"],
    queryFn: shipmentsApi.list,
    ...options,
  });
}

export function useShipment(id: string, options?: UseQueryOptions<Shipment, Error>) {
  return useQuery<Shipment, Error>({
    queryKey: ["shipment", id],
    queryFn: () => shipmentsApi.get(id),
    enabled: Boolean(id),
    ...options,
  });
}

export function useCreateShipment(
  options?: UseMutationOptions<Shipment, Error, Omit<Shipment, "id">>,
) {
  return useMutation<Shipment, Error, Omit<Shipment, "id">>({
    mutationFn: shipmentsApi.create,
    ...options,
  });
}

export function useUpdateShipmentStatus(
  options?: UseMutationOptions<Shipment, Error, { id: string; status: ShipmentStatus }>,
) {
  return useMutation<Shipment, Error, { id: string; status: ShipmentStatus }>({
    mutationFn: ({ id, status }) => shipmentsApi.updateStatus(id, status),
    ...options,
  });
}

export function useInventory(options?: UseQueryOptions<InventoryItem[], Error>) {
  return useQuery<InventoryItem[], Error>(
    {
      queryKey: ["inventory"],
      queryFn: inventoryApi.list,
      staleTime: 1000 * 60,
      gcTime: 1000 * 60 * 5,
      ...options,
    },
  );
}

export function useProducts(options?: UseQueryOptions<Product[], Error>) {
  return useQuery<Product[], Error>({
    queryKey: ["products"],
    queryFn: productsApi.list,
    staleTime: 1000 * 60,
    gcTime: 1000 * 60 * 5,
    ...options,
  });
}

export function useWarehouseZones(options?: UseQueryOptions<WarehouseZone[], Error>) {
  return useQuery<WarehouseZone[], Error>({
    queryKey: ["warehouse-zones"],
    queryFn: warehouseZonesApi.list,
    staleTime: 1000 * 60,
    gcTime: 1000 * 60 * 5,
    ...options,
  });
}

export function useWarehouseCapacitySummary(options?: UseQueryOptions<WarehouseCapacitySummary, Error>) {
  return useQuery<WarehouseCapacitySummary, Error>({
    queryKey: ["warehouse-zones", "capacity-summary"],
    queryFn: warehouseZonesApi.capacitySummary,
    staleTime: 1000 * 60,
    gcTime: 1000 * 60 * 5,
    ...options,
  });
}

/**
 * Hook to fetch operational dashboard KPIs.
 * Returns real-time inventory, warehouse, shipment, and procurement metrics.
 */
export function useDashboardSummary(options?: UseQueryOptions<DashboardSummary, Error>) {
  return useQuery<DashboardSummary, Error>({
    queryKey: ["dashboard", "summary"],
    queryFn: dashboardApi.getSummary,
    staleTime: 1000 * 60, // Data is fresh for 1 minute
    gcTime: 1000 * 60 * 5, // Keep in cache for 5 minutes
    ...options,
  });
}
