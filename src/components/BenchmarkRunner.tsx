import { memo, useCallback, useEffect, useMemo, useRef, useState } from "react";
import { leoFetch, getApiBase } from "@/lib/leo-client";
import { toast } from "sonner";
import { saveRun, type BenchmarkRun } from "@/lib/benchmark-history";
import { useChartOptions, smoothSeries } from "@/lib/chart-options";
import { pushSseLog } from "@/lib/sse-log";

type TransportMode = "auto" | "sse-only" | "polling-only";
const TRANSPORT_KEY = "leo.bench.transportMode";
const DIAG_KEY = "leo.bench.sse-diag";

type PersistedDiag = {
  lastEventAt: number | null;
  lastError: string | null;
  reconnectAttempts: number;
  transport: "sse" | "polling";
  status: "idle" | "open" | "reconnecting" | "closed" | "error" | "polling";
  savedAt: number;
};

function loadDiag(): PersistedDiag | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = window.localStorage.getItem(DIAG_KEY);
    return raw ? (JSON.parse(raw) as PersistedDiag) : null;
  } catch {
    return null;
  }
}
function saveDiag(d: PersistedDiag) {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(DIAG_KEY, JSON.stringify(d));
  } catch {
    /* ignore quota */
  }
}
function loadTransportMode(): TransportMode {
  if (typeof window === "undefined") return "auto";
  const v = window.localStorage.getItem(TRANSPORT_KEY);
  return v === "sse-only" || v === "polling-only" ? v : "auto";
}

type Sample = { t: number; latencyMs: number; ok: boolean };
type Bucket = { tSec: number; count: number; sumMs: number; errors: number };
type LiveMetric = { t: number; rps60?: number; total?: number };

// Preset request mixes model different NVIDIA-style workloads.
type MixPreset = {
  id: string;
  label: string;
  description: string;
  // path : relative weight
  paths: { path: string; weight: number }[];
};

const MIX_PRESETS: MixPreset[] = [
  {
    id: "metrics-only",
    label: "Metrics only",
    description: "Single lightweight endpoint. Baseline latency.",
    paths: [{ path: "/api/v1/leo/metrics", weight: 1 }],
  },
  {
    id: "inference-heavy",
    label: "Inference heavy (H100-style)",
    description: "70% metrics / 30% health — approximates hot cache serving.",
    paths: [
      { path: "/api/v1/leo/metrics", weight: 7 },
      { path: "/health", weight: 3 },
    ],
  },
  {
    id: "mixed-training",
    label: "Mixed training (A100-style)",
    description: "50/50 across metrics and diagnostics — bursty pattern.",
    paths: [
      { path: "/api/v1/leo/metrics", weight: 5 },
      { path: "/api/v1/leo/diagnostics", weight: 5 },
    ],
  },
  {
    id: "edge-inference",
    label: "Edge inference (L4-style)",
    description: "Small requests dominated by /health checks.",
    paths: [
      { path: "/health", weight: 8 },
      { path: "/api/v1/leo/metrics", weight: 2 },
    ],
  },
];

function percentile(sorted: number[], p: number): number {
  if (sorted.length === 0) return 0;
  const idx = Math.min(sorted.length - 1, Math.floor((p / 100) * sorted.length));
  return sorted[idx];
}

function pickPath(mix: MixPreset["paths"]): string {
  const total = mix.reduce((s, m) => s + m.weight, 0);
  let r = Math.random() * total;
  for (const m of mix) {
    r -= m.weight;
    if (r <= 0) return m.path;
  }
  return mix[0].path;
}

