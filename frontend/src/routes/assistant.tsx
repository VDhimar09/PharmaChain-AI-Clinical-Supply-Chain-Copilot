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
    }, 900);
  }

  const approved = true;

  return (
    <AppLayout>
      <div className="grid gap-6 lg:grid-cols-[380px_1fr]">
        {/* ─── LEFT: Procurement Request Form ─── */}
        <Card className="h-fit">
          <CardContent className="p-6 space-y-5">
            <div className="flex items-center gap-3">
              <div className="size-10 rounded-xl bg-gradient-to-br from-primary to-teal text-primary-foreground grid place-items-center shadow-lg shadow-primary/20">
                <Package className="size-5" />
              </div>
              <div>
              <div className="text-xl font-bold font-[family-name:var(--font-heading)]">Procurement Request</div>
              <p className="text-sm text-muted-foreground">Fill details to get an AI recommendation</p>
              </div>
            </div>

            <div className="space-y-4">
              <div className="space-y-1.5">
                <Label htmlFor="product" className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                  Product
                </Label>
                <div className="relative">
                  <Box className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
                  <select
                    id="product"
                    value={product}
                    onChange={(e) => setProduct(e.target.value)}
                    className="w-full h-9 pl-9 pr-3 rounded-md border border-input bg-transparent text-sm appearance-none focus:outline-none focus:ring-1 focus:ring-ring"
                  >
                    {products.map((p) => (
                      <option key={p} value={p}>
                        {p}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="space-y-1.5">
                <Label htmlFor="supplier" className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                  Supplier
                </Label>
                <div className="relative">
                  <ShieldCheck className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
                  <select
                    id="supplier"
                    value={supplier}
                    onChange={(e) => setSupplier(e.target.value)}
                    className="w-full h-9 pl-9 pr-3 rounded-md border border-input bg-transparent text-sm appearance-none focus:outline-none focus:ring-1 focus:ring-ring"
                  >
                    {suppliers.map((s) => (
                      <option key={s} value={s}>
                        {s}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <Label htmlFor="quantity" className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                    Quantity
                  </Label>
                  <Input
                    id="quantity"
                    type="number"
                    value={quantity}
                    onChange={(e) => setQuantity(e.target.value)}
                  />
                </div>
                <div className="space-y-1.5">
                  <Label htmlFor="arrival" className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                    Arrival Date
                  </Label>
                  <div className="relative">
                    <CalendarDays className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
                    <Input
                      id="arrival"
                      type="date"
                      value={arrival}
                      onChange={(e) => setArrival(e.target.value)}
                      className="pl-9"
                    />
                  </div>
                </div>
              </div>

              <div className="space-y-1.5">
                <Label htmlFor="temp" className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                  Temperature Requirement
                </Label>
                <div className="relative">
                  <Thermometer className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
                  <select
                    id="temp"
                    value={temp}
                    onChange={(e) => setTemp(e.target.value)}
                    className="w-full h-9 pl-9 pr-3 rounded-md border border-input bg-transparent text-sm appearance-none focus:outline-none focus:ring-1 focus:ring-ring"
                  >
                    {temps.map((t) => (
                      <option key={t} value={t}>
                        {t}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="flex flex-wrap gap-2 pt-1">
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
                      <AlertTriangle className="size-3" /> Short Lead Time
                    </Badge>
                  )}
                </div>
              </div>

              <Button
                onClick={analyze}
                className="w-full bg-gradient-to-r from-primary to-teal hover:opacity-95 shadow-lg shadow-primary/20"
              >
                <BrainCircuit className="size-4 mr-2" />
                Analyze Procurement
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* ─── RIGHT: AI Recommendation Panel ─── */}
        <div className="space-y-4">
          {/* AI greeting */}
          <Card>
            <CardContent className="p-5 flex items-start gap-3">
              <div className="size-10 rounded-xl bg-gradient-to-br from-primary to-teal text-primary-foreground grid place-items-center shrink-0 shadow-lg shadow-primary/20">
                <Sparkles className="size-5" />
              </div>
              <div className="text-sm leading-relaxed">
                <div className="text-xl font-bold font-[family-name:var(--font-heading)]">AI Procurement Copilot</div>
                <p className="text-sm text-muted-foreground mt-1">
                  I analyze warehouse capacity, expiry risk, temperature chain integrity, and demand forecasts to recommend optimal storage zones.
                </p>
              </div>
            </CardContent>
          </Card>

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

          {loading && (
            <Card>
              <CardContent className="p-5 flex items-center gap-3">
                <div className="size-10 rounded-xl bg-gradient-to-br from-primary to-teal text-primary-foreground grid place-items-center animate-pulse">
                  <Sparkles className="size-5" />
                </div>
                <div className="text-sm text-muted-foreground">Analyzing capacity, demand forecasts, and cold-chain integrity…</div>
              </CardContent>
            </Card>
          )}

          {submitted && !loading && (
            <Card className="overflow-hidden border-success/40">
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

function daysUntil(dateStr: string): number {
  const diff = new Date(dateStr).getTime() - Date.now();
  return Math.max(0, Math.ceil(diff / (1000 * 60 * 60 * 24)));
}
