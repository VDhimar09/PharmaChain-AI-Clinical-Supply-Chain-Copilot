import { Card, CardContent } from "@/components/ui/card";

import type { ProcurementReasoningStep } from "@/lib/api/endpoints";

const statusTone: Record<ProcurementReasoningStep["status"], string> = {
  PASS: "bg-success/15 text-success border-success/30",
  ATTENTION: "bg-warning/15 text-warning-foreground border-warning/30",
  FAIL: "bg-destructive/12 text-destructive border-destructive/30",
};

export function ReasoningTimeline({
  steps,
}: {
  steps: ProcurementReasoningStep[];
}) {
  return (
    <Card>
      <CardContent className="p-5">
        <div className="text-xs uppercase tracking-wider text-muted-foreground font-semibold">
          Reasoning timeline
        </div>
        <div className="mt-4 space-y-3">
          {steps.map((step) => (
            <div key={step.step} className="rounded-xl border border-border/70 bg-muted/30 p-3.5">
              <div className="flex items-start justify-between gap-3">
                <div className="text-sm font-semibold">{step.step}</div>
                <span className={`rounded-full border px-2 py-0.5 text-[11px] font-semibold ${statusTone[step.status]}`}>
                  {step.status}
                </span>
              </div>
              <p className="mt-1.5 text-sm text-muted-foreground leading-relaxed">{step.message}</p>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
