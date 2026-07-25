// Import a previously exported debug report or health history JSON and
// restore the full debugging state — thresholds, health history, last
// CORS preflight result, and SSE reconnect settings — in one click.
import { useRef, useState } from "react";
import { toast } from "sonner";
import {
  importHealthEntries,
  setThresholds,
  DEFAULT_THRESHOLDS,
  type ImportReport,
  type HealthThresholds,
} from "@/lib/health-history";
import { setSseConfig, DEFAULT_SSE_CONFIG } from "@/lib/sse-config";

const CORS_RESULT_KEY = "leo.cors.last_result";
const SSE_DIAG_KEY = "leo.bench.sse-diag";

interface RestoreSummary {
  history: ImportReport | null;
  thresholds: boolean;
  sseConfig: boolean;
  corsResult: boolean;
  sseDiag: boolean;
  notes: string[];
}

function applyThresholds(input: unknown): boolean {
  if (!input || typeof input !== "object") return false;
  const t = input as Partial<HealthThresholds>;
  // Only apply if it looks like a thresholds object.
  const keys: (keyof HealthThresholds)[] = [
    "latencyWarnMs",
    "timeoutMs",
    "failureRatePct",
    "windowSize",
    "consecutiveFailLimit",
    "avgLatencyWarnMs",
  ];
  const has = keys.some((k) => typeof t[k] === "number");
  if (!has) return false;
  setThresholds({ ...DEFAULT_THRESHOLDS, ...t });
  return true;
}

function applySseConfig(input: unknown): boolean {
  if (!input || typeof input !== "object") return false;
  const c = input as Record<string, unknown>;
  const has =
    typeof c.maxAttempts === "number" ||
    typeof c.initialBackoffMs === "number" ||
    typeof c.maxBackoffMs === "number";
  if (!has) return false;
  setSseConfig({ ...DEFAULT_SSE_CONFIG, ...(c as object) });
  return true;
}

