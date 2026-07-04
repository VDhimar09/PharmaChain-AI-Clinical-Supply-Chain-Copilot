export type InventoryItem = {
  id: string;
  name: string;
  sku: string;
  category: "Vaccine" | "Medicine" | "Clinical Trial";
  temperature: string;
  available: number;
  reserved: number;
  expiry: string;
  status: "In Stock" | "Low Stock" | "Critical" | "Expiring Soon";
};

export const inventory: InventoryItem[] = [
  { id: "1", name: "Pfizer COVID-19 Vaccine", sku: "VAC-PFZ-001", category: "Vaccine", temperature: "-70°C", available: 12400, reserved: 3200, expiry: "2026-09-15", status: "In Stock" },
  { id: "2", name: "Moderna mRNA-1273", sku: "VAC-MOD-002", category: "Vaccine", temperature: "-20°C", available: 8200, reserved: 1500, expiry: "2026-08-12", status: "In Stock" },
  { id: "3", name: "Insulin Glargine", sku: "MED-INS-014", category: "Medicine", temperature: "2-8°C", available: 540, reserved: 200, expiry: "2026-07-30", status: "Low Stock" },
  { id: "4", name: "Trial Compound X-117", sku: "CLT-X117-009", category: "Clinical Trial", temperature: "-80°C", available: 320, reserved: 320, expiry: "2026-12-01", status: "In Stock" },
  { id: "5", name: "Amoxicillin 500mg", sku: "MED-AMX-022", category: "Medicine", temperature: "Ambient", available: 18450, reserved: 2300, expiry: "2027-03-22", status: "In Stock" },
  { id: "6", name: "Influenza Quadrivalent", sku: "VAC-INF-031", category: "Vaccine", temperature: "2-8°C", available: 95, reserved: 80, expiry: "2026-07-05", status: "Critical" },
  { id: "7", name: "Oncology Trial OXC-44", sku: "CLT-OXC-044", category: "Clinical Trial", temperature: "-20°C", available: 210, reserved: 90, expiry: "2026-07-18", status: "Expiring Soon" },
  { id: "8", name: "Heparin Sodium", sku: "MED-HEP-007", category: "Medicine", temperature: "2-8°C", available: 1820, reserved: 420, expiry: "2027-01-10", status: "In Stock" },
  { id: "9", name: "HPV Gardasil 9", sku: "VAC-HPV-019", category: "Vaccine", temperature: "2-8°C", available: 670, reserved: 250, expiry: "2026-11-04", status: "In Stock" },
  { id: "10", name: "Trial Biologic BIO-22", sku: "CLT-BIO-022", category: "Clinical Trial", temperature: "-70°C", available: 48, reserved: 40, expiry: "2026-08-28", status: "Critical" },
  { id: "11", name: "Paracetamol IV", sku: "MED-PCM-051", category: "Medicine", temperature: "Ambient", available: 9300, reserved: 800, expiry: "2027-06-15", status: "In Stock" },
  { id: "12", name: "MMR Vaccine", sku: "VAC-MMR-027", category: "Vaccine", temperature: "2-8°C", available: 410, reserved: 110, expiry: "2026-10-19", status: "Low Stock" },
];

export type Zone = {
  id: string;
  name: string;
  temperature: string;
  capacity: number;
  occupied: number;
  forecast: number;
};

export const zones: Zone[] = [
  { id: "csa", name: "Cold Storage A", temperature: "2-8°C", capacity: 1200, occupied: 864, forecast: 920 },
  { id: "csb", name: "Cold Storage B", temperature: "2-8°C", capacity: 1500, occupied: 1080, forecast: 1260 },
  { id: "amb", name: "Ambient Storage", temperature: "15-25°C", capacity: 2400, occupied: 1560, forecast: 1700 },
  { id: "frz", name: "Frozen Storage", temperature: "-20°C / -70°C", capacity: 800, occupied: 612, forecast: 700 },
];

export type Shipment = {
  id: string;
  supplier: string;
  product: string;
  quantity: number;
  arrival: string;
  status: "In Transit" | "Delivered" | "Delayed" | "Processing";
};

export const shipments: Shipment[] = [
  { id: "SHP-10231", supplier: "Pfizer Global Logistics", product: "Pfizer COVID-19 Vaccine", quantity: 2400, arrival: "2026-06-18", status: "In Transit" },
  { id: "SHP-10232", supplier: "Moderna Distribution", product: "Moderna mRNA-1273", quantity: 1800, arrival: "2026-06-17", status: "Processing" },
  { id: "SHP-10233", supplier: "Sanofi Pharma", product: "Influenza Quadrivalent", quantity: 950, arrival: "2026-06-16", status: "Delivered" },
  { id: "SHP-10234", supplier: "Merck Logistics", product: "HPV Gardasil 9", quantity: 600, arrival: "2026-06-20", status: "In Transit" },
  { id: "SHP-10235", supplier: "Roche Clinical", product: "Trial Compound X-117", quantity: 120, arrival: "2026-06-19", status: "Delayed" },
  { id: "SHP-10236", supplier: "Novartis Supply Co", product: "Insulin Glargine", quantity: 800, arrival: "2026-06-22", status: "In Transit" },
  { id: "SHP-10237", supplier: "GSK Distribution", product: "Amoxicillin 500mg", quantity: 5000, arrival: "2026-06-15", status: "Delivered" },
  { id: "SHP-10238", supplier: "Bayer Pharma", product: "Heparin Sodium", quantity: 1100, arrival: "2026-06-21", status: "Processing" },
  { id: "SHP-10239", supplier: "AstraZeneca Logistics", product: "Oncology Trial OXC-44", quantity: 90, arrival: "2026-06-23", status: "Delayed" },
];

export const inventoryTrend = [
  { month: "Jan", inventory: 38200, demand: 31200 },
  { month: "Feb", inventory: 41100, demand: 33500 },
  { month: "Mar", inventory: 39800, demand: 36100 },
  { month: "Apr", inventory: 43500, demand: 38400 },
  { month: "May", inventory: 45200, demand: 40100 },
  { month: "Jun", inventory: 47800, demand: 42500 },
];

export const occupancyTrend = zones.map(z => ({
  zone: z.name.replace("Storage ", ""),
  occupied: Math.round((z.occupied / z.capacity) * 100),
  forecast: Math.round((z.forecast / z.capacity) * 100),
}));
