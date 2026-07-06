import { ArrowUpRight, ArrowRight, Sparkles } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import type { InsightRecommendation } from "@/lib/api/endpoints";

type RecommendationCardProps = {
  recommendation: InsightRecommendation;
};

const priorityClassName = {
  HIGH: "border-red-500/30 bg-red-500/10 text-red-700",
  MEDIUM: "border-amber-500/30 bg-amber-500/10 text-amber-700",
  LOW: "border-emerald-500/30 bg-emerald-500/10 text-emerald-700",
} as const;

export function RecommendationCard({ recommendation }: RecommendationCardProps) {
  return (
    <Card className="border-border/70 bg-gradient-to-br from-card to-muted/30">
      <CardContent className="p-4">
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center gap-2">
            <span className="grid size-9 place-items-center rounded-xl bg-primary/10 text-primary">
              <Sparkles className="size-4" />
            </span>
            <div>
              <div className="text-sm font-semibold">{recommendation.title}</div>
              <Badge variant="outline" className={`mt-1 ${priorityClassName[recommendation.priority]}`}>
                {recommendation.priority} PRIORITY
              </Badge>
            </div>
          </div>
          {recommendation.priority === "HIGH" ? (
            <ArrowUpRight className="size-4 text-primary" />
          ) : (
            <ArrowRight className="size-4 text-muted-foreground" />
          )}
        </div>
        <p className="mt-3 text-sm leading-relaxed text-muted-foreground">{recommendation.message}</p>
      </CardContent>
    </Card>
  );
}
