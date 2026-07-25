// SSE diagnostics log panel: shows chronological reconnect attempts, backoff
// values, and error/event messages captured by BenchmarkRunner. Includes
// copy-to-clipboard and clear actions for easy debugging.
import { useMemo, useState } from "react";
import { toast } from "sonner";
import { useSseLog, clearSseLog, type SseLogEntry } from "@/lib/sse-log";

const KIND_STYLES: Record<SseLogEntry["kind"], string> = {
  connect: "text-muted-foreground",
  open: "text-leo",
  error: "text-red-400",
  reconnect: "text-yellow-400",
  "polling-start": "text-yellow-400",
  "polling-recover": "text-leo",
  closed: "text-muted-foreground",
  info: "text-muted-foreground",
};

function formatEntry(e: SseLogEntry): string {
  const ts = new Date(e.at).toISOString();
  const bits = [ts, e.kind.toUpperCase(), e.message];
  if (e.attempt != null) bits.push(`attempt=${e.attempt}`);
  if (e.backoffMs != null) bits.push(`backoff=${e.backoffMs}ms`);
  if (e.transport) bits.push(`transport=${e.transport}`);
  if (e.readyState != null) bits.push(`readyState=${e.readyState}`);
  return bits.join(" · ");
}

export function SseDiagnosticsLog() {
  const log = useSseLog();
  const [filter, setFilter] = useState<"all" | SseLogEntry["kind"]>("all");

  const filtered = useMemo(
    () => (filter === "all" ? log : log.filter((e) => e.kind === filter)),
    [log, filter],
  );

  async function copyAll() {
    const text = filtered.map(formatEntry).join("\n");
    if (!text) {
      toast.error("No SSE log entries to copy");
      return;
    }
    try {
      await navigator.clipboard.writeText(text);
      toast.success(`Copied ${filtered.length} log entries`);
    } catch {
      toast.error("Clipboard write failed");
    }
  }

  async function copyOne(e: SseLogEntry) {
    try {
      await navigator.clipboard.writeText(formatEntry(e));
      toast.success("Entry copied");
    } catch {
      toast.error("Clipboard write failed");
    }
  }

  return (
    <div className="border border-border p-4">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <div>
          <p className="eyebrow">SSE diagnostics log</p>
          <p className="mt-1 text-xs text-muted-foreground">
            Last {log.length} lifecycle events · reconnect attempts, backoff, errors
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2 text-xs">
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value as typeof filter)}
            className="border border-border bg-background px-2 py-1 font-mono text-xs focus:border-leo focus:outline-none"
            aria-label="Filter SSE log entries"
          >
            <option value="all">all</option>
            <option value="open">open</option>
            <option value="error">error</option>
            <option value="reconnect">reconnect</option>
            <option value="polling-start">polling-start</option>
            <option value="polling-recover">polling-recover</option>
            <option value="connect">connect</option>
            <option value="closed">closed</option>
            <option value="info">info</option>
          </select>
          <button
            type="button"
            onClick={copyAll}
            className="border border-border px-2 py-1 text-xs font-semibold hover:border-leo hover:text-leo"
          >
            Copy all
          </button>
          <button
            type="button"
            onClick={() => {
              clearSseLog();
              toast.message("SSE log cleared");
            }}
            className="border border-border px-2 py-1 text-xs font-semibold hover:border-red-400 hover:text-red-400"
          >
            Clear
          </button>
        </div>
      </div>

      <div className="mt-3 max-h-72 overflow-y-auto border border-border bg-background/60 font-mono text-[11px]">
        {filtered.length === 0 ? (
          <p className="p-3 text-muted-foreground">
            No SSE events recorded yet. Start the benchmark runner to capture stream lifecycle.
          </p>
        ) : (
          <ul className="divide-y divide-border/60">
            {filtered
              .slice()
              .reverse()
              .map((e) => (
                <li key={e.id} className="flex items-start gap-2 p-2">
                  <span className="w-20 shrink-0 text-muted-foreground">
                    {new Date(e.at).toLocaleTimeString()}
                  </span>
                  <span className={`w-24 shrink-0 font-semibold ${KIND_STYLES[e.kind]}`}>
                    {e.kind}
                  </span>
                  <span className="flex-1 break-all">
                    {e.message}
                    {e.attempt != null && (
                      <span className="ml-2 text-muted-foreground">attempt={e.attempt}</span>
                    )}
                    {e.backoffMs != null && (
                      <span className="ml-2 text-muted-foreground">backoff={e.backoffMs}ms</span>
                    )}
                    {e.transport && (
                      <span className="ml-2 text-muted-foreground">transport={e.transport}</span>
                    )}
                    {e.readyState != null && (
                      <span className="ml-2 text-muted-foreground">rs={e.readyState}</span>
                    )}
                  </span>
                  <button
                    type="button"
                    onClick={() => copyOne(e)}
                    className="shrink-0 border border-border px-1.5 py-0.5 text-[10px] hover:border-leo hover:text-leo"
                    title="Copy this entry"
                  >
                    copy
                  </button>
                </li>
              ))}
          </ul>
        )}
      </div>
    </div>
  );
}
