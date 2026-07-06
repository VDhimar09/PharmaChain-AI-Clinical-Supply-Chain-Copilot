import { BrainCircuit, Clock3, ShieldCheck } from "lucide-react";
import { Badge } from "@/components/ui/badge";

type ConversationHeaderProps = {
  isThinking: boolean;
  lastUpdated?: string;
};

export function ConversationHeader({ isThinking, lastUpdated }: ConversationHeaderProps) {
  return (
    <section className="relative overflow-hidden rounded-3xl border border-border/70 bg-[radial-gradient(circle_at_top_right,_rgba(20,184,166,0.14),_transparent_24%),linear-gradient(135deg,_rgba(15,23,42,1),_rgba(15,23,42,0.92)_58%,_rgba(10,20,35,1))] p-6 text-white shadow-[0_30px_80px_-42px_rgba(15,23,42,0.95)] md:p-8">
      <div className="absolute inset-0 bg-[radial-gradient(circle,_rgba(255,255,255,0.06)_1px,_transparent_1px)] [background-size:28px_28px] opacity-20" />
      <div className="relative flex flex-wrap items-start justify-between gap-4">
        <div className="max-w-3xl">
          <div className="flex flex-wrap items-center gap-2 text-[11px] font-semibold uppercase tracking-[0.22em] text-emerald-300/90">
            <span className="inline-flex items-center gap-2">
              <span className="relative flex size-2">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-70" />
                <span className="relative inline-flex size-2 rounded-full bg-emerald-400" />
              </span>
              Executive Copilot
            </span>
            <span className="text-white/35">|</span>
            <span className="text-white/60">{isThinking ? "Deterministic reasoning active" : "Awaiting request"}</span>
          </div>
          <h1 className="mt-4 text-3xl font-bold tracking-tight md:text-4xl">
            Ask operational questions and inspect the evidence behind every answer.
          </h1>
          <p className="mt-3 text-sm leading-relaxed text-white/70 md:text-[15px]">
            The copilot reuses the existing planner, tool registry, reasoning engine, and AI Insights service to produce explainable executive responses without any LLM dependency.
          </p>
        </div>
        <div className="flex flex-col items-start gap-2 sm:items-end">
          <Badge variant="outline" className="border-white/15 bg-white/5 text-white/80">
            <BrainCircuit className="mr-1 size-3" />
            Rule-based planning
          </Badge>
          <Badge variant="outline" className="border-white/15 bg-white/5 text-white/80">
            <ShieldCheck className="mr-1 size-3" />
            Audit-ready evidence
          </Badge>
          {lastUpdated ? (
            <Badge variant="outline" className="border-white/15 bg-white/5 text-white/80">
              <Clock3 className="mr-1 size-3" />
              {lastUpdated}
            </Badge>
          ) : null}
        </div>
      </div>
    </section>
  );
}
