import { createFileRoute } from "@tanstack/react-router";
import {
  Activity,
  AlertTriangle,
  Boxes,
  BrainCircuit,
  ClipboardList,
  Package,
  Warehouse,
} from "lucide-react";
import { AppLayout } from "@/components/AppLayout";
import { AlertCard } from "@/components/insights/AlertCard";
import { ExecutiveSummaryCard } from "@/components/insights/ExecutiveSummaryCard";
import { InsightsSection } from "@/components/insights/InsightsSection";
import { InventoryHealthCard } from "@/components/insights/InventoryHealthCard";
import { KPIGrid } from "@/components/insights/KPIGrid";
import { ProcurementCard } from "@/components/insights/ProcurementCard";
import { RecommendationCard } from "@/components/insights/RecommendationCard";
import { ShipmentCard } from "@/components/insights/ShipmentCard";
import { TrendChart } from "@/components/insights/TrendChart";
import { WarehouseHealthCard } from "@/components/insights/WarehouseHealthCard";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useAiInsights } from "@/lib/api/hooks";

export const Route = createFileRoute("/insights")({
  head: () => ({
    meta: [
      { title: "AI Insights | PharmaChain Operations Centre" },
      {
        name: "description",
        content:
          "Live AI operations centre for inventory, warehouse, shipment, and procurement intelligence.",
      },
    ],
  }),
  component: InsightsPage,
});

