import { CheckCircle2, XCircle } from "lucide-react";
import type { CopilotToolExecution } from "@/lib/api/endpoints";

export function OperationalEvidenceChecklist({ items }: { items: CopilotToolExecution[] }) {
  if (items.length === 0) {
    return null;
  }

  return (
    <ul className="space-y-1.5">
      {items.map((item) => (
        <li key={item.tool} className="flex items-center gap-1.5 text-xs text-muted-foreground">
          {item.status === "SUCCESS" ? (
            <CheckCircle2 className="size-3.5 shrink-0 text-emerald-600" />
          ) : (
            <XCircle className="size-3.5 shrink-0 text-red-600" />
          )}
          <span className="font-medium text-foreground">{item.tool}</span>
        </li>
      ))}
    </ul>
  );
}
