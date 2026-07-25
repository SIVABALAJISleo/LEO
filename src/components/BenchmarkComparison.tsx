import { useEffect, useMemo, useRef, useState } from "react";
import { useBenchmarkHistory, type BenchmarkRun } from "@/lib/benchmark-history";
import { useRegressionThresholds, evaluateRegressions } from "@/lib/regression-thresholds";
import { buildShareUrl, encodeComparisonShare } from "@/lib/share-link";
import { toPng } from "html-to-image";
import { toast } from "sonner";

type Metric = {
  key: keyof BenchmarkRun;
  label: string;
  unit: string;
  higherIsWorse: boolean;
  fmt: (v: number) => string;
};

const METRICS: Metric[] = [
  {
    key: "throughputRps",
    label: "Throughput",
    unit: "rps",
    higherIsWorse: false,
    fmt: (v) => v.toFixed(1),
  },
  { key: "p50Ms", label: "p50", unit: "ms", higherIsWorse: true, fmt: (v) => v.toFixed(1) },
  { key: "p95Ms", label: "p95", unit: "ms", higherIsWorse: true, fmt: (v) => v.toFixed(1) },
  { key: "p99Ms", label: "p99", unit: "ms", higherIsWorse: true, fmt: (v) => v.toFixed(1) },
  { key: "meanMs", label: "mean", unit: "ms", higherIsWorse: true, fmt: (v) => v.toFixed(1) },
  {
    key: "errorRatePct",
    label: "Error rate",
    unit: "%",
    higherIsWorse: true,
    fmt: (v) => v.toFixed(2),
  },
];

function pctDelta(a: number, b: number): number {
  if (a === 0) return b === 0 ? 0 : 100;
  return ((b - a) / Math.abs(a)) * 100;
}

