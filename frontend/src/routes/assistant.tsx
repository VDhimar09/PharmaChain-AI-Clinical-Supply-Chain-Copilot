import { createFileRoute } from "@tanstack/react-router";
import { AppLayout } from "@/components/AppLayout";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { StatusBadge } from "@/components/StatusBadge";
import {
  Sparkles,
  CheckCircle2,
  ShieldCheck,
  Warehouse,
  AlertTriangle,
  User,
  Thermometer,
  Snowflake,
  Package,
  TrendingUp,
  BrainCircuit,
  CalendarDays,
  Box,
  ArrowRight,
  Radio,
  Activity,
  Lock,
} from "lucide-react";

import { useState } from "react";

export const Route = createFileRoute("/assistant")({
  head: () => ({
    meta: [
      { title: "AI Procurement Assistant — PharmaChain Supply Copilot" },
      {
        name: "description",
        content: "AI-powered procurement recommendations for pharmaceutical inventory.",
      },
    ],
  }),
  component: AssistantPage,
});

const suppliers = [
  "Pfizer Global Logistics",
  "Moderna Distribution",
  "Sanofi Pharma",
  "Merck Logistics",
  "Roche Clinical",
  "Novartis Supply Co",
  "GSK Distribution",
  "Bayer Pharma",
  "AstraZeneca Logistics",
];

const products = [
  "Pfizer COVID-19 Vaccine",
  "Moderna mRNA-1273",
  "Insulin Glargine",
  "Trial Compound X-117",
  "Amoxicillin 500mg",
  "Influenza Quadrivalent",
  "Oncology Trial OXC-44",
  "Heparin Sodium",
  "HPV Gardasil 9",
  "Trial Biologic BIO-22",
  "Paracetamol IV",
  "MMR Vaccine",
];

const temps = [
  "-80°C (Ultra Low)",
  "-70°C (Deep Freeze)",
  "-20°C (Frozen)",
  "2-8°C (Refrigerated)",
  "15-25°C (Ambient)",
];

