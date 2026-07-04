import { createFileRoute } from "@tanstack/react-router";
import { AppLayout } from "@/components/AppLayout";
import { useDashboardSummary } from "@/lib/api/hooks";
import {
  Boxes,
  Warehouse,
  Truck,
  TrendingUp,
  AlertTriangle,
  ArrowUpRight,
  ArrowDownRight,
  Sparkles,
  Snowflake,
  Thermometer,
  CheckCircle2,
  Bot,
  ShieldAlert,
  ArrowRight,
  Activity,
  CircleDot,
  Flame,
  PackageCheck,
  Clock,
  Pill,
  Zap,
  AlertCircle,
  Loader2,
} from "lucide-react";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  RadialBar,
  RadialBarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  ReferenceLine,
} from "recharts";
import { inventoryTrend, zones } from "@/lib/mock-data";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Clinical Supply Chain Operations Center — PharmaChain" },
      {
        name: "description",
        content:
          "Real-time visibility across inventory, shipments, warehouse capacity and procurement decisions powered by AI.",
      },
    ],
  }),
  component: Dashboard,
});

/* ============================================================
   Atoms
   ============================================================ */

function SectionHeader({
  eyebrow,
  title,
  subtitle,
  action,
}: {
  eyebrow?: string;
  title: string;
  subtitle?: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="flex flex-wrap items-end justify-between gap-3 mb-4">
      <div className="min-w-0">
        {eyebrow && (
          <div className="text-[10px] font-bold uppercase tracking-[0.22em] text-primary mb-1.5">
            {eyebrow}
          </div>
        )}
        <h2 className="text-[20px] font-bold font-[family-name:var(--font-heading)] tracking-tight text-foreground">
          {title}
        </h2>
        {subtitle && (
          <p className="text-[13px] text-muted-foreground mt-0.5 max-w-2xl">{subtitle}</p>
        )}
      </div>
      {action}
    </div>
  );
}

function Sparkline({ data, color }: { data: number[]; color: string }) {
  const series = data.map((v, i) => ({ i, v }));
  return (
    <ResponsiveContainer width="100%" height={40}>
      <LineChart data={series} margin={{ top: 4, right: 0, bottom: 4, left: 0 }}>
        <defs>
          <linearGradient id={`spark-${color.replace(/[^a-z]/gi, "")}`} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={color} stopOpacity={0.35} />
            <stop offset="100%" stopColor={color} stopOpacity={0} />
          </linearGradient>
        </defs>
        <Line type="monotone" dataKey="v" stroke={color} strokeWidth={2} dot={false} />
      </LineChart>
    </ResponsiveContainer>
  );
}

/* ============================================================
   SECTION 1 — Executive header KPIs
   ============================================================ */

type Kpi = {
  label: string;
  value: string;
  unit?: string;
  caption: string;
  delta: string;
  up: boolean;
  positive: boolean;
  icon: React.ComponentType<{ className?: string }>;
  tint: string; // tailwind gradient stops via arbitrary color-mix
  stroke: string;
  spark: number[];
};

// Static mock KPI base with sparklines
const mockKpis: Kpi[] = [
  {
    label: "Total Inventory",
    value: "47,820",
    unit: "units",
    caption: "Across 4 storage zones",
    delta: "+5.7%",
    up: true,
    positive: true,
    icon: Boxes,
    tint: "var(--color-primary)",
    stroke: "var(--color-primary)",
    spark: [32, 38, 36, 42, 45, 44, 48],
  },
  {
    label: "Warehouse Occupancy",
    value: "72",
    unit: "%",
    caption: "Healthy · target < 80%",
    delta: "+3.2%",
    up: true,
    positive: true,
    icon: Warehouse,
    tint: "var(--color-teal)",
    stroke: "var(--color-teal)",
    spark: [60, 62, 65, 64, 68, 70, 72],
  },
  {
    label: "Incoming Shipments",
    value: "18",
    unit: "in 7d",
    caption: "3 require approval",
    delta: "+2",
    up: true,
    positive: true,
    icon: Truck,
    tint: "var(--color-info)",
    stroke: "var(--color-info)",
    spark: [10, 14, 12, 15, 13, 16, 18],
  },
  {
    label: "Forecast Capacity",
    value: "84",
    unit: "%",
    caption: "In 14 days · capacity risk",
    delta: "+12%",
    up: true,
    positive: false,
    icon: TrendingUp,
    tint: "var(--color-warning)",
    stroke: "var(--color-warning)",
    spark: [68, 70, 72, 75, 78, 81, 84],
  },
];

/**
 * Update KPI cards with live backend data, preserving static sparklines.
 * Only replaces value, unit, and caption fields from backend metrics.
 * Keeps existing sparklines and deltas until historical analytics endpoint exists.
 */
