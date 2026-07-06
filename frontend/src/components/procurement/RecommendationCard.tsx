import { Card, CardContent } from "@/components/ui/card";

export function RecommendationCard({
  recommendation,
  explanation,
}: {
  recommendation: string;
  explanation: string;
}) {
  return (
    <Card>
      <CardContent className="p-5 space-y-4">
        <div>
          <div className="text-xs uppercase tracking-wider text-muted-foreground font-semibold">
            Recommendation
          </div>
          <p className="mt-2 text-base font-semibold leading-relaxed">{recommendation}</p>
        </div>
        <div>
          <div className="text-xs uppercase tracking-wider text-muted-foreground font-semibold">
            Explanation
          </div>
          <pre className="mt-2 whitespace-pre-wrap break-words text-sm leading-relaxed text-muted-foreground font-sans">
            {explanation}
          </pre>
        </div>
      </CardContent>
    </Card>
  );
}
