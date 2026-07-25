// Fire a burst of health checks back-to-back to reproduce issues on demand.
// Count, interval, and endpoint path are user-configurable via inline
// controls; settings persist across reloads. Each result feeds
// pushHealthEntry so the chart, alert, and timeline update live.
import { useRef, useState } from "react";
import { toast } from "sonner";
import { pushHealthEntry } from "@/lib/health-history";
import {
  useBurstConfig,
  DEFAULT_BURST_CONFIG,
  recordLastRunBurstConfig,
  useLastRunBurstConfig,
  type BurstConfig,
} from "@/lib/burst-config";
import { getApiBase } from "@/lib/leo-client";
import type { HealthResult } from "@/lib/backend-health";

const TIMEOUT_MS = 5000;

async function probe(path: string): Promise<HealthResult> {
  const base = getApiBase().replace(/\/+$/, "");
  const url = `${base}${path.startsWith("/") ? path : "/" + path}`;
  const started = performance.now();
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);
  try {
    const res = await fetch(url, { method: "GET", signal: controller.signal });
    const latencyMs = Math.round(performance.now() - started);
    const text = await res.text().catch(() => "");
    const bodyExcerpt = text.length > 240 ? text.slice(0, 240) + "…" : text;
    return {
      status: res.ok ? "online" : "error",
      url,
      latencyMs,
      httpStatus: res.status,
      checkedAt: Date.now(),
      bodyExcerpt,
      message: res.ok ? undefined : `HTTP ${res.status}`,
      failureKind: res.ok ? undefined : "http",
    };
  } catch (err) {
    const latencyMs = Math.round(performance.now() - started);
    const isAbort = err instanceof DOMException && err.name === "AbortError";
    return {
      status: "unreachable",
      url,
      latencyMs,
      checkedAt: Date.now(),
      failureKind: isAbort ? "timeout" : "network",
      errorName: err instanceof Error ? err.name : "Error",
      message: err instanceof Error ? err.message : String(err),
    };
  } finally {
    clearTimeout(timer);
  }
}

export function BurstHealthCheckButton() {
  const [cfg, setCfg] = useBurstConfig();
  const lastRun = useLastRunBurstConfig();
  const [open, setOpen] = useState(false);
  const [running, setRunning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [progressTotal, setProgressTotal] = useState(0);
  const cancelRef = useRef(false);

  async function runWith(runCfg: BurstConfig) {
    if (running) {
      cancelRef.current = true;
      return;
    }
    setRunning(true);
    cancelRef.current = false;
    setProgress(0);
    setProgressTotal(runCfg.count);
    recordLastRunBurstConfig(runCfg);
    let fails = 0;
    for (let i = 0; i < runCfg.count; i++) {
      if (cancelRef.current) break;
      const r = await probe(runCfg.path);
      pushHealthEntry(r);
      if (r.status !== "online") fails++;
      setProgress(i + 1);
      if (i < runCfg.count - 1 && runCfg.intervalMs > 0) {
        await new Promise((res) => setTimeout(res, runCfg.intervalMs));
      }
    }
    setRunning(false);
    if (cancelRef.current) toast.message("Burst cancelled");
    else if (fails === 0)
      toast.success(`Ran ${runCfg.count} checks on ${runCfg.path} — all online`);
    else toast.error(`Ran ${runCfg.count} checks on ${runCfg.path} — ${fails} failed`);
  }

  const run = () => runWith(cfg);
  const runAgain = () => lastRun && runWith(lastRun);

  const runAgainTitle = lastRun
    ? `Replay last run: ${lastRun.count}× ${lastRun.path} @ ${lastRun.intervalMs}ms`
    : "No previous burst run yet";

  return (
    <div className="inline-flex flex-wrap items-center gap-2">
      <button
        type="button"
        onClick={run}
        aria-live="polite"
        className="border border-leo bg-leo/10 px-3 py-1.5 text-xs font-semibold text-leo hover:bg-leo/20 focus:outline-none focus-visible:ring-2 focus-visible:ring-leo"
      >
        {running ? `Running ${progress}/${progressTotal}…` : "Run health checks now"}
      </button>
      <button
        type="button"
        onClick={runAgain}
        disabled={!lastRun || running}
        aria-label="Run again with last used burst config"
        title={runAgainTitle}
        className="border border-border px-3 py-1.5 text-xs font-semibold hover:border-leo hover:text-leo focus:outline-none focus-visible:ring-2 focus-visible:ring-leo disabled:opacity-40 disabled:cursor-not-allowed"
      >
        ↻ Run again
        {lastRun && (
          <span className="ml-1 font-mono text-[10px] text-muted-foreground">
            {lastRun.count}× {lastRun.path}
          </span>
        )}
      </button>
      <button
        type="button"
        onClick={() => setOpen((s) => !s)}
        aria-expanded={open}
        title="Configure burst count, interval, and path"
        className="border border-border px-2 py-1.5 text-xs font-semibold hover:border-leo hover:text-leo focus:outline-none focus-visible:ring-2 focus-visible:ring-leo"
      >
        ⚙ Burst
      </button>

      {open && (
        <fieldset className="mt-2 flex w-full flex-wrap items-end gap-3 border border-border bg-background/60 px-3 py-2 text-xs">
          <legend className="px-1 text-[11px] uppercase tracking-wide text-muted-foreground">
            Burst config
          </legend>
          <label className="flex flex-col gap-1">
            <span className="text-muted-foreground">Count (1–100)</span>
            <input
              type="number"
              min={1}
              max={100}
              value={cfg.count}
              onChange={(e) => setCfg({ count: Number(e.target.value) })}
              className="w-20 border border-border bg-background px-2 py-1 font-mono text-xs focus:border-leo focus:outline-none"
            />
          </label>
          <label className="flex flex-col gap-1">
            <span className="text-muted-foreground">Interval (ms)</span>
            <input
              type="number"
              min={0}
              max={60000}
              step={50}
              value={cfg.intervalMs}
              onChange={(e) => setCfg({ intervalMs: Number(e.target.value) })}
              className="w-24 border border-border bg-background px-2 py-1 font-mono text-xs focus:border-leo focus:outline-none"
            />
          </label>
          <label className="flex flex-col gap-1">
            <span className="text-muted-foreground">Path</span>
            <input
              type="text"
              value={cfg.path}
              onChange={(e) => setCfg({ path: e.target.value })}
              placeholder="/health"
              spellCheck={false}
              list="burst-path-presets"
              className="w-56 border border-border bg-background px-2 py-1 font-mono text-xs focus:border-leo focus:outline-none"
            />
            <datalist id="burst-path-presets">
              <option value="/health" />
              <option value="/api/v1/leo/metrics" />
              <option value="/api/v1/leo/diagnostics" />
            </datalist>
          </label>
          <button
            type="button"
            onClick={() => setCfg(DEFAULT_BURST_CONFIG)}
            className="border border-border px-2 py-1 text-xs hover:border-leo hover:text-leo"
          >
            Reset
          </button>
        </fieldset>
      )}
    </div>
  );
}
