import { Boxes, FileText, Layers, LucideIcon } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import type { CopilotEvidenceRequirement } from "@/lib/api/endpoints";

const CONFIG: Record<
  CopilotEvidenceRequirement,
  { label: string; icon: LucideIcon; className: string }
> = {
  OPERATIONAL: {
    label: "Operational evidence",
    icon: Boxes,
    className: "border-sky-500/30 bg-sky-500/10 text-sky-700",
  },
  DOCUMENT: {
    label: "Document evidence",
    icon: FileText,
    className: "border-violet-500/30 bg-violet-500/10 text-violet-700",
  },
  OPERATIONAL_AND_DOCUMENT: {
    label: "Operational + document",
    icon: Layers,
    className: "border-indigo-500/30 bg-indigo-500/10 text-indigo-700",
  },
};

export function EvidenceRequirementBadge({
  requirement,
}: {
  requirement: CopilotEvidenceRequirement;
}) {
  const config = CONFIG[requirement] ?? CONFIG.OPERATIONAL;
  const Icon = config.icon;

  return (
    <Badge variant="outline" className={config.className}>
      <Icon className="mr-1 size-3" />
      {config.label}
    </Badge>
  );
}
