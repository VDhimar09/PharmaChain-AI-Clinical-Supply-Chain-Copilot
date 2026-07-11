import { apiClient } from "./client";
import type { AuthenticatedUser } from "@/lib/auth/token-storage";

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
  description: string;
  dosage_form: string;
  unit_of_measure: string;
  temperature_min: number;
  temperature_max: number;
  shelf_life_days: number;
  safety_stock: number;
  supplier_id: string;
};

export type Supplier = {
  id: string;
  name: string;
  country: string;
  contact_person: string;
  email: string;
  phone: string;
  lead_time_days: number;
  reliability_score: number;
};

export type ProcurementAIRequest = {
  product_name: string;
  pallet_quantity: number;
  month: string;
};

export type ProcurementAIResponse = {
  decision: "APPROVE" | "REJECT" | "REVIEW";
  confidence: number;
  reasoning: string[];
  inventory_units: number;
  risk_level: "LOW" | "MEDIUM" | "HIGH";
  recommended_zone: string;
  temperature_fit: "MATCH" | "MISMATCH";
  badges: string[];
  current_occupancy_percent: number;
  projected_occupancy_percent: number;
};

export type ProcurementAnalysisRequest = {
  product_id: string;
  supplier_id: string;
  requested_quantity: number;
};

export type ProcurementToolExecution = {
  tool: string;
  status: "SUCCESS" | "FAILED";
};

export type ProcurementReasoningStep = {
  step: string;
  status: "PASS" | "ATTENTION" | "FAIL";
  message: string;
};

export type ProcurementRequestDetails = {
  product_id: string;
  product_name: string;
  supplier_id: string;
  supplier_name: string;
  requested_quantity: number;
  temperature_min: number;
  temperature_max: number;
  safety_stock: number;
  shelf_life_days: number;
};

export type ProcurementInventoryEvidence = {
  available_units: number;
  requested_quantity: number;
  safety_stock: number;
  below_safety_stock: boolean;
};

export type ProcurementWarehouseEvidence = {
  recommended_zone: string;
  current_occupancy_percent: number;
  projected_occupancy_percent: number;
  available_capacity_units: number;
};

export type ProcurementShipmentEvidence = {
  incoming_shipments: number;
  incoming_units: number;
  conflict_detected: boolean;
};

export type ProcurementSupplierEvidence = {
  supplier_name: string;
  reliability_score: number;
  lead_time_days: number;
};

export type ProcurementColdChainEvidence = {
  compatible: boolean;
  temperature_min: number;
  temperature_max: number;
  zone_name: string;
};

export type ProcurementDecisionEvidence = {
  demand_forecast: string;
  shelf_life_valid: boolean;
  shelf_life_days: number;
};

export type ProcurementEvidenceBundle = {
  inventory: ProcurementInventoryEvidence;
  warehouse: ProcurementWarehouseEvidence;
  shipments: ProcurementShipmentEvidence;
  supplier: ProcurementSupplierEvidence;
  cold_chain: ProcurementColdChainEvidence;
  procurement: ProcurementDecisionEvidence;
};