function InsightsPage() {
  const { data, isLoading, isError, error, refetch, isFetching } = useAiInsights();

  return (
    <AppLayout>
      <div className="space-y-6">
        <section className="relative overflow-hidden rounded-3xl border border-border/60 bg-[radial-gradient(circle_at_top_right,_rgba(20,184,166,0.16),_transparent_28%),linear-gradient(135deg,_rgba(15,23,42,1),_rgba(15,23,42,0.88)_55%,_rgba(9,18,32,1))] p-6 text-white shadow-[0_30px_70px_-40px_rgba(15,23,42,0.95)] md:p-8">
          <div className="absolute inset-0 bg-[radial-gradient(circle,_rgba(255,255,255,0.06)_1px,_transparent_1px)] [background-size:26px_26px] opacity-20" />
          <div className="relative flex flex-wrap items-start justify-between gap-4">
            <div className="max-w-3xl">
              <div className="flex flex-wrap items-center gap-2 text-[11px] font-semibold uppercase tracking-[0.22em] text-emerald-300/90">
                <span className="inline-flex items-center gap-2">
                  <span className="relative flex size-2">
                    <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-70" />
                    <span className="relative inline-flex size-2 rounded-full bg-emerald-400" />
                  </span>
                  AI Operations Centre
                </span>
                <span className="text-white/40">|</span>
                <span className="text-white/65">{isFetching ? "Refreshing" : "Live backend feed"}</span>
              </div>
              <h1 className="mt-4 text-3xl font-bold tracking-tight md:text-4xl">
                Operational intelligence for inventory, warehouse, shipments, and procurement.
              </h1>
              <p className="mt-3 text-sm leading-relaxed text-white/70 md:text-[15px]">
                The insights page now renders directly from the FastAPI backend, with AI recommendations and alerts generated server-side from live operational data.
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => refetch()}
                className="border-white/15 bg-white/5 text-white hover:bg-white/10 hover:text-white"
              >
                Refresh insights
              </Button>
              {data ? (
                <Badge variant="outline" className="border-white/15 bg-white/5 text-white/80">
                  Confidence {data.confidence}%
                </Badge>
              ) : null}
            </div>
          </div>
        </section>

        {isLoading ? <InsightsLoadingState /> : null}

        {isError ? (
          <Card className="border-red-500/20 bg-red-500/5">
            <CardContent className="flex flex-col gap-4 p-6">
              <div className="flex items-center gap-3 text-red-700">
                <AlertTriangle className="size-5" />
                <div className="text-lg font-semibold">Unable to load AI insights</div>
              </div>
              <p className="text-sm text-muted-foreground">
                {error instanceof Error ? error.message : "The backend response could not be loaded."}
              </p>
              <div>
                <Button onClick={() => refetch()}>Retry</Button>
              </div>
            </CardContent>
          </Card>
        ) : null}

        {!isLoading && !isError && data ? (
          <>
            <InsightsSection
              eyebrow="Executive"
              title="Executive KPI summary"
              description={`Generated ${new Date(data.generated_at).toLocaleString()}`}
            >
              <KPIGrid>
                <ExecutiveSummaryCard
                  title="Inventory footprint"
                  value={data.executive_summary.inventory_value.toLocaleString()}
                  subtitle="Current tracked inventory units"
                  icon={Boxes}
                />
                <ExecutiveSummaryCard
                  title="Warehouse utilisation"
                  value={`${data.executive_summary.warehouse_utilisation}%`}
                  subtitle="Current occupied capacity across zones"
                  icon={Warehouse}
                />
                <ExecutiveSummaryCard
                  title="Pending procurements"
                  value={data.executive_summary.pending_procurements.toLocaleString()}
                  subtitle="Requests awaiting action"
                  icon={ClipboardList}
                />
                <ExecutiveSummaryCard
                  title="Critical alerts"
                  value={data.executive_summary.critical_alerts.toLocaleString()}
                  subtitle="High severity issues requiring attention"
                  icon={AlertTriangle}
                />
              </KPIGrid>
            </InsightsSection>

            <InsightsSection
              eyebrow="Alerts"
              title="Critical alerts"
              description="AI-prioritized issues surfaced from live backend operational rules."
              actions={<Badge variant="outline">{data.alerts.length} active</Badge>}
            >
              {data.alerts.length === 0 ? (
                <EmptyState message="No operational alerts were generated from the current dataset." />
              ) : (
                <div className="grid gap-4 lg:grid-cols-2">
                  {data.alerts.map((alert) => (
                    <AlertCard key={`${alert.severity}-${alert.title}`} alert={alert} />
                  ))}
                </div>
              )}
            </InsightsSection>

            <div className="grid gap-6 xl:grid-cols-2">
              <InsightsSection eyebrow="Inventory" title="Inventory health" description="Low stock, expiry risk, velocity, and overstock exposure.">
                <div className="grid gap-4 md:grid-cols-2">
                  <InventoryHealthCard title="Low stock" items={data.inventory.low_stock} />
                  <InventoryHealthCard title="Near expiry" items={data.inventory.near_expiry} />
                  <InventoryHealthCard title="Fast moving" items={data.inventory.fast_moving} />
                  <InventoryHealthCard title="Slow moving / overstock" items={[...data.inventory.slow_moving, ...data.inventory.overstock].slice(0, 5)} />
                </div>
              </InsightsSection>

              <InsightsSection eyebrow="Warehouse" title="Warehouse health" description="Capacity, cold-chain exposure, and available space by zone.">
                <div className="grid gap-4 md:grid-cols-2">
                  <WarehouseHealthCard title="Highest occupancy" items={data.warehouse.occupancy} />
                  <WarehouseHealthCard title="Cold-chain zones" items={data.warehouse.cold_chain} />
                  <div className="md:col-span-2">
                    <WarehouseHealthCard title="Available capacity" items={data.warehouse.available_capacity} />
                  </div>
                </div>
              </InsightsSection>
            </div>

            <div className="grid gap-6 xl:grid-cols-2">
              <InsightsSection eyebrow="Shipments" title="Shipment intelligence" description="Inbound, outbound, and delayed shipment visibility from the backend.">
                <div className="grid gap-4 md:grid-cols-3">
                  <ShipmentCard title="Incoming" items={data.shipments.incoming} />
                  <ShipmentCard title="Outgoing" items={data.shipments.outgoing} />
                  <ShipmentCard title="Delayed" items={data.shipments.delayed} />
                </div>
              </InsightsSection>

              <InsightsSection eyebrow="Procurement" title="Procurement overview" description="Current request states and AI decision support metadata.">
                <div className="grid gap-4 md:grid-cols-3">
                  <ProcurementCard title="Pending" items={data.procurement.pending} />
                  <ProcurementCard title="Approved" items={data.procurement.approved} />
                  <ProcurementCard title="Rejected" items={data.procurement.rejected} />
                </div>
              </InsightsSection>
            </div>

            <InsightsSection
              eyebrow="Recommendations"
              title="AI recommendations"
              description="Backend-generated actions assembled from live inventory, warehouse, shipment, and procurement signals."
              actions={
                <Badge variant="outline" className="gap-1">
                  <BrainCircuit className="size-3" />
                  {data.recommendations.length} recommendations
                </Badge>
              }
            >
              {data.recommendations.length === 0 ? (
                <EmptyState message="No recommendations were generated from the current dataset." />
              ) : (
                <div className="grid gap-4 lg:grid-cols-2 xl:grid-cols-3">
                  {data.recommendations.map((recommendation) => (
                    <RecommendationCard
                      key={`${recommendation.priority}-${recommendation.title}`}
                      recommendation={recommendation}
                    />
                  ))}
                </div>
              )}
            </InsightsSection>

            <InsightsSection
              eyebrow="Trends"
              title="Operational trends"
              description="Recent backend-derived operational patterns across inventory, shipments, and warehouse usage."
              actions={<Badge variant="outline" className="gap-1"><Activity className="size-3" /> Trend feed</Badge>}
            >
              <div className="grid gap-4 xl:grid-cols-3">
                <TrendChart
                  title="Inventory trend"
                  description="Received units vs currently available units."
                  data={data.trend_data.inventory}
                  primaryLabel="Received units"
                  secondaryLabel="Available units"
                />
                <TrendChart
                  title="Shipment trend"
                  description="Total shipments vs delayed shipments."
                  data={data.trend_data.shipments}
                  primaryLabel="Total shipments"
                  secondaryLabel="Delayed shipments"
                />
                <TrendChart
                  title="Warehouse trend"
                  description="Occupied capacity vs remaining capacity by zone."
                  data={data.trend_data.warehouse}
                  primaryLabel="Occupied units"
                  secondaryLabel="Available units"
                />
              </div>
            </InsightsSection>
          </>
        ) : null}
      </div>
    </AppLayout>
  );
}

function InsightsLoadingState() {
  return (
    <div className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {Array.from({ length: 4 }).map((_, index) => (
          <Skeleton key={index} className="h-36 rounded-2xl" />
        ))}
      </div>
      <Skeleton className="h-40 rounded-2xl" />
      <div className="grid gap-6 xl:grid-cols-2">
        <Skeleton className="h-96 rounded-2xl" />
        <Skeleton className="h-96 rounded-2xl" />
      </div>
      <Skeleton className="h-96 rounded-2xl" />
    </div>
  );
}

function EmptyState({ message }: { message: string }) {
  return (
    <div className="rounded-2xl border border-dashed border-border p-8 text-sm text-muted-foreground">
      {message}
    </div>
  );
}
