// Export the health-check history + latency stats + alert-episode timeline as CSV.
// Sits alongside the JSON debug report on /benchmarks.
import { toast } from "sonner";
import { getHealthHistory, computeReliability } from "@/lib/health-history";
import { getApiBase } from "@/lib/leo-client";
import { getAlertTimeline } from "@/lib/health-alert-timeline";

function csvEscape(v: unknown): string {
  if (v === null || v === undefined) return "";
  const s = String(v);
  if (/[",\r\n]/.test(s)) return `"${s.replace(/"/g, '""')}"`;
  return s;
}

function toCsv(rows: (string | number | null | undefined)[][]): string {
  return rows.map((r) => r.map(csvEscape).join(",")).join("\r\n") + "\r\n";
}

function percentile(sorted: number[], p: number): number {
  if (!sorted.length) return 0;
  const idx = Math.min(sorted.length - 1, Math.floor((p / 100) * sorted.length));
  return sorted[idx];
}

export function ExportHealthCsvButton() {
  function download() {
    try {
      const history = getHealthHistory();
      if (!history.length) {
        toast.error("No health checks recorded yet");
        return;
      }
      const latencies = history
        .map((h) => (typeof h.latencyMs === "number" ? h.latencyMs : null))
        .filter((n): n is number => n !== null)
        .sort((a, b) => a - b);
      const rel = computeReliability(history);
      const online = history.filter((h) => h.status === "online").length;
      const offline = history.length - online;
      const timeline = getAlertTimeline();

      const summary: (string | number | null | undefined)[][] = [
        ["# LEO health history export"],
        ["generatedAt", new Date().toISOString()],
        ["apiBase", getApiBase()],
        ["samples", history.length],
        ["online", online],
        ["offline", offline],
        ["failureRatePct", rel.failureRatePct.toFixed(2)],
        ["reliabilityLevel", rel.level],
        ["latency_p50_ms", percentile(latencies, 50)],
        ["latency_p95_ms", percentile(latencies, 95)],
        ["latency_p99_ms", percentile(latencies, 99)],
        [
          "latency_avg_ms",
          latencies.length
            ? Math.round(latencies.reduce((a, b) => a + b, 0) / latencies.length)
            : 0,
        ],
        ["alert_episodes", timeline.length],
        [],
      ];

      const header = [
        "id",
        "checkedAt",
        "isoTime",
        "status",
        "httpStatus",
        "latencyMs",
        "url",
        "failureKind",
        "errorName",
        "message",
        "bodyExcerpt",
      ];
      const rows: (string | number | null | undefined)[][] = history.map((h) => [
        h.id,
        h.checkedAt ?? "",
        h.checkedAt ? new Date(h.checkedAt).toISOString() : "",
        h.status,
        h.httpStatus ?? "",
        h.latencyMs ?? "",
        h.url,
        h.failureKind ?? "",
        h.errorName ?? "",
        h.message ?? "",
        h.bodyExcerpt ?? "",
      ]);

      // Alert episode timeline section — start/end/duration/peak/reasons.
      const alertHeader = [
        "episode_id",
        "level",
        "peakLevel",
        "startedAtIso",
        "endedAtIso",
        "durationSec",
        "startReasons",
        "lastReasons",
      ];
      const now = Date.now();
      const alertRows: (string | number | null | undefined)[][] = timeline.map((ep) => [
        ep.id,
        ep.level,
        ep.peakLevel,
        new Date(ep.startedAt).toISOString(),
        ep.endedAt ? new Date(ep.endedAt).toISOString() : "",
        Math.round(((ep.endedAt ?? now) - ep.startedAt) / 1000),
        ep.startReasons.join("; "),
        ep.lastReasons.join("; "),
      ]);

      const csv =
        toCsv(summary) +
        toCsv([header, ...rows]) +
        "\r\n" +
        toCsv([["# alert episodes"]]) +
        toCsv([alertHeader, ...alertRows]);
      const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `leo-health-history-${Date.now()}.csv`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
      toast.success(
        `Health CSV exported (${history.length} rows, ${timeline.length} alert episodes)`,
      );
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "CSV export failed");
    }
  }

  return (
    <button
      type="button"
      onClick={download}
      className="border border-border px-3 py-1.5 text-xs font-semibold hover:border-leo hover:text-leo focus:outline-none focus-visible:ring-2 focus-visible:ring-leo"
    >
      Export health CSV
    </button>
  );
}
