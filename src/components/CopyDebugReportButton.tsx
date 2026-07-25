// One-click "Copy debug report": bundles the effective API base URL,
// recent health-check history, last classified error, and timestamps into
// a single JSON block for pasting into bug reports.
import { useState } from "react";
import { toast } from "sonner";
import { getApiBase, getApiBaseSource, getEnvApiBase } from "@/lib/leo-client";
import { getHealthHistory, getDiagnosticsMeta, computeReliability } from "@/lib/health-history";

export function CopyDebugReportButton() {
  const [busy, setBusy] = useState(false);

  async function copy() {
    setBusy(true);
    try {
      const history = getHealthHistory().slice(-30);
      const lastError =
        [...history].reverse().find((e) => e.status !== "online" && e.status !== "checking") ??
        null;
      const report = {
        generatedAt: new Date().toISOString(),
        apiBase: {
          effective: getApiBase(),
          source: getApiBaseSource(),
          env: getEnvApiBase() ?? null,
        },
        meta: getDiagnosticsMeta(),
        reliability: computeReliability(history),
        lastError: lastError
          ? {
              at: lastError.checkedAt ? new Date(lastError.checkedAt).toISOString() : null,
              status: lastError.status,
              failureKind: lastError.failureKind,
              httpStatus: lastError.httpStatus,
              errorName: lastError.errorName,
              message: lastError.message,
              hints: lastError.hints,
              url: lastError.url,
            }
          : null,
        history: history.map((e) => ({
          at: e.checkedAt ? new Date(e.checkedAt).toISOString() : null,
          status: e.status,
          latencyMs: e.latencyMs,
          httpStatus: e.httpStatus,
          failureKind: e.failureKind,
          message: e.message,
          url: e.url,
        })),
      };
      const json = JSON.stringify(report, null, 2);
      await navigator.clipboard.writeText(json);
      toast.success("Debug report copied to clipboard");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Copy failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <button
      type="button"
      onClick={copy}
      disabled={busy}
      className="border border-border px-3 py-1.5 text-xs font-semibold hover:border-leo hover:text-leo disabled:opacity-40 focus:outline-none focus-visible:ring-2 focus-visible:ring-leo"
    >
      {busy ? "Copying…" : "Copy debug report"}
    </button>
  );
}
