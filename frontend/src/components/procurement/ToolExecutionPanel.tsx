import { Card, CardContent } from "@/components/ui/card";
import { CheckCircle2, XCircle } from "lucide-react";

import type { ProcurementToolExecution } from "@/lib/api/endpoints";

export function ToolExecutionPanel({
  items,
}: {
  items: ProcurementToolExecution[];
}) {
  return (
    <Card>
      <CardContent className="p-5">
        <div className="text-xs uppercase tracking-wider text-muted-foreground font-semibold">
          Tool execution
        </div>
        <div className="mt-4 space-y-2">
          {items.map((item) => {
            const ok = item.status === "SUCCESS";
            const Icon = ok ? CheckCircle2 : XCircle;

            return (
              <div
                key={`${item.tool}-${item.status}`}
                className="flex items-center justify-between rounded-lg border border-border/70 bg-card px-3 py-2.5"
              >
                <div className="flex items-center gap-2.5">
                  <Icon className={ok ? "size-4 text-success" : "size-4 text-destructive"} />
                  <span className="text-sm font-medium">{item.tool}</span>
                </div>
                <span className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                  {item.status}
                </span>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