export function ImportDebugReportButton() {
  const [open, setOpen] = useState(false);
  const [text, setText] = useState("");
  const [mode, setMode] = useState<"merge" | "replace">("merge");
  const [summary, setSummary] = useState<RestoreSummary | null>(null);
  const fileRef = useRef<HTMLInputElement | null>(null);

  function apply(raw: string) {
    let parsed: unknown;
    try {
      parsed = JSON.parse(raw);
    } catch (e) {
      toast.error("Invalid JSON: " + (e instanceof Error ? e.message : "parse failed"));
      return;
    }

    const notes: string[] = [];
    const report = importHealthEntries(parsed, mode);

    let thresholdsApplied = false;
    let sseApplied = false;
    let corsApplied = false;
    let sseDiagApplied = false;

    if (parsed && typeof parsed === "object") {
      const o = parsed as Record<string, unknown>;

      // Thresholds may live at top-level or inside meta.
      const thresholdsCandidate =
        o.thresholds ??
        (o.meta && typeof o.meta === "object"
          ? (o.meta as Record<string, unknown>).thresholds
          : undefined);
      thresholdsApplied = applyThresholds(thresholdsCandidate);

      // SSE reconnect config (from debug report shape).
      const sseCandidate =
        o.sseConfig ??
        o.sseReconnect ??
        (o.meta && typeof o.meta === "object"
          ? (o.meta as Record<string, unknown>).sseReconnect
          : undefined);
      sseApplied = applySseConfig(sseCandidate);

      // CORS preflight result — write straight back into localStorage.
      if (o.corsPreflight && typeof o.corsPreflight === "object") {
        try {
          window.localStorage.setItem(CORS_RESULT_KEY, JSON.stringify(o.corsPreflight));
          corsApplied = true;
        } catch {
          notes.push("Failed to restore CORS result (storage quota).");
        }
      }

      // SSE diagnostic snapshot (most recent status).
      if (o.sseDiagnostic && typeof o.sseDiagnostic === "object") {
        try {
          window.localStorage.setItem(SSE_DIAG_KEY, JSON.stringify(o.sseDiagnostic));
          sseDiagApplied = true;
        } catch {
          notes.push("Failed to restore SSE diagnostic snapshot.");
        }
      }
    }

    const restored: RestoreSummary = {
      history: report,
      thresholds: thresholdsApplied,
      sseConfig: sseApplied,
      corsResult: corsApplied,
      sseDiag: sseDiagApplied,
      notes,
    };
    setSummary(restored);

    const restoredParts = [
      report.imported > 0 ? `${report.imported} history entries` : null,
      thresholdsApplied ? "thresholds" : null,
      sseApplied ? "SSE settings" : null,
      corsApplied ? "CORS result" : null,
      sseDiagApplied ? "SSE diagnostic" : null,
    ].filter(Boolean);

    if (restoredParts.length) toast.success(`Restored ${restoredParts.join(", ")}`);
    else toast.error("Nothing recognizable to import");
  }

  async function onFile(f: File) {
    const raw = await f.text();
    setText(raw);
    apply(raw);
  }

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen((s) => !s)}
        className="border border-border px-3 py-1.5 text-xs font-semibold hover:border-leo hover:text-leo focus:outline-none focus-visible:ring-2 focus-visible:ring-leo"
        aria-expanded={open}
      >
        {open ? "Close import" : "Import debug report"}
      </button>

      {open && (
        <div className="mt-3 w-full border border-border bg-background/60 p-4">
          <p className="eyebrow">Import debug report</p>
          <p className="mt-1 text-xs text-muted-foreground">
            Paste a previously exported debug report JSON or upload a file. Restores health history,
            thresholds, CORS preflight result, and SSE reconnect settings in one click.
          </p>

          <div className="mt-3 flex flex-wrap items-center gap-3 text-xs">
            <label className="inline-flex items-center gap-1">
              <input
                type="radio"
                name="import-mode"
                checked={mode === "merge"}
                onChange={() => setMode("merge")}
              />
              Merge history (dedupe by timestamp+url)
            </label>
            <label className="inline-flex items-center gap-1">
              <input
                type="radio"
                name="import-mode"
                checked={mode === "replace"}
                onChange={() => setMode("replace")}
              />
              Replace history
            </label>
            <input
              ref={fileRef}
              type="file"
              accept="application/json,.json"
              onChange={(e) => {
                const f = e.target.files?.[0];
                if (f) void onFile(f);
              }}
              className="text-xs"
            />
          </div>

          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder='{"history":[…],"thresholds":{…},"sseConfig":{…},"corsPreflight":{…}}'
            spellCheck={false}
            className="mt-3 h-32 w-full resize-y border border-border bg-background p-2 font-mono text-[11px] focus:border-leo focus:outline-none"
          />

          <div className="mt-3 flex flex-wrap gap-2">
            <button
              type="button"
              onClick={() => apply(text)}
              disabled={!text.trim()}
              className="bg-leo px-3 py-1.5 text-xs font-semibold text-leo-foreground disabled:opacity-40 focus:outline-none focus-visible:ring-2 focus-visible:ring-white"
            >
              Import & restore
            </button>
            <button
              type="button"
              onClick={() => {
                setText("");
                setSummary(null);
                if (fileRef.current) fileRef.current.value = "";
              }}
              className="border border-border px-3 py-1.5 text-xs font-semibold hover:bg-input"
            >
              Clear
            </button>
          </div>

          {summary && (
            <div className="mt-4 border-l-2 border-leo/60 bg-input/30 p-3 text-xs">
              <p className="font-semibold">Restore summary</p>
              <ul className="mt-2 space-y-0.5 font-mono text-[11px]">
                <li>
                  · history: imported {summary.history?.imported ?? 0}, skipped{" "}
                  {summary.history?.skipped ?? 0} (
                  {summary.history?.replaced ? "replaced" : "merged"})
                </li>
                <li>· thresholds: {summary.thresholds ? "restored" : "not present"}</li>
                <li>· SSE reconnect settings: {summary.sseConfig ? "restored" : "not present"}</li>
                <li>· CORS preflight result: {summary.corsResult ? "restored" : "not present"}</li>
                <li>· SSE diagnostic snapshot: {summary.sseDiag ? "restored" : "not present"}</li>
              </ul>
              {(summary.history?.errors.length ?? 0) > 0 && (
                <details className="mt-2">
                  <summary className="cursor-pointer text-red-400">
                    {summary.history!.errors.length} history parse error(s)
                  </summary>
                  <ul className="mt-1 space-y-0.5 font-mono text-[11px]">
                    {summary.history!.errors.slice(0, 20).map((e, i) => (
                      <li key={i}>· {e}</li>
                    ))}
                  </ul>
                </details>
              )}
              {summary.notes.length > 0 && (
                <ul className="mt-2 space-y-0.5 text-yellow-400">
                  {summary.notes.map((n, i) => (
                    <li key={i}>! {n}</li>
                  ))}
                </ul>
              )}
            </div>
          )}
        </div>
      )}
    </>
  );
}
