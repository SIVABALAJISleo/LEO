// Generate a downloadable PDF report combining the health-history chart
// (with alert episode overlays via html-to-image), CSV-style latency and
// alert stats, and the SSE diagnostics log.
import { useState } from "react";
import { toast } from "sonner";
import { toPng } from "html-to-image";
import jsPDF from "jspdf";
import { getHealthHistory, computeReliability, getThresholds } from "@/lib/health-history";
import { getAlertTimeline } from "@/lib/health-alert-timeline";
import { getSseLog } from "@/lib/sse-log";
import { getApiBase } from "@/lib/leo-client";

function percentile(sorted: number[], p: number): number | null {
  if (!sorted.length) return null;
  const idx = Math.min(sorted.length - 1, Math.floor((p / 100) * sorted.length));
  return sorted[idx];
}

function fmtDuration(ms: number): string {
  if (ms < 1000) return `${ms}ms`;
  const s = Math.round(ms / 1000);
  if (s < 60) return `${s}s`;
  const m = Math.floor(s / 60);
  return `${m}m ${s % 60}s`;
}

export function GeneratePdfReportButton() {
  const [busy, setBusy] = useState(false);

  async function generate() {
    setBusy(true);
    try {
      const doc = new jsPDF({ unit: "pt", format: "a4" });
      const pageW = doc.internal.pageSize.getWidth();
      const pageH = doc.internal.pageSize.getHeight();
      const margin = 36;
      let y = margin;

      // Title
      doc.setFont("helvetica", "bold");
      doc.setFontSize(18);
      doc.text("LEO AI — Benchmarks report", margin, y);
      y += 22;
      doc.setFont("helvetica", "normal");
      doc.setFontSize(10);
      doc.setTextColor(120);
      doc.text(`Generated ${new Date().toLocaleString()}`, margin, y);
      y += 14;
      doc.text(`API base: ${getApiBase()}`, margin, y);
      y += 20;
      doc.setTextColor(0);

      // Chart image
      const chartEl = document.getElementById("health-history-chart");
      if (chartEl) {
        try {
          const dataUrl = await toPng(chartEl, {
            pixelRatio: 2,
            backgroundColor: "#0a0a0a",
            cacheBust: true,
          });
          const imgW = pageW - margin * 2;
          const imgH = (chartEl.clientHeight / chartEl.clientWidth) * imgW;
          doc.addImage(dataUrl, "PNG", margin, y, imgW, imgH);
          y += imgH + 16;
        } catch (err) {
          doc.setTextColor(180, 0, 0);
          doc.text(
            "Chart snapshot failed: " + (err instanceof Error ? err.message : "unknown"),
            margin,
            y,
          );
          y += 16;
          doc.setTextColor(0);
        }
      } else {
        doc.setTextColor(120);
        doc.text("Health history chart not on page — skipped.", margin, y);
        y += 16;
        doc.setTextColor(0);
      }

      // Stats
      const history = getHealthHistory();
      const reliability = computeReliability(history);
      const thresholds = getThresholds();
      const okCount = history.filter((h) => h.status === "online").length;
      const failCount = history.filter(
        (h) => h.status !== "online" && h.status !== "checking",
      ).length;
      const latencies = history
        .filter((h) => h.status === "online" && typeof h.latencyMs === "number")
        .map((h) => h.latencyMs as number)
        .sort((a, b) => a - b);
      const avgLatency = latencies.length
        ? Math.round(latencies.reduce((s, n) => s + n, 0) / latencies.length)
        : null;
      const rows: [string, string][] = [
        ["Samples", String(history.length)],
        ["Online", String(okCount)],
        ["Failures", String(failCount)],
        ["Failure rate", `${reliability.failureRatePct.toFixed(1)}%`],
        ["Reliability level", reliability.level],
        ["p50 latency", latencies.length ? `${percentile(latencies, 50)}ms` : "—"],
        ["p95 latency", latencies.length ? `${percentile(latencies, 95)}ms` : "—"],
        ["p99 latency", latencies.length ? `${percentile(latencies, 99)}ms` : "—"],
        ["Avg latency", avgLatency != null ? `${avgLatency}ms` : "—"],
        [
          "Thresholds",
          `latencyWarn=${thresholds.latencyWarnMs}ms, avgLatencyWarn=${thresholds.avgLatencyWarnMs}ms, failRate=${thresholds.failureRatePct}%, consecutive=${thresholds.consecutiveFailLimit}`,
        ],
      ];

      if (y > pageH - 200) {
        doc.addPage();
        y = margin;
      }
      doc.setFont("helvetica", "bold");
      doc.setFontSize(12);
      doc.text("Reliability stats", margin, y);
      y += 14;
      doc.setFont("helvetica", "normal");
      doc.setFontSize(10);
      for (const [k, v] of rows) {
        if (y > pageH - margin) {
          doc.addPage();
          y = margin;
        }
        doc.setTextColor(120);
        doc.text(k, margin, y);
        doc.setTextColor(0);
        doc.text(String(v), margin + 140, y, { maxWidth: pageW - margin * 2 - 140 });
        y += 14;
      }
      y += 10;

      // Alert episodes
      const alerts = getAlertTimeline();
      if (y > pageH - 120) {
        doc.addPage();
        y = margin;
      }
      doc.setFont("helvetica", "bold");
      doc.setFontSize(12);
      doc.text(`Alert episodes (${alerts.length})`, margin, y);
      y += 14;
      doc.setFont("helvetica", "normal");
      doc.setFontSize(9);
      if (alerts.length === 0) {
        doc.setTextColor(120);
        doc.text("No alert episodes recorded.", margin, y);
        y += 14;
        doc.setTextColor(0);
      } else {
        for (const ep of alerts.slice(-40).reverse()) {
          if (y > pageH - margin) {
            doc.addPage();
            y = margin;
          }
          const dur = (ep.endedAt ?? Date.now()) - ep.startedAt;
          const line1 = `[${ep.peakLevel.toUpperCase()}] ${new Date(
            ep.startedAt,
          ).toLocaleString()} → ${ep.endedAt ? new Date(ep.endedAt).toLocaleString() : "ongoing"} · ${fmtDuration(dur)}`;
          doc.text(line1, margin, y, { maxWidth: pageW - margin * 2 });
          y += 12;
          const reasons = ep.lastReasons.length ? ep.lastReasons : ep.startReasons;
          if (reasons.length) {
            doc.setTextColor(120);
            doc.text("· " + reasons.join("; "), margin + 12, y, {
              maxWidth: pageW - margin * 2 - 12,
            });
            doc.setTextColor(0);
            y += 12;
          }
        }
      }
      y += 6;

      // SSE log
      const log = getSseLog();
      if (y > pageH - 120) {
        doc.addPage();
        y = margin;
      }
      doc.setFont("helvetica", "bold");
      doc.setFontSize(12);
      doc.text(`SSE diagnostics log (${log.length})`, margin, y);
      y += 14;
      doc.setFont("courier", "normal");
      doc.setFontSize(8);
      if (log.length === 0) {
        doc.setFont("helvetica", "normal");
        doc.setTextColor(120);
        doc.text("No SSE events recorded.", margin, y);
        doc.setTextColor(0);
        y += 14;
      } else {
        for (const e of log.slice(-120)) {
          if (y > pageH - margin) {
            doc.addPage();
            y = margin;
          }
          const bits = [
            new Date(e.at).toISOString(),
            e.kind.toUpperCase(),
            e.message,
            e.attempt != null ? `attempt=${e.attempt}` : "",
            e.backoffMs != null ? `backoff=${e.backoffMs}ms` : "",
            e.transport ? `t=${e.transport}` : "",
          ]
            .filter(Boolean)
            .join(" · ");
          doc.text(bits, margin, y, { maxWidth: pageW - margin * 2 });
          y += 10;
        }
      }

      const pageCount = doc.getNumberOfPages();
      for (let i = 1; i <= pageCount; i++) {
        doc.setPage(i);
        doc.setFont("helvetica", "normal");
        doc.setFontSize(8);
        doc.setTextColor(140);
        doc.text(`Page ${i} of ${pageCount}`, pageW - margin, pageH - 18, { align: "right" });
        doc.setTextColor(0);
      }

      doc.save(`leo-benchmarks-${Date.now()}.pdf`);
      toast.success("PDF report generated");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "PDF generation failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <button
      type="button"
      onClick={generate}
      disabled={busy}
      className="border border-border px-3 py-1.5 text-xs font-semibold hover:border-leo hover:text-leo focus:outline-none focus-visible:ring-2 focus-visible:ring-leo disabled:opacity-50"
    >
      {busy ? "Generating PDF…" : "Generate PDF report"}
    </button>
  );
}
