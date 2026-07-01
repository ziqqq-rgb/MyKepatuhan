import type { IngestJob } from "@/lib/api";

type StatusKey = "status_queued" | "status_processing" | "status_done" | "status_failed";

const STATUS_STYLES: Record<IngestJob["status"], { key: StatusKey; cls: string }> = {
  queued: { key: "status_queued", cls: "bg-secondary text-muted-foreground" },
  processing: { key: "status_processing", cls: "bg-primary/10 text-primary animate-pulse" },
  done: { key: "status_done", cls: "bg-success/10 text-success" },
  failed: { key: "status_failed", cls: "bg-destructive/10 text-destructive" },
};

export function StatusBadge({
  status,
  tr,
}: {
  status: IngestJob["status"];
  tr: (k: StatusKey) => string;
}) {
  const { key, cls } = STATUS_STYLES[status];
  return (
    <span className={`shrink-0 rounded-full px-2.5 py-0.5 text-xs font-medium ${cls}`}>
      {tr(key)}
    </span>
  );
}