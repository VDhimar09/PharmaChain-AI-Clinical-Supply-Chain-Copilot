import { createFileRoute } from "@tanstack/react-router";
import { AppLayout } from "@/components/AppLayout";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Snowflake,
  Thermometer,
  Warehouse as WarehouseIcon,
  TrendingUp,
  ArrowRight,
} from "lucide-react";
import { AiInsight } from "@/components/AiInsight";
import { useWarehouseZones, useWarehouseCapacitySummary } from "@/lib/api/hooks";

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
  const { data: zonesData, isLoading: zonesLoading, error: zonesError } = useWarehouseZones();
  const {
    data: capacityData,
    isLoading: capacityLoading,
    error: capacityError,
  } = useWarehouseCapacitySummary();

  const zones = zonesData ?? [];
  const totalCap = capacityData?.total_capacity ?? zones.reduce((a, z) => a + z.capacity_units, 0);
  const totalOcc =
    capacityData?.occupied_capacity ?? zones.reduce((a, z) => a + z.occupied_units, 0);
  const totalAvailable = capacityData?.available_capacity ?? Math.max(totalCap - totalOcc, 0);
  const currentPct =
    capacityData?.occupancy_percentage ??
    (totalCap > 0 ? Math.round((totalOcc / totalCap) * 100) : 0);
  const atRisk = zones.filter(
    (z) => z.capacity_units > 0 && z.occupied_units / z.capacity_units >= 0.8,
  );
  const loading = zonesLoading || capacityLoading;
  const error = zonesError || capacityError;

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* KPI strip */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <Kpi
            icon={WarehouseIcon}
            label="Total capacity"
            value={`${totalCap.toLocaleString()}`}
            caption={`${zones.length} zones tracked`}
            tone="primary"
          />
          <Kpi
            icon={WarehouseIcon}
            label="Occupied today"
            value={`${currentPct}%`}
            caption={`${totalOcc.toLocaleString()} / ${totalCap.toLocaleString()}`}
            tone={currentPct >= 80 ? "warning" : "success"}
          />
          <Kpi
            icon={TrendingUp}
            label="Available capacity"
            value={`${totalAvailable.toLocaleString()}`}
            caption={`${Math.max(totalAvailable, 0).toLocaleString()} units available`}
            tone={totalAvailable <= totalCap * 0.2 ? "warning" : "info"}
          />
          <Kpi
            icon={Snowflake}
            label="Zones at risk"
            value={String(atRisk.length)}
            caption="≥ 80% occupancy"
            tone={atRisk.length ? "warning" : "success"}
          />
        </div>

        {/* AI capacity insight */}
        <AiInsight
          eyebrow="Capacity copilot"
          detected={
            zones.length > 0
              ? `Cold Storage occupancy is ${Math.round(((zones[0]?.occupied_units ?? 0) / (zones[0]?.capacity_units ?? 1)) * 100)}% in the first zone monitored.`
              : "Warehouse capacity data is being analyzed for hot spots."
          }
          matters="Several storage zones are close to capacity, which could impact inbound cold-chain shipments if not rebalanced."
          action="Review critical zones and prioritize inbound staging for high-risk products."
          confidence={88}
          risk={atRisk.length > 0 ? "medium" : "low"}
          cta="Review plan"
        />

        {/* Zone cards */}
        <div className="grid gap-4 md:grid-cols-2">
          {loading ? (
            Array.from({ length: 4 }).map((_, index) => (
              <Card key={index} className="border border-border/80 animate-pulse">
                <CardContent className="p-5 space-y-5">
                  <Skeleton className="h-5 w-2/5" />
                  <div className="grid grid-cols-3 gap-3">
                    <Skeleton className="h-16 rounded-lg col-span-1" />
                    <Skeleton className="h-16 rounded-lg col-span-1" />
                    <Skeleton className="h-16 rounded-lg col-span-1" />
                  </div>
                  <Skeleton className="h-3 w-full" />
                  <Skeleton className="h-3 w-5/6" />
                  <Skeleton className="h-10 w-full" />
                </CardContent>
              </Card>
            ))
          ) : error ? (
            <div className="col-span-1 text-destructive py-10 text-center">
              Failed to load warehouse capacity. Please refresh the page or try again.
            </div>
          ) : zones.length === 0 ? (
            <div className="col-span-1 text-muted-foreground py-10 text-center">
              No warehouse zones are currently available.
            </div>
          ) : (
            zones.map((z) => {
              const occ =
                z.capacity_units > 0 ? Math.round((z.occupied_units / z.capacity_units) * 100) : 0;
              const availablePct =
                z.capacity_units > 0
                  ? Math.round(((z.capacity_units - z.occupied_units) / z.capacity_units) * 100)
                  : 0;
              const zoneRisk = riskOf(occ);
              const s = riskStyles[zoneRisk];
              const isCold =
                z.zone_type.toLowerCase().includes("cold") ||
                z.zone_type.toLowerCase().includes("frozen") ||
                z.name.toLowerCase().includes("cold") ||
                z.name.toLowerCase().includes("frozen");
              const Icon = isCold ? Snowflake : Thermometer;
              const temperatureLabel =
                z.temperature_min != null && z.temperature_max != null
                  ? `${z.temperature_min}°C – ${z.temperature_max}°C`
                  : z.temperature_min != null
                    ? `${z.temperature_min}°C`
                    : z.temperature_max != null
                      ? `${z.temperature_max}°C`
                      : "N/A";

              return (
                <Card
                  key={z.id}
                  className={`border ${s.ring} transition-shadow hover:shadow-[0_12px_32px_-18px_color-mix(in_oklab,var(--color-foreground)_22%,transparent)]`}
                >
                  <CardContent className="p-5 space-y-5">
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex items-center gap-3 min-w-0">
                        <div
                          className={`size-10 rounded-xl grid place-items-center shrink-0 ${isCold ? "bg-info/12 text-info" : "bg-warning/15 text-warning-foreground"}`}
                        >
                          <Icon className="size-5" />
                        </div>
                        <div className="min-w-0">
                          <div className="text-[16px] font-bold font-[family-name:var(--font-heading)] tracking-tight truncate">
                            {z.name}
                          </div>
                          <div className="text-xs text-muted-foreground inline-flex items-center gap-1">
                            <Thermometer className="size-3" /> {temperatureLabel}
                          </div>
                        </div>
                      </div>
                      <span
                        className={`inline-flex items-center gap-1 text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md border ${s.chip}`}
                      >
                        {zoneRisk}
                      </span>
                    </div>

                    <div className="grid grid-cols-3 gap-3">
                      <Stat label="Capacity" value={z.capacity_units.toLocaleString()} />
                      <Stat label="Occupied" value={z.occupied_units.toLocaleString()} />
                      <Stat
                        label="Available"
                        value={(z.capacity_units - z.occupied_units).toLocaleString()}
                      />
                    </div>

                    <div className="space-y-3">
                      <Bar label="Current occupancy" pct={occ} tone="primary" />
                      <Bar
                        label="Available capacity"
                        pct={availablePct}
                        tone={
                          availablePct >= 30
                            ? "teal"
                            : availablePct >= 10
                              ? "warning"
                              : "destructive"
                        }
                      />
                    </div>

                    <button className="w-full inline-flex items-center justify-center gap-1.5 text-xs font-semibold px-3 py-2 rounded-md border border-border bg-card hover:bg-muted transition-colors">
                      Open zone planner
                      <ArrowRight className="size-3" />
                    </button>
                  </CardContent>
                </Card>
              );
            })
          )}
        </div>
      </div>
    </AppLayout>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg bg-muted/50 p-3">
      <div className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
        {label}
      </div>
      <div className="text-[16px] font-bold font-[family-name:var(--font-heading)] tabular-nums mt-0.5">
        {value}
      </div>
    </div>
  );
}

function Bar({
  label,
  pct,
  tone,
}: {
  label: string;
  pct: number;
  tone: "primary" | "teal" | "warning" | "destructive";
}) {
  const colors = {
    primary: "bg-primary",
    teal: "bg-teal",
    warning: "bg-warning",
    destructive: "bg-destructive",
  };
  return (
    <div>
      <div className="flex items-center justify-between text-xs mb-1.5">
        <span className="text-muted-foreground">{label}</span>
        <span className="font-semibold tabular-nums">{pct}%</span>
      </div>
      <div className="h-2 w-full rounded-full bg-muted overflow-hidden">
        <div
          className={`h-full rounded-full ${colors[tone]} transition-all duration-700`}
          style={{ width: `${pct}%` }}
        />
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
        <div className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
          {label}
        </div>
        <div className="mt-1 text-[32px] leading-none font-bold font-[family-name:var(--font-heading)] tabular-nums tracking-tight">
          {value}
        </div>
        <div className="mt-1.5 text-[12px] text-muted-foreground">{caption}</div>
      </div>
    </div>
  );
}