function updateKpisWithLiveData(data: any): Kpi[] {
  if (!data) return mockKpis;

  const updated = [...mockKpis];

  // Update Total Inventory card
  updated[0] = {
    ...updated[0],
    value:
      (data.total_inventory_units / 1000)
        .toLocaleString("en-US", {
          minimumFractionDigits: 0,
          maximumFractionDigits: 1,
        })
        .replace(".0", "") + "k",
    caption: `${data.available_inventory_units.toLocaleString()} available · ${data.reserved_inventory_units.toLocaleString()} reserved`,
  };

  // Update Warehouse Occupancy card
  updated[1] = {
    ...updated[1],
    value: Math.round(data.warehouse_occupancy).toString(),
    caption: `${data.warehouse_available_capacity.toLocaleString()} units available · ${data.warehouse_occupancy < 80 ? "healthy" : "approaching limit"}`,
    positive: data.warehouse_occupancy < 80,
  };

  // Update Incoming Shipments card
  updated[2] = {
    ...updated[2],
    value: data.incoming_shipments.toString(),
    unit: data.incoming_shipments === 1 ? "pending" : "pending",
    caption: `${data.delayed_shipments} delayed · ${data.outgoing_shipments} outgoing`,
    positive: data.delayed_shipments === 0,
  };

  // Update Low Stock / Forecast Capacity card
  updated[3] = {
    ...updated[3],
    value: data.low_stock_products.toString(),
    unit: "items",
    caption: `${data.procurement_requests} procurement requests`,
    positive: data.low_stock_products < 15,
  };

  return updated;
}

function ExecutiveKpiCard({ kpi }: { kpi: Kpi }) {
  const Icon = kpi.icon;
  return (
    <div className="group relative overflow-hidden rounded-2xl border border-border/70 bg-card p-5 transition-all duration-300 hover:-translate-y-0.5 hover:shadow-[0_12px_32px_-16px_color-mix(in_oklab,var(--color-foreground)_22%,transparent)] hover:border-border">
      {/* tint wash */}
      <div
        aria-hidden
        className="absolute inset-0 opacity-[0.06] group-hover:opacity-[0.1] transition-opacity"
        style={{
          background: `radial-gradient(120% 80% at 100% 0%, ${kpi.tint} 0%, transparent 55%)`,
        }}
      />
      <div className="relative">
        <div className="flex items-center justify-between">
          <span
            className="inline-flex size-9 items-center justify-center rounded-xl ring-1"
            style={{
              background: `color-mix(in oklab, ${kpi.tint} 14%, transparent)`,
              color: kpi.tint,
              borderColor: `color-mix(in oklab, ${kpi.tint} 25%, transparent)`,
            }}
          >
            <Icon className="size-4.5" />
          </span>
          <div
            className={`inline-flex items-center gap-0.5 text-[11px] font-bold tabular-nums px-2 py-0.5 rounded-full ${
              kpi.positive ? "text-success bg-success/10" : "text-warning-foreground bg-warning/15"
            }`}
          >
            {kpi.up ? <ArrowUpRight className="size-3" /> : <ArrowDownRight className="size-3" />}
            {kpi.delta}
          </div>
        </div>

        <div className="mt-5">
          <div className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
            {kpi.label}
          </div>
          <div className="mt-1 flex items-baseline gap-1.5">
            <span className="text-[40px] leading-none font-bold font-[family-name:var(--font-heading)] tabular-nums tracking-tight">
              {kpi.value}
            </span>
            {kpi.unit && (
              <span className="text-[13px] font-medium text-muted-foreground">{kpi.unit}</span>
            )}
          </div>
          <div className="mt-1.5 text-[12px] text-muted-foreground">{kpi.caption}</div>
        </div>

        <div className="mt-3 -mx-1">
          <Sparkline data={kpi.spark} color={kpi.stroke} />
        </div>
      </div>
    </div>
  );
}

/**
 * Skeleton loader for KPI cards while data is loading.
 */
function KpiCardSkeleton() {
  return (
    <div className="rounded-2xl border border-border/70 bg-card p-5 animate-pulse">
      <div className="flex items-center justify-between">
        <div className="size-9 rounded-xl bg-muted" />
        <div className="h-6 w-16 rounded-full bg-muted" />
      </div>
      <div className="mt-5">
        <div className="h-3 w-24 rounded bg-muted" />
        <div className="mt-3 h-10 w-32 rounded bg-muted" />
        <div className="mt-2 h-3 w-40 rounded bg-muted" />
      </div>
    </div>
  );
}

/**
 * Error state for dashboard KPIs.
 */
function KpiLoadError() {
  return (
    <div className="rounded-2xl border border-destructive/30 bg-destructive/[0.04] p-5">
      <div className="flex items-start gap-3">
        <AlertCircle className="size-5 text-destructive shrink-0 mt-0.5" />
        <div>
          <h3 className="text-sm font-semibold text-destructive">Failed to load dashboard</h3>
          <p className="text-xs text-muted-foreground mt-1">
            Could not connect to the backend. Showing mock data for demonstration.
          </p>
        </div>
      </div>
    </div>
  );
}

/* ============================================================
   SECTION 2 — Critical alerts
   ============================================================ */

type AlertTone = "critical" | "warning" | "healthy";
type Alert = {
  id: string;
  tone: AlertTone;
  icon: React.ComponentType<{ className?: string }>;
  category: string;
  title: string;
  impact: string;
  action: string;
  cta: string;
};

