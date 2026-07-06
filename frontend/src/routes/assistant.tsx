import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import {
  Activity,
  AlertTriangle,
  ArrowRight,
  BrainCircuit,
  CalendarDays,
  Lock,
  Radio,
  ShieldCheck,
  Snowflake,
  Sparkles,
  Thermometer,
  TrendingUp,
  User,
  Warehouse,
} from "lucide-react";

import { AppLayout } from "@/components/AppLayout";
import { ConfidenceGauge } from "@/components/procurement/ConfidenceGauge";
import { DecisionCard } from "@/components/procurement/DecisionCard";
import { EvidencePanel } from "@/components/procurement/EvidencePanel";
import { ReasoningTimeline } from "@/components/procurement/ReasoningTimeline";
import { RecommendationCard } from "@/components/procurement/RecommendationCard";
import { ToolExecutionPanel } from "@/components/procurement/ToolExecutionPanel";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { useAnalyzeProcurement, useProducts, useSuppliers } from "@/lib/api/hooks";
import type { ProcurementAnalysisResponse, Product } from "@/lib/api/endpoints";
import { ApiError } from "@/lib/api/types";

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

function AssistantPage() {
  const productsQuery = useProducts();
  const suppliersQuery = useSuppliers();
  const analyzeMutation = useAnalyzeProcurement();

  const [productId, setProductId] = useState("");
  const [supplierId, setSupplierId] = useState("");
  const [quantity, setQuantity] = useState("500");
  const [submittedRequest, setSubmittedRequest] = useState<{
    productName: string;
    supplierName: string;
    quantity: number;
  } | null>(null);

  const products = productsQuery.data ?? [];
  const suppliers = suppliersQuery.data ?? [];

  useEffect(() => {
    if (!productId && products.length > 0) {
      setProductId(products[0].id);
    }
  }, [productId, products]);

  useEffect(() => {
    if (!supplierId && suppliers.length > 0) {
      setSupplierId(suppliers[0].id);
    }
  }, [supplierId, suppliers]);

  const selectedProduct = products.find((item) => item.id === productId) ?? null;
  const selectedSupplier = suppliers.find((item) => item.id === supplierId) ?? null;
  const isFormReady = Boolean(selectedProduct && selectedSupplier && Number(quantity) > 0);
  const requestError = !productsQuery.isLoading && !suppliersQuery.isLoading && (!selectedProduct || !selectedSupplier);

  function handleProductChange(nextProductId: string) {
    setProductId(nextProductId);

    const nextProduct = products.find((item) => item.id === nextProductId);
    if (nextProduct?.supplier_id) {
      setSupplierId(nextProduct.supplier_id);
    }
  }

  function analyze() {
    if (!selectedProduct || !selectedSupplier) {
      return;
    }

    const requestedQuantity = Number(quantity);
    setSubmittedRequest({
      productName: selectedProduct.name,
      supplierName: selectedSupplier.name,
      quantity: requestedQuantity,
    });

    analyzeMutation.mutate({
      product_id: selectedProduct.id,
      supplier_id: selectedSupplier.id,
      requested_quantity: requestedQuantity,
    });
  }

  const analysis = analyzeMutation.data;
  const loading = analyzeMutation.isPending;
  const errorMessage = getErrorMessage(
    analyzeMutation.error ??
      productsQuery.error ??
      suppliersQuery.error ??
      (requestError ? new Error("Unable to load procurement form options.") : null),
  );

  return (
    <AppLayout>
      <div className="grid gap-6 xl:grid-cols-[minmax(0,460px)_minmax(0,1fr)]">
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
              Compose the request below. The Copilot will reason across inventory, capacity,
              cold-chain fit, incoming shipments, and supplier reliability.
            </p>
          </div>

          <CardContent className="p-6 space-y-6">
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
                  width="w-24"
                />{" "}
                units of{" "}
                <InlineSelect
                  id="product"
                  value={productId}
                  onChange={handleProductChange}
                  options={products.map((product) => ({
                    value: product.id,
                    label: product.name,
                  }))}
                  disabled={productsQuery.isLoading}
                />
                {" "}from{" "}
                <InlineSelect
                  id="supplier"
                  value={supplierId}
                  onChange={setSupplierId}
                  options={suppliers.map((supplier) => ({
                    value: supplier.id,
                    label: supplier.name,
                  }))}
                  disabled={suppliersQuery.isLoading}
                />
                .
              </div>
            </div>

            <div>
              <div className="text-[10px] font-semibold uppercase tracking-[0.18em] text-muted-foreground mb-2 flex items-center gap-1.5">
                <Sparkles className="size-3 text-primary" />
                Copilot detected
              </div>
              <div className="flex flex-wrap gap-2">
                {selectedProduct && (
                  <TemperatureBadge product={selectedProduct} />
                )}
                {selectedProduct && (
                  <Badge variant="outline" className="text-warning-foreground border-warning/40 bg-warning/10 gap-1">
                    <AlertTriangle className="size-3" /> Safety stock {selectedProduct.safety_stock}
                  </Badge>
                )}
                {selectedSupplier && (
                  <Badge variant="outline" className="text-success border-success/40 bg-success/10 gap-1">
                    <ShieldCheck className="size-3" /> Reliability {selectedSupplier.reliability_score.toFixed(2)}
                  </Badge>
                )}
              </div>
            </div>

            {errorMessage && (
              <div className="rounded-lg border border-destructive/30 bg-destructive/10 p-3 text-sm text-destructive">
                {errorMessage}
              </div>
            )}

            <Button
              onClick={analyze}
              disabled={!isFormReady || loading || productsQuery.isLoading || suppliersQuery.isLoading}
              className="w-full h-11 bg-gradient-to-r from-primary to-teal hover:opacity-95 shadow-lg shadow-primary/20 group"
            >
              <BrainCircuit className="size-4 mr-2" />
              {loading ? "Analyzing..." : "Analyze Procurement"}
              <ArrowRight className="size-4 ml-2 transition-transform group-hover:translate-x-0.5" />
            </Button>

            <div className="flex items-center justify-between text-[11px] text-muted-foreground pt-2 border-t border-border/50">
              <span className="inline-flex items-center gap-1.5">
                <Lock className="size-3" /> GxP · HIPAA · GDPR
              </span>
              <span>
                {productsQuery.isLoading || suppliersQuery.isLoading ? "Loading options..." : "Live backend analysis"}
              </span>
            </div>
          </CardContent>
        </Card>

        <div className="space-y-4">
          {!submittedRequest && !loading && !analysis && <CopilotStandby />}

          {submittedRequest && (
            <Card className="bg-secondary/40">
              <CardContent className="p-5 flex items-start gap-3 justify-end flex-row-reverse">
                <div className="size-9 rounded-full bg-muted grid place-items-center shrink-0">
                  <User className="size-4" />
                </div>
                <div className="text-sm leading-relaxed text-right">
                  <div className="font-medium">You</div>
                  <p className="text-muted-foreground mt-1">
                    Requesting <span className="text-foreground font-medium">{submittedRequest.quantity} units</span> of{" "}
                    <span className="text-foreground font-medium">{submittedRequest.productName}</span> from{" "}
                    <span className="text-foreground font-medium">{submittedRequest.supplierName}</span>.
                  </p>
                </div>
              </CardContent>
            </Card>
          )}

          {loading && <AiThinking />}

          {analysis && !loading && (
            <div className="space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-500">
              <DecisionCard decision={analysis.decision} summary={analysis.summary} />

              <div className="grid gap-4 lg:grid-cols-[280px_minmax(0,1fr)]">
                <ConfidenceGauge confidence={analysis.confidence} />
                <RequestDetailsCard analysis={analysis} />
              </div>

              <div className="grid gap-4 xl:grid-cols-[minmax(0,0.9fr)_minmax(0,1.1fr)]">
                <ToolExecutionPanel items={analysis.tool_execution} />
                <ReasoningTimeline steps={analysis.reasoning} />
              </div>

              <EvidencePanel evidence={analysis.evidence} />

              <RecommendationCard
                recommendation={analysis.recommendation}
                explanation={analysis.explanation}
              />
            </div>
          )}
        </div>
      </div>
    </AppLayout>
  );
}