export function BenchmarkRunner({
  onResult,
  onLiveRun,
}: {
  onResult?: (run: BenchmarkRun) => void;
  onLiveRun?: (rps: number | undefined) => void;
}) {
  // Load parameters — configurable to match different NVIDIA-style workloads.
  const [mode, setMode] = useState<"count" | "duration">("count");
  const [total, setTotal] = useState(200);
  const [durationSec, setDurationSec] = useState(30);
  const [concurrency, setConcurrency] = useState(8);
  const [warmupSec, setWarmupSec] = useState(2);
  const [mixId, setMixId] = useState<string>(MIX_PRESETS[0].id);
  const mix = MIX_PRESETS.find((m) => m.id === mixId) ?? MIX_PRESETS[0];

  // Persisted chart rendering options (range, smoothing, visible metrics)
  // so refreshing the page keeps the same comparison view.
  const [chartOpts, setChartOpts] = useChartOptions();

  const [running, setRunning] = useState(false);
  const [phase, setPhase] = useState<"idle" | "warmup" | "measure" | "done">("idle");
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState<BenchmarkRun | null>(null);
  const [buckets, setBuckets] = useState<Bucket[]>([]);
  const [live, setLive] = useState<LiveMetric[]>([]);
  const [streamStatus, setStreamStatus] = useState<
    "idle" | "open" | "reconnecting" | "closed" | "error" | "polling"
  >("idle");
  const [reconnectAttempts, setReconnectAttempts] = useState(0);
  const [lastEventAt, setLastEventAt] = useState<number | null>(null);
  const [lastEventDelta, setLastEventDelta] = useState<number>(0);
  const [lastError, setLastError] = useState<string | null>(null);
  const [transport, setTransport] = useState<"sse" | "polling">("sse");
  const [transportMode, setTransportMode] = useState<TransportMode>("auto");

  // Perf profiling: counters live in refs so updating them can't trigger a
  // re-render loop. We flush a snapshot into state every 500ms.
  const [perfSnapshot, setPerfSnapshot] = useState<{ renders: number; lastMs: number }>({
    renders: 0,
    lastMs: 0,
  });
  const renderCountRef = useRef(0);
  const lastCommitRef = useRef<number>(performance.now());
  const lastRenderMsRef = useRef(0);
  {
    const now = performance.now();
    lastRenderMsRef.current = now - lastCommitRef.current;
    lastCommitRef.current = now;
    renderCountRef.current += 1;
  }

  const samplesRef = useRef<Sample[]>([]);
  const abortRef = useRef<AbortController | null>(null);
  const tickRef = useRef<number | null>(null);
  const startRef = useRef<number>(0);
  const diagPersistRef = useRef<number | null>(null);

  // ── Hydrate persisted transport preference + last-known diagnostics.
  useEffect(() => {
    setTransportMode(loadTransportMode());
    const d = loadDiag();
    if (d) {
      setLastEventAt(d.lastEventAt);
      setLastError(d.lastError);
      setReconnectAttempts(d.reconnectAttempts);
      setTransport(d.transport);
      setStreamStatus(d.status === "open" ? "closed" : d.status);
    }
    const onModeChange = () => setTransportMode(loadTransportMode());
    window.addEventListener("leo:transport-mode-changed", onModeChange);
    return () => window.removeEventListener("leo:transport-mode-changed", onModeChange);
  }, []);

  // ── Flush perf snapshot every 500ms; avoids a state-update-per-render loop.
  useEffect(() => {
    const id = window.setInterval(() => {
      setPerfSnapshot({ renders: renderCountRef.current, lastMs: lastRenderMsRef.current });
    }, 500);
    return () => window.clearInterval(id);
  }, []);

  // ── "Time since last event" ticker for the diagnostics panel.
  useEffect(() => {
    if (!running || lastEventAt == null) return;
    const id = window.setInterval(() => {
      setLastEventDelta(Date.now() - lastEventAt);
    }, 500);
    return () => window.clearInterval(id);
  }, [running, lastEventAt]);

  // ── SSE live-metrics stream with automatic reconnect + polling fallback.
  //
  // Auto-switch policy: only certain error CLASSES trigger a fallback to
  // polling; transient parse errors or a single dropped connection do not.
  // While in polling fallback, we probe SSE every 20s and switch back the
  // moment it recovers.
  useEffect(() => {
    if (!running) return;
    let es: EventSource | null = null;
    let pollTimer: number | null = null;
    let recoveryTimer: number | null = null;
    let disposed = false;
    let attempts = 0;
    let retryTimer: number | null = null;
    let fatalErrorStreak = 0;
    const base = getApiBase() || "";
    const sseUrl = `${base}/api/v1/leo/metrics/stream`;
    const pollUrl = `${base}/api/v1/leo/metrics`;
    const sseCfg = (() => {
      try {
        // Inline import to avoid pulling the hook here — the effect just needs current values.
        const raw =
          typeof window !== "undefined"
            ? window.localStorage.getItem("leo.sse.reconnect_v1")
            : null;
        const parsed = raw ? JSON.parse(raw) : {};
        return {
          maxAttempts: Number.isFinite(parsed.maxAttempts) ? parsed.maxAttempts : 5,
          initialBackoffMs: Number.isFinite(parsed.initialBackoffMs)
            ? parsed.initialBackoffMs
            : 500,
          maxBackoffMs: Number.isFinite(parsed.maxBackoffMs) ? parsed.maxBackoffMs : 15000,
        };
      } catch {
        return { maxAttempts: 5, initialBackoffMs: 500, maxBackoffMs: 15000 };
      }
    })();
    const MAX_SSE_ATTEMPTS = sseCfg.maxAttempts;

    // Classify SSE errors. "fatal" ⇒ switch to polling immediately; "soft"
    // ⇒ let normal reconnect+backoff handle it.
    const classifyError = (readyState: number | undefined): "fatal" | "soft" => {
      // CLOSED (2) after handshake typically means the server rejected the
      // request (404/CORS/DNS). Two of those in a row = fatal.
      if (readyState === 2) return ++fatalErrorStreak >= 2 ? "fatal" : "soft";
      fatalErrorStreak = 0;
      return "soft";
    };

    const applyMetric = (d: Record<string, unknown>) => {
      setLastEventAt(Date.now());
      setLive((prev) =>
        [
          ...prev,
          {
            t: (performance.now() - startRef.current) / 1000,
            rps60: typeof d.leo_rps_60s === "number" ? (d.leo_rps_60s as number) : undefined,
            total:
              typeof d.leo_total_requests === "number"
                ? (d.leo_total_requests as number)
                : undefined,
          },
        ].slice(-240),
      );
    };

    const stopPolling = () => {
      if (pollTimer != null) {
        window.clearInterval(pollTimer);
        pollTimer = null;
      }
      if (recoveryTimer != null) {
        window.clearInterval(recoveryTimer);
        recoveryTimer = null;
      }
    };

    const startPolling = (reason?: string) => {
      setTransport("polling");
      setStreamStatus("polling");
      if (reason) setLastError(reason);
      const tick = async () => {
        if (disposed) return;
        try {
          const res = await fetch(pollUrl, { cache: "no-store" });
          if (!res.ok) throw new Error(`HTTP ${res.status}`);
          const d = (await res.json()) as Record<string, unknown>;
          applyMetric(d);
          setLastError(null);
        } catch (e) {
          setLastError((e as Error).message);
        }
      };
      void tick();
      pollTimer = window.setInterval(tick, 2000);

      // Recovery probe: try SSE again every 20s. If it opens cleanly, we
      // switch back automatically without user action.
      if (transportMode === "auto" && recoveryTimer == null) {
        recoveryTimer = window.setInterval(() => {
          if (disposed) return;
          try {
            const probe = new EventSource(sseUrl, { withCredentials: false });
            const probeTimeout = window.setTimeout(() => {
              try {
                probe.close();
              } catch {
                /* ignore */
              }
            }, 3000);
            probe.onopen = () => {
              window.clearTimeout(probeTimeout);
              try {
                probe.close();
              } catch {
                /* ignore */
              }
              if (disposed) return;
              toast.success("SSE recovered — switching back from polling");
              pushSseLog({
                kind: "polling-recover",
                message: "SSE recovered, resuming stream",
                transport: "sse",
              });
              stopPolling();
              attempts = 0;
              fatalErrorStreak = 0;
              setReconnectAttempts(0);
              connect();
            };
            probe.onerror = () => {
              window.clearTimeout(probeTimeout);
              try {
                probe.close();
              } catch {
                /* ignore */
              }
            };
          } catch {
            /* ignore */
          }
        }, 20000);
      }
    };

    const connect = () => {
      if (disposed) return;
      pushSseLog({ kind: "connect", message: `Opening EventSource ${sseUrl}` });
      try {
        es = new EventSource(sseUrl, { withCredentials: false });
      } catch (e) {
        setLastError((e as Error).message);
        pushSseLog({ kind: "error", message: `Constructor threw: ${(e as Error).message}` });
        scheduleRetry("soft");
        return;
      }
      es.onopen = () => {
        if (disposed) return;
        attempts = 0;
        fatalErrorStreak = 0;
        setReconnectAttempts(0);
        setTransport("sse");
        setStreamStatus("open");
        setLastError(null);
        pushSseLog({ kind: "open", message: "SSE connection established", transport: "sse" });
      };
      es.addEventListener("metrics", (ev) => {
        try {
          const d = JSON.parse((ev as MessageEvent).data) as Record<string, unknown>;
          applyMetric(d);
        } catch (e) {
          // Parse errors are soft — the stream itself is fine.
          setLastError("parse: " + (e as Error).message);
          pushSseLog({ kind: "error", message: `Parse error: ${(e as Error).message}` });
        }
      });
      es.onerror = () => {
        if (disposed) return;
        const rs = es?.readyState;
        setLastError(`SSE error (readyState=${rs ?? "?"})`);
        pushSseLog({
          kind: "error",
          message: "SSE error event",
          readyState: rs ?? null,
        });
        try {
          es?.close();
        } catch {
          /* ignore */
        }
        scheduleRetry(classifyError(rs));
      };
    };

    const scheduleRetry = (severity: "fatal" | "soft") => {
      if (disposed) return;
      attempts += 1;
      setReconnectAttempts(attempts);
      if (severity === "fatal" || attempts > MAX_SSE_ATTEMPTS) {
        if (transportMode === "sse-only") {
          setStreamStatus("error");
          setLastError("SSE unreachable and polling fallback disabled by user.");
          pushSseLog({
            kind: "error",
            message: "SSE-only mode: giving up after exhausting attempts",
            attempt: attempts,
          });
          return;
        }
        toast.warning(
          severity === "fatal"
            ? "SSE returned fatal error — switching to 2s polling"
            : "SSE unavailable — falling back to 2s polling",
        );
        pushSseLog({
          kind: "polling-start",
          message:
            severity === "fatal"
              ? "Fatal SSE error — falling back to polling"
              : `Exhausted ${MAX_SSE_ATTEMPTS} attempts — falling back to polling`,
          attempt: attempts,
          transport: "polling",
        });
        startPolling();
        return;
      }
      setStreamStatus("reconnecting");
      const delay = Math.min(
        sseCfg.maxBackoffMs,
        sseCfg.initialBackoffMs * 2 ** Math.min(attempts, 6),
      );
      pushSseLog({
        kind: "reconnect",
        message: `Reconnect scheduled (severity=${severity})`,
        attempt: attempts,
        backoffMs: delay,
      });
      retryTimer = window.setTimeout(connect, delay);
    };

    if (transportMode === "polling-only") startPolling("Forced by user (Polling-only mode).");
    else connect();

    return () => {
      disposed = true;
      if (retryTimer != null) window.clearTimeout(retryTimer);
      stopPolling();
      try {
        es?.close();
      } catch {
        /* ignore */
      }
      setStreamStatus("closed");
    };
  }, [running, transportMode]);

  // ── Persist SSE diagnostics so the panel is useful across reloads.
  useEffect(() => {
    if (diagPersistRef.current != null) window.clearTimeout(diagPersistRef.current);
    diagPersistRef.current = window.setTimeout(() => {
      saveDiag({
        lastEventAt,
        lastError,
        reconnectAttempts,
        transport,
        status: streamStatus,
        savedAt: Date.now(),
      });
    }, 250);
    return () => {
      if (diagPersistRef.current != null) window.clearTimeout(diagPersistRef.current);
    };
  }, [lastEventAt, lastError, reconnectAttempts, transport, streamStatus]);

  const changeTransportMode = useCallback((m: TransportMode) => {
    setTransportMode(m);
    try {
      window.localStorage.setItem(TRANSPORT_KEY, m);
    } catch {
      /* ignore */
    }
  }, []);

  // Aggregate samples into 1s buckets on a UI tick.
  useEffect(() => {
    if (!running) return;
    tickRef.current = window.setInterval(() => {
      const s = samplesRef.current;
      const map = new Map<number, Bucket>();
      for (const x of s) {
        const tSec = Math.floor(x.t);
        const b = map.get(tSec) ?? { tSec, count: 0, sumMs: 0, errors: 0 };
        if (x.ok) {
          b.count += 1;
          b.sumMs += x.latencyMs;
        } else b.errors += 1;
        map.set(tSec, b);
      }
      setBuckets(Array.from(map.values()).sort((a, b) => a.tSec - b.tSec));
    }, 250);
    return () => {
      if (tickRef.current != null) window.clearInterval(tickRef.current);
    };
  }, [running]);

  async function run() {
    if (running) return;
    setRunning(true);
    setResult(null);
    setProgress(0);
    setBuckets([]);
    setLive([]);
    setPhase("warmup");
    samplesRef.current = [];
    const controller = new AbortController();
    abortRef.current = controller;

    // Warm-up phase: send traffic but don't record samples.
    const warmupUntil = performance.now() + Math.max(0, warmupSec) * 1000;
    const warmupWorker = async () => {
      while (performance.now() < warmupUntil && !controller.signal.aborted) {
        try {
          const res = await leoFetch(pickPath(mix.paths), { signal: controller.signal });
          try {
            await res.text();
          } catch {
            /* ignore */
          }
        } catch {
          /* ignore */
        }
      }
    };
    if (warmupSec > 0) {
      await Promise.all(Array.from({ length: concurrency }, () => warmupWorker()));
    }
    if (controller.signal.aborted) {
      finalize(controller, 0, 0, [], performance.now());
      return;
    }

    setPhase("measure");
    const latencies: number[] = [];
    let errors = 0;
    let completed = 0;
    const started = performance.now();
    startRef.current = started;
    const stopAt = mode === "duration" ? started + durationSec * 1000 : Infinity;

    const worker = async () => {
      while (!controller.signal.aborted) {
        if (mode === "count" && completed + errors >= total) break;
        if (mode === "duration" && performance.now() >= stopAt) break;
        const t0 = performance.now();
        try {
          const res = await leoFetch(pickPath(mix.paths), { signal: controller.signal });
          const dt = performance.now() - t0;
          const ok = res.ok;
          samplesRef.current.push({ t: (t0 - started) / 1000, latencyMs: dt, ok });
          if (ok) {
            latencies.push(dt);
            completed += 1;
          } else {
            errors += 1;
          }
          try {
            await res.text();
          } catch {
            /* ignore */
          }
        } catch {
          errors += 1;
          samplesRef.current.push({
            t: (performance.now() - started) / 1000,
            latencyMs: performance.now() - t0,
            ok: false,
          });
        }
        if (mode === "count") setProgress(completed + errors);
        else
          setProgress(Math.min(100, ((performance.now() - started) / (durationSec * 1000)) * 100));
      }
    };

    try {
      await Promise.all(Array.from({ length: concurrency }, () => worker()));
    } finally {
      finalize(controller, completed, errors, latencies, started);
    }
  }

  function finalize(
    controller: AbortController,
    completed: number,
    errors: number,
    latencies: number[],
    started: number,
  ) {
    const durationMs = performance.now() - started;
    const sorted = [...latencies].sort((a, b) => a - b);
    const sum = sorted.reduce((a, b) => a + b, 0);
    const totalReq = latencies.length + errors;
    const label = mix.paths.length === 1 ? mix.paths[0].path : `mix:${mix.id}`;
    const r: BenchmarkRun = {
      id: `${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
      timestamp: new Date().toISOString(),
      apiBase: getApiBase(),
      path: label,
      totalRequests: totalReq,
      concurrency,
      durationMs,
      errors,
      errorRatePct: totalReq ? (errors / totalReq) * 100 : 0,
      throughputRps: durationMs > 0 ? (latencies.length / durationMs) * 1000 : 0,
      p50Ms: percentile(sorted, 50),
      p95Ms: percentile(sorted, 95),
      p99Ms: percentile(sorted, 99),
      minMs: sorted[0] ?? 0,
      maxMs: sorted[sorted.length - 1] ?? 0,
      meanMs: sorted.length ? sum / sorted.length : 0,
    };
    setResult(r);
    setPhase("done");
    if (totalReq > 0) {
      saveRun(r);
      onResult?.(r);
      onLiveRun?.(r.throughputRps);
      if (r.errorRatePct > 50) toast.error(`Benchmark: ${r.errors}/${totalReq} failed`);
      else toast.success(`Benchmark done · ${r.throughputRps.toFixed(1)} rps`);
    }
    setRunning(false);
    abortRef.current = null;
    // referenced to silence unused-var warnings in some builds
    void controller;
    void completed;
  }

  function stop() {
    abortRef.current?.abort();
  }

  function exportJson() {
    if (!result) return;
    const payload = {
      ...result,
      config: { mode, total, durationSec, concurrency, warmupSec, mix },
      userAgent: typeof navigator !== "undefined" ? navigator.userAgent : "",
      buckets,
      liveMetrics: live,
    };
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `leo-benchmark-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  const progressPct =
    mode === "count" ? (progress / Math.max(1, total)) * 100 : Math.min(100, progress);

  return (
    <section
      aria-labelledby="bench-runner-title"
      className="border border-border bg-background p-6"
    >
      <p className="eyebrow">Load test</p>
      <h2 id="bench-runner-title" className="mt-1 font-display text-2xl font-bold">
        Benchmark run
      </h2>
      <p className="mt-1 text-xs text-muted-foreground">
        Configurable load against{" "}
        <span className="font-mono text-leo">{getApiBase() || "(no backend)"}</span>. Live server
        counters stream over SSE from <span className="font-mono">/api/v1/leo/metrics/stream</span>.
      </p>

      <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        <label className="flex flex-col gap-1 text-xs">
          <span className="uppercase tracking-wide text-muted-foreground">Mode</span>
          <select
            value={mode}
            onChange={(e) => setMode(e.target.value as "count" | "duration")}
            disabled={running}
            className="border border-border bg-background px-2 py-1 font-mono text-xs focus:border-leo focus:outline-none"
          >
            <option value="count">Fixed requests</option>
            <option value="duration">Fixed duration</option>
          </select>
        </label>
        {mode === "count" ? (
          <label className="flex flex-col gap-1 text-xs">
            <span className="uppercase tracking-wide text-muted-foreground">Total requests</span>
            <input
              type="number"
              min={1}
              max={5000}
              value={total}
              disabled={running}
              onChange={(e) => setTotal(Math.min(5000, Math.max(1, Number(e.target.value) || 1)))}
              className="border border-border bg-background px-2 py-1 font-mono text-xs focus:border-leo focus:outline-none"
            />
          </label>
        ) : (
          <label className="flex flex-col gap-1 text-xs">
            <span className="uppercase tracking-wide text-muted-foreground">Duration (s)</span>
            <input
              type="number"
              min={1}
              max={600}
              value={durationSec}
              disabled={running}
              onChange={(e) =>
                setDurationSec(Math.min(600, Math.max(1, Number(e.target.value) || 1)))
              }
              className="border border-border bg-background px-2 py-1 font-mono text-xs focus:border-leo focus:outline-none"
            />
          </label>
        )}
        <label className="flex flex-col gap-1 text-xs">
          <span className="uppercase tracking-wide text-muted-foreground">Concurrency</span>
          <input
            type="number"
            min={1}
            max={64}
            value={concurrency}
            disabled={running}
            onChange={(e) => setConcurrency(Math.min(64, Math.max(1, Number(e.target.value) || 1)))}
            className="border border-border bg-background px-2 py-1 font-mono text-xs focus:border-leo focus:outline-none"
          />
        </label>
        <label className="flex flex-col gap-1 text-xs">
          <span className="uppercase tracking-wide text-muted-foreground">Warm-up (s)</span>
          <input
            type="number"
            min={0}
            max={60}
            value={warmupSec}
            disabled={running}
            onChange={(e) => setWarmupSec(Math.min(60, Math.max(0, Number(e.target.value) || 0)))}
            className="border border-border bg-background px-2 py-1 font-mono text-xs focus:border-leo focus:outline-none"
          />
        </label>
        <label className="flex flex-col gap-1 text-xs sm:col-span-2">
          <span className="uppercase tracking-wide text-muted-foreground">Request mix</span>
          <select
            value={mixId}
            onChange={(e) => setMixId(e.target.value)}
            disabled={running}
            className="border border-border bg-background px-2 py-1 font-mono text-xs focus:border-leo focus:outline-none"
          >
            {MIX_PRESETS.map((p) => (
              <option key={p.id} value={p.id}>
                {p.label}
              </option>
            ))}
          </select>
          <span className="text-[10px] text-muted-foreground">{mix.description}</span>
          <span className="font-mono text-[10px] text-muted-foreground">
            {mix.paths.map((p) => `${p.path} × ${p.weight}`).join("  ·  ")}
          </span>
        </label>
      </div>

      <div className="mt-4 flex flex-wrap items-center gap-3">
        <button
          type="button"
          onClick={run}
          disabled={running}
          className="border border-leo bg-leo px-4 py-2 text-xs font-semibold text-primary-foreground hover:bg-leo/90 disabled:opacity-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-leo"
        >
          {running ? (phase === "warmup" ? "Warming up…" : "Running…") : "Run benchmark"}
        </button>
        <button
          type="button"
          onClick={stop}
          disabled={!running}
          className="border border-border px-4 py-2 text-xs hover:border-leo hover:text-leo disabled:opacity-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-leo"
        >
          Stop
        </button>
        <button
          type="button"
          onClick={exportJson}
          disabled={!result}
          className="border border-border px-4 py-2 text-xs hover:border-leo hover:text-leo disabled:opacity-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-leo"
        >
          Export JSON
        </button>
        <fieldset
          className="inline-flex items-stretch border border-border text-[10px]"
          aria-label="Live-metrics transport mode"
        >
          <legend className="sr-only">Live-metrics transport mode</legend>
          {(["auto", "sse-only", "polling-only"] as TransportMode[]).map((m) => {
            const active = transportMode === m;
            const label = m === "auto" ? "Auto" : m === "sse-only" ? "SSE" : "Poll";
            const isActiveTransport =
              (m === "sse-only" && transport === "sse") ||
              (m === "polling-only" && transport === "polling") ||
              (m === "auto" && running);
            return (
              <button
                key={m}
                type="button"
                onClick={() => changeTransportMode(m)}
                className={`px-2 py-1 border-l first:border-l-0 border-border font-mono focus:outline-none focus-visible:ring-2 focus-visible:ring-leo ${
                  active ? "bg-leo/20 text-leo" : "text-muted-foreground hover:text-leo"
                }`}
                aria-pressed={active}
                title={
                  m === "auto"
                    ? "Prefer SSE, auto-fallback to 2s polling after repeated errors"
                    : m === "sse-only"
                      ? "Force EventSource; do not fall back to polling"
                      : "Skip EventSource; poll /api/v1/leo/metrics every 2s"
                }
              >
                {label}
                {active && isActiveTransport ? " •" : ""}
              </button>
            );
          })}
        </fieldset>
        {running && (
          <span className="font-mono text-xs text-muted-foreground" aria-live="polite">
            {phase === "warmup"
              ? `warmup ${warmupSec}s`
              : mode === "count"
                ? `${progress}/${total}`
                : `${progressPct.toFixed(0)}%`}
          </span>
        )}
        <span
          className={`ml-auto font-mono text-[10px] ${
            streamStatus === "open"
              ? "text-leo"
              : streamStatus === "error"
                ? "text-destructive"
                : streamStatus === "polling"
                  ? "text-yellow-600"
                  : "text-muted-foreground"
          }`}
          aria-live="polite"
        >
          {transport === "sse" ? "SSE" : "POLL"}: {streamStatus}
          {streamStatus === "reconnecting" && reconnectAttempts > 0
            ? ` · attempt ${reconnectAttempts}`
            : ""}
        </span>
      </div>

      {/* Stream + perf diagnostics — visible whenever a run is active or has produced data. */}
      {(running || live.length > 0) && (
        <div
          className="mt-4 grid gap-3 border border-border bg-muted/10 p-3 text-[11px] sm:grid-cols-2 lg:grid-cols-4"
          role="region"
          aria-label="Stream and render diagnostics"
        >
          <DiagStat
            label="Transport"
            value={transport === "sse" ? "Server-Sent Events" : "Polling (2s)"}
            tone={transport === "sse" ? "leo" : "warn"}
          />
          <DiagStat
            label="Stream state"
            value={`${streamStatus}${reconnectAttempts > 0 ? ` · ${reconnectAttempts} retries` : ""}`}
            tone={
              streamStatus === "open"
                ? "leo"
                : streamStatus === "reconnecting" || streamStatus === "polling"
                  ? "warn"
                  : streamStatus === "error"
                    ? "err"
                    : "muted"
            }
          />
          <DiagStat
            label="Last event"
            value={lastEventAt == null ? "—" : `${(lastEventDelta / 1000).toFixed(1)}s ago`}
            tone={lastEventDelta > 5000 ? "warn" : "muted"}
          />
          <DiagStat
            label="Render commits"
            value={`${perfSnapshot.renders} · Δ${perfSnapshot.lastMs.toFixed(0)}ms`}
            tone={perfSnapshot.lastMs > 100 ? "warn" : "muted"}
          />
          {lastError && (
            <div className="sm:col-span-2 lg:col-span-4 border-t border-border/60 pt-2 font-mono text-destructive">
              error: {lastError}
            </div>
          )}
        </div>
      )}

      {running && (
        <div className="mt-3 h-1 w-full bg-border">
          <div className="h-full bg-leo transition-[width]" style={{ width: `${progressPct}%` }} />
        </div>
      )}

      {(running || buckets.length > 0) && (
        <>
          <fieldset className="mt-6 inline-flex flex-wrap items-center gap-3 border border-border bg-background/60 px-3 py-2 text-[11px]">
            <legend className="px-1 text-[10px] uppercase tracking-wide text-muted-foreground">
              Chart options
            </legend>
            <label className="inline-flex items-center gap-1">
              <span className="text-muted-foreground">Range</span>
              <select
                value={chartOpts.rangeBuckets}
                onChange={(e) => setChartOpts({ rangeBuckets: Number(e.target.value) })}
                className="border border-border bg-background px-2 py-0.5 font-mono focus:border-leo focus:outline-none"
                aria-label="Chart range"
              >
                <option value={30}>last 30s</option>
                <option value={60}>last 60s</option>
                <option value={120}>last 120s</option>
                <option value={0}>all</option>
              </select>
            </label>
            <label className="inline-flex items-center gap-1">
              <span className="text-muted-foreground">Smoothing</span>
              <select
                value={chartOpts.smoothingWindow}
                onChange={(e) => setChartOpts({ smoothingWindow: Number(e.target.value) })}
                className="border border-border bg-background px-2 py-0.5 font-mono focus:border-leo focus:outline-none"
                aria-label="Smoothing window"
              >
                <option value={1}>off</option>
                <option value={3}>3-pt</option>
                <option value={5}>5-pt</option>
                <option value={7}>7-pt</option>
              </select>
            </label>
            <label className="inline-flex items-center gap-1">
              <input
                type="checkbox"
                checked={chartOpts.showLatency}
                onChange={(e) => setChartOpts({ showLatency: e.target.checked })}
              />
              <span>Latency</span>
            </label>
            <label className="inline-flex items-center gap-1">
              <input
                type="checkbox"
                checked={chartOpts.showThroughput}
                onChange={(e) => setChartOpts({ showThroughput: e.target.checked })}
              />
              <span>Throughput</span>
            </label>
            <span className="text-muted-foreground">saved automatically</span>
          </fieldset>
          <div
            className={`mt-3 grid gap-6 ${
              chartOpts.showLatency && chartOpts.showThroughput ? "lg:grid-cols-2" : ""
            }`}
          >
            {chartOpts.showLatency && (
              <LiveChart
                title="Latency (mean per 1s bucket)"
                buckets={buckets}
                kind="latency"
                rangeBuckets={chartOpts.rangeBuckets}
                smoothingWindow={chartOpts.smoothingWindow}
              />
            )}
            {chartOpts.showThroughput && (
              <LiveChart
                title="Throughput (req/s per 1s bucket)"
                buckets={buckets}
                kind="throughput"
                rangeBuckets={chartOpts.rangeBuckets}
                smoothingWindow={chartOpts.smoothingWindow}
              />
            )}
          </div>
        </>
      )}

      {live.length > 0 && (
        <div className="mt-6 border border-border bg-muted/10 p-4">
          <p className="eyebrow">Live server counters (SSE)</p>
          <div className="mt-2 grid gap-3 text-xs sm:grid-cols-3">
            <LiveStat
              label="Server rps (60s)"
              value={live[live.length - 1]?.rps60?.toFixed(2) ?? "—"}
            />
            <LiveStat
              label="Server total"
              value={live[live.length - 1]?.total?.toLocaleString() ?? "—"}
            />
            <LiveStat label="Samples" value={String(live.length)} />
          </div>
        </div>
      )}

      {result && (
        <div className="mt-6 grid gap-px bg-border sm:grid-cols-2 lg:grid-cols-4">
          <Stat label="Throughput" value={`${result.throughputRps.toFixed(1)} rps`} highlight />
          <Stat label="Error rate" value={`${result.errorRatePct.toFixed(2)}%`} />
          <Stat label="Requests" value={`${result.totalRequests}`} />
          <Stat label="Duration" value={`${(result.durationMs / 1000).toFixed(2)}s`} />
          <Stat label="p50" value={`${result.p50Ms.toFixed(1)} ms`} />
          <Stat label="p95" value={`${result.p95Ms.toFixed(1)} ms`} highlight />
          <Stat label="p99" value={`${result.p99Ms.toFixed(1)} ms`} highlight />
          <Stat
            label="min / max"
            value={`${result.minMs.toFixed(0)} / ${result.maxMs.toFixed(0)} ms`}
          />
        </div>
      )}
    </section>
  );
}

function Stat({ label, value, highlight }: { label: string; value: string; highlight?: boolean }) {
  return (
    <div className="bg-background p-4">
      <div className="text-[11px] uppercase tracking-wide text-muted-foreground">{label}</div>
      <div
        className={`mt-1 font-display text-xl font-bold ${highlight ? "text-leo" : "text-foreground"}`}
      >
        {value}
      </div>
    </div>
  );
}

function LiveStat({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <div className="text-[11px] uppercase tracking-wide text-muted-foreground">{label}</div>
      <div className="mt-1 font-mono text-lg text-leo">{value}</div>
    </div>
  );
}

// Memoized chart. Compares by kind, title, and a lightweight bucket signature
// so noisy re-renders from parent state (perf snapshot, live counters) do NOT
// force an SVG rebuild when the underlying data is unchanged. Bucket data is
// mutated in place elsewhere via a new array reference each tick, so we hash
// length + last-bucket totals for the shallow-equality cutoff.
const LiveChart = memo(
  function LiveChart({
    title,
    buckets,
    kind,
    rangeBuckets = 120,
    smoothingWindow = 1,
  }: {
    title: string;
    buckets: Bucket[];
    kind: "latency" | "throughput";
    rangeBuckets?: number;
    smoothingWindow?: number;
  }) {
    const w = 480;
    const h = 140;
    const pad = 24;

    // Virtualize: honour the persisted range (30/60/120/all).
    const visible = useMemo(() => {
      if (rangeBuckets <= 0) return buckets;
      return buckets.length > rangeBuckets ? buckets.slice(-rangeBuckets) : buckets;
    }, [buckets, rangeBuckets]);

    const { values, points, max, stepX } = useMemo(() => {
      const raw = visible.map((b) =>
        kind === "latency" ? (b.count > 0 ? b.sumMs / b.count : 0) : b.count,
      );
      const vals = smoothSeries(raw, smoothingWindow);
      const mx = Math.max(1, ...vals);
      const step = visible.length > 1 ? (w - pad * 2) / (visible.length - 1) : 0;
      const pts = vals
        .map((v, i) => {
          const x = pad + i * step;
          const y = h - pad - (v / mx) * (h - pad * 2);
          return `${x.toFixed(1)},${y.toFixed(1)}`;
        })
        .join(" ");
      return { values: vals, points: pts, max: mx, stepX: step };
    }, [visible, kind, smoothingWindow]);

    const unit = kind === "latency" ? "ms" : "rps";

    return (
      <figure className="border border-border bg-background p-4" aria-label={title}>
        <figcaption className="mb-2 flex items-baseline justify-between">
          <span className="text-[11px] uppercase tracking-wide text-muted-foreground">{title}</span>
          <span className="font-mono text-xs text-leo">
            peak {max.toFixed(kind === "latency" ? 1 : 0)} {unit}
            {smoothingWindow > 1 ? ` · smooth ${smoothingWindow}` : ""}
          </span>
        </figcaption>
        <svg
          viewBox={`0 0 ${w} ${h}`}
          preserveAspectRatio="none"
          className="h-32 w-full"
          role="img"
        >
          <line
            x1={pad}
            y1={h - pad}
            x2={w - pad}
            y2={h - pad}
            stroke="currentColor"
            opacity="0.2"
          />
          <line x1={pad} y1={pad} x2={pad} y2={h - pad} stroke="currentColor" opacity="0.2" />
          {points && (
            <polyline
              points={points}
              fill="none"
              stroke="#76B900"
              strokeWidth="1.5"
              strokeLinejoin="round"
            />
          )}
          {values.map((v, i) => {
            const x = pad + i * stepX;
            const y = h - pad - (v / max) * (h - pad * 2);
            return <circle key={i} cx={x} cy={y} r="1.5" fill="#76B900" />;
          })}
        </svg>
        <div className="mt-1 flex justify-between text-[10px] text-muted-foreground">
          <span>0s</span>
          <span>{visible.length > 0 ? `${visible[visible.length - 1].tSec}s` : "—"}</span>
        </div>
      </figure>
    );
  },
  (prev, next) => {
    if (
      prev.kind !== next.kind ||
      prev.title !== next.title ||
      prev.rangeBuckets !== next.rangeBuckets ||
      prev.smoothingWindow !== next.smoothingWindow
    )
      return false;
    const a = prev.buckets;
    const b = next.buckets;
    if (a.length !== b.length) return false;
    if (a.length === 0) return true;
    const la = a[a.length - 1];
    const lb = b[b.length - 1];
    return (
      la.tSec === lb.tSec &&
      la.count === lb.count &&
      la.sumMs === lb.sumMs &&
      la.errors === lb.errors
    );
  },
);

function DiagStat({
  label,
  value,
  tone = "muted",
}: {
  label: string;
  value: string;
  tone?: "leo" | "warn" | "err" | "muted";
}) {
  const cls =
    tone === "leo"
      ? "text-leo"
      : tone === "warn"
        ? "text-yellow-600"
        : tone === "err"
          ? "text-destructive"
          : "text-foreground";
  return (
    <div>
      <div className="text-[10px] uppercase tracking-wide text-muted-foreground">{label}</div>
      <div className={`mt-0.5 font-mono ${cls}`}>{value}</div>
    </div>
  );
}
