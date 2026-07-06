import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { CheckCircle2, AlertTriangle, XCircle } from "lucide-react";

type Decision = "APPROVE" | "REJECT" | "REVIEW";

const decisionMeta: Record<
  Decision,
  {
    icon: typeof CheckCircle2;
    tone: string;
    badge: string;
  }
> = {
  APPROVE: {
    icon: CheckCircle2,
    tone: "border-success/40 bg-success/10",
    badge: "text-success border-success/40 bg-success/10",
  },
  REVIEW: {
    icon: AlertTriangle,
    tone: "border-warning/40 bg-warning/10",
    badge: "text-warning-foreground border-warning/40 bg-warning/10",
  },
  REJECT: {
    icon: XCircle,
    tone: "border-destructive/40 bg-destructive/10",
    badge: "text-destructive border-destructive/40 bg-destructive/10",
  },
};

export function DecisionCard({
  decision,
  summary,
}: {
  decision: Decision;
  summary: string;
}) {
  const meta = decisionMeta[decision];
  const Icon = meta.icon;

  return (
    <Card className={meta.tone}>
      <CardContent className="p-5 flex items-start justify-between gap-4">
        <div className="flex items-start gap-3">
          <div className="size-11 rounded-full bg-background grid place-items-center shrink-0">
            <Icon className="size-5" />
          </div>
          <div>
            <div className="text-xs uppercase tracking-wider text-muted-foreground font-semibold">
              Decision
            </div>
            <div className="text-2xl font-bold font-[family-name:var(--font-heading)]">{decision}</div>
            <p className="mt-1 text-sm text-muted-foreground leading-relaxed">{summary}</p>
          </div>
        </div>
        <Badge variant="outline" className={meta.badge}>
          {decision}
        </Badge>
      </CardContent>
    </Card>
  );
}
