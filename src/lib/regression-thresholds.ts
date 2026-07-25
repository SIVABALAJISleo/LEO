import { useEffect, useState } from "react";

export type RegressionThresholds = {
  enabled: boolean;
  p50PctIncrease: number; // e.g. 20 = alert if p50 grows >20% vs baseline
  p95PctIncrease: number;
  p99PctIncrease: number;
  errorRateAbsPct: number; // absolute % error rate that triggers alert
  throughputPctDrop: number; // alert if throughput drops more than N%
};

const KEY = "leo.bench.thresholds";

export const DEFAULT_THRESHOLDS: RegressionThresholds = {
  enabled: true,
  p50PctIncrease: 15,
  p95PctIncrease: 20,
  p99PctIncrease: 25,
  errorRateAbsPct: 2,
  throughputPctDrop: 15,
};

function read(): RegressionThresholds {
  if (typeof window === "undefined") return DEFAULT_THRESHOLDS;
  try {
    const raw = window.localStorage.getItem(KEY);
    return raw ? { ...DEFAULT_THRESHOLDS, ...JSON.parse(raw) } : DEFAULT_THRESHOLDS;
  } catch {
    return DEFAULT_THRESHOLDS;
  }
}

export function useRegressionThresholds(): [
  RegressionThresholds,
  (next: RegressionThresholds) => void,
] {
  const [t, setT] = useState<RegressionThresholds>(DEFAULT_THRESHOLDS);
  useEffect(() => {
    setT(read());
    const on = () => setT(read());
    window.addEventListener("leo:thresholds", on);
    window.addEventListener("storage", on);
    return () => {
      window.removeEventListener("leo:thresholds", on);
      window.removeEventListener("storage", on);
    };
  }, []);
  const save = (next: RegressionThresholds) => {
    setT(next);
    try {
      window.localStorage.setItem(KEY, JSON.stringify(next));
      window.dispatchEvent(new CustomEvent("leo:thresholds"));
    } catch {
      /* ignore */
    }
  };
  return [t, save];
}

export type RegressionFinding = {
  metric: "p50" | "p95" | "p99" | "throughput" | "errorRate";
  label: string;
  base: number;
  target: number;
  delta: number; // signed % change
  breach: number; // threshold that was violated (%)
  severity: "warn" | "critical";
};

export function evaluateRegressions(
  base: {
    p50Ms: number;
    p95Ms: number;
    p99Ms: number;
    throughputRps: number;
    errorRatePct: number;
  } | null,
  target: {
    p50Ms: number;
    p95Ms: number;
    p99Ms: number;
    throughputRps: number;
    errorRatePct: number;
  } | null,
  t: RegressionThresholds,
): RegressionFinding[] {
  if (!base || !target || !t.enabled) return [];
  const findings: RegressionFinding[] = [];
  const pct = (a: number, b: number) =>
    a === 0 ? (b === 0 ? 0 : 100) : ((b - a) / Math.abs(a)) * 100;

  const checks: {
    metric: RegressionFinding["metric"];
    label: string;
    delta: number;
    breach: number;
    triggered: boolean;
  }[] = [
    {
      metric: "p50",
      label: "p50 latency",
      delta: pct(base.p50Ms, target.p50Ms),
      breach: t.p50PctIncrease,
      triggered: pct(base.p50Ms, target.p50Ms) > t.p50PctIncrease,
    },
    {
      metric: "p95",
      label: "p95 latency",
      delta: pct(base.p95Ms, target.p95Ms),
      breach: t.p95PctIncrease,
      triggered: pct(base.p95Ms, target.p95Ms) > t.p95PctIncrease,
    },
    {
      metric: "p99",
      label: "p99 latency",
      delta: pct(base.p99Ms, target.p99Ms),
      breach: t.p99PctIncrease,
      triggered: pct(base.p99Ms, target.p99Ms) > t.p99PctIncrease,
    },
    {
      metric: "throughput",
      label: "throughput",
      delta: pct(base.throughputRps, target.throughputRps),
      breach: -t.throughputPctDrop,
      triggered: pct(base.throughputRps, target.throughputRps) < -t.throughputPctDrop,
    },
    {
      metric: "errorRate",
      label: "error rate",
      delta: target.errorRatePct - base.errorRatePct,
      breach: t.errorRateAbsPct,
      triggered:
        target.errorRatePct >= t.errorRateAbsPct && target.errorRatePct > base.errorRatePct,
    },
  ];

  for (const c of checks) {
    if (!c.triggered) continue;
    const mag = Math.abs(c.delta) / Math.max(1, Math.abs(c.breach));
    findings.push({
      metric: c.metric,
      label: c.label,
      base:
        c.metric === "throughput"
          ? base.throughputRps
          : c.metric === "errorRate"
            ? base.errorRatePct
            : (base as Record<string, number>)[`${c.metric}Ms`],
      target:
        c.metric === "throughput"
          ? target.throughputRps
          : c.metric === "errorRate"
            ? target.errorRatePct
            : (target as Record<string, number>)[`${c.metric}Ms`],
      delta: c.delta,
      breach: c.breach,
      severity: mag >= 2 ? "critical" : "warn",
    });
  }
  return findings;
}
