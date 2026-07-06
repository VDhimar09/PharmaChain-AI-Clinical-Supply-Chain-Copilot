import { Card, CardContent } from "@/components/ui/card";
import type { CopilotToolExecution } from "@/lib/api/endpoints";

export function ToolExecutionTimeline({ items }: { items: CopilotToolExecution[] }) {
  return (
    <Card className="border-border/70">
      <CardContent className="p-5">
        <div className="text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">Tool execution</div>
        <div className="mt-4 space-y-3">
          {items.map((item) => (
            <div key={`${item.tool}-${item.execution_time_ms}`} className="rounded-xl border border-border/70 bg-muted/25 p-3">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <div className="text-sm font-semibold">{item.tool}</div>
                  <div className="text-xs text-muted-foreground">{item.status}</div>
                </div>
                <div className="text-xs font-medium tabular-nums text-muted-foreground">
                  {item.execution_time_ms.toFixed(2)} ms
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
