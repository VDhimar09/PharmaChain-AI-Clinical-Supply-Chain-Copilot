import { cn } from "@/lib/utils";

type Tone = "success" | "warning" | "destructive" | "info" | "muted" | "primary";

const toneClass: Record<Tone, string> = {
  success: "bg-success/15 text-success border-success/30",
  warning: "bg-warning/15 text-warning-foreground border-warning/40",
  destructive: "bg-destructive/15 text-destructive border-destructive/30",
  info: "bg-info/15 text-info border-info/30",
  muted: "bg-muted text-muted-foreground border-border",
  primary: "bg-primary/10 text-primary border-primary/30",
};

export function StatusBadge({ label, tone = "muted", className }: { label: string; tone?: Tone; className?: string }) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium border",
        toneClass[tone],
        className,
      )}
    >
      <span className={cn("size-1.5 rounded-full", {
        "bg-success": tone === "success",
        "bg-warning": tone === "warning",
        "bg-destructive": tone === "destructive",
        "bg-info": tone === "info",
        "bg-muted-foreground": tone === "muted",
        "bg-primary": tone === "primary",
      })} />
      {label}
    </span>
  );
}

export function statusTone(status: string): Tone {
  switch (status) {
    case "In Stock":
    case "Delivered":
    case "APPROVED":
      return "success";
    case "Low Stock":
    case "Processing":
    case "Expiring Soon":
      return "warning";
    case "Critical":
    case "Delayed":
      return "destructive";
    case "In Transit":
      return "info";
    default:
      return "muted";
  }
}
