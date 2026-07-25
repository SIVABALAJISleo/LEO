// Compact SSE connection status pill for the /benchmarks page header.
// Shows current state (connecting/open/error/reconnecting), reconnect
// attempt count, and the most recent backoff value from the sse-log.
import { useEffect, useState } from "react";
import { useSseLog } from "@/lib/sse-log";

const DIAG_KEY = "leo.bench.sse-diag";

type PersistedDiag = {
  lastEventAt: number | null;
  lastError: string | null;
  reconnectAttempts: number;
  transport: "sse" | "polling";
  status: "idle" | "open" | "reconnecting" | "closed" | "error" | "polling";
  savedAt: number;
};

function read(): PersistedDiag | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = window.localStorage.getItem(DIAG_KEY);
    return raw ? (JSON.parse(raw) as PersistedDiag) : null;
  } catch {
    return null;
  }
}

export function SseLiveIndicator() {
  const [diag, setDiag] = useState<PersistedDiag | null>(() => read());
  const log = useSseLog();

  useEffect(() => {
    const id = setInterval(() => setDiag(read()), 1000);
    return () => clearInterval(id);
  }, []);

  const status = diag?.status ?? "idle";
  const attempts = diag?.reconnectAttempts ?? 0;
  const lastReconnect = [...log].reverse().find((e) => e.kind === "reconnect");
  const backoff = lastReconnect?.backoffMs;

  const styles: Record<string, string> = {
    open: "border-leo bg-leo/10 text-leo",
    polling: "border-blue-400 bg-blue-400/10 text-blue-300",
    reconnecting: "border-yellow-400 bg-yellow-400/10 text-yellow-300",
    error: "border-red-500 bg-red-500/10 text-red-300",
    closed: "border-border text-muted-foreground",
    idle: "border-border text-muted-foreground",
  };
  const pulse = status === "reconnecting" ? "animate-pulse" : "";
  const label =
    status === "open"
      ? "SSE open"
      : status === "polling"
        ? "SSE → polling"
        : status === "reconnecting"
          ? "SSE reconnecting"
          : status === "error"
            ? "SSE error"
            : status === "closed"
              ? "SSE closed"
              : "SSE idle";

  return (
    <span
      role="status"
      aria-live="polite"
      title={diag?.lastError ? `Last error: ${diag.lastError}` : "Live SSE benchmark stream status"}
      className={`inline-flex items-center gap-2 border px-2.5 py-1 text-[11px] font-semibold uppercase tracking-wide ${styles[status] ?? styles.idle} ${pulse}`}
    >
      <span
        className={`inline-block h-1.5 w-1.5 rounded-full ${
          status === "open"
            ? "bg-leo"
            : status === "polling"
              ? "bg-blue-400"
              : status === "reconnecting"
                ? "bg-yellow-400"
                : status === "error"
                  ? "bg-red-500"
                  : "bg-muted-foreground/60"
        }`}
        aria-hidden
      />
      <span>{label}</span>
      {status === "reconnecting" && (
        <span className="font-mono normal-case tracking-normal text-[10px] text-foreground/80">
          attempt {attempts}
          {backoff != null ? ` · ${backoff}ms` : ""}
        </span>
      )}
      {status !== "reconnecting" && attempts > 0 && (
        <span className="font-mono normal-case tracking-normal text-[10px] text-foreground/60">
          {attempts} retries
        </span>
      )}
    </span>
  );
}
