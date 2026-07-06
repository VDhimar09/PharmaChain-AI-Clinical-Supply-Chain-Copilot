import { Sparkles } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";

const steps = [
  "Detecting intent from the executive request...",
  "Building deterministic execution plan...",
  "Collecting evidence from operational tools...",
  "Composing explainable response...",
];

export function ThinkingIndicator() {
  return (
    <Card className="overflow-hidden">
      <div className="h-0.5 w-full bg-gradient-to-r from-transparent via-primary to-transparent bg-[length:200%_100%] animate-[ai-shimmer_1.6s_linear_infinite]" />
      <CardContent className="p-5">
        <div className="flex items-center gap-3">
          <div className="relative size-11 shrink-0">
            <div className="absolute inset-0 rounded-2xl border-2 border-primary/25 border-t-primary ai-orbit" />
            <div className="absolute inset-1 grid place-items-center rounded-xl bg-gradient-to-br from-primary to-teal shadow-lg shadow-primary/25">
              <Sparkles className="size-4 text-primary-foreground" />
            </div>
          </div>
          <div>
            <div className="text-[11px] font-bold uppercase tracking-[0.22em] text-primary">Executive Copilot thinking</div>
            <div className="text-[15px] font-semibold">Gathering evidence across the operational stack</div>
          </div>
        </div>
        <ul className="mt-4 grid gap-2">
          {steps.map((step, index) => (
            <li
              key={step}
              className="flex items-center gap-2.5 text-[12.5px] text-muted-foreground opacity-0 animate-in fade-in slide-in-from-left-1"
              style={{ animationDelay: `${index * 140}ms`, animationDuration: "400ms", animationFillMode: "forwards" }}
            >
              <span className="size-1.5 rounded-full bg-primary/70 animate-pulse" />
              <span>{step}</span>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
}