function AssistantPage() {
  const [product, setProduct] = useState("Pfizer COVID-19 Vaccine");
  const [supplier, setSupplier] = useState("Pfizer Global Logistics");
  const [quantity, setQuantity] = useState("2000");
  const [temp, setTemp] = useState("-70°C (Deep Freeze)");
  const [arrival, setArrival] = useState("2026-07-15");

  const [submitted, setSubmitted] = useState<null | {
    product: string;
    supplier: string;
    quantity: string;
    temp: string;
    arrival: string;
  }>(null);
  const [loading, setLoading] = useState(false);

  function analyze() {
    setLoading(true);
    setSubmitted(null);
    setTimeout(() => {
      setSubmitted({ product, supplier, quantity, temp, arrival });
      setLoading(false);
    }, 1600);

  }

  const approved = true;

  return (
    <AppLayout>
      <div className="grid gap-6 xl:grid-cols-[minmax(0,460px)_minmax(0,1fr)]">
        {/* ─── LEFT: Prompt-style Procurement Request ─── */}
        <Card className="h-fit overflow-hidden">
          <div className="px-6 pt-6 pb-4 border-b border-border/60 bg-gradient-to-b from-muted/40 to-transparent">
            <div className="flex items-center gap-2">
              <span className="size-1.5 rounded-full bg-primary shadow-[0_0_10px_color-mix(in_oklab,var(--color-primary)_70%,transparent)]" />
              <span className="text-[10px] font-bold uppercase tracking-[0.22em] text-primary">
                New procurement intent
              </span>
            </div>
            <h2 className="mt-2 text-[22px] font-bold font-[family-name:var(--font-heading)] tracking-tight text-foreground">
              Draft AI request
            </h2>
            <p className="mt-1 text-[13px] text-muted-foreground leading-relaxed">
              Compose the request below. The Copilot will reason across capacity, cold-chain, expiry, and demand forecasts.
            </p>
          </div>

          <CardContent className="p-6 space-y-6">
            {/* Natural-language prompt */}
            <div>
              <div className="text-[10px] font-semibold uppercase tracking-[0.18em] text-muted-foreground mb-3">
                The request
              </div>
              <div className="text-[17px] leading-[1.85] font-light text-foreground/85 font-[family-name:var(--font-heading)]">
                Procure{" "}
                <InlineNumberInput
                  id="quantity"
                  value={quantity}
                  onChange={setQuantity}
                  placeholder="0"
                  width="w-20"
                />{" "}
                units of{" "}
                <InlineSelect id="product" value={product} onChange={setProduct} options={products} />
                {" "}from{" "}
                <InlineSelect id="supplier" value={supplier} onChange={setSupplier} options={suppliers} />
                , arriving{" "}
                <InlineDateInput id="arrival" value={arrival} onChange={setArrival} />{" "}
                at{" "}
                <InlineSelect id="temp" value={temp} onChange={setTemp} options={temps} />.
              </div>
            </div>

            {/* Auto-detected chips */}
            <div>
              <div className="text-[10px] font-semibold uppercase tracking-[0.18em] text-muted-foreground mb-2 flex items-center gap-1.5">
                <Sparkles className="size-3 text-primary" />
                Copilot detected
              </div>
              <div className="flex flex-wrap gap-2">
                {temp.includes("-70") || temp.includes("-80") ? (
                  <Badge variant="outline" className="text-teal border-teal/40 bg-teal/10 gap-1">
                    <Snowflake className="size-3" /> Deep Freeze Chain
                  </Badge>
                ) : temp.includes("-20") ? (
                  <Badge variant="outline" className="text-info border-info/40 bg-info/10 gap-1">
                    <Snowflake className="size-3" /> Frozen Chain
                  </Badge>
                ) : temp.includes("2-8") ? (
                  <Badge variant="outline" className="text-primary border-primary/40 bg-primary/10 gap-1">
                    <Thermometer className="size-3" /> Cold Chain
                  </Badge>
                ) : (
                  <Badge variant="outline" className="text-muted-foreground border-border bg-muted/50 gap-1">
                    <Thermometer className="size-3" /> Ambient
                  </Badge>
                )}
                {daysUntil(arrival) <= 14 && (
                  <Badge variant="outline" className="text-warning-foreground border-warning/40 bg-warning/10 gap-1">
                    <AlertTriangle className="size-3" /> Short Lead Time · {daysUntil(arrival)}d
                  </Badge>
                )}
                <Badge variant="outline" className="text-success border-success/40 bg-success/10 gap-1">
                  <ShieldCheck className="size-3" /> GxP validated supplier
                </Badge>
              </div>
            </div>

            <Button
              onClick={analyze}
              disabled={loading}
              className="w-full h-11 bg-gradient-to-r from-primary to-teal hover:opacity-95 shadow-lg shadow-primary/20 group"
            >
              <BrainCircuit className="size-4 mr-2" />
              {loading ? "Analyzing…" : "Analyze procurement"}
              <ArrowRight className="size-4 ml-2 transition-transform group-hover:translate-x-0.5" />
            </Button>

            <div className="flex items-center justify-between text-[11px] text-muted-foreground pt-2 border-t border-border/50">
              <span className="inline-flex items-center gap-1.5">
                <Lock className="size-3" /> GxP · HIPAA · GDPR
              </span>
              <span>Draft auto-saves</span>
            </div>
          </CardContent>
        </Card>

        {/* ─── RIGHT: AI Copilot canvas ─── */}
        <div className="space-y-4">
          {!submitted && !loading && <CopilotStandby />}

          {submitted && (
            <Card className="bg-secondary/40">
              <CardContent className="p-5 flex items-start gap-3 justify-end flex-row-reverse">
                <div className="size-9 rounded-full bg-muted grid place-items-center shrink-0">
                  <User className="size-4" />
                </div>
                <div className="text-sm leading-relaxed text-right">
                  <div className="font-medium">You</div>
                  <p className="text-muted-foreground mt-1">
                    Requesting <span className="text-foreground font-medium">{submitted.quantity} units</span> of{" "}
                    <span className="text-foreground font-medium">{submitted.product}</span> from{" "}
                    <span className="text-foreground font-medium">{submitted.supplier}</span>, arriving{" "}
                    <span className="text-foreground font-medium">{submitted.arrival}</span>.
                  </p>
                </div>
              </CardContent>
            </Card>
          )}

          {loading && <AiThinking />}

          {submitted && !loading && (
            <Card className="overflow-hidden border-success/40 animate-in fade-in slide-in-from-bottom-2 duration-500">


              {/* Header */}
              <div className="bg-gradient-to-r from-success/20 via-success/5 to-transparent px-6 py-5 flex items-center justify-between border-b border-success/30">
                <div className="flex items-center gap-3">
                  <div className="size-12 rounded-full bg-success text-success-foreground grid place-items-center shadow-lg shadow-success/30">
                    <CheckCircle2 className="size-6" />
                  </div>
                  <div>
                    <div className="text-xs uppercase tracking-wider text-success font-semibold">Recommendation</div>
                    <div className="text-xl font-bold">APPROVED</div>
                  </div>
                </div>
                <div className="flex flex-col items-end gap-2">
                  <StatusBadge label="Risk: LOW" tone="success" />
                  <Badge variant="outline" className="text-primary border-primary/40 bg-primary/10 gap-1">
                    <BrainCircuit className="size-3" /> 94% Confidence
                  </Badge>
                </div>
              </div>

              <CardContent className="p-6 space-y-6">
                {/* Metrics Grid */}
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  <MetricCard
                    icon={Warehouse}
                    label="Current Occupancy"
                    value="72%"
                    sub="1,080 / 1,500 pallets"
                    bar={72}
                    barTone="primary"
                  />
                  <MetricCard
                    icon={TrendingUp}
                    label="Forecast Occupancy"
                    value="84%"
                    sub="1,260 / 1,500 pallets"
                    bar={84}
                    barTone="teal"
                  />
                  <MetricCard
                    icon={Warehouse}
                    label="Recommended Zone"
                    value="Cold Storage B"
                    sub="2-8°C capacity"
                  />
                  <MetricCard
                    icon={AlertTriangle}
                    label="Risk Level"
                    value="LOW"
                    valueTone="success"
                    sub="Under 90% safety threshold"
                  />
                  <MetricCard
                    icon={BrainCircuit}
                    label="Confidence Score"
                    value="94%"
                    valueTone="primary"
                    sub="Based on 6 months of data"
                  />
                  <MetricCard
                    icon={Thermometer}
                    label="Temperature Fit"
                    value="Match"
                    valueTone="teal"
                    sub="Cold chain validated"
                  />
                </div>

                {/* Cold Chain & Expiry Indicators */}
                <div className="flex flex-wrap gap-2">
                  <Badge variant="outline" className="text-primary border-primary/40 bg-primary/10 gap-1">
                    <Thermometer className="size-3" /> Cold Chain: Verified
                  </Badge>
                  <Badge variant="outline" className="text-success border-success/40 bg-success/10 gap-1">
                    <Snowflake className="size-3" /> Continuous Monitoring
                  </Badge>
                  <Badge variant="outline" className="text-teal border-teal/40 bg-teal/10 gap-1">
                    <ShieldCheck className="size-3" /> GxP Compliant
                  </Badge>
                  <Badge variant="outline" className="text-warning-foreground border-warning/40 bg-warning/10 gap-1">
                    <AlertTriangle className="size-3" /> Expiry Risk: Low
                  </Badge>
                  <Badge variant="outline" className="text-muted-foreground border-border bg-muted/50 gap-1">
                    <CalendarDays className="size-3" /> Shelf Life: 14 mo
                  </Badge>
                </div>

                {/* Reasoning */}
                <div className="rounded-xl border border-border bg-muted/40 p-5 space-y-3">
                  <div className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">Reasoning</div>
                  <div className="grid gap-3">
                    <ReasonItem icon={Warehouse} text="Clinical Trial X ends next month, freeing 30 pallet spaces in Cold Storage B." />
                    <ReasonItem icon={TrendingUp} text="Forecast occupancy stays under the 90% safety threshold even after this shipment." />
                    <ReasonItem icon={Thermometer} text="Arrival window aligns with cold-chain capacity rotation schedule." />
                    <ReasonItem icon={ShieldCheck} text="Supplier cold-chain audit passed (last reviewed 2026-05-12)." />
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </AppLayout>
  );
}

function MetricCard({
  icon: Icon,
  label,
  value,
  sub,
  bar,
  barTone = "primary",
  valueTone = "default",
}: {
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  value: string;
  sub?: string;
  bar?: number;
  barTone?: "primary" | "teal" | "success" | "warning";
  valueTone?: "default" | "success" | "primary" | "teal" | "warning";
}) {
  const toneMap = {
    primary: "text-primary bg-primary/10",
    teal: "text-teal-foreground bg-teal/15",
    success: "text-success bg-success/15",
    warning: "text-warning-foreground bg-warning/15",
  };

  const valueColor = {
    default: "text-foreground",
    primary: "text-primary",
    teal: "text-teal-foreground",
    success: "text-success",
    warning: "text-warning-foreground",
  };

  const barColor = {
    primary: "bg-primary",
    teal: "bg-teal",
    success: "bg-success",
    warning: "bg-warning",
  };

  return (
    <div className="rounded-xl border bg-card p-4 space-y-3">
      <div className="flex items-start justify-between">
        <div className={`size-8 rounded-lg grid place-items-center ${toneMap[barTone]}`}>
          <Icon className="size-4" />
        </div>
        {valueTone !== "default" && (
          <span className={`text-xs font-semibold ${valueColor[valueTone]}`}>{value}</span>
        )}
      </div>
      <div>
        <div className="text-sm font-medium uppercase tracking-wide text-muted-foreground">{label}</div>
        {valueTone === "default" && <div className="text-lg font-bold font-[family-name:var(--font-heading)] mt-0.5">{value}</div>}
        {sub && <div className="text-sm text-muted-foreground mt-0.5">{sub}</div>}
      </div>
      {bar !== undefined && (
        <div className="space-y-1">
          <div className="h-1.5 w-full overflow-hidden rounded-full bg-primary/10">
            <div
              className={`h-full rounded-full ${barColor[barTone]} transition-all`}
              style={{ width: `${bar}%` }}
            />
          </div>
        </div>
      )}
    </div>
  );
}

function ReasonItem({
  icon: Icon,
  text,
}: {
  icon: React.ComponentType<{ className?: string }>;
  text: string;
}) {
  return (
    <div className="flex items-start gap-3">
      <div className="size-6 rounded-md bg-primary/10 grid place-items-center shrink-0 mt-0.5">
        <Icon className="size-3.5 text-primary" />
      </div>
      <p className="text-sm leading-relaxed text-foreground">{text}</p>
    </div>
  );
}

function AiThinking() {
  const steps = [
    "Parsing procurement request…",
    "Scanning warehouse capacity across 4 zones…",
    "Validating cold-chain compatibility…",
    "Cross-referencing 6-month demand forecast…",
    "Composing recommendation…",
  ];
  return (
    <Card className="overflow-hidden animate-in fade-in slide-in-from-bottom-2 duration-300">
      <div className="h-0.5 w-full bg-gradient-to-r from-transparent via-primary to-transparent bg-[length:200%_100%] animate-[ai-shimmer_1.6s_linear_infinite]" />
      <CardContent className="p-5">
        <div className="flex items-center gap-3">
          <div className="relative size-11 shrink-0">
            <div className="absolute inset-0 rounded-2xl border-2 border-primary/25 border-t-primary ai-orbit" />
            <div className="absolute inset-1 rounded-xl bg-gradient-to-br from-primary to-teal grid place-items-center shadow-lg shadow-primary/25">
              <Sparkles className="size-4 text-primary-foreground" />
            </div>
          </div>
          <div className="min-w-0">
            <div className="text-[11px] font-bold uppercase tracking-[0.22em] text-primary">AI Copilot thinking</div>
            <div className="text-[15px] font-semibold ai-shimmer-text">
              Analyzing capacity, demand, and cold-chain integrity
            </div>
          </div>
        </div>
        <ul className="mt-4 grid gap-2">
          {steps.map((s, i) => (
            <li
              key={s}
              className="flex items-center gap-2.5 text-[12.5px] text-muted-foreground opacity-0 animate-in fade-in slide-in-from-left-1"
              style={{ animationDelay: `${i * 140}ms`, animationDuration: "400ms", animationFillMode: "forwards" }}
            >
              <span className="size-1.5 rounded-full bg-primary/70 animate-pulse" />
              <span>{s}</span>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
}

function daysUntil(dateStr: string): number {
  const diff = new Date(dateStr).getTime() - Date.now();
  return Math.max(0, Math.ceil(diff / (1000 * 60 * 60 * 24)));
}

/* ─── Inline prompt controls ─── */

function InlineSelect({
  id,
  value,
  onChange,
  options,
}: {
  id: string;
  value: string;
  onChange: (v: string) => void;
  options: readonly string[];
}) {
  return (
    <span className="relative inline-block align-baseline">
      <select
        id={id}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="appearance-none bg-primary/8 hover:bg-primary/12 focus:bg-primary/14 border-b-2 border-primary/40 hover:border-primary focus:border-primary focus:outline-none rounded-t-md px-2 py-0.5 text-primary font-semibold cursor-pointer transition-colors max-w-[240px] truncate"
      >
        {options.map((o) => (
          <option key={o} value={o} className="text-foreground">
            {o}
          </option>
        ))}
      </select>
    </span>
  );
}

function InlineNumberInput({
  id,
  value,
  onChange,
  placeholder,
  width = "w-20",
}: {
  id: string;
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;
  width?: string;
}) {
  return (
    <input
      id={id}
      type="number"
      value={value}
      placeholder={placeholder}
      onChange={(e) => onChange(e.target.value)}
      className={`${width} bg-primary/8 hover:bg-primary/12 focus:bg-primary/14 border-b-2 border-primary/40 hover:border-primary focus:border-primary focus:outline-none rounded-t-md px-2 py-0.5 text-primary font-semibold text-center tabular-nums transition-colors [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none`}
    />
  );
}

function InlineDateInput({
  id,
  value,
  onChange,
}: {
  id: string;
  value: string;
  onChange: (v: string) => void;
}) {
  return (
    <input
      id={id}
      type="date"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="bg-primary/8 hover:bg-primary/12 focus:bg-primary/14 border-b-2 border-primary/40 hover:border-primary focus:border-primary focus:outline-none rounded-t-md px-2 py-0.5 text-primary font-semibold transition-colors"
    />
  );
}

/* ─── Copilot standby canvas (pharma navy) ─── */

function CopilotStandby() {
  const capabilities = [
    { icon: Warehouse, label: "Capacity scanner", status: "Ready" },
    { icon: Snowflake, label: "Cold-chain validator", status: "Ready" },
    { icon: TrendingUp, label: "Demand forecaster", status: "Ready" },
    { icon: CalendarDays, label: "Expiry monitor", status: "Ready" },
  ];

  return (
    <div
      className="relative overflow-hidden rounded-2xl min-h-[560px] xl:min-h-[640px] border shadow-[0_20px_60px_-30px_color-mix(in_oklab,#0b1e3a_75%,transparent)] animate-in fade-in duration-500"
      style={{
        background:
          "radial-gradient(120% 100% at 100% 0%, color-mix(in oklab, #0f2c52 92%, transparent) 0%, #0a1f3d 55%, #071528 100%)",
        borderColor: "color-mix(in oklab, #ffffff 10%, transparent)",
      }}
    >
      {/* Ambient glows */}
      <div
        aria-hidden
        className="absolute top-[-15%] right-[-10%] size-[520px] rounded-full blur-3xl opacity-40 pointer-events-none"
        style={{
          background:
            "radial-gradient(circle, color-mix(in oklab, var(--color-primary) 60%, transparent) 0%, transparent 70%)",
        }}
      />
      <div
        aria-hidden
        className="absolute bottom-[-20%] left-[-10%] size-[420px] rounded-full blur-3xl opacity-30 pointer-events-none"
        style={{
          background:
            "radial-gradient(circle, color-mix(in oklab, var(--color-teal) 55%, transparent) 0%, transparent 70%)",
        }}
      />
      {/* Subtle grid */}
      <div
        aria-hidden
        className="absolute inset-0 opacity-[0.06] pointer-events-none"
        style={{
          backgroundImage:
            "radial-gradient(circle, #ffffff 1px, transparent 1px)",
          backgroundSize: "28px 28px",
        }}
      />

      {/* Top status bar */}
      <div className="relative flex items-center justify-between px-6 pt-5 text-[10px] font-mono uppercase tracking-[0.18em] text-white/45">
        <span className="inline-flex items-center gap-2">
          <span className="relative flex size-1.5">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-70" />
            <span className="relative inline-flex size-1.5 rounded-full bg-emerald-400" />
          </span>
          Copilot · online
        </span>
        <span className="inline-flex items-center gap-4">
          <span>Model · pharma-supply-v2.4</span>
          <span className="hidden sm:inline">Latency · 42ms</span>
        </span>
      </div>

      {/* Center hero */}
      <div className="relative flex flex-col items-center text-center px-8 pt-14 pb-10">
        <div className="relative mb-7">
          <div
            className="absolute -inset-6 rounded-full border ai-orbit"
            style={{ borderColor: "color-mix(in oklab, var(--color-primary) 35%, transparent)" }}
          />
          <div
            className="absolute -inset-3 rounded-full border"
            style={{ borderColor: "color-mix(in oklab, var(--color-teal) 25%, transparent)" }}
          />
          <div
            className="relative size-20 rounded-2xl grid place-items-center backdrop-blur-xl border"
            style={{
              background:
                "linear-gradient(135deg, color-mix(in oklab, var(--color-primary) 65%, transparent), color-mix(in oklab, var(--color-teal) 55%, transparent))",
              borderColor: "color-mix(in oklab, #ffffff 20%, transparent)",
              boxShadow:
                "0 10px 40px -10px color-mix(in oklab, var(--color-primary) 60%, transparent)",
            }}
          >
            <Sparkles className="size-8 text-white" />
          </div>
        </div>

        <div className="text-[10px] font-bold uppercase tracking-[0.28em] text-emerald-300/80 mb-2">
          Procurement Copilot
        </div>
        <h3 className="text-white text-[26px] font-bold font-[family-name:var(--font-heading)] tracking-tight">
          Standing by
        </h3>
        <p className="mt-2 max-w-md text-[13.5px] leading-relaxed text-white/60">
          Copilot is monitoring warehouse telemetry in real time. Complete your request on the left to run
          capacity, cold-chain, expiry, and demand analysis.
        </p>

        {/* Capability grid */}
        <div className="mt-10 grid grid-cols-1 sm:grid-cols-2 gap-2.5 w-full max-w-lg">
          {capabilities.map((c) => {
            const Icon = c.icon;
            return (
              <div
                key={c.label}
                className="group flex items-center justify-between rounded-xl border px-3.5 py-2.5 transition-colors hover:bg-white/[0.04]"
                style={{
                  background: "color-mix(in oklab, #ffffff 3%, transparent)",
                  borderColor: "color-mix(in oklab, #ffffff 8%, transparent)",
                }}
              >
                <div className="flex items-center gap-2.5 min-w-0">
                  <span
                    className="size-7 rounded-lg grid place-items-center shrink-0 transition-colors"
                    style={{
                      background:
                        "color-mix(in oklab, var(--color-primary) 20%, transparent)",
                      color: "color-mix(in oklab, var(--color-primary) 80%, #ffffff)",
                    }}
                  >
                    <Icon className="size-3.5" />
                  </span>
                  <span className="text-[12.5px] text-white/80 truncate text-left">{c.label}</span>
                </div>
                <span className="inline-flex items-center gap-1.5 text-[10px] font-mono uppercase tracking-wider text-emerald-300/90">
                  <span className="size-1 rounded-full bg-emerald-400" />
                  {c.status}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Bottom telemetry */}
      <div className="relative px-6 pb-5">
        <div className="h-px w-full bg-gradient-to-r from-transparent via-white/15 to-transparent mb-3" />
        <div className="flex flex-wrap items-center justify-between gap-3 text-[10px] font-mono uppercase tracking-[0.18em] text-white/45">
          <span className="inline-flex items-center gap-1.5">
            <Radio className="size-3" />
            4 zones · 12 sensors
          </span>
          <span className="inline-flex items-center gap-1.5">
            <Activity className="size-3" />
            Last scan · 2s ago
          </span>
          <span className="inline-flex items-center gap-1.5">
            <Lock className="size-3" />
            GxP · HIPAA · GDPR
          </span>
        </div>
      </div>
    </div>
  );
}


