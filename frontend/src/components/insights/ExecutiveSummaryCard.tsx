import type { LucideIcon } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";

type ExecutiveSummaryCardProps = {
  title: string;
  value: string;
  subtitle: string;
  icon: LucideIcon;
};

export function ExecutiveSummaryCard({
  title,
  value,
  subtitle,
  icon: Icon,
}: ExecutiveSummaryCardProps) {
  return (
    <Card className="overflow-hidden border-border/70 bg-gradient-to-br from-card via-card to-muted/30">
      <CardContent className="p-5">
        <div className="flex items-start justify-between gap-4">
          <div>
            <div className="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted-foreground">
              {title}
            </div>
            <div className="mt-3 text-3xl font-bold tracking-tight">{value}</div>
            <div className="mt-2 text-sm text-muted-foreground">{subtitle}</div>
          </div>
          <span className="grid size-11 place-items-center rounded-2xl bg-primary/10 text-primary">
            <Icon className="size-5" />
          </span>
        </div>
      </CardContent>
    </Card>
  );
}
