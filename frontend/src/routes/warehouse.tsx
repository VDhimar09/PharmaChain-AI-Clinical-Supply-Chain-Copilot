import { createFileRoute } from "@tanstack/react-router";
import { AppLayout } from "@/components/AppLayout";
import { Card, CardContent } from "@/components/ui/card";
import { zones } from "@/lib/mock-data";
import { Snowflake, Thermometer, Warehouse as WarehouseIcon, TrendingUp, ArrowRight } from "lucide-react";
import { AiInsight } from "@/components/AiInsight";

export const Route = createFileRoute("/warehouse")({
  head: () => ({
    meta: [
      { title: "Warehouse Capacity — AI Clinical Supply Chain Copilot" },
      { name: "description", content: "Monitor warehouse zone capacity, occupancy, and forecast." },
    ],
  }),
  component: WarehousePage,
});

type Risk = "healthy" | "warning" | "critical";
function riskOf(pct: number): Risk {
  if (pct >= 90) return "critical";
  if (pct >= 80) return "warning";
  return "healthy";
}
const riskStyles: Record<Risk, { chip: string; bar: string; text: string; ring: string }> = {
  healthy: {
    chip: "bg-success/12 text-success border-success/25",
    bar: "bg-primary",
    text: "text-foreground",
    ring: "border-border/70",
  },
  warning: {
    chip: "bg-warning/15 text-warning-foreground border-warning/30",
    bar: "bg-warning",
    text: "text-warning-foreground",
    ring: "border-warning/30",
  },
  critical: {
    chip: "bg-destructive/12 text-destructive border-destructive/25",
    bar: "bg-destructive",
    text: "text-destructive",
    ring: "border-destructive/30",
  },
};

