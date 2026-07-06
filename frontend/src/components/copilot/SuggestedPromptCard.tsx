import { ArrowUpRight } from "lucide-react";
import { Button } from "@/components/ui/button";

type SuggestedPromptCardProps = {
  prompt: string;
  onSelect: (prompt: string) => void;
};

export function SuggestedPromptCard({ prompt, onSelect }: SuggestedPromptCardProps) {
  return (
    <button
      type="button"
      onClick={() => onSelect(prompt)}
      className="group rounded-2xl border border-border/70 bg-card p-4 text-left transition-all hover:-translate-y-0.5 hover:border-primary/35 hover:shadow-[0_20px_40px_-30px_rgba(15,23,42,0.8)]"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="text-sm font-medium leading-relaxed text-foreground">{prompt}</div>
        <ArrowUpRight className="size-4 shrink-0 text-muted-foreground transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5 group-hover:text-primary" />
      </div>
      <Button variant="ghost" className="mt-3 h-auto px-0 text-xs text-muted-foreground hover:bg-transparent hover:text-primary">
        Use prompt
      </Button>
    </button>
  );
}