const alerts: Alert[] = [
  {
    id: "a1",
    tone: "critical",
    icon: Pill,
    category: "Stock shortage",
    title: "Influenza vaccine below safety stock",
    impact: "95 units left · 14-day coverage at risk",
    action: "Reorder 600 units from Sanofi within 48h",
    cta: "Initiate PO",
  },
  {
    id: "a2",
    tone: "warning",
    icon: Warehouse,
    category: "Capacity risk",
    title: "Cold Storage B reaching 84% in 14 days",
    impact: "Inbound Pfizer shipment may not fit",
    action: "Move 30 pallets from Trial X to Zone A",
    cta: "Review plan",
  },
  {
    id: "a3",
    tone: "warning",
    icon: Clock,
    category: "Delayed shipment",
    title: "SHP-10239 Oncology Trial OXC-44",
    impact: "AstraZeneca · ETA pushed by 2 days",
    action: "Notify clinical site and adjust kit allocation",
    cta: "Open shipment",
  },
  {
    id: "a4",
    tone: "healthy",
    icon: Thermometer,
    category: "Cold chain",
    title: "All temperature ranges within tolerance",
    impact: "4 zones · 0 excursions in last 24h",
    action: "No action required",
    cta: "View telemetry",
  },
];

const toneMap: Record<
  AlertTone,
  { ring: string; bg: string; chip: string; bar: string; text: string }
> = {
  critical: {
    ring: "border-destructive/30",
    bg: "bg-destructive/[0.04]",
    chip: "bg-destructive/12 text-destructive border-destructive/25",
    bar: "bg-destructive",
    text: "text-destructive",
  },
  warning: {
    ring: "border-warning/35",
    bg: "bg-warning/[0.06]",
    chip: "bg-warning/15 text-warning-foreground border-warning/30",
    bar: "bg-warning",
    text: "text-warning-foreground",
  },
  healthy: {
    ring: "border-success/25",
    bg: "bg-success/[0.04]",
    chip: "bg-success/12 text-success border-success/25",
    bar: "bg-success",
    text: "text-success",
  },
};

function AlertCard({ alert }: { alert: Alert }) {
  const t = toneMap[alert.tone];
  const Icon = alert.icon;
  return (
    <article
      className={`group relative overflow-hidden rounded-xl border ${t.ring} ${t.bg} pl-4 pr-4 py-4 transition-all hover:shadow-[0_8px_24px_-14px_color-mix(in_oklab,var(--color-foreground)_18%,transparent)]`}
    >
      <span className={`absolute left-0 top-0 bottom-0 w-1 ${t.bar}`} />
      <div className="flex items-start gap-3">
        <div className={`size-9 rounded-lg grid place-items-center shrink-0 border ${t.chip}`}>
          <Icon className="size-4" />
        </div>
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2 flex-wrap">
            <span
              className={`inline-flex items-center gap-1 text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md border ${t.chip}`}
            >
              <CircleDot className="size-2.5" />
              {alert.category}
            </span>
          </div>
          <h4 className="mt-1.5 text-[14px] font-semibold leading-snug text-foreground">
            {alert.title}
          </h4>
          <p className="mt-1 text-[12px] text-muted-foreground">{alert.impact}</p>
          <div className="mt-3 pt-3 border-t border-border/50 flex items-center justify-between gap-2">
            <p className="text-[12px] text-foreground/80 truncate">
              <span className="font-semibold">Action: </span>
              {alert.action}
            </p>
            <button
              className={`shrink-0 inline-flex items-center gap-1 text-[11px] font-semibold px-2.5 py-1.5 rounded-md border ${t.chip} hover:brightness-105 transition`}
            >
              {alert.cta}
              <ArrowRight className="size-3" />
            </button>
          </div>
        </div>
      </div>
    </article>
  );
}

/* ============================================================
   SECTION 3 — AI Copilot recommendations
   ============================================================ */

type Reco = {
  id: string;
  priority: "P1" | "P2" | "P3";
  priorityLabel: string;
  icon: React.ComponentType<{ className?: string }>;
  title: string;
  rationale: string;
  confidence: number;
  impact: string;
  cta: string;
};

const recos: Reco[] = [
  {
    id: "r1",
    priority: "P1",
    priorityLabel: "Critical",
    icon: ShieldAlert,
    title: "Move 30 pallets from Trial X to Cold Storage A",
    rationale:
      "Inbound Pfizer shipment SHP-10231 arrives Jul 12. Cold Storage B will hit 84% capacity. Relocation avoids overflow.",
    confidence: 92,
    impact: "Frees 12% capacity · prevents detention costs",
    cta: "Review plan",
  },
  {
    id: "r2",
    priority: "P1",
    priorityLabel: "Critical",
    icon: PackageCheck,
    title: "Approve incoming Pfizer shipment SHP-10231",
    rationale:
      "2,400 units inbound. Cold chain, temperature, and customs documents pass automated checks. Aligned with Q3 demand forecast.",
    confidence: 96,
    impact: "Maintains 28-day coverage at 2 trial sites",
    cta: "Approve",
  },
  {
    id: "r3",
    priority: "P2",
    priorityLabel: "High",
    icon: Pill,
    title: "Reorder 600 units of Influenza Quadrivalent",
    rationale:
      "Current stock 95 units, projected stockout in 9 days. Sanofi lead time 5 days. Place order today to maintain coverage.",
    confidence: 88,
    impact: "Prevents stockout · +14d safety buffer",
    cta: "Initiate PO",
  },
];

const priorityChip: Record<Reco["priority"], { bg: string; text: string; dot: string }> = {
  P1: { bg: "bg-destructive/12", text: "text-destructive", dot: "bg-destructive" },
  P2: {
    bg: "bg-warning/15",
    text: "text-warning-foreground",
    dot: "bg-warning",
  },
  P3: { bg: "bg-success/12", text: "text-success", dot: "bg-success" },
};

