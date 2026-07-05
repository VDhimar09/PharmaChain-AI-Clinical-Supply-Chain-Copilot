import { createFileRoute } from "@tanstack/react-router";
import { AppLayout } from "@/components/AppLayout";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { StatusBadge, statusTone } from "@/components/StatusBadge";
import { inventory, zones, shipments, inventoryTrend } from "@/lib/mock-data";
import {
  BrainCircuit,
  Sparkles,
  ShieldCheck,
  Snowflake,
  Thermometer,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  CheckCircle2,
  Activity,
  Radio,
  Lock,
  ArrowRight,
  Clock,
  Wrench,
  Warehouse as WarehouseIcon,
  Package as PackageIcon,
  Truck,
  FileCheck2,
  Eye,
  Zap,
  FlaskConical,
  RefreshCw,
  Download,
} from "lucide-react";
import {
  AreaChart,
  Area,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  CartesianGrid,
  ReferenceLine,
  RadialBarChart,
  RadialBar,
  PolarAngleAxis,
} from "recharts";
import type { ComponentType } from "react";

export const Route = createFileRoute("/insights")({
  head: () => ({
    meta: [
      { title: "AI Insights — PharmaChain Decision Intelligence Center" },
      {
        name: "description",
        content:
          "Enterprise AI command center for pharmaceutical supply chain — executive summary, risk heatmap, forecasts, and copilot decisions.",
      },
      { property: "og:title", content: "AI Insights — PharmaChain Decision Intelligence" },
      {
        property: "og:description",
        content:
          "Executive AI briefings, risk heatmap, forecasts, and procurement decisions across the clinical supply chain.",
      },
    ],
  }),
  component: InsightsPage,
});

/* ─────────────────────────────  derived intelligence  ───────────────────────────── */

const critical = inventory.filter((i) => i.status === "Critical").length;
const lowStock = inventory.filter((i) => i.status === "Low Stock").length;
const expiring = inventory.filter((i) => i.status === "Expiring Soon").length;
const inStock = inventory.filter((i) => i.status === "In Stock").length;
const inventoryHealth = Math.round((inStock / inventory.length) * 100);

const totalCap = zones.reduce((a, z) => a + z.capacity, 0);
const totalOcc = zones.reduce((a, z) => a + z.occupied, 0);
const totalFc = zones.reduce((a, z) => a + z.forecast, 0);
const capacityHealth = Math.max(0, 100 - Math.round((totalFc / totalCap) * 100));

const delayed = shipments.filter((s) => s.status === "Delayed").length;
const shipmentHealth = Math.round(((shipments.length - delayed) / shipments.length) * 100);

const coldChainHealth = 96; // preview capability — telemetry stream not yet wired
const overallHealth = Math.round(
  inventoryHealth * 0.3 + capacityHealth * 0.25 + shipmentHealth * 0.25 + coldChainHealth * 0.2,
);

const forecastSeries = [
  ...inventoryTrend.map((t) => ({ ...t, kind: "actual" as const })),
  { month: "Jul", inventory: 49100, demand: 44200, kind: "forecast" as const },
  { month: "Aug", inventory: 50700, demand: 46000, kind: "forecast" as const },
  { month: "Sep", inventory: 52200, demand: 47800, kind: "forecast" as const },
];

const timeline = [
  {
    time: "2m ago",
    type: "recommendation" as const,
    title: "Rebalance 30 pallets · Trial X → Cold Storage A",
    detail: "Cold Storage B forecast to hit 84% on Jul 12. Avoids overflow and detention costs.",
    confidence: 92,
    icon: WarehouseIcon,
  },
  {
    time: "9m ago",
    type: "risk" as const,
    title: "Stock-out risk detected · Influenza Quadrivalent",
    detail: "95 units · projected stock-out in 9 days. Sanofi lead time 5 days.",
    confidence: 91,
    icon: AlertTriangle,
  },
  {
    time: "22m ago",
    type: "approval" as const,
    title: "Approved procurement · SHP-10231 (Pfizer)",
    detail: "2,400 units · cold-chain + customs docs pass automated checks.",
    confidence: 96,
    icon: CheckCircle2,
  },
  {
    time: "1h ago",
    type: "risk" as const,
    title: "Carrier disruption · SHP-10235",
    detail: "Weather-related delay · reroute via Frankfurt recovers ~36h.",
    confidence: 87,
    icon: Truck,
  },
  {
    time: "3h ago",
    type: "insight" as const,
    title: "Demand spike · Q3 Insulin Glargine (+12%)",
    detail: "Model detects seasonal driver. Recommend PO to Novartis this week.",
    confidence: 84,
    icon: TrendingUp,
  },
];

