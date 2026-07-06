import { Badge } from "@/components/ui/badge";

export function ConfidenceBadge({ confidence }: { confidence: number }) {
  const toneClassName =
    confidence >= 90
      ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-700"
      : confidence >= 75
        ? "border-amber-500/30 bg-amber-500/10 text-amber-700"
        : "border-red-500/30 bg-red-500/10 text-red-700";

  return (
    <Badge variant="outline" className={toneClassName}>
      Confidence {confidence}%
    </Badge>
  );
}
