import { Card, CardContent } from "@/components/ui/card";
import type { CopilotEvidenceBundle } from "@/lib/api/endpoints";

const sections: Array<keyof CopilotEvidenceBundle> = [
  "inventory",
  "warehouse",
  "shipments",
  "procurement",
  "ai_insights",
];

export function EvidenceViewer({ evidence }: { evidence: CopilotEvidenceBundle }) {
  return (
    <Card className="border-border/70">
      <CardContent className="p-5">
        <div className="text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">Evidence</div>
        <div className="mt-4 grid gap-4 xl:grid-cols-2">
          {sections.map((section) => (
            <div key={section} className="rounded-xl border border-border/70 bg-muted/20 p-4">
              <div className="text-sm font-semibold capitalize">{section.replace("_", " ")}</div>
              <pre className="mt-3 overflow-x-auto whitespace-pre-wrap text-xs leading-relaxed text-muted-foreground">
                {JSON.stringify(evidence[section], null, 2)}
              </pre>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
