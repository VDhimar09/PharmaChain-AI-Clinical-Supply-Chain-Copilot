import type { ReactNode } from "react";

type KPIGridProps = {
  children: ReactNode;
};

export function KPIGrid({ children }: KPIGridProps) {
  return <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">{children}</div>;
}
