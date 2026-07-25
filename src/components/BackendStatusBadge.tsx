import { useBackendHealth } from "@/lib/backend-health";
import { usePollingIntervals } from "@/lib/health-history";

const DOT: Record<string, string> = {
  checking: "bg-yellow-400 animate-pulse",
  online: "bg-leo",
  unreachable: "bg-red-500",
  error: "bg-orange-400",
};
const LABEL: Record<string, string> = {
  checking: "Checking…",
  online: "Backend online",
  unreachable: "Backend unreachable",
  error: "Backend error",
};

export function BackendStatusBadge({ compact = false }: { compact?: boolean }) {
  const [polling] = usePollingIntervals();
  const h = useBackendHealth(polling.healthMs);

  const title = `${LABEL[h.status]} — ${h.url}${h.message ? ` (${h.message})` : ""}${
    h.latencyMs != null ? ` · ${h.latencyMs}ms` : ""
  }`;

  return (
    <div
      role="status"
      aria-live="polite"
      title={title}
      className="inline-flex items-center gap-2 border border-border bg-background/60 px-3 py-1.5 text-xs font-medium"
    >
      <span className={`inline-block h-2 w-2 rounded-full ${DOT[h.status]}`} aria-hidden />
      <span>{LABEL[h.status]}</span>
      {!compact && (
        <>
          <span className="text-muted-foreground">·</span>
          <code
            className="max-w-[280px] truncate font-mono text-[11px] text-muted-foreground"
            aria-label="Request URL"
          >
            {h.url}
          </code>
          {h.latencyMs != null && h.status === "online" && (
            <span className="text-muted-foreground">· {h.latencyMs}ms</span>
          )}
          <button
            type="button"
            onClick={h.refresh}
            className="ml-1 border border-border px-2 py-0.5 text-[11px] hover:border-leo hover:text-leo focus:outline-none focus-visible:ring-2 focus-visible:ring-leo"
            aria-label="Re-check backend health"
          >
            Retry
          </button>
        </>
      )}
      {h.status !== "online" && h.status !== "checking" && h.message && !compact && (
        <span className="ml-2 text-red-400" role="alert">
          {h.message}
        </span>
      )}
    </div>
  );
}
