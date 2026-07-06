import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";

export function ConfidenceGauge({ confidence }: { confidence: number }) {
  return (
    <Card>
      <CardContent className="p-4">
        <div className="flex items-end justify-between gap-3">
          <div>
            <div className="text-xs uppercase tracking-wider text-muted-foreground font-semibold">
              Confidence
            </div>
            <div className="text-3xl font-bold font-[family-name:var(--font-heading)]">
              {confidence}%
            </div>
          </div>
          <div className="text-sm text-muted-foreground">Decision certainty</div>
        </div>
        <Progress value={confidence} className="mt-4 h-2" />
      </CardContent>
    </Card>
  );
}
