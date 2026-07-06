import { Card, CardContent } from "@/components/ui/card";

import type { ProcurementEvidenceBundle } from "@/lib/api/endpoints";

export function EvidencePanel({
  evidence,
}: {
  evidence: ProcurementEvidenceBundle;
}) {
  return (
    <Card>
      <CardContent className="p-5">
        <div className="text-xs uppercase tracking-wider text-muted-foreground font-semibold">
          Evidence collected
        </div>
        <div className="mt-4 grid gap-3 md:grid-cols-2">
          <EvidenceBlock
            title="Inventory"
            rows={[
              ["Available units", String(evidence.inventory.available_units)],
              ["Requested quantity", String(evidence.inventory.requested_quantity)],
              ["Safety stock", String(evidence.inventory.safety_stock)],
              ["Below safety stock", evidence.inventory.below_safety_stock ? "Yes" : "No"],
            ]}
          />
          <EvidenceBlock
            title="Warehouse"
            rows={[
              ["Recommended zone", evidence.warehouse.recommended_zone],
              ["Current occupancy", `${evidence.warehouse.current_occupancy_percent}%`],
              ["Projected occupancy", `${evidence.warehouse.projected_occupancy_percent}%`],
              ["Available capacity", `${evidence.warehouse.available_capacity_units} units`],
            ]}
          />
          <EvidenceBlock
            title="Shipments"
            rows={[
              ["Incoming shipments", String(evidence.shipments.incoming_shipments)],
              ["Incoming units", String(evidence.shipments.incoming_units)],
              ["Conflict detected", evidence.shipments.conflict_detected ? "Yes" : "No"],
            ]}
          />
          <EvidenceBlock
            title="Supplier"
            rows={[
              ["Supplier", evidence.supplier.supplier_name],
              ["Reliability score", String(evidence.supplier.reliability_score)],
              ["Lead time", `${evidence.supplier.lead_time_days} days`],
            ]}
          />
          <EvidenceBlock
            title="Cold chain"
            rows={[
              ["Compatible", evidence.cold_chain.compatible ? "Yes" : "No"],
              ["Required range", `${evidence.cold_chain.temperature_min}°C to ${evidence.cold_chain.temperature_max}°C`],
              ["Zone", evidence.cold_chain.zone_name],
            ]}
          />
          <EvidenceBlock
            title="Procurement"
            rows={[
              ["Demand forecast", evidence.procurement.demand_forecast],
              ["Shelf life valid", evidence.procurement.shelf_life_valid ? "Yes" : "No"],
              ["Shelf life", `${evidence.procurement.shelf_life_days} days`],
            ]}
          />
        </div>
      </CardContent>
    </Card>
  );
}

function EvidenceBlock({
  title,
  rows,
}: {
  title: string;
  rows: Array<readonly [string, string]>;
}) {
  return (
    <div className="rounded-xl border border-border/70 bg-muted/20 p-3.5">
      <div className="text-sm font-semibold">{title}</div>
      <div className="mt-3 space-y-2">
        {rows.map(([label, value]) => (
          <div key={label} className="flex items-start justify-between gap-3 text-sm">
            <span className="text-muted-foreground">{label}</span>
            <span className="text-right font-medium">{value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