const tools = [
  { name: "Capacity Scanner", runs: 148, latency: "38ms", icon: WarehouseIcon, status: "healthy" as const },
  { name: "Cold-Chain Validator", runs: 96, latency: "52ms", icon: Snowflake, status: "healthy" as const },
  { name: "Demand Forecaster", runs: 42, latency: "410ms", icon: TrendingUp, status: "healthy" as const },
  { name: "Expiry Monitor", runs: 210, latency: "24ms", icon: Clock, status: "healthy" as const },
  { name: "Supplier Audit", runs: 18, latency: "1.2s", icon: ShieldCheck, status: "healthy" as const },
  { name: "Route Optimizer", runs: 34, latency: "620ms", icon: Truck, status: "degraded" as const },
];

/* ────────────────────────────────────  page  ──────────────────────────────────── */

function InsightsPage() {
  return (
    <AppLayout>
      <div className="space-y-6">
        {/* ═════ 1. Executive AI Summary ═════ */}
        <ExecutiveSummary />

        {/* ═════ 2. Health strip + Confidence rail ═════ */}
        <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_320px]">
          <HealthComposite />
          <ConfidenceRail />
        </div>

        {/* ═════ 3. Recommendations ═════ */}
        <Recommendations />

        {/* ═════ 4. Risk Heatmap + Forecast ═════ */}
        <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_minmax(0,1.15fr)]">
          <RiskHeatmap />
          <ForecastPanel />
        </div>

        {/* ═════ 5. Timeline + Tool activity ═════ */}
        <div className="grid gap-4 xl:grid-cols-[minmax(0,1.3fr)_minmax(0,1fr)]">
          <AiTimeline />
          <ToolActivity />
        </div>

        {/* ═════ 6. Recent Procurement Decisions ═════ */}
        <RecentDecisions />
      </div>
    </AppLayout>
  );
}

/* ═══════════════════════════════  1. Exec Summary  ═══════════════════════════════ */

