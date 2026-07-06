import { Card, CardContent } from "@/components/ui/card";

export function RecommendationPanel({ recommendations }: { recommendations: string[] }) {
  return (
    <Card className="border-border/70">
      <CardContent className="p-5">
        <div className="text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">Recommendations</div>
        <div className="mt-4 space-y-3">
          {recommendations.length === 0 ? (
            <p className="text-sm text-muted-foreground">No recommendations returned for this request.</p>
          ) : (
            recommendations.map((recommendation) => (
              <div key={recommendation} className="rounded-xl border border-border/70 bg-muted/20 p-3 text-sm leading-relaxed text-muted-foreground">
                {recommendation}
              </div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  );
}