function RequestDetailsCard({
  analysis,
}: {
  analysis: ProcurementAnalysisResponse;
}) {
  const details = analysis.request_details;

  return (
    <Card>
      <CardContent className="p-5">
        <div className="text-xs uppercase tracking-wider text-muted-foreground font-semibold">
          Procurement request details
        </div>
        <div className="mt-4 grid gap-3 sm:grid-cols-2">
          <DetailItem label="Product" value={details.product_name} />
          <DetailItem label="Supplier" value={details.supplier_name} />
          <DetailItem label="Requested quantity" value={`${details.requested_quantity} units`} />
          <DetailItem label="Temperature range" value={`${details.temperature_min}°C to ${details.temperature_max}°C`} />
          <DetailItem label="Safety stock" value={`${details.safety_stock} units`} />
          <DetailItem label="Shelf life" value={`${details.shelf_life_days} days`} />
        </div>
      </CardContent>
    </Card>
  );
}

function DetailItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-border/70 bg-muted/20 p-3">
      <div className="text-xs uppercase tracking-wide text-muted-foreground">{label}</div>
      <div className="mt-1 text-sm font-semibold leading-relaxed">{value}</div>
    </div>
  );
}

function TemperatureBadge({ product }: { product: Product }) {
  const isDeepFreeze = product.temperature_max <= -20;
  const isColdChain = product.temperature_min <= 8 && product.temperature_max <= 8;

  if (isDeepFreeze) {
    return (
      <Badge variant="outline" className="text-teal border-teal/40 bg-teal/10 gap-1">
        <Snowflake className="size-3" /> Deep freeze chain
      </Badge>
    );
  }

  if (isColdChain) {
    return (
      <Badge variant="outline" className="text-primary border-primary/40 bg-primary/10 gap-1">
        <Thermometer className="size-3" /> Cold chain
      </Badge>
    );
  }

  return (
    <Badge variant="outline" className="text-muted-foreground border-border bg-muted/50 gap-1">
      <Thermometer className="size-3" /> Ambient storage
    </Badge>
  );
}

