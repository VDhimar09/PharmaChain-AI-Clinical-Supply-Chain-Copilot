import { createFileRoute } from "@tanstack/react-router";
import { AppLayout } from "@/components/AppLayout";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { StatusBadge } from "@/components/StatusBadge";
import { ProcurementAIResponse } from "@/lib/api/endpoints";
import { ApiError } from "@/lib/api/types";
import {
  useEvaluateProcurement,
  useProducts,
  useSuppliers,
} from "@/lib/api/hooks";
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
import { useEffect, useState } from "react";

export const Route = createFileRoute("/assistant")({
  head: () => ({
    meta: [
      { title: "AI Procurement Assistant - PharmaChain Supply Copilot" },
      {
        name: "description",
        content: "AI-powered procurement recommendations for pharmaceutical inventory.",
      },
    ],
  }),
  component: AssistantPage,
});

const temps = [
  "-80C (Ultra Low)",
  "-70C (Deep Freeze)",
  "-20C (Frozen)",
  "2-8C (Refrigerated)",
  "15-25C (Ambient)",
];

function AssistantPage() {
  const {
    data: productsData,
    isLoading: productsLoading,
    error: productsError,
  } = useProducts();
  const {
    data: suppliersData,
    isLoading: suppliersLoading,
    error: suppliersError,
  } = useSuppliers();
  const procurementEvaluation = useEvaluateProcurement();

  const products = productsData ?? [];
  const suppliers = suppliersData ?? [];

  const [product, setProduct] = useState("");
  const [supplier, setSupplier] = useState("");
  const [quantity, setQuantity] = useState("2000");
  const [temp, setTemp] = useState("-70C (Deep Freeze)");
  const [arrival, setArrival] = useState("2026-07-15");

  const [submitted, setSubmitted] = useState<null | {
    product: string;
    supplier: string;
    quantity: string;
    temp: string;
    arrival: string;
  }>(null);

  useEffect(() => {
    if (!product && products.length > 0) {
      setProduct(products[0].name);
    }
  }, [product, products]);

  useEffect(() => {
    if (!supplier && suppliers.length > 0) {
      setSupplier(suppliers[0].name);
    }
  }, [supplier, suppliers]);

  function analyze() {
    if (!product || !supplier) {
      return;
    }

    const palletQuantity = Number(quantity);
    if (!Number.isFinite(palletQuantity) || palletQuantity <= 0) {
      return;
    }

    const nextSubmitted = {
      product,
      supplier,
      quantity,
      temp,
      arrival,
    };

    setSubmitted(nextSubmitted);
    procurementEvaluation.mutate({
      product_name: product,
      pallet_quantity: palletQuantity,
      month: formatMonth(arrival),
    });
  }

  const procurementOptionsLoading = productsLoading || suppliersLoading;
  const procurementOptionsError = productsError || suppliersError;
  const canAnalyze =
    !procurementOptionsLoading &&
    !procurementOptionsError &&
    !procurementEvaluation.isPending &&
    products.length > 0 &&
    suppliers.length > 0 &&
    Boolean(product) &&
    Boolean(supplier);

  const recommendation = procurementEvaluation.data;
  const loading = procurementEvaluation.isPending;
  const evaluationError = procurementEvaluation.error;
  const riskTone = getRiskTone(recommendation?.risk_level);
  const recommendationTone = getRecommendationTone(recommendation?.decision);
  const confidencePercent = formatPercent(recommendation?.confidence, true);
  const recommendationErrorMessage =
    evaluationError instanceof ApiError
      ? getApiErrorMessage(evaluationError)
      : evaluationError?.message;

  return (
    <AppLayout>
      <div className="grid gap-6 lg:grid-cols-[380px_1fr]">
        <Card className="h-fit">
          <CardContent className="p-6 space-y-5">
            <div className="flex items-center gap-3">
              <div className="size-10 rounded-xl bg-gradient-to-br from-primary to-teal text-primary-foreground grid place-items-center shadow-lg shadow-primary/20">
                <Package className="size-5" />
              </div>
              <div>
                <div className="text-xl font-bold font-[family-name:var(--font-heading)]">
                  Procurement Request
                </div>
                <p className="text-sm text-muted-foreground">
                  Fill details to get an AI recommendation
                </p>
              </div>
            </div>

            <div className="space-y-4">
              <div className="space-y-1.5">
                <Label
                  htmlFor="product"
                  className="text-xs font-medium uppercase tracking-wide text-muted-foreground"
                >
                  Product
                </Label>
                <div className="relative">
                  <Box className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
                  <select
                    id="product"
                    value={product}
                    onChange={(e) => setProduct(e.target.value)}
                    disabled={productsLoading || Boolean(productsError) || products.length === 0}
                    className="w-full h-9 pl-9 pr-3 rounded-md border border-input bg-transparent text-sm appearance-none focus:outline-none focus:ring-1 focus:ring-ring"
                  >
                    {productsLoading && <option value="">Loading products...</option>}
                    {!productsLoading && productsError && (
                      <option value="">Unable to load products</option>
                    )}
                    {!productsLoading && !productsError && products.length === 0 && (
                      <option value="">No products available</option>
                    )}
                    {products.map((item) => (
                      <option key={item.id} value={item.name}>
                        {item.name}
                      </option>
                    ))}
                  </select>
                </div>
                {productsError && (
                  <p className="text-xs text-destructive mt-1">
                    Failed to load products from the backend.
                  </p>
                )}
              </div>

              <div className="space-y-1.5">
                <Label
                  htmlFor="supplier"
                  className="text-xs font-medium uppercase tracking-wide text-muted-foreground"
                >
                  Supplier
                </Label>
                <div className="relative">
                  <ShieldCheck className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
                  <select
                    id="supplier"
                    value={supplier}
                    onChange={(e) => setSupplier(e.target.value)}
                    disabled={suppliersLoading || Boolean(suppliersError) || suppliers.length === 0}
                    className="w-full h-9 pl-9 pr-3 rounded-md border border-input bg-transparent text-sm appearance-none focus:outline-none focus:ring-1 focus:ring-ring"
                  >
                    {suppliersLoading && <option value="">Loading suppliers...</option>}
                    {!suppliersLoading && suppliersError && (
                      <option value="">Unable to load suppliers</option>
                    )}
                    {!suppliersLoading && !suppliersError && suppliers.length === 0 && (
                      <option value="">No suppliers available</option>
                    )}
                    {suppliers.map((item) => (
                      <option key={item.id} value={item.name}>
                        {item.name}
                      </option>
                    ))}
                  </select>
                </div>
                {suppliersError && (
                  <p className="text-xs text-destructive mt-1">
                    Failed to load suppliers from the backend.
                  </p>
                )}
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <Label
                    htmlFor="quantity"
                    className="text-xs font-medium uppercase tracking-wide text-muted-foreground"
                  >
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
                  <Label
                    htmlFor="arrival"
                    className="text-xs font-medium uppercase tracking-wide text-muted-foreground"
                  >
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
                <Label
                  htmlFor="temp"
                  className="text-xs font-medium uppercase tracking-wide text-muted-foreground"
                >
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
                    {temps.map((item) => (
                      <option key={item} value={item}>
                        {item}
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
                    <Badge
                      variant="outline"
                      className="text-warning-foreground border-warning/40 bg-warning/10 gap-1"
                    >
                      <AlertTriangle className="size-3" /> Short Lead Time
                    </Badge>
                  )}
                </div>
              </div>

              <Button
                onClick={analyze}
                disabled={!canAnalyze}
                className="w-full bg-gradient-to-r from-primary to-teal hover:opacity-95 shadow-lg shadow-primary/20"
              >
                <BrainCircuit className="size-4 mr-2" />
                {loading ? "Analyzing..." : procurementOptionsLoading ? "Loading Options..." : "Analyze Procurement"}
              </Button>
              {procurementOptionsError && (
                <p className="text-xs text-destructive">
                  Procurement form options could not be loaded. Please refresh and try again.
                </p>
              )}
              {recommendationErrorMessage && (
                <p className="text-xs text-destructive">
                  {recommendationErrorMessage}
                </p>
              )}
            </div>
          </CardContent>
        </Card>

        <div className="space-y-4">
          <Card>
            <CardContent className="p-5 flex items-start gap-3">
              <div className="size-10 rounded-xl bg-gradient-to-br from-primary to-teal text-primary-foreground grid place-items-center shrink-0 shadow-lg shadow-primary/20">
                <Sparkles className="size-5" />
              </div>
              <div className="text-sm leading-relaxed">
                <div className="text-xl font-bold font-[family-name:var(--font-heading)]">
                  AI Procurement Copilot
                </div>
                <p className="text-sm text-muted-foreground mt-1">
                  I analyze warehouse capacity, expiry risk, temperature chain integrity, and
                  demand forecasts to recommend optimal storage zones.
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
                    <span className="text-foreground font-medium">{submitted.supplier}</span>,
                    arriving <span className="text-foreground font-medium">{submitted.arrival}</span>.
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
                <div className="text-sm text-muted-foreground">
                  Analyzing capacity, demand forecasts, and cold-chain integrity...
                </div>
              </CardContent>
            </Card>
          )}

          {submitted && recommendation && !loading && (
            <Card className="overflow-hidden border-success/40">
              <div className="bg-gradient-to-r from-success/20 via-success/5 to-transparent px-6 py-5 flex items-center justify-between border-b border-success/30">
                <div className="flex items-center gap-3">
                  <div className={`size-12 rounded-full grid place-items-center shadow-lg ${recommendationTone.badgeClass}`}>
                    <CheckCircle2 className="size-6" />
                  </div>
                  <div>
                    <div className="text-xs uppercase tracking-wider text-success font-semibold">
                      Recommendation
                    </div>
                    <div className="text-xl font-bold">{recommendation.decision}</div>
                  </div>
                </div>
                <div className="flex flex-col items-end gap-2">
                  <StatusBadge label={`Risk: ${recommendation.risk_level}`} tone={riskTone} />
                  <Badge variant="outline" className="text-primary border-primary/40 bg-primary/10 gap-1">
                    <BrainCircuit className="size-3" /> {confidencePercent} Confidence
                  </Badge>
                </div>
              </div>

              <CardContent className="p-6 space-y-6">
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  <MetricCard
                    icon={Warehouse}
                    label="Current Occupancy"
                    value={formatPercent(recommendation.current_occupancy_percent)}
                    sub={`${formatPercent(recommendation.current_occupancy_percent)} current warehouse utilization`}
                    bar={recommendation.current_occupancy_percent}
                    barTone="primary"
                  />
                  <MetricCard
                    icon={TrendingUp}
                    label="Forecast Occupancy"
                    value={formatPercent(recommendation.projected_occupancy_percent)}
                    sub={`${formatPercent(recommendation.projected_occupancy_percent)} after this procurement`}
                    bar={recommendation.projected_occupancy_percent}
                    barTone="teal"
                  />
                  <MetricCard
                    icon={Warehouse}
                    label="Recommended Zone"
                    value={recommendation.recommended_zone}
                    sub={getBadgeValue(recommendation.badges, "Zone Type")}
                  />
                  <MetricCard
                    icon={AlertTriangle}
                    label="Risk Level"
                    value={recommendation.risk_level}
                    valueTone={getRiskValueTone(recommendation.risk_level)}
                    sub={riskLevelDescription(recommendation.risk_level)}
                  />
                  <MetricCard
                    icon={BrainCircuit}
                    label="Confidence Score"
                    value={confidencePercent}
                    valueTone="primary"
                    sub={`${recommendation.inventory_units.toLocaleString()} units currently in inventory`}
                  />
                  <MetricCard
                    icon={Thermometer}
                    label="Temperature Fit"
                    value={formatTemperatureFit(recommendation.temperature_fit)}
                    valueTone={recommendation.temperature_fit === "MATCH" ? "teal" : "warning"}
                    sub={getBadgeValue(recommendation.badges, "Temperature Fit")}
                  />
                </div>

                <div className="flex flex-wrap gap-2">
                  {recommendation.badges.map((badge) => (
                    <RecommendationBadge key={badge} badge={badge} />
                  ))}
                </div>

                <div className="rounded-xl border border-border bg-muted/40 p-5 space-y-3">
                  <div className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">
                    Reasoning
                  </div>
                  <div className="grid gap-3">
                    {recommendation.reasoning.map((item) => (
                      <ReasonItem key={item} icon={iconForReason(item)} text={item} />
                    ))}
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
        <div className="text-sm font-medium uppercase tracking-wide text-muted-foreground">
          {label}
        </div>
        {valueTone === "default" && (
          <div className="text-lg font-bold font-[family-name:var(--font-heading)] mt-0.5">
            {value}
          </div>
        )}
        {sub && <div className="text-sm text-muted-foreground mt-0.5">{sub}</div>}
      </div>
      {bar !== undefined && (
        <div className="space-y-1">
          <div className="h-1.5 w-full overflow-hidden rounded-full bg-primary/10">
            <div
              className={`h-full rounded-full ${barColor[barTone]} transition-all`}
              style={{ width: `${Math.max(0, Math.min(bar, 100))}%` }}
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

function RecommendationBadge({
  badge,
}: {
  badge: string;
}) {
  const icon = iconForBadge(badge);
  const className = classNameForBadge(badge);
  const Icon = icon;

  return (
    <Badge variant="outline" className={className}>
      <Icon className="size-3" /> {badge}
    </Badge>
  );
}

function formatMonth(dateStr: string): string {
  const date = new Date(`${dateStr}T00:00:00`);
  if (Number.isNaN(date.getTime())) {
    return "Unknown";
  }

  return date.toLocaleString("en-US", { month: "long" });
}

function formatPercent(value: number | undefined, fromUnit = false): string {
  if (typeof value !== "number" || Number.isNaN(value)) {
    return "N/A";
  }

  const percentage = fromUnit ? value * 100 : value;
  return `${Math.round(percentage)}%`;
}

function formatTemperatureFit(value: ProcurementAIResponse["temperature_fit"]): string {
  return value === "MATCH" ? "Match" : "Mismatch";
}

function getBadgeValue(badges: string[], prefix: string): string {
  const match = badges.find((badge) => badge.startsWith(`${prefix}:`));
  if (!match) {
    return "Not provided";
  }

  return match.split(":").slice(1).join(":").trim();
}

function getRiskTone(riskLevel: ProcurementAIResponse["risk_level"] | undefined) {
  if (riskLevel === "HIGH") {
    return "destructive";
  }

  if (riskLevel === "MEDIUM") {
    return "warning";
  }

  return "success";
}

function getRiskValueTone(riskLevel: ProcurementAIResponse["risk_level"]) {
  if (riskLevel === "HIGH") {
    return "warning";
  }

  if (riskLevel === "MEDIUM") {
    return "primary";
  }

  return "success";
}

function riskLevelDescription(riskLevel: ProcurementAIResponse["risk_level"]): string {
  if (riskLevel === "HIGH") {
    return "Recommendation requires capacity or temperature remediation";
  }

  if (riskLevel === "MEDIUM") {
    return "Recommendation requires additional operational review";
  }

  return "Recommendation is within current operating thresholds";
}

function getRecommendationTone(decision: ProcurementAIResponse["decision"] | undefined) {
  if (decision === "REJECT") {
    return {
      badgeClass: "bg-destructive/90 text-destructive-foreground shadow-destructive/30",
    };
  }

  if (decision === "REVIEW") {
    return {
      badgeClass: "bg-warning text-warning-foreground shadow-warning/30",
    };
  }

  return {
    badgeClass: "bg-success text-success-foreground shadow-success/30",
  };
}

function iconForReason(reason: string) {
  const text = reason.toLowerCase();

  if (text.includes("temperature")) {
    return Thermometer;
  }

  if (text.includes("shipment")) {
    return TrendingUp;
  }

  if (text.includes("inventory") || text.includes("warehouse") || text.includes("zone")) {
    return Warehouse;
  }

  return ShieldCheck;
}

function iconForBadge(badge: string) {
  const text = badge.toLowerCase();

  if (text.includes("temperature")) {
    return Thermometer;
  }

  if (text.includes("shelf life")) {
    return CalendarDays;
  }

  if (text.includes("shipment")) {
    return AlertTriangle;
  }

  if (text.includes("zone")) {
    return Warehouse;
  }

  return ShieldCheck;
}

function classNameForBadge(badge: string): string {
  const text = badge.toLowerCase();

  if (text.includes("mismatch") || text.includes("pending")) {
    return "text-warning-foreground border-warning/40 bg-warning/10 gap-1";
  }

  if (text.includes("match") || text.includes("no incoming")) {
    return "text-success border-success/40 bg-success/10 gap-1";
  }

  if (text.includes("zone")) {
    return "text-primary border-primary/40 bg-primary/10 gap-1";
  }

  return "text-muted-foreground border-border bg-muted/50 gap-1";
}

function getApiErrorMessage(error: ApiError): string {
  if (typeof error.body?.detail === "string") {
    return error.body.detail;
  }

  if (Array.isArray(error.body?.detail)) {
    return error.body.detail.join(", ");
  }

  if (typeof error.body?.message === "string") {
    return error.body.message;
  }

  return error.message;
}

function daysUntil(dateStr: string): number {
  const diff = new Date(dateStr).getTime() - Date.now();
  return Math.max(0, Math.ceil(diff / (1000 * 60 * 60 * 24)));
}