export type ProcurementAnalysisResponse = {
  request_details: ProcurementRequestDetails;
  decision: "APPROVE" | "REJECT" | "REVIEW";
  confidence: number;
  tool_execution: ProcurementToolExecution[];
  reasoning: ProcurementReasoningStep[];
  evidence: ProcurementEvidenceBundle;
  recommendation: string;
  summary: string;
  explanation: string;
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

export const suppliersApi = {
  list: () => apiClient.get<Supplier[]>("/api/suppliers"),
};

export const procurementAiApi = {
  evaluate: (payload: ProcurementAIRequest) =>
    apiClient.post<ProcurementAIResponse>("/api/procurement-ai/evaluate", payload),
  analyze: (payload: ProcurementAnalysisRequest) =>
    apiClient.post<ProcurementAnalysisResponse>("/api/ai/procurement/analyze", payload),
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

export type InsightAlert = {
  severity: "LOW" | "MEDIUM" | "HIGH";
  title: string;
  message: string;
};

export type InsightRecommendation = {
  priority: "LOW" | "MEDIUM" | "HIGH";
  title: string;
  message: string;
};

export type InventoryInsightItem = {
  id: string;
  product_name: string;
  sku: string;
  category: string;
  warehouse_zone: string;
  quantity: number;
  available_quantity: number;
  reserved_quantity: number;
  expiry_date: string | null;
  days_to_expiry: number | null;
  status: string;
};

export type WarehouseInsightItem = {
  id: string;
  name: string;
  zone_type: string;
  capacity_units: number;
  occupied_units: number;
  available_capacity: number;
  occupancy_percentage: number;
  temperature_min: number | null;
  temperature_max: number | null;
  status: string;
};

export type ShipmentInsightItem = {
  id: string;
  shipment_number: string;
  shipment_type: string;
  product_name: string;
  supplier_name: string;
  quantity: number;
  status: string;
  expected_arrival: string;
  delay_days: number | null;
};

export type ProcurementInsightItem = {
  id: string;
  product_name: string;
  requested_quantity: number;
  priority: string;
  status: string;
  ai_recommendation: string | null;
  ai_confidence: number | null;
  created_by: string;
  created_at: string;
  approved_at: string | null;
};

export type TrendPoint = {
  label: string;
  value: number;
  secondary_value: number | null;
};

export type AIInsightsResponse = {
  generated_at: string;
  confidence: number;
  executive_summary: {
    inventory_value: number;
    warehouse_utilisation: number;
    pending_procurements: number;
    critical_alerts: number;
  };
  inventory: {
    low_stock: InventoryInsightItem[];
    overstock: InventoryInsightItem[];
    near_expiry: InventoryInsightItem[];
    fast_moving: InventoryInsightItem[];
    slow_moving: InventoryInsightItem[];
  };
  warehouse: {
    occupancy: WarehouseInsightItem[];
    cold_chain: WarehouseInsightItem[];
    available_capacity: WarehouseInsightItem[];
  };
  shipments: {
    incoming: ShipmentInsightItem[];
    outgoing: ShipmentInsightItem[];
    delayed: ShipmentInsightItem[];
  };
  procurement: {
    pending: ProcurementInsightItem[];
    approved: ProcurementInsightItem[];
    rejected: ProcurementInsightItem[];
  };
  alerts: InsightAlert[];
  recommendations: InsightRecommendation[];
  trend_data: {
    inventory: TrendPoint[];
    shipments: TrendPoint[];
    warehouse: TrendPoint[];
  };
};

export const aiInsightsApi = {
  get: () => apiClient.get<AIInsightsResponse>("/api/ai/insights"),
};

export type CopilotChatRequest = {
  message: string;
};

export type CopilotReasoningStep = {
  step: string;
  status: string;
};

export type CopilotToolExecution = {
  tool: string;
  status: string;
  execution_time_ms: number;
};

export type CopilotEvidenceBundle = {
  inventory: Record<string, unknown>;
  warehouse: Record<string, unknown>;
  shipments: Record<string, unknown>;
  procurement: Record<string, unknown>;
  ai_insights: Record<string, unknown>;
};

export type CopilotChatResponse = {
  conversation_id: string;
  generated_at: string;
  intent: string;
  confidence: number;
  tools_used: string[];
  reasoning: CopilotReasoningStep[];
  tool_execution: CopilotToolExecution[];
  evidence: CopilotEvidenceBundle;
  recommendations: string[];
  response: string;
};

export const copilotApi = {
  chat: (payload: CopilotChatRequest) =>
    apiClient.post<CopilotChatResponse>("/api/ai/copilot/chat", payload),
};

export type CurrentUser = AuthenticatedUser;

export type LoginRequest = {
  email: string;
  password: string;
};

export type TokenResponse = {
  access_token: string;
  refresh_token: string;
  token_type: "bearer";
  expires_in: number;
  refresh_expires_in: number;
  user: CurrentUser;
};

export const authApi = {
  login: (payload: LoginRequest) =>
    apiClient.post<TokenResponse>("/api/auth/login", payload),
  refresh: (refreshToken: string) =>
    apiClient.post<TokenResponse>(
      "/api/auth/refresh",
      { refresh_token: refreshToken },
    ),
  logout: (refreshToken: string) =>
    apiClient.post<void>(
      "/api/auth/logout",
      { refresh_token: refreshToken },
    ),
  me: () => apiClient.get<CurrentUser>("/api/auth/me"),
};