function AiThinking() {
  const steps = [
    "Building deterministic execution plan...",
    "Running inventory and warehouse checks...",
    "Evaluating shipments and supplier evidence...",
    "Composing procurement recommendation...",
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
              Analyzing inventory, capacity, shipments, and procurement policy
            </div>
          </div>
        </div>
        <ul className="mt-4 grid gap-2">
          {steps.map((step, index) => (
            <li
              key={step}
              className="flex items-center gap-2.5 text-[12.5px] text-muted-foreground opacity-0 animate-in fade-in slide-in-from-left-1"
              style={{ animationDelay: `${index * 140}ms`, animationDuration: "400ms", animationFillMode: "forwards" }}
            >
              <span className="size-1.5 rounded-full bg-primary/70 animate-pulse" />
              <span>{step}</span>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
}

function InlineSelect({
  id,
  value,
  onChange,
  options,
  disabled = false,
}: {
  id: string;
  value: string;
  onChange: (value: string) => void;
  options: Array<{ value: string; label: string }>;
  disabled?: boolean;
}) {
  return (
    <span className="relative inline-block align-baseline">
      <select
        id={id}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        disabled={disabled}
        className="appearance-none bg-primary/8 hover:bg-primary/12 focus:bg-primary/14 border-b-2 border-primary/40 hover:border-primary focus:border-primary focus:outline-none rounded-t-md px-2 py-0.5 text-primary font-semibold cursor-pointer transition-colors max-w-[240px] truncate disabled:cursor-not-allowed disabled:opacity-60"
      >
        {options.map((option) => (
          <option key={option.value} value={option.value} className="text-foreground">
            {option.label}
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
  onChange: (value: string) => void;
  placeholder?: string;
  width?: string;
}) {
  return (
    <input
      id={id}
      type="number"
      min="1"
      value={value}
      placeholder={placeholder}
      onChange={(event) => onChange(event.target.value)}
      className={`${width} bg-primary/8 hover:bg-primary/12 focus:bg-primary/14 border-b-2 border-primary/40 hover:border-primary focus:border-primary focus:outline-none rounded-t-md px-2 py-0.5 text-primary font-semibold text-center tabular-nums transition-colors [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none`}
    />
  );
}

function CopilotStandby() {
  const capabilities = [
    { icon: Warehouse, label: "Capacity scanner", status: "Ready" },
    { icon: Snowflake, label: "Cold-chain validator", status: "Ready" },
    { icon: TrendingUp, label: "Demand checker", status: "Ready" },
    { icon: CalendarDays, label: "Shelf-life validator", status: "Ready" },
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
      <div
        aria-hidden
        className="absolute inset-0 opacity-[0.06] pointer-events-none"
        style={{
          backgroundImage: "radial-gradient(circle, #ffffff 1px, transparent 1px)",
          backgroundSize: "28px 28px",
        }}
      />

      <div className="relative flex items-center justify-between px-6 pt-5 text-[10px] font-mono uppercase tracking-[0.18em] text-white/45">
        <span className="inline-flex items-center gap-2">
          <span className="relative flex size-1.5">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-70" />
            <span className="relative inline-flex size-1.5 rounded-full bg-emerald-400" />
          </span>
          Copilot · online
        </span>
        <span className="inline-flex items-center gap-4">
          <span>Model · deterministic-v1</span>
          <span className="hidden sm:inline">Planner · rule-based</span>
        </span>
      </div>

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
          Complete the request on the left to run the live backend reasoning engine and generate
          a procurement decision with auditable evidence.
        </p>

        <div className="mt-10 grid grid-cols-1 sm:grid-cols-2 gap-2.5 w-full max-w-lg">
          {capabilities.map((capability) => {
            const Icon = capability.icon;
            return (
              <div
                key={capability.label}
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
                      background: "color-mix(in oklab, var(--color-primary) 20%, transparent)",
                      color: "color-mix(in oklab, var(--color-primary) 80%, #ffffff)",
                    }}
                  >
                    <Icon className="size-3.5" />
                  </span>
                  <span className="text-[12.5px] text-white/80 truncate text-left">{capability.label}</span>
                </div>
                <span className="inline-flex items-center gap-1.5 text-[10px] font-mono uppercase tracking-wider text-emerald-300/90">
                  <span className="size-1 rounded-full bg-emerald-400" />
                  {capability.status}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      <div className="relative px-6 pb-5">
        <div className="h-px w-full bg-gradient-to-r from-transparent via-white/15 to-transparent mb-3" />
        <div className="flex flex-wrap items-center justify-between gap-3 text-[10px] font-mono uppercase tracking-[0.18em] text-white/45">
          <span className="inline-flex items-center gap-1.5">
            <Radio className="size-3" />
            4 tools registered
          </span>
          <span className="inline-flex items-center gap-1.5">
            <Activity className="size-3" />
            Live evidence collection
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

function getErrorMessage(error: Error | null): string | null {
  if (!error) {
    return null;
  }

  if (error instanceof ApiError) {
    if (typeof error.body?.detail === "string") {
      return error.body.detail;
    }
    if (typeof error.body?.message === "string") {
      return error.body.message;
    }
  }

  return error.message;
}
