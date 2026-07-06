import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import type { ProcurementInsightItem } from "@/lib/api/endpoints";

type ProcurementCardProps = {
  title: string;
  items: ProcurementInsightItem[];
};

export function ProcurementCard({ title, items }: ProcurementCardProps) {
  return (
    <Card className="border-border/70">
      <CardContent className="p-4">
        <div className="text-sm font-semibold">{title}</div>
        <div className="mt-3 space-y-3">
          {items.length === 0 ? (
            <p className="text-sm text-muted-foreground">No procurement requests in this state.</p>
          ) : (
            items.map((item) => (
              <div key={item.id} className="rounded-xl border border-border/70 bg-muted/25 p-3">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <div className="text-sm font-semibold">{item.product_name}</div>
                    <div className="text-xs text-muted-foreground">
                      {item.priority} priority · requested by {item.created_by}
                    </div>
                  </div>
                  <Badge variant="outline">{item.status}</Badge>
                </div>
                <div className="mt-2 text-xs text-muted-foreground">
                  {item.requested_quantity.toLocaleString()} units · created {new Date(item.created_at).toLocaleDateString()}
                </div>
                {item.ai_recommendation ? (
                  <div className="mt-1 text-xs text-muted-foreground">
                    AI recommendation {item.ai_recommendation}
                    {item.ai_confidence !== null ? ` · ${Math.round(item.ai_confidence)}% confidence` : ""}
                  </div>
                ) : null}
              </div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  );
}
