import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import type { ShipmentInsightItem } from "@/lib/api/endpoints";

type ShipmentCardProps = {
  title: string;
  items: ShipmentInsightItem[];
};

export function ShipmentCard({ title, items }: ShipmentCardProps) {
  return (
    <Card className="border-border/70">
      <CardContent className="p-4">
        <div className="text-sm font-semibold">{title}</div>
        <div className="mt-3 space-y-3">
          {items.length === 0 ? (
            <p className="text-sm text-muted-foreground">No shipments in this view.</p>
          ) : (
            items.map((item) => (
              <div key={item.id} className="rounded-xl border border-border/70 bg-muted/25 p-3">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <div className="text-sm font-semibold">{item.shipment_number}</div>
                    <div className="text-xs text-muted-foreground">
                      {item.product_name} · {item.supplier_name}
                    </div>
                  </div>
                  <Badge variant="outline">{item.status}</Badge>
                </div>
                <div className="mt-2 text-xs text-muted-foreground">
                  {item.shipment_type} · {item.quantity.toLocaleString()} units
                </div>
                <div className="mt-1 text-xs text-muted-foreground">
                  ETA {new Date(item.expected_arrival).toLocaleDateString()}
                  {item.delay_days !== null ? ` · ${item.delay_days} day delay` : ""}
                </div>
              </div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  );
}
