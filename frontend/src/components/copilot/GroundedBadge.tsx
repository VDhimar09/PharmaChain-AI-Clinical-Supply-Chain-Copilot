import { ShieldAlert, ShieldCheck } from "lucide-react";
import { Badge } from "@/components/ui/badge";

/**
 * `grounded` is `null` for the deterministic, non-LLM operational path
 * (nothing to badge - it was never "grounded" or "ungrounded", it's a
 * direct tool result). Only document-only and combined answers set it.
 */
export function GroundedBadge({ grounded }: { grounded: boolean | null }) {
  if (grounded === null) {
    return null;
  }

  if (grounded) {
    return (
      <Badge variant="outline" className="border-emerald-500/30 bg-emerald-500/10 text-emerald-700">
        <ShieldCheck className="mr-1 size-3" />
        Grounded in documents
      </Badge>
    );
  }

  return (
    <Badge variant="outline" className="border-amber-500/30 bg-amber-500/10 text-amber-700">
      <ShieldAlert className="mr-1 size-3" />
      No document evidence found
    </Badge>
  );
}