function WarehousePage() {
  const totalCap = zones.reduce((a, z) => a + z.capacity, 0);
  const totalOcc = zones.reduce((a, z) => a + z.occupied, 0);
  const totalFc = zones.reduce((a, z) => a + z.forecast, 0);
  const currentPct = Math.round((totalOcc / totalCap) * 100);
  const fcPct = Math.round((totalFc / totalCap) * 100);
  const atRisk = zones.filter((z) => z.forecast / z.capacity >= 0.8);

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* KPI strip */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <Kpi icon={WarehouseIcon} label="Total capacity" value={`${totalCap.toLocaleString()}`} caption="pallets · 4 zones" tone="primary" />
          <Kpi icon={WarehouseIcon} label="Occupied today" value={`${currentPct}%`} caption={`${totalOcc.toLocaleString()} / ${totalCap.toLocaleString()}`} tone={currentPct >= 80 ? "warning" : "success"} />
          <Kpi icon={TrendingUp} label="Forecast (30d)" value={`${fcPct}%`} caption={`+${(totalFc - totalOcc).toLocaleString()} pallets`} tone={fcPct >= 80 ? "warning" : "info"} />
          <Kpi icon={Snowflake} label="Zones at risk" value={String(atRisk.length)} caption="≥ 80% forecast" tone={atRisk.length ? "warning" : "success"} />
        </div>

        {/* AI capacity insight */}
        <AiInsight
          eyebrow="Capacity copilot"
          detected={`Cold Storage B is projected to reach ${Math.round((zones[1].forecast / zones[1].capacity) * 100)}% within 14 days.`}
          matters="Inbound Pfizer shipment SHP-10231 (2,400 units) is unlikely to fit without rebalancing. Risk of detention costs and split storage."
          action="Move 30 pallets from Trial X cohort to Cold Storage A. Frees ~12% capacity ahead of arrival."
          confidence={92}
          risk="medium"
          cta="Review plan"
        />

        {/* Zone cards */}
        <div className="grid gap-4 md:grid-cols-2">
          {zones.map((z) => {
            const occ = Math.round((z.occupied / z.capacity) * 100);
            const fc = Math.round((z.forecast / z.capacity) * 100);
            const fcRisk = riskOf(fc);
            const s = riskStyles[fcRisk];
            const isCold = z.name.toLowerCase().includes("cold") || z.name.toLowerCase().includes("frozen");
            const Icon = isCold ? Snowflake : Thermometer;
            return (
              <Card key={z.id} className={`border ${s.ring} transition-shadow hover:shadow-[0_12px_32px_-18px_color-mix(in_oklab,var(--color-foreground)_22%,transparent)]`}>
                <CardContent className="p-5 space-y-5">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-center gap-3 min-w-0">
                      <div className={`size-10 rounded-xl grid place-items-center shrink-0 ${isCold ? "bg-info/12 text-info" : "bg-warning/15 text-warning-foreground"}`}>
                        <Icon className="size-5" />
                      </div>
                      <div className="min-w-0">
                        <div className="text-[16px] font-bold font-[family-name:var(--font-heading)] tracking-tight truncate">{z.name}</div>
                        <div className="text-xs text-muted-foreground inline-flex items-center gap-1">
                          <Thermometer className="size-3" /> {z.temperature}
                        </div>
                      </div>
                    </div>
                    <span className={`inline-flex items-center gap-1 text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md border ${s.chip}`}>
                      {fcRisk}
                    </span>
                  </div>

                  <div className="grid grid-cols-3 gap-3">
                    <Stat label="Capacity" value={z.capacity.toLocaleString()} />
                    <Stat label="Occupied" value={z.occupied.toLocaleString()} />
                    <Stat label="Available" value={(z.capacity - z.occupied).toLocaleString()} />
                  </div>

                  <div className="space-y-3">
                    <Bar label="Current occupancy" pct={occ} tone="primary" />
                    <Bar label="Forecast (30d)" pct={fc} tone={fcRisk === "healthy" ? "teal" : fcRisk === "warning" ? "warning" : "destructive"} />
                  </div>

                  <button className="w-full inline-flex items-center justify-center gap-1.5 text-xs font-semibold px-3 py-2 rounded-md border border-border bg-card hover:bg-muted transition-colors">
                    Open zone planner
                    <ArrowRight className="size-3" />
                  </button>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>
    </AppLayout>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg bg-muted/50 p-3">
      <div className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">{label}</div>
      <div className="text-[16px] font-bold font-[family-name:var(--font-heading)] tabular-nums mt-0.5">{value}</div>
    </div>
  );
}

function Bar({ label, pct, tone }: { label: string; pct: number; tone: "primary" | "teal" | "warning" | "destructive" }) {
  const colors = { primary: "bg-primary", teal: "bg-teal", warning: "bg-warning", destructive: "bg-destructive" };
  return (
    <div>
      <div className="flex items-center justify-between text-xs mb-1.5">
        <span className="text-muted-foreground">{label}</span>
        <span className="font-semibold tabular-nums">{pct}%</span>
      </div>
      <div className="h-2 w-full rounded-full bg-muted overflow-hidden">
        <div className={`h-full rounded-full ${colors[tone]} transition-all duration-700`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

function Kpi({
  icon: Icon,
  label,
  value,
  caption,
  tone,
}: {
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  value: string;
  caption: string;
  tone: "primary" | "success" | "warning" | "info";
}) {
  const toneMap = {
    primary: "bg-primary/10 text-primary",
    success: "bg-success/12 text-success",
    warning: "bg-warning/15 text-warning-foreground",
    info: "bg-info/12 text-info",
  };
  return (
    <div className="kpi-card p-5">
      <div className="flex items-start justify-between">
        <span className={`size-9 rounded-xl grid place-items-center ${toneMap[tone]}`}>
          <Icon className="size-4" />
        </span>
      </div>
      <div className="mt-4">
        <div className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">{label}</div>
        <div className="mt-1 text-[32px] leading-none font-bold font-[family-name:var(--font-heading)] tabular-nums tracking-tight">{value}</div>
        <div className="mt-1.5 text-[12px] text-muted-foreground">{caption}</div>
      </div>
    </div>
  );
}
