import { Sparkles, ArrowRight, ShieldAlert, AlertTriangle, CheckCircle2 } from "lucide-react";
import type { ReactNode } from "react";

export type RiskLevel = "low" | "medium" | "high";

const riskMap: Record<RiskLevel, { label: string; chip: string; dot: string; icon: typeof ShieldAlert }> = {
  low: {
    label: "Low risk",
    chip: "bg-success/10 text-success border-success/25",
    dot: "bg-success",
    icon: CheckCircle2,
  },
  medium: {
    label: "Medium risk",
    chip: "bg-warning/15 text-warning-foreground border-warning/30",
    dot: "bg-warning",
    icon: AlertTriangle,
  },
  high: {
    label: "High risk",
    chip: "bg-destructive/10 text-destructive border-destructive/25",
    dot: "bg-destructive",
    icon: ShieldAlert,
  },
};

export interface AiInsightProps {
  eyebrow?: string;
  detected: string;
  matters: string;
  action: string;
  confidence: number;
  risk: RiskLevel;
  cta?: string;
  onCta?: () => void;
  trailing?: ReactNode;
}

export function AiInsight({
  eyebrow = "AI insight",
  detected,
  matters,
  action,
  confidence,
  risk,
  cta = "Review",
  onCta,
  trailing,
}: AiInsightProps) {
  const r = riskMap[risk];
  const RiskIcon = r.icon;

  return (
    <section
      aria-label="AI insight"
      className="relative overflow-hidden rounded-2xl border border-primary/15 bg-gradient-to-br from-card via-card to-[color-mix(in_oklab,var(--color-primary)_5%,var(--color-card))] shadow-[0_1px_2px_color-mix(in_oklab,var(--color-foreground)_4%,transparent),0_16px_40px_-24px_color-mix(in_oklab,var(--color-primary)_30%,transparent)]"
    >
      <div
        aria-hidden
        className="absolute -top-16 -right-16 size-56 rounded-full blur-3xl opacity-30 pointer-events-none"
        style={{
          background:
            "radial-gradient(circle, color-mix(in oklab, var(--color-primary) 55%, transparent) 0%, transparent 70%)",
        }}
      />
      <div className="relative grid grid-cols-1 md:grid-cols-[auto_minmax(0,1fr)_auto] items-center gap-5 p-5">
        <div className="flex items-start gap-3 md:block">
          <div className="size-11 rounded-2xl bg-gradient-to-br from-primary to-teal grid place-items-center shadow-md shadow-primary/25 ring-1 ring-primary/20 shrink-0">
            <Sparkles className="size-5 text-primary-foreground" />
          </div>
        </div>

        <div className="min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-[10px] font-bold uppercase tracking-[0.22em] text-primary">
              {eyebrow}
            </span>
            <span
              className={`inline-flex items-center gap-1 text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md border ${r.chip}`}
            >
              <RiskIcon className="size-2.5" />
              {r.label}
            </span>
            <span className="inline-flex items-center gap-1 text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md border border-border bg-muted/60 text-muted-foreground tabular-nums">
              {confidence}% confidence
            </span>
          </div>
          <h3 className="mt-1.5 text-[16px] md:text-[17px] font-bold font-[family-name:var(--font-heading)] tracking-tight text-foreground leading-snug">
            {detected}
          </h3>
          <div className="mt-2 grid gap-1 text-[12.5px] leading-relaxed">
            <p className="text-muted-foreground">
              <span className="font-semibold text-foreground/80">Why it matters · </span>
              {matters}
            </p>
            <p className="text-muted-foreground">
              <span className="font-semibold text-foreground/80">Recommended action · </span>
              {action}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 md:flex-col md:items-end shrink-0">
          {trailing}
          <button
            onClick={onCta}
            className="inline-flex items-center gap-1.5 text-xs font-semibold px-3.5 py-2 rounded-md bg-primary text-primary-foreground hover:brightness-105 transition-all shadow-sm shadow-primary/25"
          >
            {cta}
            <ArrowRight className="size-3" />
          </button>
        </div>
      </div>
    </section>
  );
}