function RecoCard({ reco }: { reco: Reco }) {
  const Icon = reco.icon;
  const p = priorityChip[reco.priority];
  return (
    <article className="group relative rounded-2xl border border-border/60 bg-card overflow-hidden transition-all duration-300 hover:-translate-y-0.5 hover:shadow-[0_16px_40px_-20px_color-mix(in_oklab,var(--color-primary)_28%,transparent)] hover:border-primary/40">
      {/* confidence top bar */}
      <div className="h-1 w-full bg-muted">
        <div
          className="h-full bg-gradient-to-r from-primary to-teal transition-all duration-700"
          style={{ width: `${reco.confidence}%` }}
        />
      </div>
      <div className="p-5">
        <div className="flex items-center justify-between gap-2">
          <span
            className={`inline-flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md ${p.bg} ${p.text}`}
          >
            <span className={`size-1.5 rounded-full ${p.dot}`} />
            {reco.priority} · {reco.priorityLabel}
          </span>
          <span className="text-[11px] font-semibold text-muted-foreground tabular-nums">
            {reco.confidence}% confidence
          </span>
        </div>

        <div className="mt-4 flex items-start gap-3">
          <div className="size-10 rounded-xl grid place-items-center bg-gradient-to-br from-primary/15 to-teal/15 text-primary shrink-0 ring-1 ring-primary/15">
            <Icon className="size-5" />
          </div>
          <h4 className="text-[15px] font-bold font-[family-name:var(--font-heading)] leading-snug text-foreground tracking-tight">
            {reco.title}
          </h4>
        </div>

        <p className="mt-3 text-[12.5px] text-muted-foreground leading-relaxed">{reco.rationale}</p>

        <div className="mt-4 pt-4 border-t border-border/60 flex items-center justify-between gap-2">
          <div className="flex items-center gap-1.5 text-[11.5px] text-foreground/80">
            <Zap className="size-3 text-primary" />
            <span>{reco.impact}</span>
          </div>
          <button className="inline-flex items-center gap-1 text-xs font-semibold px-3 py-1.5 rounded-md bg-primary text-primary-foreground hover:brightness-105 transition-all shadow-sm shadow-primary/25">
            {reco.cta}
            <ArrowRight className="size-3" />
          </button>
        </div>
      </div>
    </article>
  );
}

/* ============================================================
   SECTION 4 — Operational KPIs (radial)
   ============================================================ */

type OpKpi = {
  label: string;
  value: number;
  caption: string;
  color: string;
  icon: React.ComponentType<{ className?: string }>;
  detail: string;
};

const opKpis: OpKpi[] = [
  {
    label: "Inventory Health",
    value: 94,
    caption: "12 SKUs healthy · 2 critical",
    color: "var(--color-primary)",
    icon: Boxes,
    detail: "Stock coverage vs demand",
  },
  {
    label: "Cold Chain Health",
    value: 98,
    caption: "0 excursions · 4.2°C avg",
    color: "var(--color-teal)",
    icon: Snowflake,
    detail: "Temperature compliance",
  },
  {
    label: "Warehouse Utilization",
    value: 72,
    caption: "4 zones · 3,116 / 5,900 slots",
    color: "var(--color-info)",
    icon: Warehouse,
    detail: "Average across zones",
  },
  {
    label: "Shipment Performance",
    value: 87,
    caption: "26 of 30 on-time · 2 delayed",
    color: "var(--color-warning)",
    icon: Truck,
    detail: "On-time delivery (30d)",
  },
];

function RadialKpi({ kpi }: { kpi: OpKpi }) {
  const Icon = kpi.icon;
  const data = [{ name: kpi.label, value: kpi.value, fill: kpi.color }];
  return (
    <div className="group rounded-2xl border border-border/70 bg-card p-5 transition-all duration-300 hover:-translate-y-0.5 hover:shadow-[0_12px_32px_-18px_color-mix(in_oklab,var(--color-foreground)_22%,transparent)]">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span
            className="size-8 rounded-lg grid place-items-center"
            style={{
              background: `color-mix(in oklab, ${kpi.color} 14%, transparent)`,
              color: kpi.color,
            }}
          >
            <Icon className="size-4" />
          </span>
          <div>
            <div className="text-[13px] font-semibold text-foreground">{kpi.label}</div>
            <div className="text-[11px] text-muted-foreground">{kpi.detail}</div>
          </div>
        </div>
      </div>

      <div className="mt-2 relative h-40">
        <ResponsiveContainer width="100%" height="100%">
          <RadialBarChart
            innerRadius="72%"
            outerRadius="100%"
            data={data}
            startAngle={90}
            endAngle={-270}
            barSize={10}
          >
            <defs>
              <linearGradient
                id={`grad-${kpi.label.replace(/\s/g, "")}`}
                x1="0"
                y1="0"
                x2="1"
                y2="1"
              >
                <stop offset="0%" stopColor={kpi.color} stopOpacity={1} />
                <stop offset="100%" stopColor={kpi.color} stopOpacity={0.5} />
              </linearGradient>
            </defs>
            <RadialBar
              dataKey="value"
              cornerRadius={20}
              background={{ fill: "color-mix(in oklab, var(--color-muted) 100%, transparent)" }}
              fill={`url(#grad-${kpi.label.replace(/\s/g, "")})`}
            />
          </RadialBarChart>
        </ResponsiveContainer>
        <div className="absolute inset-0 grid place-items-center pointer-events-none">
          <div className="text-center">
            <div className="text-[34px] leading-none font-bold font-[family-name:var(--font-heading)] tabular-nums tracking-tight">
              {kpi.value}
              <span className="text-[16px] text-muted-foreground font-semibold">%</span>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-1 text-center text-[11.5px] text-muted-foreground">{kpi.caption}</div>
    </div>
  );
}

