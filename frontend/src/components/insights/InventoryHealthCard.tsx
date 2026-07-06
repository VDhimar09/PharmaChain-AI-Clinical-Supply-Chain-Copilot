import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import type { InventoryInsightItem } from "@/lib/api/endpoints";

type InventoryHealthCardProps = {
  title: string;
  items: InventoryInsightItem[];
};

export function InventoryHealthCard({ title, items }: InventoryHealthCardProps) {
  return (
    <Card className="border-border/70">
      <CardContent className="p-4">
        <div className="text-sm font-semibold">{title}</div>
        <div className="mt-3 space-y-3">
          {items.length === 0 ? (
            <p className="text-sm text-muted-foreground">No items in this category right now.</p>
          ) : (
            items.map((item) => (
              <div key={item.id} className="rounded-xl border border-border/70 bg-muted/25 p-3">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <div className="text-sm font-semibold">{item.product_name}</div>
                    <div className="text-xs text-muted-foreground">
                      {item.sku} · {item.category} · {item.warehouse_zone}
                    </div>
                  </div>
                  <Badge variant="outline">{item.status}</Badge>
                </div>
                <div className="mt-2 text-xs text-muted-foreground">
                  {item.available_quantity} available · {item.reserved_quantity} reserved · {item.quantity} total
                </div>
                {item.days_to_expiry !== null ? (
                  <div className="mt-1 text-xs text-muted-foreground">Expires in {item.days_to_expiry} days</div>
                ) : null}
              </div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  );
}
