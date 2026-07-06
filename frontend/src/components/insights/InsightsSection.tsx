import type { ReactNode } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";

type InsightsSectionProps = {
  eyebrow: string;
  title: string;
  description?: string;
  actions?: ReactNode;
  children: ReactNode;
};

export function InsightsSection({
  eyebrow,
  title,
  description,
  actions,
  children,
}: InsightsSectionProps) {
  return (
    <Card className="border-border/70 shadow-sm">
      <CardHeader className="flex flex-row items-start justify-between gap-4 space-y-0">
        <div>
          <div className="text-[10px] font-bold uppercase tracking-[0.22em] text-primary">{eyebrow}</div>
          <CardTitle className="mt-1 text-xl font-bold tracking-tight">{title}</CardTitle>
          {description ? <CardDescription className="mt-1 text-sm">{description}</CardDescription> : null}
        </div>
        {actions}
      </CardHeader>
      <CardContent>{children}</CardContent>
    </Card>
  );
}