/* ============================================================
   SECTION 5 — Forecasting & trends
   ============================================================ */

// Extend trend with forecast tail (Jul–Sep)
const trendWithForecast = [
  ...inventoryTrend.map((d) => ({ ...d, forecast: null as number | null })),
  { month: "Jul", inventory: null, demand: 43800, forecast: 49100 },
  { month: "Aug", inventory: null, demand: 45200, forecast: 50800 },
  { month: "Sep", inventory: null, demand: 46100, forecast: 51900 },
];

const capacityForecast = [
  { month: "Jan", actual: 58, projected: null as number | null },
  { month: "Feb", actual: 61, projected: null },
  { month: "Mar", actual: 64, projected: null },
  { month: "Apr", actual: 68, projected: null },
  { month: "May", actual: 70, projected: null },
  { month: "Jun", actual: 72, projected: null },
  { month: "Jul", actual: null, projected: 78 },
  { month: "Aug", actual: null, projected: 84 },
  { month: "Sep", actual: null, projected: 88 },
];

/* ============================================================
   Dashboard
   ============================================================ */

/* ============================================================
   Today's Priorities — merged alerts + AI recos
   ============================================================ */

type Priority = {
  id: string;
  kind: "alert" | "reco";
  priority: "P1" | "P2" | "P3";
  tone: "critical" | "warning" | "healthy";
  icon: React.ComponentType<{ className?: string }>;
  category: string;
  title: string;
  rationale: string;
  impact: string;
  confidence: number;
  cta: string;
};

const priorities: Priority[] = [
  {
    id: "p1",
    kind: "alert",
    priority: "P1",
    tone: "critical",
    icon: Pill,
    category: "Stock shortage",
    title: "Influenza vaccine below safety stock",
    rationale:
      "Current stock 95 units · projected stockout in 9 days. Sanofi lead time 5 days — order today preserves 14-day coverage.",
    impact: "Prevents stockout · +14d safety buffer",
    confidence: 91,
    cta: "Initiate PO",
  },
  {
    id: "p2",
    kind: "reco",
    priority: "P1",
    tone: "warning",
    icon: ShieldAlert,
    category: "Capacity risk",
    title: "Move 30 pallets from Trial X to Cold Storage A",
    rationale:
      "Inbound Pfizer shipment SHP-10231 arrives Jul 12. Cold Storage B will hit 84%. Relocation avoids overflow and detention costs.",
    impact: "Frees 12% capacity · avoids detention costs",
    confidence: 92,
    cta: "Review plan",
  },
  {
    id: "p3",
    kind: "reco",
    priority: "P2",
    tone: "healthy",
    icon: PackageCheck,
    category: "Procurement",
    title: "Approve incoming Pfizer shipment SHP-10231",
    rationale:
      "2,400 units inbound. Cold chain, temperature and customs documents pass automated checks. Aligned with Q3 demand forecast.",
    impact: "Maintains 28-day coverage at 2 sites",
    confidence: 96,
    cta: "Approve",
  },
];

const pToneMap: Record<Priority["tone"], { ring: string; bar: string; chip: string; cta: string }> =
  {
    critical: {
      ring: "border-destructive/30 hover:border-destructive/45",
      bar: "bg-destructive",
      chip: "bg-destructive/10 text-destructive border-destructive/25",
      cta: "bg-destructive text-destructive-foreground hover:brightness-105",
    },
    warning: {
      ring: "border-warning/35 hover:border-warning/55",
      bar: "bg-warning",
      chip: "bg-warning/15 text-warning-foreground border-warning/30",
      cta: "bg-warning text-warning-foreground hover:brightness-105",
    },
    healthy: {
      ring: "border-border/60 hover:border-primary/40",
      bar: "bg-primary",
      chip: "bg-success/12 text-success border-success/25",
      cta: "bg-primary text-primary-foreground hover:brightness-105",
    },
  };

function PriorityCard({ p }: { p: Priority }) {
  const t = pToneMap[p.tone];
  const Icon = p.icon;
  return (
    <article
      className={`group relative overflow-hidden rounded-2xl border bg-card transition-all duration-300 hover:-translate-y-0.5 hover:shadow-[0_16px_40px_-22px_color-mix(in_oklab,var(--color-foreground)_28%,transparent)] ${t.ring}`}
    >
      <span className={`absolute left-0 top-0 bottom-0 w-1 ${t.bar}`} />
      <div className="p-5">
        <div className="flex items-center justify-between gap-2">
          <span
            className={`inline-flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md border ${t.chip}`}
          >
            <span className={`size-1.5 rounded-full ${t.bar}`} />
            {p.priority} · {p.category}
          </span>
          <span className="text-[11px] font-semibold text-muted-foreground tabular-nums">
            {p.confidence}% conf.
          </span>
        </div>

        <div className="mt-4 flex items-start gap-3">
          <div className="size-10 rounded-xl grid place-items-center bg-gradient-to-br from-primary/12 to-teal/12 text-primary shrink-0 ring-1 ring-primary/15">
            <Icon className="size-5" />
          </div>
          <h4 className="text-[15px] font-bold font-[family-name:var(--font-heading)] leading-snug text-foreground tracking-tight">
            {p.title}
          </h4>
        </div>

        <p className="mt-3 text-[12.5px] text-muted-foreground leading-relaxed">{p.rationale}</p>

        <div className="mt-4 pt-4 border-t border-border/60 flex items-center justify-between gap-2">
          <div className="flex items-center gap-1.5 text-[11.5px] text-foreground/80 min-w-0">
            <Zap className="size-3 text-primary shrink-0" />
            <span className="truncate">{p.impact}</span>
          </div>
          <button
            className={`shrink-0 inline-flex items-center gap-1 text-xs font-semibold px-3 py-1.5 rounded-md shadow-sm transition-all ${t.cta}`}
          >
            {p.cta}
            <ArrowRight className="size-3" />
          </button>
        </div>
      </div>
    </article>
  );
}

