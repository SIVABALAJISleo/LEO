// Health degradation alert: watches the last 30 health entries and raises
// a toast + inline banner when consecutive failures occur or average latency
// crosses the configured threshold. Fires only on state transitions so it
// won't spam while the backend stays down.
import { useEffect, useRef, useState } from "react";
import { toast } from "sonner";
import { useHealthHistory, useThresholds } from "@/lib/health-history";
import { recordAlertTransition } from "@/lib/health-alert-timeline";

const WINDOW = 30;

type Level = "ok" | "warn" | "critical";

export function HealthDegradationAlert() {
  const history = useHealthHistory();
  const [thresholds] = useThresholds();
  const lastLevel = useRef<Level>("ok");
  const [alert, setAlert] = useState<{ level: Level; reasons: string[] } | null>(null);

  useEffect(() => {
    const window = history.slice(-WINDOW);
    if (window.length === 0) return;

    // Consecutive failures at the tail
    let consecutive = 0;
    for (let i = window.length - 1; i >= 0; i--) {
      if (window[i].status !== "online") consecutive++;
      else break;
    }

    const latencies = window
      .filter((e) => typeof e.latencyMs === "number" && e.status === "online")
      .map((e) => e.latencyMs as number);
    const avg = latencies.length
      ? Math.round(latencies.reduce((a, b) => a + b, 0) / latencies.length)
      : 0;
    const over = latencies.filter((l) => l > thresholds.latencyWarnMs).length;

    const reasons: string[] = [];
    let level: Level = "ok";

    if (consecutive >= thresholds.consecutiveFailLimit) {
      level = "critical";
      reasons.push(
        `${consecutive} consecutive failed health checks (limit ${thresholds.consecutiveFailLimit})`,
      );
    }
    if (latencies.length >= 5 && avg > thresholds.avgLatencyWarnMs) {
      if (level !== "critical") level = "warn";
      reasons.push(
        `Avg latency ${avg}ms over last ${latencies.length} samples (> ${thresholds.avgLatencyWarnMs}ms)`,
      );
    }
    if (over >= Math.ceil(latencies.length / 2) && latencies.length >= 6) {
      if (level !== "critical") level = "warn";
      reasons.push(`${over}/${latencies.length} slow samples over ${thresholds.latencyWarnMs}ms`);
    }

    setAlert(level === "ok" ? null : { level, reasons });

    if (level !== lastLevel.current) {
      if (level === "critical") toast.error("Backend degraded — " + reasons[0]);
      else if (level === "warn") toast.warning("Backend slow — " + reasons[0]);
      else toast.success("Backend recovered");
      lastLevel.current = level;
      recordAlertTransition(level, reasons);
    } else if (level !== "ok") {
      // Keep the ongoing episode's reasons fresh.
      recordAlertTransition(level, reasons);
    }
  }, [history, thresholds]);

  if (!alert) return null;

  const color =
    alert.level === "critical"
      ? "border-red-500 bg-red-500/5 text-red-300"
      : "border-yellow-500 bg-yellow-500/5 text-yellow-200";

  return (
    <div role="alert" aria-live="assertive" className={`border-l-2 p-3 text-xs ${color}`}>
      <p className="font-semibold uppercase tracking-wide">
        {alert.level === "critical" ? "Health degraded" : "Health warning"}
      </p>
      <ul className="mt-1 list-inside list-disc space-y-0.5">
        {alert.reasons.map((r) => (
          <li key={r}>{r}</li>
        ))}
      </ul>
    </div>
  );
}
