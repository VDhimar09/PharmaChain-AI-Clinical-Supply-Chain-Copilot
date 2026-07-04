import { createFileRoute } from "@tanstack/react-router";
import { AppLayout } from "@/components/AppLayout";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useMemo, useState } from "react";
import { Search, Truck, CheckCircle2, AlertTriangle, Clock } from "lucide-react";
import { useShipments } from "@/lib/api/hooks";
import { StatusBadge, statusTone } from "@/components/StatusBadge";
import { AiInsight } from "@/components/AiInsight";

export const Route = createFileRoute("/shipments")({
  head: () => ({
    meta: [
      { title: "Shipments — AI Clinical Supply Chain Copilot" },
      {
        name: "description",
        content: "Track incoming pharmaceutical shipments with live statuses.",
      },
    ],
  }),
  component: ShipmentsPage,
});

const STATUSES = ["All", "In Transit", "Delivered", "Delayed", "Processing"] as const;

function ShipmentsPage() {
  const [q, setQ] = useState("");
  const [status, setStatus] = useState<(typeof STATUSES)[number]>("All");

  const { data: shipmentsData, isLoading, error } = useShipments();
  const shipments = shipmentsData ?? [];

  const filtered = useMemo(() => {
    const term = q.toLowerCase();
    return shipments.filter(
      (s) =>
        (status === "All" || s.status === status) &&
        (s.shipment_number.toLowerCase().includes(term) ||
          s.supplier_name.toLowerCase().includes(term) ||
          s.product_name.toLowerCase().includes(term)),
    );
  }, [q, status, shipments]);

  const counts = useMemo(
    () => ({
      "In Transit": shipments.filter((s) => s.status === "In Transit").length,
      Delivered: shipments.filter((s) => s.status === "Delivered").length,
      Delayed: shipments.filter((s) => s.status === "Delayed").length,
      Processing: shipments.filter((s) => s.status === "Processing").length,
    }),
    [shipments],
  );

  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Stat icon={Truck} label="In Transit" value={counts["In Transit"]} tone="info" />
          <Stat icon={CheckCircle2} label="Delivered" value={counts.Delivered} tone="success" />
          <Stat icon={AlertTriangle} label="Delayed" value={counts.Delayed} tone="destructive" />
          <Stat icon={Clock} label="Processing" value={counts.Processing} tone="warning" />
        </div>

        <AiInsight
          eyebrow="Shipment copilot"
          detected="2 inbound shipments are at risk of delay this week."
          matters="SHP-10239 (Oncology Trial OXC-44) ETA pushed by 2 days. SHP-10235 carrier reports weather disruption. 1 clinical site impacted."
          action="Notify the affected trial site and reroute SHP-10235 via the Frankfurt hub to recover 36h."
          confidence={87}
          risk="medium"
          cta="Open at-risk shipments"
        />

        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
          <div className="relative w-full md:w-96">
            <Search className="size-4 text-muted-foreground absolute left-3 top-1/2 -translate-y-1/2" />
            <Input
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="Search shipment, supplier, product…"
              className="pl-9 bg-card"
            />
          </div>
          <div className="flex gap-2 flex-wrap">
            {STATUSES.map((s) => (
              <button
                key={s}
                onClick={() => setStatus(s)}
                className={`px-3 py-1.5 rounded-md text-xs font-semibold border transition-colors ${
                  status === s
                    ? "bg-primary text-primary-foreground border-primary shadow-sm shadow-primary/20"
                    : "bg-card hover:bg-muted border-border text-muted-foreground hover:text-foreground"
                }`}
              >
                {s}
              </button>
            ))}
          </div>
        </div>

        <Card className="overflow-hidden">
          <CardContent className="p-0 overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow className="bg-muted/40 hover:bg-muted/40">
                  <TableHead>Shipment ID</TableHead>
                  <TableHead>Supplier</TableHead>
                  <TableHead>Product</TableHead>
                  <TableHead className="text-right">Quantity</TableHead>
                  <TableHead>Arrival Date</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {isLoading ? (
                  Array.from({ length: 6 }).map((_, index) => (
                    <TableRow key={index}>
                      <TableCell colSpan={6} className="py-5">
                        <div className="h-4 bg-muted rounded animate-pulse" />
                      </TableCell>
                    </TableRow>
                  ))
                ) : error ? (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center text-destructive py-10">
                      Failed to load shipments. Please refresh the page or try again later.
                    </TableCell>
                  </TableRow>
                ) : filtered.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center text-muted-foreground py-10">
                      No shipments match your filters.
                    </TableCell>
                  </TableRow>
                ) : (
                  filtered.map((s) => {
                    const delayed = s.status === "Delayed";
                    return (
                      <TableRow
                        key={s.id}
                        className={`cursor-pointer transition-colors ${
                          delayed
                            ? "bg-destructive/[0.03] hover:bg-destructive/[0.06]"
                            : "hover:bg-muted/40"
                        }`}
                      >
                        <TableCell className="font-mono text-xs relative">
                          {delayed && (
                            <span className="absolute left-0 top-2 bottom-2 w-0.5 rounded-full bg-destructive" />
                          )}
                          {s.shipment_number}
                        </TableCell>
                        <TableCell className="font-medium">{s.supplier_name}</TableCell>
                        <TableCell className="text-muted-foreground">{s.product_name}</TableCell>
                        <TableCell className="text-right tabular-nums">
                          {s.quantity.toLocaleString()}
                        </TableCell>
                        <TableCell className="tabular-nums">
                          {new Date(s.expected_arrival).toLocaleDateString()}
                        </TableCell>
                        <TableCell>
                          <StatusBadge label={s.status} tone={statusTone(s.status)} />
                        </TableCell>
                      </TableRow>
                    );
                  })
                )}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}

function Stat({
  icon: Icon,
  label,
  value,
  tone,
}: {
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  value: number;
  tone: "info" | "success" | "destructive" | "warning";
}) {
  const toneMap = {
    info: "bg-info/12 text-info",
    success: "bg-success/12 text-success",
    destructive: "bg-destructive/12 text-destructive",
    warning: "bg-warning/15 text-warning-foreground",
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
      </div>
    </div>
  );
}
