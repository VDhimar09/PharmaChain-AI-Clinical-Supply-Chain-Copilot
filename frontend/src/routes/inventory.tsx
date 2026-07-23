import { createFileRoute } from "@tanstack/react-router";
import { AppLayout } from "@/components/AppLayout";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Search, Thermometer, Boxes, AlertTriangle, Clock, CheckCircle2 } from "lucide-react";
import { useMemo, useState } from "react";
import { StatusBadge, statusTone } from "@/components/StatusBadge";
import { AiInsight } from "@/components/AiInsight";
import { useInventory } from "@/lib/api/hooks";

export const Route = createFileRoute("/inventory")({
  head: () => ({
    meta: [
      { title: "Inventory — AI Clinical Supply Chain Copilot" },
      { name: "description", content: "Searchable inventory of vaccines, medicines, and clinical trial products." },
    ],
  }),
  component: InventoryPage,
});

function InventoryPage() {
  const [q, setQ] = useState("");
  const [cat, setCat] = useState<string>("All");
  const { data: inventory = [], isLoading, isError } = useInventory();

  const filtered = useMemo(() => {
    const term = q.toLowerCase();
    return inventory.filter(
      (i) =>
        (cat === "All" || i.category === cat) &&
        (i.product_name.toLowerCase().includes(term) || i.sku.toLowerCase().includes(term)),
    );
  }, [q, cat]);

  const summary = useMemo(() => {
    const total = inventory.reduce((a, i) => a + i.available_quantity, 0);
    const critical = inventory.filter((i) => i.status === "Critical").length;
    const low = inventory.filter((i) => i.status === "Low Stock").length;
    const expiring = inventory.filter((i) => i.status === "Expiring Soon").length;
    const healthy = inventory.filter((i) => i.status === "In Stock").length;
    return { total, critical, low, expiring, healthy };
  }, [inventory]);
  const inventoryUnavailable = isLoading || isError;

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* KPI summary */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <KpiTile icon={Boxes} label="Total units" value={inventoryUnavailable ? "Unavailable" : summary.total.toLocaleString()} caption={isLoading ? "Loading inventory" : isError ? "No backend data" : `${inventory.length} SKUs tracked`} tone="primary" />
          <KpiTile icon={CheckCircle2} label="Healthy SKUs" value={inventoryUnavailable ? "Unavailable" : String(summary.healthy)} caption="In stock & in spec" tone="success" />
          <KpiTile icon={AlertTriangle} label="Low / critical" value={inventoryUnavailable ? "Unavailable" : String(summary.low + summary.critical)} caption={inventoryUnavailable ? "Unavailable" : `${summary.critical} critical · ${summary.low} low`} tone="warning" />
          <KpiTile icon={Clock} label="Expiring soon" value={inventoryUnavailable ? "Unavailable" : String(summary.expiring)} caption={inventoryUnavailable ? "Unavailable" : "< 30 days to expiry"} tone="info" />
        </div>

        {/* AI insight */}
        <AiInsight
          eyebrow="Inventory copilot"
          detected="2 SKUs are projected to stock out within 14 days at current run-rate."
          matters="Influenza Quadrivalent (95 units) and Trial Biologic BIO-22 (48 units) fall below safety stock against forecast demand."
          action="Initiate POs to Sanofi (600 units) and Roche (40 units) today to preserve coverage."
          confidence={91}
          risk="high"
          cta="Open procurement"
        />

        {/* Filters */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
          <div className="relative w-full md:w-96">
            <Search className="size-4 text-muted-foreground absolute left-3 top-1/2 -translate-y-1/2" />
            <Input
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="Search by product or SKU…"
              className="pl-9 bg-card"
            />
          </div>
          <div className="flex gap-2 flex-wrap">
            {["All", "Vaccine", "Medicine", "Clinical Trial"].map((c) => (
              <button
                key={c}
                onClick={() => setCat(c)}
                className={`px-3 py-1.5 rounded-md text-xs font-semibold border transition-colors ${
                  cat === c
                    ? "bg-primary text-primary-foreground border-primary shadow-sm shadow-primary/20"
                    : "bg-card hover:bg-muted border-border text-muted-foreground hover:text-foreground"
                }`}
              >
                {c}
              </button>
            ))}
          </div>
        </div>

        <Card className="overflow-hidden">
          <CardContent className="p-0 overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow className="bg-muted/40 hover:bg-muted/40">
                  <TableHead>Product Name</TableHead>
                  <TableHead>SKU</TableHead>
                  <TableHead>Category</TableHead>
                  <TableHead>Temperature</TableHead>
                  <TableHead className="text-right">Available</TableHead>
                  <TableHead className="text-right">Reserved</TableHead>
                  <TableHead>Expiry Date</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filtered.map((i) => {
                  const critical = i.status === "Critical";
                  return (
                    <TableRow
                      key={i.id}
                      className={`group cursor-pointer transition-colors ${
                        critical ? "bg-destructive/[0.03] hover:bg-destructive/[0.06]" : "hover:bg-muted/40"
                      }`}
                    >
                      <TableCell className="font-medium relative">
                        {critical && (
                          <span className="absolute left-0 top-2 bottom-2 w-0.5 rounded-full bg-destructive" />
                        )}
                        {i.product_name}
                      </TableCell>
                      <TableCell className="text-muted-foreground font-mono text-xs">{i.sku}</TableCell>
                      <TableCell>
                        <span className="text-xs px-2 py-0.5 rounded-md bg-secondary text-secondary-foreground">
                          {i.category}
                        </span>
                      </TableCell>
                      <TableCell>
                        <span className="inline-flex items-center gap-1 text-xs text-muted-foreground">
                          <Thermometer className="size-3" />
                          {i.temperature_requirement}
                        </span>
                      </TableCell>
                      <TableCell className="text-right tabular-nums font-medium">{i.available_quantity.toLocaleString()}</TableCell>
                      <TableCell className="text-right tabular-nums text-muted-foreground">{i.reserved_quantity.toLocaleString()}</TableCell>
                      <TableCell className="text-sm tabular-nums">{i.expiry_date}</TableCell>
                      <TableCell><StatusBadge label={i.status} tone={statusTone(i.status)} /></TableCell>
                    </TableRow>
                  );
                })}
                {filtered.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={8} className="text-center text-muted-foreground py-10">
                      {isLoading ? "Loading inventory…" : isError ? "Unable to load inventory." : "No products match your search."}
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}

function KpiTile({
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
      <div className="flex items-center justify-between">
        <span className={`size-9 rounded-xl grid place-items-center ${toneMap[tone]}`}>
          <Icon className="size-4" />
        </span>
      </div>
      <div className="mt-4">
        <div className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">{label}</div>
        <div className="mt-1 text-[32px] leading-none font-bold font-[family-name:var(--font-heading)] tabular-nums tracking-tight">
          {value}
        </div>
        <div className="mt-1.5 text-[12px] text-muted-foreground">{caption}</div>
      </div>
    </div>
  );
}
