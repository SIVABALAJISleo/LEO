// Download debug report as JSON file. Bundles health history, SSE diagnostic
// logs, and the latest CORS preflight result for sharing.
import { toast } from "sonner";
import { getApiBase, getApiBaseSource, getEnvApiBase } from "@/lib/leo-client";
import {
  getHealthHistory,
  getDiagnosticsMeta,
  computeReliability,
  getThresholds,
} from "@/lib/health-history";
import { getSseConfig } from "@/lib/sse-config";
import { getAlertTimeline } from "@/lib/health-alert-timeline";
import { getSseLog } from "@/lib/sse-log";

const SSE_DIAG_KEY = "leo.bench.sse-diag";
const CORS_RESULT_KEY = "leo.cors.last_result";

function readJson<T>(key: string): T | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = window.localStorage.getItem(key);
    return raw ? (JSON.parse(raw) as T) : null;
  } catch {
    return null;
  }
}

export function buildDebugReport() {
  const history = getHealthHistory().slice(-30);
  return {
    generatedAt: new Date().toISOString(),
    apiBase: {
      effective: getApiBase(),
      source: getApiBaseSource(),
      env: getEnvApiBase() ?? null,
    },
    meta: getDiagnosticsMeta(),
    thresholds: getThresholds(),
    sseConfig: getSseConfig(),
    reliability: computeReliability(history),
    sseDiagnostic: readJson(SSE_DIAG_KEY),
    sseLog: getSseLog(),
    alertTimeline: getAlertTimeline(),
    corsPreflight: readJson(CORS_RESULT_KEY),
    history,
  };
}

export function ExportDebugReportButton() {
  function download() {
    try {
      const report = buildDebugReport();
      const blob = new Blob([JSON.stringify(report, null, 2)], {
        type: "application/json",
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `leo-debug-report-${Date.now()}.json`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
      toast.success("Debug report downloaded");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Export failed");
    }
  }

  return (
    <button
      type="button"
      onClick={download}
      className="border border-border px-3 py-1.5 text-xs font-semibold hover:border-leo hover:text-leo focus:outline-none focus-visible:ring-2 focus-visible:ring-leo"
    >
      Export debug report
    </button>
  );
}
