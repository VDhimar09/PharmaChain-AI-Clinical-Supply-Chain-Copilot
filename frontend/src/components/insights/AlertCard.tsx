import { AlertTriangle, Info, Siren, TriangleAlert } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import type { InsightAlert } from "@/lib/api/endpoints";

type AlertCardProps = {
  alert: InsightAlert;
};

const toneMap = {
  HIGH: {
    icon: Siren,
    badgeClassName: "border-red-500/30 bg-red-500/10 text-red-700",
    cardClassName: "border-red-500/20 bg-red-500/5",
  },
  MEDIUM: {
    icon: TriangleAlert,
    badgeClassName: "border-amber-500/30 bg-amber-500/10 text-amber-700",
    cardClassName: "border-amber-500/20 bg-amber-500/5",
  },
  LOW: {
    icon: Info,
    badgeClassName: "border-sky-500/30 bg-sky-500/10 text-sky-700",
    cardClassName: "border-sky-500/20 bg-sky-500/5",
  },
} as const;

export function AlertCard({ alert }: AlertCardProps) {
  const tone = toneMap[alert.severity];
  const Icon = tone.icon ?? AlertTriangle;

  return (
    <Card className={tone.cardClassName}>
      <CardContent className="flex gap-3 p-4">
        <span className="mt-0.5 grid size-9 shrink-0 place-items-center rounded-xl bg-background/80">
          <Icon className="size-4" />
        </span>
        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <Badge variant="outline" className={tone.badgeClassName}>
              {alert.severity}
            </Badge>
            <div className="text-sm font-semibold">{alert.title}</div>
          </div>
          <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{alert.message}</p>
        </div>
      </CardContent>
    </Card>
  );
}
