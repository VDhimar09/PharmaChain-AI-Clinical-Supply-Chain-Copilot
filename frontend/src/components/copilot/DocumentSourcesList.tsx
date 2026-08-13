import { FileText } from "lucide-react";
import type { CopilotCitation } from "@/lib/api/endpoints";

/**
 * Renders only server-validated citations - never raw retrieved chunks
 * and never a fabricated SOURCE_N. When a document-requiring question
 * produced no valid citations, this shows the controlled no-evidence
 * state instead of guessing.
 */
export function DocumentSourcesList({ citations }: { citations: CopilotCitation[] }) {
  if (citations.length === 0) {
    return (
      <p className="text-xs leading-relaxed text-muted-foreground">
        No supporting document evidence was found for this answer.
      </p>
    );
  }

  return (
    <ul className="space-y-1.5">
      {citations.map((citation, index) => (
        <li
          key={`${citation.document_id}-${citation.page_number}-${index}`}
          className="flex items-center gap-1.5 text-xs text-muted-foreground"
        >
          <FileText className="size-3.5 shrink-0 text-violet-600" />
          <span className="truncate font-medium text-foreground">{citation.filename}</span>
          <span className="text-muted-foreground/70">— Page {citation.page_number}</span>
        </li>
      ))}
    </ul>
  );
}
