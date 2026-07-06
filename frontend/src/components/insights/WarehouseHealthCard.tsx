import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import type { WarehouseInsightItem } from "@/lib/api/endpoints";

type WarehouseHealthCardProps = {
  title: string;
  items: WarehouseInsightItem[];
};

export function WarehouseHealthCard({ title, items }: WarehouseHealthCardProps) {
  return (
    <Card className="border-border/70">
      <CardContent className="p-4">
        <div className="text-sm font-semibold">{title}</div>
        <div className="mt-3 space-y-3">
          {items.length === 0 ? (
            <p className="text-sm text-muted-foreground">No warehouse zones to show.</p>
          ) : (
            items.map((item) => (
              <div key={item.id} className="rounded-xl border border-border/70 bg-muted/25 p-3">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <div className="text-sm font-semibold">{item.name}</div>
                    <div className="text-xs text-muted-foreground">{item.zone_type}</div>
                  </div>
                  <Badge variant="outline">{item.status}</Badge>
                </div>
                <div className="mt-2 text-xs text-muted-foreground">
                  {item.occupied_units}/{item.capacity_units} occupied · {item.available_capacity} free
                </div>
                <div className="mt-1 h-2 overflow-hidden rounded-full bg-muted">
                  <div className="h-full rounded-full bg-primary" style={{ width: `${Math.min(item.occupancy_percentage, 100)}%` }} />
                </div>
                <div className="mt-1 text-xs text-muted-foreground">{item.occupancy_percentage}% occupancy</div>
              </div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  );
}
