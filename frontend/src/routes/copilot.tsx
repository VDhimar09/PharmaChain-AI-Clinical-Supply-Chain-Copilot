import { createFileRoute } from "@tanstack/react-router";
import { FormEvent, useMemo, useState } from "react";
import { SendHorizonal } from "lucide-react";
import { AppLayout } from "@/components/AppLayout";
import { ChatMessage } from "@/components/copilot/ChatMessage";
import { ConversationHeader } from "@/components/copilot/ConversationHeader";
import { EvidenceViewer } from "@/components/copilot/EvidenceViewer";
import { RecommendationPanel } from "@/components/copilot/RecommendationPanel";
import { SuggestedPromptCard } from "@/components/copilot/SuggestedPromptCard";
import { ThinkingIndicator } from "@/components/copilot/ThinkingIndicator";
import { ToolExecutionTimeline } from "@/components/copilot/ToolExecutionTimeline";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { useCopilotChat } from "@/lib/api/hooks";
import type { CopilotChatResponse } from "@/lib/api/endpoints";
import { ApiError } from "@/lib/api/types";

export const Route = createFileRoute("/copilot")({
  head: () => ({
    meta: [
      { title: "AI Executive Copilot | PharmaChain" },
      {
        name: "description",
        content: "Deterministic AI executive copilot for operational questions and explainable evidence.",
      },
    ],
  }),
  component: CopilotPage,
});

type ConversationEntry =
  | { role: "user"; content: string }
  | { role: "assistant"; content: string; result: CopilotChatResponse };

const suggestedPrompts = [
  "What should I prioritise today?",
  "Summarise today's operations.",
  "Show warehouse risks.",
  "Show inventory risks.",
  "Which procurement requests require attention?",
  "Show delayed shipments.",
  "Explain today's AI recommendations.",
];

function CopilotPage() {
  const chatMutation = useCopilotChat();
  const [message, setMessage] = useState("What should I prioritise today?");
  const [conversation, setConversation] = useState<ConversationEntry[]>([]);

  const latestAssistantResult = useMemo(() => {
    for (let index = conversation.length - 1; index >= 0; index -= 1) {
      const entry = conversation[index];
      if (entry.role === "assistant") {
        return entry.result;
      }
    }
    return null;
  }, [conversation]);

  function submit(nextMessage: string) {
    const trimmed = nextMessage.trim();
    if (!trimmed || chatMutation.isPending) {
      return;
    }

    setConversation((current) => [...current, { role: "user", content: trimmed }]);
    setMessage("");

    chatMutation.mutate(
      { message: trimmed },
      {
        onSuccess: (result) => {
          setConversation((current) => [
            ...current,
            { role: "assistant", content: result.response, result },
          ]);
        },
        onError: (error) => {
          setConversation((current) => [
            ...current,
            {
              role: "assistant",
              content: getErrorMessage(error),
              result: {
                conversation_id: crypto.randomUUID(),
                generated_at: new Date().toISOString(),
                intent: "UNKNOWN",
                confidence: 0,
                tools_used: [],
                reasoning: [],
                tool_execution: [],
                evidence: {
                  inventory: {},
                  warehouse: {},
                  shipments: {},
                  procurement: {},
                  ai_insights: {},
                },
                recommendations: [],
                response: getErrorMessage(error),
              },
            },
          ]);
        },
      },
    );
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    submit(message);
  }

  return (
    <AppLayout>
      <div className="space-y-6">
        <ConversationHeader
          isThinking={chatMutation.isPending}
          lastUpdated={latestAssistantResult ? new Date(latestAssistantResult.generated_at).toLocaleString() : undefined}
        />

        <div className="grid gap-6 xl:grid-cols-[minmax(0,420px)_minmax(0,1fr)]">
          <div className="space-y-6">
            <Card className="border-border/70">
              <CardContent className="p-5">
                <div className="text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                  Suggested prompts
                </div>
                <div className="mt-4 grid gap-3">
                  {suggestedPrompts.map((prompt) => (
                    <SuggestedPromptCard key={prompt} prompt={prompt} onSelect={submit} />
                  ))}
                </div>
              </CardContent>
            </Card>

            {latestAssistantResult ? (
              <>
                <ToolExecutionTimeline items={latestAssistantResult.tool_execution} />
                <RecommendationPanel recommendations={latestAssistantResult.recommendations} />
              </>
            ) : null}
          </div>

          <div className="space-y-4">
            <Card className="border-border/70">
              <CardContent className="p-5">
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div>
                    <div className="text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                      Ask the copilot
                    </div>
                    <textarea
                      value={message}
                      onChange={(event) => setMessage(event.target.value)}
                      placeholder="Ask about priorities, risks, warehouse capacity, low stock, delayed shipments, or AI recommendations."
                      className="mt-3 min-h-28 w-full rounded-2xl border border-border/70 bg-background px-4 py-3 text-sm outline-none transition-colors focus:border-primary"
                    />
                  </div>
                  <div className="flex justify-end">
                    <Button type="submit" disabled={chatMutation.isPending || !message.trim()} className="gap-2">
                      <SendHorizonal className="size-4" />
                      {chatMutation.isPending ? "Analyzing..." : "Send to copilot"}
                    </Button>
                  </div>
                </form>
              </CardContent>
            </Card>

            {conversation.length === 0 ? (
              <Card className="border-border/70 bg-muted/20">
                <CardContent className="p-8 text-sm leading-relaxed text-muted-foreground">
                  Start with a suggested prompt or ask your own question. The Executive Copilot will plan tool usage, collect operational evidence, and return a structured, explainable answer.
                </CardContent>
              </Card>
            ) : (
              <div className="space-y-4">
                {conversation.map((entry, index) =>
                  entry.role === "user" ? (
                    <ChatMessage key={`${entry.role}-${index}`} role="user" content={entry.content} />
                  ) : (
                    <ChatMessage
                      key={`${entry.role}-${index}`}
                      role="assistant"
                      content={entry.content}
                      result={entry.result}
                    />
                  ),
                )}
              </div>
            )}

            {chatMutation.isPending ? <ThinkingIndicator /> : null}

            {latestAssistantResult ? <EvidenceViewer evidence={latestAssistantResult.evidence} /> : null}
          </div>
        </div>
      </div>
    </AppLayout>
  );
}

function getErrorMessage(error: Error): string {
  if (error instanceof ApiError) {
    if (typeof error.body?.detail === "string") {
      return error.body.detail;
    }
    if (typeof error.body?.message === "string") {
      return error.body.message;
    }
  }

  return error.message || "Unable to complete the copilot request.";
}