export function BenchmarkComparison({
  presetBase,
  presetTarget,
}: {
  presetBase?: BenchmarkRun | null;
  presetTarget?: BenchmarkRun | null;
} = {}) {
  const runs = useBenchmarkHistory();
  const [baseId, setBaseId] = useState<string>("");
  const [targetId, setTargetId] = useState<string>("");
  const [thresholds] = useRegressionThresholds();
  const cardRef = useRef<HTMLDivElement>(null);

  const options = useMemo(() => {
    const map = new Map<string, BenchmarkRun>();
    for (const r of runs) map.set(r.id, r);
    if (presetBase) map.set(presetBase.id, presetBase);
    if (presetTarget) map.set(presetTarget.id, presetTarget);
    return [...map.values()].sort(
      (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime(),
    );
  }, [runs, presetBase, presetTarget]);

  const base = options.find((r) => r.id === baseId) ?? presetBase ?? options[1] ?? null;
  const target = options.find((r) => r.id === targetId) ?? presetTarget ?? options[0] ?? null;

  const rows = useMemo(() => {
    if (!base || !target) return [];
    return METRICS.map((m) => {
      const a = Number(base[m.key] ?? 0);
      const b = Number(target[m.key] ?? 0);
      const delta = pctDelta(a, b);
      const improved = m.higherIsWorse ? delta < 0 : delta > 0;
      const changed = Math.abs(delta) > 0.5;
      return { m, a, b, delta, improved, changed };
    });
  }, [base, target]);

  const findings = useMemo(
    () => evaluateRegressions(base, target, thresholds),
    [base, target, thresholds],
  );

  // Alert once per unique base+target combination.
  const lastKeyRef = useRef<string>("");
  useEffect(() => {
    if (!base || !target || findings.length === 0) return;
    const key = `${base.id}::${target.id}`;
    if (lastKeyRef.current === key) return;
    lastKeyRef.current = key;
    const critical = findings.filter((f) => f.severity === "critical").length;
    const msg = `Regression detected: ${findings.length} metric${findings.length > 1 ? "s" : ""} breached thresholds${
      critical > 0 ? ` (${critical} critical)` : ""
    }`;
    if (critical > 0) toast.error(msg);
    else toast.warning(msg);
  }, [findings, base, target]);

  async function copyShareLink() {
    if (!base || !target) return;
    const url = buildShareUrl("compare", encodeComparisonShare(base, target));
    try {
      await navigator.clipboard.writeText(url);
      toast.success("Share link copied");
    } catch {
      toast.error("Copy failed — link: " + url.slice(0, 60) + "…");
    }
  }

  const [exporting, setExporting] = useState<"png" | "pdf" | null>(null);
  const [exportProgress, setExportProgress] = useState<{
    kind: "png" | "pdf";
    startedAt: number;
    elapsedMs: number;
    step: string;
  } | null>(null);
  const [lastExportError, setLastExportError] = useState<{
    kind: "png" | "pdf";
    reason: string;
    at: number;
  } | null>(null);
  const [retryAttempts, setRetryAttempts] = useState<{ png: number; pdf: number }>({
    png: 0,
    pdf: 0,
  });
  const cancelRef = useRef<{ cancelled: boolean } | null>(null);

  // Live tick for the "elapsed" counter while exporting.
  useEffect(() => {
    if (!exportProgress) return;
    const id = window.setInterval(() => {
      setExportProgress((p) => (p ? { ...p, elapsedMs: Date.now() - p.startedAt } : p));
    }, 200);
    return () => window.clearInterval(id);
  }, [exportProgress?.startedAt, exportProgress]);

  function cancelExport() {
    if (cancelRef.current) cancelRef.current.cancelled = true;
    setExportProgress(null);
    setExporting(null);
    toast.message("Export cancelled");
  }

  function assertReady(kind: "png" | "pdf"): string | null {
    if (!base || !target) return "Select both a baseline and target run before exporting.";
    if (options.length < 2) return "Save at least two benchmark runs to export a comparison.";
    if (!cardRef.current) return "Comparison card isn't mounted yet — try again in a moment.";
    const rect = cardRef.current.getBoundingClientRect();
    if (rect.width < 40 || rect.height < 40) {
      return "Comparison card isn't fully rendered yet. Scroll it into view and retry.";
    }
    if (rows.length === 0) return "No metric rows available to render.";
    void kind;
    return null;
  }

  async function exportPng() {
    const err = assertReady("png");
    if (err) {
      setLastExportError({ kind: "png", reason: err, at: Date.now() });
      toast.error(err);
      return;
    }
    setExporting("png");
    const token = { cancelled: false };
    cancelRef.current = token;
    setExportProgress({
      kind: "png",
      startedAt: Date.now(),
      elapsedMs: 0,
      step: "waiting for layout",
    });
    const tid = toast.loading("Rendering PNG…");
    try {
      await new Promise((r) => requestAnimationFrame(() => r(null)));
      if (token.cancelled) throw new Error("cancelled");
      setExportProgress((p) => (p ? { ...p, step: "rasterizing" } : p));
      const dataUrl = await toPng(cardRef.current!, {
        pixelRatio: 2,
        backgroundColor: getComputedStyle(document.body).backgroundColor || "#0a0a0a",
        cacheBust: true,
      });
      if (token.cancelled) throw new Error("cancelled");
      setExportProgress((p) => (p ? { ...p, step: "downloading" } : p));
      const a = document.createElement("a");
      a.href = dataUrl;
      a.download = `leo-comparison-${Date.now()}.png`;
      a.click();
      setLastExportError(null);
      setRetryAttempts((r) => ({ ...r, png: 0 }));
      toast.success("Comparison exported as PNG", { id: tid });
    } catch (e) {
      const reason = (e as Error).message || "unknown error";
      if (reason !== "cancelled") {
        setLastExportError({ kind: "png", reason, at: Date.now() });
        setRetryAttempts((r) => ({ ...r, png: r.png + 1 }));
        toast.error("PNG export failed: " + reason, { id: tid });
      } else {
        toast.dismiss(tid);
      }
    } finally {
      cancelRef.current = null;
      setExporting(null);
      setExportProgress(null);
    }
  }

  function printPdf() {
    const err = assertReady("pdf");
    if (err) {
      setLastExportError({ kind: "pdf", reason: err, at: Date.now() });
      toast.error(err);
      return;
    }
    setExporting("pdf");
    setExportProgress({
      kind: "pdf",
      startedAt: Date.now(),
      elapsedMs: 0,
      step: "opening print dialog",
    });
    const token = { cancelled: false };
    cancelRef.current = token;
    const style = document.createElement("style");
    style.setAttribute("data-bench-print", "1");
    style.textContent = `
      @media print {
        body * { visibility: hidden !important; }
        [data-bench-compare-card], [data-bench-compare-card] * { visibility: visible !important; }
        [data-bench-compare-card] { position: absolute !important; left: 0; top: 0; width: 100%; padding: 24px; }
        [data-print-hide] { display: none !important; }
      }
    `;
    document.head.appendChild(style);
    const cleanup = () => {
      style.remove();
      cancelRef.current = null;
      setExporting(null);
      setExportProgress(null);
      window.removeEventListener("afterprint", cleanup);
    };
    window.addEventListener("afterprint", cleanup);
    try {
      window.print();
      if (token.cancelled) throw new Error("cancelled");
      setLastExportError(null);
      setRetryAttempts((r) => ({ ...r, pdf: 0 }));
    } catch (e) {
      const reason = (e as Error).message || "unknown error";
      if (reason !== "cancelled") {
        setLastExportError({ kind: "pdf", reason, at: Date.now() });
        setRetryAttempts((r) => ({ ...r, pdf: r.pdf + 1 }));
        toast.error("Print failed: " + reason);
      }
      cleanup();
    }
  }

  // Exponential backoff for retries. After 2+ PDF failures, fall back to
  // the lighter PNG (image-only) export automatically.
  function retryLastExport() {
    if (!lastExportError) return;
    const kind = lastExportError.kind;
    const attempts = retryAttempts[kind];
    const delay = Math.min(8000, 500 * 2 ** Math.min(attempts, 4));
    const fallback = kind === "pdf" && attempts >= 2;
    if (fallback) {
      toast.message(
        `PDF failed ${attempts}× — falling back to PNG in ${Math.round(delay / 100) / 10}s`,
      );
    } else {
      toast.message(
        `Retrying ${kind.toUpperCase()} in ${Math.round(delay / 100) / 10}s (attempt ${attempts + 1})`,
      );
    }
    window.setTimeout(() => {
      if (fallback) void exportPng();
      else if (kind === "png") void exportPng();
      else printPdf();
    }, delay);
  }

  return (
    <section
      aria-labelledby="bench-compare-title"
      className="border border-border bg-background p-6"
      data-bench-compare-card
      ref={cardRef}
    >
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="eyebrow">Compare</p>
          <h2 id="bench-compare-title" className="mt-1 font-display text-2xl font-bold">
            Run-to-run comparison
          </h2>
          <p className="mt-1 text-xs text-muted-foreground">
            Green = improvement, red = regression. Deltas are percentage change from baseline to
            target.
          </p>
        </div>
        <div className="flex flex-wrap gap-2" data-print-hide>
          <button
            type="button"
            onClick={copyShareLink}
            disabled={!base || !target}
            className="border border-border px-3 py-1.5 text-xs hover:border-leo hover:text-leo disabled:opacity-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-leo"
          >
            Copy share link
          </button>
          <button
            type="button"
            onClick={exportPng}
            disabled={!base || !target || exporting !== null}
            className="border border-border px-3 py-1.5 text-xs hover:border-leo hover:text-leo disabled:opacity-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-leo"
          >
            {exporting === "png" ? "Rendering…" : "Export PNG"}
          </button>
          <button
            type="button"
            onClick={printPdf}
            disabled={!base || !target || exporting !== null}
            className="border border-border px-3 py-1.5 text-xs hover:border-leo hover:text-leo disabled:opacity-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-leo"
          >
            {exporting === "pdf" ? "Preparing…" : "Print / Save PDF"}
          </button>
        </div>
      </div>

      {exportProgress && (
        <div
          role="status"
          aria-live="polite"
          data-print-hide
          className="mt-4 border border-leo/40 bg-leo/5 p-3 text-xs"
        >
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="min-w-0 flex-1">
              <div className="flex items-baseline gap-2">
                <span className="font-semibold text-leo">
                  Exporting {exportProgress.kind.toUpperCase()}
                </span>
                <span className="font-mono text-muted-foreground">
                  {exportProgress.step} · {(exportProgress.elapsedMs / 1000).toFixed(1)}s
                </span>
              </div>
              <div className="mt-2 h-1 w-full overflow-hidden bg-border">
                <div className="h-full w-1/3 animate-pulse bg-leo" />
              </div>
              {exportProgress.elapsedMs > 8000 && (
                <p className="mt-1 text-[10px] text-yellow-600">
                  Taking longer than expected — the browser may be blocked. Cancel and retry if it
                  looks stuck.
                </p>
              )}
            </div>
            <button
              type="button"
              onClick={cancelExport}
              className="border border-destructive/60 px-3 py-1.5 text-destructive hover:bg-destructive/10 focus:outline-none focus-visible:ring-2 focus-visible:ring-destructive"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {lastExportError && (
        <div
          role="alert"
          aria-live="assertive"
          data-print-hide
          className="mt-4 border border-destructive/60 bg-destructive/10 p-3 text-xs text-destructive"
        >
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div className="min-w-0">
              <p className="font-semibold">
                {lastExportError.kind === "png" ? "PNG export failed" : "PDF export failed"}
              </p>
              <p className="mt-1 font-mono break-words text-[11px] opacity-80">
                {lastExportError.reason}
              </p>
              <p className="mt-1 text-[10px] opacity-70">
                Common fixes: scroll the card into view, wait for charts to finish rendering, or
                reduce the browser zoom then retry.
                {lastExportError.kind === "pdf" && retryAttempts.pdf >= 2 && (
                  <>
                    {" "}
                    After 2 PDF failures the next retry falls back to <b>PNG (image-only)</b>.
                  </>
                )}
                {retryAttempts[lastExportError.kind] > 0 && (
                  <> · attempt {retryAttempts[lastExportError.kind]}</>
                )}
              </p>
            </div>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={retryLastExport}
                disabled={exporting !== null}
                className="border border-destructive/70 px-3 py-1.5 hover:bg-destructive/20 disabled:opacity-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-destructive"
              >
                {exporting ? "Retrying…" : `Retry ${lastExportError.kind.toUpperCase()}`}
              </button>
              <button
                type="button"
                onClick={() => setLastExportError(null)}
                className="border border-border px-3 py-1.5 text-muted-foreground hover:text-foreground focus:outline-none focus-visible:ring-2 focus-visible:ring-leo"
                aria-label="Dismiss export error"
              >
                Dismiss
              </button>
            </div>
          </div>
        </div>
      )}

      {options.length < 2 ? (
        <p className="mt-6 text-xs text-muted-foreground">
          Save at least two benchmark runs to compare.
        </p>
      ) : (
        <>
          {findings.length > 0 && (
            <div
              role="alert"
              aria-live="polite"
              className={`mt-4 border p-3 text-xs ${
                findings.some((f) => f.severity === "critical")
                  ? "border-destructive bg-destructive/10 text-destructive"
                  : "border-yellow-500/60 bg-yellow-500/10 text-yellow-600"
              }`}
            >
              <div className="font-semibold uppercase tracking-wide">
                ⚠ Regression threshold breached
              </div>
              <ul className="mt-2 space-y-0.5">
                {findings.map((f) => (
                  <li key={f.metric} className="font-mono">
                    {f.label}: {f.base.toFixed(1)} → {f.target.toFixed(1)} ({f.delta > 0 ? "+" : ""}
                    {f.delta.toFixed(1)}%) breaches {Math.abs(f.breach)}
                    {f.metric === "errorRate" ? "%" : "%"} threshold ({f.severity})
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div className="mt-4 grid gap-3 sm:grid-cols-2" data-print-hide>
            <RunPicker
              label="Baseline"
              value={base?.id ?? ""}
              onChange={setBaseId}
              options={options}
            />
            <RunPicker
              label="Target"
              value={target?.id ?? ""}
              onChange={setTargetId}
              options={options}
            />
          </div>

          <div className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {rows.map(({ m, a, b, delta, improved, changed }) => {
              const color = !changed
                ? "text-muted-foreground"
                : improved
                  ? "text-leo"
                  : "text-destructive";
              const arrow = !changed ? "→" : delta > 0 ? "▲" : "▼";
              const maxAbs = Math.max(Math.abs(a), Math.abs(b), 1);
              const aPct = (Math.abs(a) / maxAbs) * 100;
              const bPct = (Math.abs(b) / maxAbs) * 100;
              return (
                <div key={m.key} className="border border-border bg-muted/10 p-3">
                  <div className="flex items-baseline justify-between">
                    <span className="text-[11px] uppercase tracking-wide text-muted-foreground">
                      {m.label}
                    </span>
                    <span className={`font-mono text-xs ${color}`}>
                      {arrow} {delta > 0 ? "+" : ""}
                      {delta.toFixed(1)}%
                    </span>
                  </div>
                  <div className="mt-2 space-y-1.5">
                    <BarRow label="base" value={m.fmt(a)} unit={m.unit} pct={aPct} muted />
                    <BarRow
                      label="target"
                      value={m.fmt(b)}
                      unit={m.unit}
                      pct={bPct}
                      color={color}
                    />
                  </div>
                </div>
              );
            })}
          </div>

          <div className="mt-6 text-[11px] text-muted-foreground">
            Baseline: <span className="font-mono">{base?.path}</span> ·{" "}
            {base && new Date(base.timestamp).toLocaleString()} → Target:{" "}
            <span className="font-mono">{target?.path}</span> ·{" "}
            {target && new Date(target.timestamp).toLocaleString()}
          </div>
        </>
      )}
    </section>
  );
}

function RunPicker({
  label,
  value,
  onChange,
  options,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  options: BenchmarkRun[];
}) {
  return (
    <label className="flex flex-col gap-1 text-xs">
      <span className="uppercase tracking-wide text-muted-foreground">{label}</span>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="border border-border bg-background px-2 py-1 font-mono text-xs focus:border-leo focus:outline-none"
      >
        {options.map((r) => (
          <option key={r.id} value={r.id}>
            {new Date(r.timestamp).toLocaleString()} · {r.path} · {r.throughputRps.toFixed(1)} rps
          </option>
        ))}
      </select>
    </label>
  );
}

function BarRow({
  label,
  value,
  unit,
  pct,
  muted,
  color,
}: {
  label: string;
  value: string;
  unit: string;
  pct: number;
  muted?: boolean;
  color?: string;
}) {
  return (
    <div>
      <div className="flex items-baseline justify-between text-[10px]">
        <span className="uppercase tracking-wide text-muted-foreground">{label}</span>
        <span
          className={`font-mono ${color ?? (muted ? "text-muted-foreground" : "text-foreground")}`}
        >
          {value} {unit}
        </span>
      </div>
      <div className="mt-0.5 h-1 w-full bg-border">
        <div
          className={`h-full ${muted ? "bg-muted-foreground/40" : "bg-leo"}`}
          style={{ width: `${Math.min(100, pct)}%` }}
        />
      </div>
    </div>
  );
}