/* ============================================================
   Dashboard
   ============================================================ */

function Dashboard() {
  const { data: dashboardData, isLoading, error } = useDashboardSummary();
  const kpis = updateKpisWithLiveData(dashboardData);

  return (
    <AppLayout>
      <div className="space-y-7">
        {/* ===================== Hero ===================== */}
        <section>
          <div className="relative overflow-hidden rounded-2xl border border-border/60 bg-gradient-to-br from-[color-mix(in_oklab,var(--color-primary)_8%,var(--color-card))] via-card to-[color-mix(in_oklab,var(--color-teal)_6%,var(--color-card))] p-6 md:p-7 mb-5">
            <div
              aria-hidden
              className="absolute -top-20 -right-20 size-72 rounded-full blur-3xl opacity-30"
              style={{
                background:
                  "radial-gradient(circle, color-mix(in oklab, var(--color-primary) 60%, transparent) 0%, transparent 70%)",
              }}
            />
            <div className="relative flex flex-wrap items-start justify-between gap-4">
              <div className="min-w-0">
                <div className="inline-flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-[0.22em] text-primary mb-2">
                  <span
                    className={`size-1.5 rounded-full ${isLoading ? "bg-muted animate-pulse" : "bg-success animate-pulse"}`}
                  />
                  {isLoading ? "Loading..." : error ? "Connection issue" : "Live · synced now"}
                </div>
                <h1 className="text-[26px] md:text-[30px] font-bold font-[family-name:var(--font-heading)] tracking-tight text-foreground leading-tight">
                  Clinical Supply Chain Operations Center
                </h1>
                <p className="mt-1.5 text-[13.5px] text-muted-foreground max-w-2xl leading-relaxed">
                  Real-time visibility across inventory, shipments, warehouse capacity and
                  procurement decisions.
                </p>
              </div>
              <div className="flex items-center gap-1.5 text-[11px] font-medium shrink-0">
                {["24h", "7d", "30d", "QTD"].map((p, i) => (
                  <button
                    key={p}
                    className={`px-3 py-1.5 rounded-md border transition-colors ${
                      i === 1
                        ? "bg-card border-border text-foreground shadow-sm"
                        : "border-transparent text-muted-foreground hover:text-foreground hover:bg-card/60"
                    }`}
                  >
                    {p}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {isLoading ? (
              <>
                <KpiCardSkeleton />
                <KpiCardSkeleton />
                <KpiCardSkeleton />
                <KpiCardSkeleton />
              </>
            ) : error ? (
              <>
                <div className="lg:col-span-4">
                  <KpiLoadError />
                </div>
              </>
            ) : kpis.length > 0 ? (
              kpis.map((k) => <ExecutiveKpiCard key={k.label} kpi={k} />)
            ) : null}
          </div>
        </section>

        {/* ===================== Today's Priorities ===================== */}
        <section className="relative">
          <div className="rounded-2xl border border-primary/15 bg-gradient-to-br from-card via-card to-[color-mix(in_oklab,var(--color-primary)_4%,var(--color-card))] p-5 md:p-6 shadow-[0_24px_60px_-32px_color-mix(in_oklab,var(--color-primary)_40%,transparent)]">
            <div className="flex flex-wrap items-center justify-between gap-3 mb-5">
              <div className="flex items-center gap-3 min-w-0">
                <div className="size-11 rounded-2xl bg-gradient-to-br from-primary to-teal grid place-items-center shadow-md shadow-primary/25 ring-1 ring-primary/20 shrink-0">
                  <Bot className="size-5 text-primary-foreground" />
                </div>
                <div className="min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <h2 className="text-[20px] font-bold font-[family-name:var(--font-heading)] tracking-tight">
                      Today's Priorities
                    </h2>
                    <span className="inline-flex items-center gap-1 text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md bg-primary/12 text-primary border border-primary/25">
                      <Sparkles className="size-2.5" />
                      Copilot v2.4
                    </span>
                  </div>
                  <p className="text-[12.5px] text-muted-foreground mt-0.5">
                    Top 3 actions across alerts and AI recommendations — refreshed 5 min ago.
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <button className="text-xs font-semibold px-3 py-1.5 rounded-md bg-card hover:bg-muted border border-border transition-colors">
                  Audit log
                </button>
                <button className="inline-flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-md bg-foreground text-background hover:opacity-90 transition-all">
                  Run all
                  <ArrowRight className="size-3" />
                </button>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
              {priorities.map((p) => (
                <PriorityCard key={p.id} p={p} />
              ))}
            </div>
          </div>
        </section>

        {/* ===================== Operational health ===================== */}
        <section>
          <SectionHeader
            eyebrow="Operational health"
            title="Operational KPIs"
            subtitle="Composite health scores across the four pillars of supply chain operations."
            action={
              <span className="inline-flex items-center gap-1.5 text-[11px] text-success font-semibold">
                <Activity className="size-3" />
                System healthy
              </span>
            }
          />
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {opKpis.map((k) => (
              <RadialKpi key={k.label} kpi={k} />
            ))}
          </div>
        </section>

        {/* ===================== Forecasts ===================== */}
        <section>
          <SectionHeader
            eyebrow="Forecasting"
            title="Trends & Forecasts"
            subtitle="Six months of history with three months of AI-projected demand and capacity."
          />
          <div className="grid gap-5 lg:grid-cols-2">
            {/* Inventory vs Demand */}
            <div className="rounded-2xl border border-border/70 bg-card p-5">
              <div className="flex items-start justify-between gap-3 mb-4">
                <div>
                  <h3 className="text-[15px] font-bold font-[family-name:var(--font-heading)] tracking-tight">
                    Inventory vs Demand
                  </h3>
                  <p className="text-xs text-muted-foreground mt-0.5">
                    Units · 6 months actual + 3 months forecast
                  </p>
                </div>
                <div className="flex items-center gap-3 text-[11px]">
                  <span className="inline-flex items-center gap-1.5 text-muted-foreground">
                    <span className="size-2 rounded-sm bg-primary" />
                    Inventory
                  </span>
                  <span className="inline-flex items-center gap-1.5 text-muted-foreground">
                    <span className="size-2 rounded-sm bg-info" />
                    Demand
                  </span>
                  <span className="inline-flex items-center gap-1.5 text-muted-foreground">
                    <span
                      className="size-2 rounded-sm"
                      style={{ background: "var(--color-warning)" }}
                    />
                    Forecast
                  </span>
                </div>
              </div>
              <div className="h-72 -mx-2">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart
                    data={trendWithForecast}
                    margin={{ top: 10, right: 12, left: 0, bottom: 0 }}
                  >
                    <defs>
                      <linearGradient id="gInv" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="var(--color-primary)" stopOpacity={0.35} />
                        <stop offset="100%" stopColor="var(--color-primary)" stopOpacity={0} />
                      </linearGradient>
                      <linearGradient id="gDem" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="var(--color-info)" stopOpacity={0.3} />
                        <stop offset="100%" stopColor="var(--color-info)" stopOpacity={0} />
                      </linearGradient>
                      <linearGradient id="gFor" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="var(--color-warning)" stopOpacity={0.35} />
                        <stop offset="100%" stopColor="var(--color-warning)" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid
                      stroke="var(--color-border)"
                      strokeDasharray="3 3"
                      vertical={false}
                    />
                    <XAxis
                      dataKey="month"
                      tick={{
                        fill: "var(--color-muted-foreground)",
                        fontSize: 11,
                        fontWeight: 500,
                      }}
                      axisLine={false}
                      tickLine={false}
                    />
                    <YAxis
                      tick={{ fill: "var(--color-muted-foreground)", fontSize: 11 }}
                      axisLine={false}
                      tickLine={false}
                      width={48}
                    />
                    <Tooltip
                      cursor={{
                        stroke: "var(--color-primary)",
                        strokeWidth: 1,
                        strokeDasharray: "3 3",
                      }}
                      contentStyle={{
                        background: "var(--color-card)",
                        border: "1px solid var(--color-border)",
                        borderRadius: 10,
                        fontSize: 12,
                        boxShadow: "0 8px 24px -12px rgba(15,23,42,0.18)",
                      }}
                    />
                    <ReferenceLine
                      x="Jun"
                      stroke="var(--color-border)"
                      strokeDasharray="4 4"
                      label={{
                        value: "Today",
                        position: "insideTopRight",
                        fill: "var(--color-muted-foreground)",
                        fontSize: 10,
                      }}
                    />
                    <Area
                      name="Inventory"
                      type="monotone"
                      dataKey="inventory"
                      stroke="var(--color-primary)"
                      fill="url(#gInv)"
                      strokeWidth={2.5}
                      activeDot={{ r: 5 }}
                    />
                    <Area
                      name="Demand"
                      type="monotone"
                      dataKey="demand"
                      stroke="var(--color-info)"
                      fill="url(#gDem)"
                      strokeWidth={2.5}
                      activeDot={{ r: 5 }}
                    />
                    <Area
                      name="Forecast"
                      type="monotone"
                      dataKey="forecast"
                      stroke="var(--color-warning)"
                      fill="url(#gFor)"
                      strokeWidth={2.5}
                      strokeDasharray="5 4"
                      activeDot={{ r: 5 }}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Warehouse Capacity Forecast */}
            <div className="rounded-2xl border border-border/70 bg-card p-5">
              <div className="flex items-start justify-between gap-3 mb-4">
                <div>
                  <h3 className="text-[15px] font-bold font-[family-name:var(--font-heading)] tracking-tight">
                    Warehouse Capacity Forecast
                  </h3>
                  <p className="text-xs text-muted-foreground mt-0.5">
                    % occupancy · current trajectory vs 80% capacity threshold
                  </p>
                </div>
                <div className="inline-flex items-center gap-1 text-[11px] font-semibold text-warning-foreground bg-warning/15 border border-warning/30 rounded-md px-2 py-0.5">
                  <Flame className="size-3" />
                  Threshold breach in 60d
                </div>
              </div>
              <div className="h-72 -mx-2">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={capacityForecast}
                    margin={{ top: 10, right: 12, left: 0, bottom: 0 }}
                    barCategoryGap="22%"
                  >
                    <defs>
                      <linearGradient id="bAct" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="var(--color-primary)" stopOpacity={1} />
                        <stop offset="100%" stopColor="var(--color-primary)" stopOpacity={0.55} />
                      </linearGradient>
                      <linearGradient id="bProj" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="var(--color-warning)" stopOpacity={1} />
                        <stop offset="100%" stopColor="var(--color-warning)" stopOpacity={0.55} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid
                      stroke="var(--color-border)"
                      strokeDasharray="3 3"
                      vertical={false}
                    />
                    <XAxis
                      dataKey="month"
                      tick={{
                        fill: "var(--color-muted-foreground)",
                        fontSize: 11,
                        fontWeight: 500,
                      }}
                      axisLine={false}
                      tickLine={false}
                    />
                    <YAxis
                      tick={{ fill: "var(--color-muted-foreground)", fontSize: 11 }}
                      axisLine={false}
                      tickLine={false}
                      width={36}
                      domain={[0, 100]}
                      unit="%"
                    />
                    <Tooltip
                      cursor={{ fill: "color-mix(in oklab, var(--color-primary) 6%, transparent)" }}
                      contentStyle={{
                        background: "var(--color-card)",
                        border: "1px solid var(--color-border)",
                        borderRadius: 10,
                        fontSize: 12,
                        boxShadow: "0 8px 24px -12px rgba(15,23,42,0.18)",
                      }}
                    />
                    <ReferenceLine
                      y={80}
                      stroke="var(--color-destructive)"
                      strokeDasharray="4 4"
                      label={{
                        value: "Capacity threshold 80%",
                        position: "insideTopLeft",
                        fill: "var(--color-destructive)",
                        fontSize: 10,
                        fontWeight: 600,
                      }}
                    />
                    <Bar dataKey="actual" name="Actual" fill="url(#bAct)" radius={[6, 6, 0, 0]} />
                    <Bar
                      dataKey="projected"
                      name="Projected"
                      fill="url(#bProj)"
                      radius={[6, 6, 0, 0]}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        </section>

        {/* ===================== Cold Chain (expandable) ===================== */}
        <section>
          <details className="group rounded-2xl border border-border/70 bg-card overflow-hidden">
            <summary className="cursor-pointer list-none p-5 flex items-center justify-between gap-3 hover:bg-muted/30 transition-colors">
              <div className="flex items-center gap-3 min-w-0">
                <div className="size-9 rounded-xl bg-teal/12 text-teal grid place-items-center shrink-0">
                  <Snowflake className="size-4" />
                </div>
                <div className="min-w-0">
                  <h3 className="text-[15px] font-bold font-[family-name:var(--font-heading)] tracking-tight">
                    Cold Chain Health
                  </h3>
                  <p className="text-xs text-muted-foreground mt-0.5">
                    Live zone telemetry across temperature-controlled storage
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <span className="inline-flex items-center gap-1.5 text-[11px] text-success font-semibold">
                  <Activity className="size-3" />
                  98.7% compliance
                </span>
                <ArrowRight className="size-4 text-muted-foreground transition-transform duration-300 group-open:rotate-90" />
              </div>
            </summary>

            <div className="px-5 pb-5 pt-1">
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {zones.map((z) => {
                  const pct = Math.round((z.occupied / z.capacity) * 100);
                  const warn = pct >= 80;
                  const Icon = z.name.includes("Frozen")
                    ? Snowflake
                    : z.name.includes("Cold")
                      ? Thermometer
                      : Warehouse;
                  return (
                    <div
                      key={z.id}
                      className="rounded-xl border border-border/60 bg-card/50 p-4 transition-colors hover:bg-muted/40"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <div
                            className={`size-8 rounded-lg grid place-items-center ${warn ? "bg-warning/15 text-warning-foreground" : "bg-teal/15 text-teal"}`}
                          >
                            <Icon className="size-4" />
                          </div>
                          <div>
                            <div className="text-[13px] font-semibold leading-tight">{z.name}</div>
                            <div className="text-[10.5px] text-muted-foreground tabular-nums">
                              {z.temperature}
                            </div>
                          </div>
                        </div>
                        <div
                          className={`text-[18px] font-bold font-[family-name:var(--font-heading)] tabular-nums ${warn ? "text-warning-foreground" : "text-foreground"}`}
                        >
                          {pct}%
                        </div>
                      </div>
                      <div className="mt-3 h-1.5 w-full rounded-full bg-muted overflow-hidden">
                        <div
                          className={`h-full rounded-full transition-all duration-700 ${warn ? "bg-warning" : "bg-primary"}`}
                          style={{ width: `${pct}%` }}
                        />
                      </div>
                      <div className="mt-2 text-[10.5px] text-muted-foreground tabular-nums">
                        {z.occupied.toLocaleString()} / {z.capacity.toLocaleString()} slots
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </details>
        </section>
      </div>
    </AppLayout>
  );
}
