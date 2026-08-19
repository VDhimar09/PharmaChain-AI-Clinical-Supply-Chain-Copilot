import { CheckCircle2 } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import type { CopilotEvidenceBundle, CopilotToolExecution } from "@/lib/api/endpoints";

const sectionByTool = {
  inventory: "inventory",
  warehouse: "warehouse",
  shipment: "shipments",
  shipments: "shipments",
  procurement: "procurement",
  ai_insights: "ai_insights",
} as const;

const toolLabels = {
  inventory: "Inventory Tool",
  warehouse: "Warehouse Tool",
  shipment: "Shipment Tool",
  shipments: "Shipment Tool",
  procurement: "Procurement Tool",
  ai_insights: "AI Insights Tool",
} as const;

const sections: Array<keyof CopilotEvidenceBundle> = [
  "inventory",
  "warehouse",
  "shipments",
  "procurement",
  "ai_insights",
];

type EvidenceMetric = {
  label: string;
  value: string;
};

function metric(
  data: Record<string, unknown>,
  key: string,
  label: string,
  suffix = "",
): EvidenceMetric | null {
  const value = data[key];
  if (typeof value !== "number" && typeof value !== "string") {
    return null;
  }

  return { label, value: `${value}${suffix}` };
}

function metricsFor(
  section: keyof CopilotEvidenceBundle,
  data: Record<string, unknown>,
): EvidenceMetric[] {
  switch (section) {
    case "inventory":
      return [
        metric(data, "total_inventory_items", "inventory items"),
        metric(data, "total_quantity", "total units"),
        metric(data, "total_available_quantity", "available units"),
        metric(data, "low_stock_products", "low-stock products"),
      ].filter((item): item is EvidenceMetric => item !== null);
    case "warehouse":
      return [
        metric(data, "occupancy_percentage", "warehouse utilisation", "%"),
        metric(data, "available_capacity", "available capacity"),
        metric(data, "total_capacity", "total capacity"),
      ].filter((item): item is EvidenceMetric => item !== null);
    case "shipments":
      return [
        metric(data, "total_shipments", "total shipments"),
        metric(data, "delayed_shipments", "delayed shipments"),
        metric(data, "outbound_shipments", "outbound shipments"),
        metric(data, "inbound_shipments", "inbound shipments"),
      ].filter((item): item is EvidenceMetric => item !== null);
    case "procurement":
      return [
        metric(data, "decision", "decision"),
        metric(data, "risk_level", "risk level"),
        metric(data, "projected_occupancy_percent", "projected utilisation", "%"),
        metric(data, "recommended_zone", "recommended zone"),
      ].filter((item): item is EvidenceMetric => item !== null);
    case "ai_insights": {
      const executiveSummary = data.executive_summary;
      if (
        !executiveSummary ||
        typeof executiveSummary !== "object" ||
        Array.isArray(executiveSummary)
      ) {
        return [];
      }

      const summary = executiveSummary as Record<string, unknown>;
      return [
        metric(summary, "critical_alerts", "critical alerts"),
        metric(summary, "warehouse_utilisation", "warehouse utilisation", "%"),
        metric(summary, "pending_procurements", "pending procurements"),
        metric(summary, "inventory_value", "inventory units"),
      ].filter((item): item is EvidenceMetric => item !== null);
    }
  }
}

export function EvidenceViewer({
  evidence,
  toolExecution,
}: {
  evidence: CopilotEvidenceBundle;
  toolExecution: CopilotToolExecution[];
}) {
  const successfulTools = toolExecution.flatMap((tool) => {
    const normalizedTool = tool.tool.toLowerCase().replaceAll(" ", "_");
    const section = sectionByTool[normalizedTool as keyof typeof sectionByTool];

    return tool.status === "SUCCESS" && section
      ? [{ section, label: toolLabels[normalizedTool as keyof typeof toolLabels] }]
      : [];
  });

  if (successfulTools.length === 0) {
    return null;
  }

  return (
    <Card className="border-border/70">
      <CardContent className="p-5">
        <div className="text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">
          Operational Evidence
        </div>
        <div className="mt-4 space-y-3">
          {successfulTools.map(({ section, label }) => {
            const metrics = metricsFor(section, evidence[section]);

            return (
              <div key={section} className="rounded-xl border border-border/70 bg-muted/20 p-4">
                <div className="flex items-center gap-2 text-sm font-semibold">
                  <CheckCircle2 className="size-4 shrink-0 text-emerald-600" aria-hidden="true" />
                  {label}
                </div>
                {metrics.length > 0 ? (
                  <ul className="mt-2 space-y-1 text-sm text-muted-foreground">
                    {metrics.map((item) => (
                      <li key={item.label}>
                        <span className="font-medium text-foreground">{item.value}</span>{" "}
                        {item.label}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="mt-2 text-sm text-muted-foreground">
                    No summary metrics available.
                  </p>
                )}
              </div>
            );
          })}
        </div>

        <details className="group mt-4 rounded-xl border border-border/70 bg-muted/10 p-4">
          <summary className="cursor-pointer text-sm font-medium text-foreground marker:text-muted-foreground">
            <span className="group-open:hidden">View raw evidence</span>
            <span className="hidden group-open:inline">Hide raw evidence</span>
          </summary>
          <div className="mt-4 grid gap-4 xl:grid-cols-2">
            {sections.map((section) => (
              <div
                key={section}
                className="rounded-xl border border-border/70 bg-background/70 p-4"
              >
                <div className="text-sm font-semibold capitalize">{section.replace("_", " ")}</div>
                <pre className="mt-3 overflow-x-auto whitespace-pre-wrap text-xs leading-relaxed text-muted-foreground">
                  {JSON.stringify(evidence[section], null, 2)}
                </pre>
              </div>
            ))}
          </div>
        </details>
      </CardContent>
    </Card>
  );
}
