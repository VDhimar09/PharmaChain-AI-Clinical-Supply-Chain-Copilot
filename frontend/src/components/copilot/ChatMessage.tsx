import { BrainCircuit, User } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { ConfidenceBadge } from "@/components/copilot/ConfidenceBadge";
import type { CopilotChatResponse } from "@/lib/api/endpoints";

type ChatMessageProps = {
  role: "user" | "assistant";
  content: string;
  result?: CopilotChatResponse;
};

export function ChatMessage({ role, content, result }: ChatMessageProps) {
  const isUser = role === "user";

  return (
    <Card className={isUser ? "bg-secondary/45" : "border-border/70"}>
      <CardContent className={`flex gap-3 p-5 ${isUser ? "justify-end flex-row-reverse text-right" : ""}`}>
        <div className={`grid size-10 shrink-0 place-items-center rounded-2xl ${isUser ? "bg-muted" : "bg-primary/10 text-primary"}`}>
          {isUser ? <User className="size-4" /> : <BrainCircuit className="size-4" />}
        </div>
        <div className="min-w-0">
          <div className={`flex flex-wrap items-center gap-2 ${isUser ? "justify-end" : ""}`}>
            <div className="text-sm font-semibold">{isUser ? "You" : "Executive Copilot"}</div>
            {result ? <ConfidenceBadge confidence={result.confidence} /> : null}
          </div>
          <p className="mt-2 whitespace-pre-wrap text-sm leading-relaxed text-muted-foreground">{content}</p>
          {result ? (
            <div className={`mt-3 flex flex-wrap gap-2 text-xs text-muted-foreground ${isUser ? "justify-end" : ""}`}>
              <span>{result.intent}</span>
              <span>•</span>
              <span>{result.tools_used.length} tools used</span>
              <span>•</span>
              <span>{new Date(result.generated_at).toLocaleString()}</span>
            </div>
          ) : null}
        </div>
      </CardContent>
    </Card>
  );
}