function ExecutiveSummary() {
  return (
    <section
      className="relative overflow-hidden rounded-2xl border shadow-[0_20px_60px_-30px_color-mix(in_oklab,#0b1e3a_75%,transparent)]"
      style={{
        background:
          "radial-gradient(120% 100% at 100% 0%, color-mix(in oklab, #0f2c52 92%, transparent) 0%, #0a1f3d 55%, #071528 100%)",
        borderColor: "color-mix(in oklab, #ffffff 10%, transparent)",
      }}
    >
      {/* ambient glows */}
      <div
        aria-hidden
        className="absolute -top-24 -right-16 size-[520px] rounded-full blur-3xl opacity-40 pointer-events-none"
        style={{
          background:
            "radial-gradient(circle, color-mix(in oklab, var(--color-primary) 60%, transparent) 0%, transparent 70%)",
        }}
      />
      <div
        aria-hidden
        className="absolute -bottom-24 -left-16 size-[420px] rounded-full blur-3xl opacity-25 pointer-events-none"
        style={{
          background:
            "radial-gradient(circle, color-mix(in oklab, var(--color-teal) 55%, transparent) 0%, transparent 70%)",
        }}
      />
      <div
        aria-hidden
        className="absolute inset-0 opacity-[0.05] pointer-events-none"
        style={{
          backgroundImage: "radial-gradient(circle, #ffffff 1px, transparent 1px)",
          backgroundSize: "28px 28px",
        }}
      />

      <div className="relative p-6 md:p-8">
        <div className="flex items-start justify-between gap-4 flex-wrap">
          <div className="flex items-center gap-2 text-[10px] font-mono uppercase tracking-[0.22em] text-emerald-300/85">
            <span className="relative flex size-1.5">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-70" />
              <span className="relative inline-flex size-1.5 rounded-full bg-emerald-400" />
            </span>
            Decision Intelligence · live
            <span className="text-white/30 mx-2">·</span>
            <span className="text-white/50">Model pharma-supply-v2.4</span>
            <span className="text-white/30 mx-2">·</span>
            <span className="text-white/50">Refreshed 2s ago</span>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              className="h-8 gap-1.5 bg-white/[0.06] border-white/15 text-white/90 hover:bg-white/[0.1] hover:text-white"
            >
              <RefreshCw className="size-3.5" />
              Re-run analysis
            </Button>
            <Button
              variant="outline"
              size="sm"
              className="h-8 gap-1.5 bg-white/[0.06] border-white/15 text-white/90 hover:bg-white/[0.1] hover:text-white"
            >
              <Download className="size-3.5" />
              Export briefing
            </Button>
          </div>
        </div>

        <div className="mt-5 grid gap-8 lg:grid-cols-[minmax(0,1fr)_auto] items-start">
          <div className="min-w-0">
            <h1 className="text-white text-[30px] md:text-[36px] leading-[1.1] font-bold font-[family-name:var(--font-heading)] tracking-tight">
              Supply chain is <span className="text-emerald-300">stable</span>, with{" "}
              <span className="text-amber-300">2 emerging risks</span> to address today.
            </h1>
            <p className="mt-3 max-w-3xl text-[14.5px] leading-relaxed text-white/70">
              Copilot analyzed {inventory.length} SKUs across {zones.length} storage zones and{" "}
              {shipments.length} active shipments. Inventory levels are ahead of demand through Q3,
              but <span className="text-white">{critical} SKUs are critical</span> and{" "}
              <span className="text-white">Cold Storage B is forecast to reach 84% within 14 days</span>.
              {delayed} inbound shipments require attention.
            </p>

            <div className="mt-5 flex flex-wrap gap-2">
              <HeroChip icon={AlertTriangle} tone="warning">
                {critical + lowStock} stock alerts
              </HeroChip>
              <HeroChip icon={WarehouseIcon} tone="warning">
                1 zone at 80%+ forecast
              </HeroChip>
              <HeroChip icon={Truck} tone="destructive">
                {delayed} shipments delayed
              </HeroChip>
              <HeroChip icon={Snowflake} tone="success">
                Cold chain nominal
              </HeroChip>
              <HeroChip icon={ShieldCheck} tone="success">
                GxP · HIPAA · GDPR
              </HeroChip>
            </div>
          </div>

          {/* Composite score */}
          <div className="flex items-center gap-6 rounded-2xl border border-white/10 bg-white/[0.04] p-5 backdrop-blur-xl">
            <div className="relative size-32">
              <ResponsiveContainer width="100%" height="100%">
                <RadialBarChart
                  innerRadius="72%"
                  outerRadius="100%"
                  data={[{ v: overallHealth }]}
                  startAngle={90}
                  endAngle={-270}
                >
                  <PolarAngleAxis type="number" domain={[0, 100]} tick={false} />
                  <RadialBar dataKey="v" cornerRadius={12} fill="#34d399" background={{ fill: "rgba(255,255,255,0.08)" }} />
                </RadialBarChart>
              </ResponsiveContainer>
              <div className="absolute inset-0 grid place-items-center text-center">
                <div>
                  <div className="text-white text-[28px] font-bold font-[family-name:var(--font-heading)] tabular-nums leading-none">
                    {overallHealth}
                  </div>
                  <div className="text-[9px] font-mono uppercase tracking-[0.18em] text-white/50 mt-1">
                    Health
                  </div>
                </div>
              </div>
            </div>
            <div className="space-y-2 min-w-[140px]">
              <div className="text-[10px] font-bold uppercase tracking-[0.22em] text-emerald-300">
                Overall status
              </div>
              <div className="text-white text-[15px] font-semibold">Operating normally</div>
              <div className="text-[12px] text-white/60 leading-relaxed">
                Weighted across inventory, capacity, shipments, and cold chain.
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

function HeroChip({
  icon: Icon,
  tone,
  children,
}: {
  icon: ComponentType<{ className?: string }>;
  tone: "success" | "warning" | "destructive";
  children: React.ReactNode;
}) {
  const toneMap = {
    success: "border-emerald-400/40 bg-emerald-400/10 text-emerald-200",
    warning: "border-amber-400/40 bg-amber-400/10 text-amber-200",
    destructive: "border-red-400/40 bg-red-400/10 text-red-200",
  };
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-[11.5px] font-semibold ${toneMap[tone]}`}
    >
      <Icon className="size-3.5" />
      {children}
    </span>
  );
}

/* ═══════════════════════════════  2. Health composite  ═══════════════════════════ */

function HealthComposite() {
  const cards = [
    { label: "Inventory", value: inventoryHealth, sub: `${inStock}/${inventory.length} SKUs healthy`, icon: PackageIcon, tone: healthTone(inventoryHealth) },
    { label: "Capacity", value: capacityHealth, sub: `${Math.round((totalOcc / totalCap) * 100)}% occupied today`, icon: WarehouseIcon, tone: healthTone(capacityHealth) },
    { label: "Shipments", value: shipmentHealth, sub: `${shipments.length - delayed}/${shipments.length} on schedule`, icon: Truck, tone: healthTone(shipmentHealth) },
    { label: "Cold Chain", value: coldChainHealth, sub: "Telemetry preview", icon: Snowflake, tone: healthTone(coldChainHealth), preview: true },
  ];

  return (
    <Card>
      <CardContent className="p-5">
        <SectionHeader
          eyebrow="System"
          title="Supply chain health"
          subtitle="Composite score across four operational dimensions."
        />
        <div className="mt-4 grid grid-cols-2 lg:grid-cols-4 gap-3">
          {cards.map((c) => {
            const Icon = c.icon;
            return (
              <div key={c.label} className="kpi-card p-4">
                <div className="flex items-start justify-between">
                  <span className={`size-8 rounded-lg grid place-items-center ${toneBadge(c.tone)}`}>
                    <Icon className="size-4" />
                  </span>
                  {c.preview && (
                    <span className="text-[9px] font-mono uppercase tracking-wider text-muted-foreground border border-border rounded px-1.5 py-0.5">
                      Preview
                    </span>
                  )}
                </div>
                <div className="mt-3 flex items-baseline gap-1.5">
                  <div className="text-[26px] font-bold font-[family-name:var(--font-heading)] tabular-nums leading-none">
                    {c.value}
                  </div>
                  <div className="text-[11px] text-muted-foreground font-semibold">/ 100</div>
                </div>
                <div className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground mt-2">
                  {c.label}
                </div>
                <div className="text-[11.5px] text-muted-foreground mt-0.5">{c.sub}</div>
                <div className="mt-3 h-1.5 w-full rounded-full bg-muted overflow-hidden">
                  <div
                    className={`h-full rounded-full ${toneBar(c.tone)} transition-all duration-700`}
                    style={{ width: `${c.value}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}

/* ═══════════════════════════════  Confidence rail  ═══════════════════════════════ */

function ConfidenceRail() {
  const rows = [
    { label: "Recommendation confidence", value: 91, tone: "success" as const },
    { label: "Forecast confidence (30d)", value: 84, tone: "primary" as const },
    { label: "Risk detection confidence", value: 88, tone: "success" as const },
    { label: "Model coverage", value: 96, tone: "teal" as const },
  ];
  return (
    <Card>
      <CardContent className="p-5">
        <SectionHeader eyebrow="AI Copilot" title="Confidence" subtitle="Across active reasoning tasks." />
        <div className="mt-4 space-y-3.5">
          {rows.map((r) => (
            <div key={r.label}>
              <div className="flex items-center justify-between text-[12px] mb-1.5">
                <span className="text-muted-foreground">{r.label}</span>
                <span className="font-semibold tabular-nums">{r.value}%</span>
              </div>
              <div className="h-1.5 w-full rounded-full bg-muted overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-700 ${
                    r.tone === "success"
                      ? "bg-success"
                      : r.tone === "primary"
                        ? "bg-primary"
                        : "bg-teal"
                  }`}
                  style={{ width: `${r.value}%` }}
                />
              </div>
            </div>
          ))}
          <div className="pt-3 mt-1 border-t border-border/60 flex items-center justify-between text-[11px] text-muted-foreground">
            <span className="inline-flex items-center gap-1.5">
              <BrainCircuit className="size-3 text-primary" />
              Ensemble · 3 models
            </span>
            <span>Last calibrated 06/24</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

/* ═══════════════════════════════  3. Recommendations  ═══════════════════════════ */

function Recommendations() {
  const critSku = inventory.find((i) => i.status === "Critical");
  const hotZone = zones.reduce((a, b) => (a.forecast / a.capacity > b.forecast / b.capacity ? a : b));
  const inbound = shipments.find((s) => s.status === "In Transit");

  const items = [
    {
      priority: "P1",
      tag: "Stock shortage",
      title: `${critSku?.name ?? "SKU"} below safety stock`,
      detail: `Current ${critSku?.available} units · projected stock-out in 9 days. Initiating PO preserves 14-day coverage.`,
      confidence: 91,
      cta: "Initiate PO",
      tone: "destructive" as const,
      icon: AlertTriangle,
      impact: `+${critSku?.name.split(" ")[0]} · 14d coverage`,
    },
    {
      priority: "P1",
      tag: "Capacity risk",
      title: `Rebalance pallets to ${zones[0].name}`,
      detail: `${hotZone.name} forecast to reach ${Math.round((hotZone.forecast / hotZone.capacity) * 100)}% within 14 days. Move 30 pallets to preserve headroom.`,
      confidence: 92,
      cta: "Review plan",
      tone: "warning" as const,
      icon: WarehouseIcon,
      impact: "Frees 12% capacity",
    },
    {
      priority: "P2",
      tag: "Procurement",
      title: `Approve inbound ${inbound?.id}`,
      detail: `${inbound?.quantity.toLocaleString()} units · cold-chain, temperature, and customs documents pass automated checks.`,
      confidence: 96,
      cta: "Approve",
      tone: "success" as const,
      icon: CheckCircle2,
      impact: "Maintains 28d coverage",
    },
  ];

  return (
    <Card>
      <CardContent className="p-5 md:p-6">
        <div className="flex items-start justify-between gap-3 flex-wrap">
          <SectionHeader
            eyebrow="Copilot"
            title="Today's AI recommendations"
            subtitle="Prioritized decisions with rationale, confidence, and one-click actions."
          />
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="text-primary border-primary/30 bg-primary/8 gap-1">
              <Sparkles className="size-3" /> {items.length} actions
            </Badge>
          </div>
        </div>

        <div className="mt-5 grid gap-4 md:grid-cols-3">
          {items.map((it) => {
            const Icon = it.icon;
            const border = {
              destructive: "border-destructive/40",
              warning: "border-warning/40",
              success: "border-success/40",
            }[it.tone];
            const stripe = {
              destructive: "bg-destructive",
              warning: "bg-warning",
              success: "bg-success",
            }[it.tone];
            const chipTone = {
              destructive: "bg-destructive/10 text-destructive border-destructive/30",
              warning: "bg-warning/15 text-warning-foreground border-warning/30",
              success: "bg-success/15 text-success border-success/30",
            }[it.tone];

            return (
              <div
                key={it.title}
                className={`relative overflow-hidden rounded-2xl border ${border} bg-card transition-all hover:-translate-y-0.5 hover:shadow-[0_12px_32px_-18px_color-mix(in_oklab,var(--color-foreground)_25%,transparent)]`}
              >
                <span className={`absolute left-0 top-4 bottom-4 w-0.5 rounded-r-full ${stripe}`} />
                <div className="p-5 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className={`inline-flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded border ${chipTone}`}>
                      <span className="size-1 rounded-full bg-current" />
                      {it.priority} · {it.tag}
                    </span>
                    <span className="text-[11px] font-semibold text-muted-foreground tabular-nums">
                      {it.confidence}% conf.
                    </span>
                  </div>

                  <div className="flex items-start gap-2.5">
                    <div className={`size-8 rounded-lg grid place-items-center shrink-0 ${chipTone}`}>
                      <Icon className="size-4" />
                    </div>
                    <h3 className="text-[15px] font-bold font-[family-name:var(--font-heading)] leading-snug">
                      {it.title}
                    </h3>
                  </div>

                  <p className="text-[12.5px] leading-relaxed text-muted-foreground">{it.detail}</p>

                  <div className="pt-3 mt-1 border-t border-border/60 flex items-center justify-between gap-2">
                    <span className="inline-flex items-center gap-1.5 text-[11px] text-muted-foreground min-w-0 truncate">
                      <Sparkles className="size-3 text-primary shrink-0" />
                      <span className="truncate">{it.impact}</span>
                    </span>
                    <Button size="sm" className="h-7 text-[11px] gap-1">
                      {it.cta}
                      <ArrowRight className="size-3" />
                    </Button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}

/* ═══════════════════════════════  4a. Risk Heatmap  ══════════════════════════════ */

function RiskHeatmap() {
  const categories = ["Vaccine", "Medicine", "Clinical Trial"] as const;
  const dimensions = ["Stock", "Expiry", "Cold Chain", "Demand"] as const;

  // deterministic risk per (category, dimension) derived from real inventory
  const cell = (cat: (typeof categories)[number], dim: (typeof dimensions)[number]) => {
    const items = inventory.filter((i) => i.category === cat);
    if (dim === "Stock") {
      const risky = items.filter((i) => i.status === "Critical" || i.status === "Low Stock").length;
      return items.length ? Math.round((risky / items.length) * 100) : 0;
    }
    if (dim === "Expiry") {
      const risky = items.filter((i) => i.status === "Expiring Soon").length;
      // scale up for visibility, cap 100
      return Math.min(100, Math.round((risky / Math.max(items.length, 1)) * 100) + (cat === "Clinical Trial" ? 20 : 5));
    }
    if (dim === "Cold Chain") {
      const cold = items.filter((i) => i.temperature.includes("-") || i.temperature.includes("2-8")).length;
      return Math.round((cold / Math.max(items.length, 1)) * 40); // low risk baseline
    }
    // Demand
    return cat === "Vaccine" ? 55 : cat === "Medicine" ? 30 : 42;
  };

  const shade = (v: number) => {
    if (v >= 66) return { bg: "bg-destructive/85", text: "text-destructive-foreground", label: "High" };
    if (v >= 33) return { bg: "bg-warning/70", text: "text-warning-foreground", label: "Med" };
    if (v > 0) return { bg: "bg-success/60", text: "text-success-foreground", label: "Low" };
    return { bg: "bg-muted", text: "text-muted-foreground", label: "—" };
  };

  return (
    <Card>
      <CardContent className="p-5">
        <SectionHeader
          eyebrow="Risk"
          title="Risk heatmap"
          subtitle="AI-scored risk exposure by category × dimension."
        />
        <div className="mt-5">
          <div
            className="grid gap-1.5"
            style={{ gridTemplateColumns: `120px repeat(${dimensions.length}, minmax(0,1fr))` }}
          >
            <div />
            {dimensions.map((d) => (
              <div key={d} className="text-[10.5px] font-semibold uppercase tracking-wider text-muted-foreground text-center pb-1">
                {d}
              </div>
            ))}
            {categories.map((cat) => (
              <>
                <div key={`row-${cat}`} className="flex items-center text-[12.5px] font-semibold pr-2">
                  {cat}
                </div>
                {dimensions.map((dim) => {
                  const v = cell(cat, dim);
                  const s = shade(v);
                  return (
                    <div
                      key={`${cat}-${dim}`}
                      className={`group relative rounded-lg h-16 ${s.bg} ${s.text} grid place-items-center transition-transform hover:scale-[1.03] cursor-pointer`}
                      title={`${cat} · ${dim} · ${v}%`}
                    >
                      <div className="text-center">
                        <div className="text-[16px] font-bold tabular-nums leading-none">{v}</div>
                        <div className="text-[9px] font-semibold uppercase tracking-wider opacity-80 mt-0.5">
                          {s.label}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </>
            ))}
          </div>

          <div className="mt-5 flex items-center justify-between text-[11px] text-muted-foreground">
            <div className="flex items-center gap-3">
              <LegendDot className="bg-success/60" /> Low
              <LegendDot className="bg-warning/70" /> Medium
              <LegendDot className="bg-destructive/85" /> High
            </div>
            <span className="inline-flex items-center gap-1.5">
              <Eye className="size-3" />
              Click a cell to drill into affected SKUs
            </span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function LegendDot({ className }: { className: string }) {
  return <span className={`inline-block size-2 rounded-sm ${className}`} />;
}

/* ═══════════════════════════════  4b. Forecast panel  ═══════════════════════════ */

function ForecastPanel() {
  const cutoffIdx = inventoryTrend.length - 1; // last actual month
  const cutoff = forecastSeries[cutoffIdx].month;

  return (
    <Card>
      <CardContent className="p-5">
        <div className="flex items-start justify-between gap-3">
          <SectionHeader
            eyebrow="Forecast"
            title="Inventory & demand — next 90 days"
            subtitle="Historical actuals with AI-projected inventory and demand tail."
          />
          <div className="flex items-center gap-1.5">
            <Badge variant="outline" className="text-primary border-primary/30 bg-primary/8 text-[10px] gap-1">
              <BrainCircuit className="size-3" /> 84% confidence
            </Badge>
          </div>
        </div>

        <div className="mt-4 h-72">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={forecastSeries} margin={{ top: 8, right: 12, left: 0, bottom: 0 }}>
              <defs>
                <linearGradient id="fInv" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="var(--color-primary)" stopOpacity={0.35} />
                  <stop offset="100%" stopColor="var(--color-primary)" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="fDem" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="var(--color-teal)" stopOpacity={0.28} />
                  <stop offset="100%" stopColor="var(--color-teal)" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 6" stroke="color-mix(in oklab, var(--color-foreground) 10%, transparent)" vertical={false} />
              <XAxis dataKey="month" stroke="var(--color-muted-foreground)" fontSize={11} tickLine={false} axisLine={false} />
              <YAxis stroke="var(--color-muted-foreground)" fontSize={11} tickLine={false} axisLine={false} tickFormatter={(v) => `${Math.round(v / 1000)}k`} />
              <Tooltip
                contentStyle={{
                  background: "var(--color-card)",
                  border: "1px solid var(--color-border)",
                  borderRadius: 12,
                  fontSize: 12,
                }}
              />
              <ReferenceLine
                x={cutoff}
                stroke="var(--color-primary)"
                strokeDasharray="4 4"
                label={{ value: "Today", position: "top", fill: "var(--color-primary)", fontSize: 10 }}
              />
              <Area type="monotone" dataKey="demand" stroke="var(--color-teal)" strokeWidth={2} fill="url(#fDem)" />
              <Area type="monotone" dataKey="inventory" stroke="var(--color-primary)" strokeWidth={2.4} fill="url(#fInv)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="mt-4 grid grid-cols-3 gap-3 text-[12px]">
          <ForecastStat label="Inventory Sep '26" value="52.2k" delta="+9.2%" tone="success" />
          <ForecastStat label="Demand Sep '26" value="47.8k" delta="+13.4%" tone="warning" />
          <ForecastStat label="Coverage buffer" value="4.4k units" delta="−1.1k vs Q2" tone="warning" />
        </div>
      </CardContent>
    </Card>
  );
}

function ForecastStat({
  label,
  value,
  delta,
  tone,
}: {
  label: string;
  value: string;
  delta: string;
  tone: "success" | "warning";
}) {
  const Icon = tone === "success" ? TrendingUp : TrendingDown;
  const color = tone === "success" ? "text-success" : "text-warning-foreground";
  return (
    <div className="rounded-lg border border-border/70 bg-muted/30 p-3">
      <div className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">{label}</div>
      <div className="mt-1 text-[18px] font-bold font-[family-name:var(--font-heading)] tabular-nums leading-none">
        {value}
      </div>
      <div className={`mt-1.5 inline-flex items-center gap-1 text-[11px] font-semibold ${color}`}>
        <Icon className="size-3" />
        {delta}
      </div>
    </div>
  );
}

/* ═══════════════════════════════  5a. AI Timeline  ══════════════════════════════ */

function AiTimeline() {
  return (
    <Card>
      <CardContent className="p-5">
        <div className="flex items-start justify-between gap-3 flex-wrap">
          <SectionHeader
            eyebrow="Activity"
            title="AI decision timeline"
            subtitle="Chronological ledger of insights, actions, and approvals."
          />
          <Badge variant="outline" className="text-primary border-primary/30 bg-primary/8 gap-1">
            <Activity className="size-3" /> live
          </Badge>
        </div>

        <div className="mt-4 relative">
          <div className="absolute left-4 top-2 bottom-2 w-px bg-border" />
          <ul className="space-y-4">
            {timeline.map((e) => {
              const Icon = e.icon;
              const tone =
                e.type === "risk"
                  ? "bg-destructive/12 text-destructive border-destructive/30"
                  : e.type === "approval"
                    ? "bg-success/15 text-success border-success/30"
                    : e.type === "insight"
                      ? "bg-info/12 text-info border-info/30"
                      : "bg-primary/10 text-primary border-primary/30";
              return (
                <li key={e.title} className="relative pl-11">
                  <span
                    className={`absolute left-0 top-0.5 size-8 rounded-full grid place-items-center border-2 bg-card ${tone}`}
                  >
                    <Icon className="size-4" />
                  </span>
                  <div className="flex items-baseline justify-between gap-3 flex-wrap">
                    <div className="text-[10px] font-mono uppercase tracking-wider text-muted-foreground">
                      {e.type} · {e.time}
                    </div>
                    <div className="text-[11px] font-semibold text-muted-foreground tabular-nums">
                      {e.confidence}% conf.
                    </div>
                  </div>
                  <div className="mt-0.5 text-[14px] font-semibold text-foreground leading-snug">
                    {e.title}
                  </div>
                  <div className="mt-0.5 text-[12.5px] text-muted-foreground leading-relaxed">
                    {e.detail}
                  </div>
                </li>
              );
            })}
          </ul>
        </div>
      </CardContent>
    </Card>
  );
}

/* ═══════════════════════════════  5b. Tool activity  ═══════════════════════════ */

function ToolActivity() {
  return (
    <Card>
      <CardContent className="p-5">
        <div className="flex items-start justify-between gap-3">
          <SectionHeader
            eyebrow="Copilot"
            title="Tool activity"
            subtitle="Reasoning tools invoked in the last hour."
          />
          <PreviewChip />
        </div>

        <div className="mt-4 space-y-2">
          {tools.map((t) => {
            const Icon = t.icon;
            const dot = t.status === "healthy" ? "bg-success" : "bg-warning";
            return (
              <div
                key={t.name}
                className="group flex items-center justify-between rounded-lg border border-border/70 bg-card px-3 py-2.5 transition-colors hover:bg-muted/40"
              >
                <div className="flex items-center gap-3 min-w-0">
                  <span className="size-8 rounded-lg bg-primary/10 text-primary grid place-items-center shrink-0">
                    <Icon className="size-4" />
                  </span>
                  <div className="min-w-0">
                    <div className="text-[13px] font-semibold truncate">{t.name}</div>
                    <div className="text-[11px] text-muted-foreground">
                      {t.runs} runs · avg {t.latency}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`size-1.5 rounded-full ${dot}`} />
                  <Zap className="size-3.5 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
                </div>
              </div>
            );
          })}
        </div>

        <div className="mt-4 pt-3 border-t border-border/60 flex items-center justify-between text-[11px] text-muted-foreground">
          <span className="inline-flex items-center gap-1.5">
            <Wrench className="size-3" /> 6 tools · 1 degraded
          </span>
          <span className="inline-flex items-center gap-1.5">
            <Lock className="size-3" /> Audit-logged
          </span>
        </div>
      </CardContent>
    </Card>
  );
}

/* ═══════════════════════════════  6. Recent decisions  ══════════════════════════ */

function RecentDecisions() {
  const rows = shipments.slice(0, 6).map((s, i) => ({
    id: s.id,
    supplier: s.supplier,
    product: s.product,
    quantity: s.quantity,
    arrival: s.arrival,
    status: s.status,
    decision: s.status === "Delayed" ? "Reroute" : i % 3 === 0 ? "Approved" : i % 3 === 1 ? "Auto-approved" : "Review",
    confidence: 82 + ((i * 7) % 15),
  }));

  return (
    <Card>
      <CardContent className="p-5">
        <div className="flex items-start justify-between gap-3 flex-wrap">
          <SectionHeader
            eyebrow="Ledger"
            title="Recent procurement decisions"
            subtitle="Every AI-assisted approval, escalation, and reroute — auditable."
          />
          <Button size="sm" variant="outline" className="h-8 gap-1.5">
            <FileCheck2 className="size-3.5" /> Open audit log
          </Button>
        </div>

        <div className="mt-4 overflow-x-auto">
          <table className="w-full text-[13px] border-separate border-spacing-0">
            <thead>
              <tr className="text-left text-[10.5px] font-semibold uppercase tracking-wider text-muted-foreground">
                <th className="px-3 py-2 border-b border-border/70">Shipment</th>
                <th className="px-3 py-2 border-b border-border/70">Supplier</th>
                <th className="px-3 py-2 border-b border-border/70">Product</th>
                <th className="px-3 py-2 border-b border-border/70 text-right">Qty</th>
                <th className="px-3 py-2 border-b border-border/70">Arrival</th>
                <th className="px-3 py-2 border-b border-border/70">Status</th>
                <th className="px-3 py-2 border-b border-border/70">AI decision</th>
                <th className="px-3 py-2 border-b border-border/70 text-right">Conf.</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.id} className="hover:bg-muted/40 transition-colors">
                  <td className="px-3 py-2.5 border-b border-border/50 font-mono text-[12px]">{r.id}</td>
                  <td className="px-3 py-2.5 border-b border-border/50 font-medium">{r.supplier}</td>
                  <td className="px-3 py-2.5 border-b border-border/50 text-muted-foreground truncate max-w-[220px]">{r.product}</td>
                  <td className="px-3 py-2.5 border-b border-border/50 text-right tabular-nums">{r.quantity.toLocaleString()}</td>
                  <td className="px-3 py-2.5 border-b border-border/50 tabular-nums">{r.arrival}</td>
                  <td className="px-3 py-2.5 border-b border-border/50">
                    <StatusBadge label={r.status} tone={statusTone(r.status)} />
                  </td>
                  <td className="px-3 py-2.5 border-b border-border/50">
                    <DecisionBadge label={r.decision} />
                  </td>
                  <td className="px-3 py-2.5 border-b border-border/50 text-right tabular-nums font-semibold">{r.confidence}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}

function DecisionBadge({ label }: { label: string }) {
  const tone =
    label === "Approved" || label === "Auto-approved"
      ? "bg-success/15 text-success border-success/30"
      : label === "Reroute"
        ? "bg-destructive/12 text-destructive border-destructive/30"
        : "bg-warning/15 text-warning-foreground border-warning/30";
  return (
    <span className={`inline-flex items-center gap-1 text-[11px] font-semibold px-2 py-0.5 rounded border ${tone}`}>
      <BrainCircuit className="size-3" />
      {label}
    </span>
  );
}

/* ═══════════════════════════════  primitives  ════════════════════════════════ */

function SectionHeader({
  eyebrow,
  title,
  subtitle,
}: {
  eyebrow: string;
  title: string;
  subtitle?: string;
}) {
  return (
    <div>
      <div className="text-[10px] font-bold uppercase tracking-[0.22em] text-primary">{eyebrow}</div>
      <h2 className="mt-1 text-[19px] font-bold font-[family-name:var(--font-heading)] tracking-tight leading-tight">
        {title}
      </h2>
      {subtitle && <p className="mt-1 text-[12.5px] text-muted-foreground leading-relaxed">{subtitle}</p>}
    </div>
  );
}

function PreviewChip() {
  return (
    <span className="inline-flex items-center gap-1.5 rounded-md border border-border bg-muted/60 text-muted-foreground px-2 py-0.5 text-[10px] font-mono uppercase tracking-wider">
      <FlaskConical className="size-3" />
      Preview capability
    </span>
  );
}

function healthTone(v: number): "success" | "warning" | "destructive" {
  if (v >= 80) return "success";
  if (v >= 60) return "warning";
  return "destructive";
}
function toneBadge(t: "success" | "warning" | "destructive") {
  return t === "success"
    ? "bg-success/15 text-success"
    : t === "warning"
      ? "bg-warning/15 text-warning-foreground"
      : "bg-destructive/12 text-destructive";
}
function toneBar(t: "success" | "warning" | "destructive") {
  return t === "success" ? "bg-success" : t === "warning" ? "bg-warning" : "bg-destructive";
}
