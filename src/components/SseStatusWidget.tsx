// Live SSE connectivity widget: reads the persisted benchmark-runner SSE
// diagnostics from localStorage and refreshes every second so operators can
// see current transport, last event time, reconnect attempts, and the last
// SSE error without opening the benchmark card.
//
// Also exposes manual transport-mode controls (Auto / SSE-only / Polling-only)
// that write to the same `leo.bench.transportMode` key BenchmarkRunner reads,
// and broadcasts a `leo:transport-mode-changed` event so an in-flight
// benchmark switches transport immediately.
import { useEffect, useState } from "react";

const DIAG_KEY = "leo.bench.sse-diag";
const TRANSPORT_KEY = "leo.bench.transportMode";

type TransportMode = "auto" | "sse-only" | "polling-only";

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

function loadMode(): TransportMode {
  if (typeof window === "undefined") return "auto";
  const v = window.localStorage.getItem(TRANSPORT_KEY);
  return v === "sse-only" || v === "polling-only" ? v : "auto";
}

function formatAgo(ts?: number | null): string {
  if (!ts) return "never";
  const s = Math.round((Date.now() - ts) / 1000);
  if (s < 2) return "just now";
  if (s < 60) return `${s}s ago`;
  if (s < 3600) return `${Math.round(s / 60)}m ago`;
  return `${Math.round(s / 3600)}h ago`;
}

export function SseStatusWidget() {
  const [diag, setDiag] = useState<PersistedDiag | null>(() => read());
  const [mode, setMode] = useState<TransportMode>(() => loadMode());
  const [, tick] = useState(0);

  useEffect(() => {
    const id = setInterval(() => {
      setDiag(read());
      tick((n) => n + 1);
    }, 1000);
    const onModeChange = () => setMode(loadMode());
    window.addEventListener("leo:transport-mode-changed", onModeChange);
    return () => {
      clearInterval(id);
      window.removeEventListener("leo:transport-mode-changed", onModeChange);
    };
  }, []);

  function changeMode(next: TransportMode) {
    setMode(next);
    try {
      window.localStorage.setItem(TRANSPORT_KEY, next);
    } catch {
      /* ignore quota */
    }
    window.dispatchEvent(new CustomEvent("leo:transport-mode-changed", { detail: next }));
  }

  const status = diag?.status ?? "idle";
  const transport = diag?.transport ?? "sse";

  const dot =
    status === "open"
      ? "bg-leo"
      : status === "polling"
        ? "bg-blue-400"
        : status === "reconnecting"
          ? "bg-yellow-400 animate-pulse"
          : status === "error"
            ? "bg-red-500"
            : "bg-muted-foreground/40";

  const modes: { id: TransportMode; label: string; hint: string }[] = [
    { id: "auto", label: "Auto", hint: "SSE with automatic polling fallback" },
    { id: "sse-only", label: "SSE only", hint: "Force EventSource; no fallback" },
    { id: "polling-only", label: "Polling only", hint: "Skip SSE entirely" },
  ];

  return (
    <div className="border border-border p-4">
      <div className="flex flex-wrap items-center gap-3">
        <span className={`inline-block h-2.5 w-2.5 rounded-full ${dot}`} aria-hidden />
        <span className="font-semibold" role="status" aria-live="polite">
          SSE {status}
        </span>
        <span className="text-xs text-muted-foreground">
          · transport: <span className="font-mono text-foreground">{transport}</span>
        </span>
      </div>

      <fieldset
        className="mt-4 flex flex-wrap gap-1.5"
        aria-label="Force transport mode for benchmark stream"
      >
        <legend className="sr-only">Force transport mode</legend>
        {modes.map((m) => {
          const active = mode === m.id;
          return (
            <button
              key={m.id}
              type="button"
              onClick={() => changeMode(m.id)}
              aria-pressed={active}
              title={m.hint}
              className={
                "px-2.5 py-1 text-[11px] font-semibold uppercase tracking-wide transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-white " +
                (active
                  ? "bg-leo text-leo-foreground"
                  : "border border-border text-muted-foreground hover:text-foreground")
              }
            >
              {m.label}
            </button>
          );
        })}
      </fieldset>
      <p className="mt-1 text-[10px] text-muted-foreground">
        Applies to the next (or in-flight) benchmark stream.
      </p>

      <dl className="mt-4 grid gap-x-6 gap-y-2 text-xs sm:grid-cols-[max-content_1fr]">
        <dt className="text-muted-foreground">Last event</dt>
        <dd>{formatAgo(diag?.lastEventAt)}</dd>

        <dt className="text-muted-foreground">Reconnect attempts</dt>
        <dd className="font-mono">{diag?.reconnectAttempts ?? 0}</dd>

        <dt className="text-muted-foreground">Diagnostics saved</dt>
        <dd>{formatAgo(diag?.savedAt)}</dd>
      </dl>

      {diag?.lastError && (
        <div className="mt-3 border-l-2 border-red-500 bg-red-500/5 p-3 text-xs">
          <p className="font-semibold text-red-400">Last SSE error</p>
          <p className="mt-1 font-mono text-[11px] break-words">{diag.lastError}</p>
        </div>
      )}

      {!diag && (
        <p className="mt-3 text-xs text-muted-foreground">
          No SSE session yet — start a benchmark run to open the stream.
        </p>
      )}
    </div>
  );
}
