import { ResponsiveContainer, CartesianGrid, XAxis, YAxis, Tooltip, AreaChart, Area, Legend } from "recharts";
import type { TrendPoint } from "@/lib/api/endpoints";
import { Card, CardContent } from "@/components/ui/card";

type TrendChartProps = {
  title: string;
  description: string;
  data: TrendPoint[];
  primaryLabel: string;
  secondaryLabel: string;
};

export function TrendChart({
  title,
  description,
  data,
  primaryLabel,
  secondaryLabel,
}: TrendChartProps) {
  return (
    <Card className="border-border/70">
      <CardContent className="p-4">
        <div className="text-sm font-semibold">{title}</div>
        <p className="mt-1 text-sm text-muted-foreground">{description}</p>
        {data.length === 0 ? (
          <div className="mt-4 rounded-xl border border-dashed border-border p-6 text-sm text-muted-foreground">
            No trend data available yet.
          </div>
        ) : (
          <div className="mt-4 h-72">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
                <defs>
                  <linearGradient id={`primary-${title}`} x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="var(--color-primary)" stopOpacity={0.35} />
                    <stop offset="100%" stopColor="var(--color-primary)" stopOpacity={0.02} />
                  </linearGradient>
                  <linearGradient id={`secondary-${title}`} x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="var(--color-teal)" stopOpacity={0.28} />
                    <stop offset="100%" stopColor="var(--color-teal)" stopOpacity={0.02} />
                  </linearGradient>
                </defs>
                <CartesianGrid vertical={false} strokeDasharray="3 6" />
                <XAxis dataKey="label" tickLine={false} axisLine={false} fontSize={11} />
                <YAxis tickLine={false} axisLine={false} fontSize={11} />
                <Tooltip />
                <Legend />
                <Area
                  type="monotone"
                  dataKey="value"
                  name={primaryLabel}
                  stroke="var(--color-primary)"
                  fill={`url(#primary-${title})`}
                  strokeWidth={2}
                />
                <Area
                  type="monotone"
                  dataKey="secondary_value"
                  name={secondaryLabel}
                  stroke="var(--color-teal)"
                  fill={`url(#secondary-${title})`}
                  strokeWidth={2}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
