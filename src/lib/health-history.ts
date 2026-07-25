// Persistent ring buffer of backend /health check results.
// Feeds the latency sparkline, Diagnostics panel, and reliability alerts.
import { useEffect, useState } from "react";
import type { HealthResult } from "./backend-health";
import { getApiBase } from "./leo-client";

export interface HealthEntry extends HealthResult {
  id: number;
}

const MAX = 60;
const STORAGE_KEY = "leo.health_history_v1";
const THRESHOLD_KEY = "leo.health_thresholds_v1";
const POLLING_KEY = "leo.health_polling_v1";

export interface HealthThresholds {
  latencyWarnMs: number; // single-sample latency warning
  timeoutMs: number; // treated as hard failure
  failureRatePct: number; // % of last N samples failing to trigger alert
  windowSize: number; // N recent samples used for failure rate
  consecutiveFailLimit: number; // # of consecutive failures that trigger degradation alert
  avgLatencyWarnMs: number; // avg latency over the alert window
}

export const DEFAULT_THRESHOLDS: HealthThresholds = {
  latencyWarnMs: 800,
  timeoutMs: 5000,
  failureRatePct: 40,
  windowSize: 10,
  consecutiveFailLimit: 3,
  avgLatencyWarnMs: 800,
};

function loadBuffer(): HealthEntry[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];
    return parsed.slice(-MAX);
  } catch {
    return [];
  }
}

function persist() {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(buffer));
  } catch {
    /* quota — ignore */
  }
}

let buffer: HealthEntry[] = loadBuffer();
let nextId = buffer.reduce((m, e) => Math.max(m, e.id), 0) + 1;
const listeners = new Set<(list: HealthEntry[]) => void>();

function emit() {
  const snapshot = buffer.slice();
  listeners.forEach((l) => l(snapshot));
}

export function pushHealthEntry(r: HealthResult) {
  const entry: HealthEntry = { ...r, id: nextId++ };
  buffer = [...buffer, entry].slice(-MAX);
  persist();
  emit();
}

export function getHealthHistory(): HealthEntry[] {
  return buffer.slice();
}

export function clearHealthHistory() {
  buffer = [];
  persist();
  emit();
}

export interface ImportReport {
  imported: number;
  skipped: number;
  errors: string[];
  replaced: boolean;
}

/**
 * Import previously exported health entries or a full debug report JSON.
 * Accepts debug report ({history:[...]}), snapshot ({entries:[...]}), or a bare array.
 */
export function importHealthEntries(
  input: unknown,
  mode: "merge" | "replace" = "merge",
): ImportReport {
  const errors: string[] = [];
  let rawList: unknown[] = [];
  if (Array.isArray(input)) rawList = input;
  else if (input && typeof input === "object") {
    const o = input as Record<string, unknown>;
    if (Array.isArray(o.history)) rawList = o.history;
    else if (Array.isArray(o.entries)) rawList = o.entries;
    else errors.push("No `history` or `entries` array found in JSON.");
  } else {
    errors.push("Expected JSON object or array.");
  }

  const parsed: HealthEntry[] = [];
  rawList.forEach((row, i) => {
    if (!row || typeof row !== "object") {
      errors.push(`row ${i}: not an object`);
      return;
    }
    const r = row as Record<string, unknown>;
    const atRaw = r.at ?? r.checkedAt;
    const checkedAt =
      typeof atRaw === "string" ? Date.parse(atRaw) : typeof atRaw === "number" ? atRaw : undefined;
    const status = typeof r.status === "string" ? (r.status as HealthEntry["status"]) : undefined;
    if (!status) {
      errors.push(`row ${i}: missing status`);
      return;
    }
    parsed.push({
      id: nextId++,
      status,
      url: typeof r.url === "string" ? r.url : "",
      checkedAt,
      latencyMs: typeof r.latencyMs === "number" ? r.latencyMs : undefined,
      httpStatus: typeof r.httpStatus === "number" ? r.httpStatus : undefined,
      message: typeof r.message === "string" ? r.message : undefined,
      failureKind: r.failureKind as HealthEntry["failureKind"],
      errorName: typeof r.errorName === "string" ? r.errorName : undefined,
      bodyExcerpt: typeof r.bodyExcerpt === "string" ? r.bodyExcerpt : undefined,
    });
  });

  if (mode === "replace") {
    buffer = parsed.slice(-MAX);
  } else {
    const seen = new Set(buffer.map((e) => `${e.checkedAt}|${e.url}`));
    for (const e of parsed) {
      const k = `${e.checkedAt}|${e.url}`;
      if (seen.has(k)) continue;
      seen.add(k);
      buffer.push(e);
    }
    buffer = buffer.slice(-MAX);
  }
  persist();
  emit();
  return {
    imported: parsed.length,
    skipped: rawList.length - parsed.length,
    errors,
    replaced: mode === "replace",
  };
}

export function useHealthHistory(): HealthEntry[] {
  const [list, setList] = useState<HealthEntry[]>(() => buffer.slice());
  useEffect(() => {
    listeners.add(setList);
    return () => {
      listeners.delete(setList);
    };
  }, []);
  return list;
}

// Thresholds ---------------------------------------------------------------

export function getThresholds(): HealthThresholds {
  if (typeof window === "undefined") return DEFAULT_THRESHOLDS;
  try {
    const raw = window.localStorage.getItem(THRESHOLD_KEY);
    if (!raw) return DEFAULT_THRESHOLDS;
    return { ...DEFAULT_THRESHOLDS, ...(JSON.parse(raw) as Partial<HealthThresholds>) };
  } catch {
    return DEFAULT_THRESHOLDS;
  }
}

export function setThresholds(t: HealthThresholds) {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(THRESHOLD_KEY, JSON.stringify(t));
  window.dispatchEvent(new CustomEvent("leo:thresholds-changed"));
}

export function useThresholds(): [HealthThresholds, (t: HealthThresholds) => void] {
  const [t, setT] = useState<HealthThresholds>(() => getThresholds());
  useEffect(() => {
    const on = () => setT(getThresholds());
    window.addEventListener("leo:thresholds-changed", on);
    return () => window.removeEventListener("leo:thresholds-changed", on);
  }, []);
  return [
    t,
    (next) => {
      setThresholds(next);
      setT(next);
    },
  ];
}

export interface ReliabilityReport {
  level: "ok" | "warn" | "critical";
  failureRatePct: number;
  slowSamples: number;
  windowSize: number;
  reasons: string[];
}

export function computeReliability(
  entries: HealthEntry[] = buffer,
  t: HealthThresholds = getThresholds(),
): ReliabilityReport {
  const window = entries.slice(-t.windowSize);
  if (window.length === 0) {
    return { level: "ok", failureRatePct: 0, slowSamples: 0, windowSize: 0, reasons: [] };
  }
  const failures = window.filter((e) => e.status !== "online").length;
  const slow = window.filter((e) => (e.latencyMs ?? 0) > t.latencyWarnMs).length;
  const failureRatePct = Math.round((failures / window.length) * 100);
  const reasons: string[] = [];
  let level: ReliabilityReport["level"] = "ok";
  if (failureRatePct >= t.failureRatePct) {
    level = "critical";
    reasons.push(`Failure rate ${failureRatePct}% ≥ ${t.failureRatePct}%`);
  }
  if (slow >= Math.ceil(window.length / 2)) {
    if (level !== "critical") level = "warn";
    reasons.push(`${slow}/${window.length} samples over ${t.latencyWarnMs}ms`);
  }
  return { level, failureRatePct, slowSamples: slow, windowSize: window.length, reasons };
}

// Polling intervals ------------------------------------------------------

export interface PollingIntervals {
  healthMs: number; // 0 disables auto-polling
  metricsMs: number; // 0 disables auto-polling
}

export const DEFAULT_POLLING: PollingIntervals = { healthMs: 15000, metricsMs: 3000 };

export function getPollingIntervals(): PollingIntervals {
  if (typeof window === "undefined") return DEFAULT_POLLING;
  try {
    const raw = window.localStorage.getItem(POLLING_KEY);
    if (!raw) return DEFAULT_POLLING;
    return { ...DEFAULT_POLLING, ...(JSON.parse(raw) as Partial<PollingIntervals>) };
  } catch {
    return DEFAULT_POLLING;
  }
}

export function setPollingIntervals(p: PollingIntervals) {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(POLLING_KEY, JSON.stringify(p));
  window.dispatchEvent(new CustomEvent("leo:polling-changed"));
}

export function usePollingIntervals(): [PollingIntervals, (p: PollingIntervals) => void] {
  const [p, setP] = useState<PollingIntervals>(() => getPollingIntervals());
  useEffect(() => {
    const on = () => setP(getPollingIntervals());
    window.addEventListener("leo:polling-changed", on);
    return () => window.removeEventListener("leo:polling-changed", on);
  }, []);
  return [
    p,
    (next) => {
      setPollingIntervals(next);
      setP(next);
    },
  ];
}

// Snapshot / metadata ----------------------------------------------------

export interface DiagnosticsMeta {
  exportedAt: string;
  apiBase: string;
  envApiBase: string | null;
  polling: PollingIntervals;
  thresholds: HealthThresholds;
  userAgent?: string;
}

export function getDiagnosticsMeta(): DiagnosticsMeta {
  return {
    exportedAt: new Date().toISOString(),
    apiBase: getApiBase(),
    envApiBase: (import.meta.env.VITE_LEO_API_BASE_URL as string | undefined) ?? null,
    polling: getPollingIntervals(),
    thresholds: getThresholds(),
    userAgent: typeof navigator !== "undefined" ? navigator.userAgent : undefined,
  };
}

export function getDiagnosticsSnapshot(count = 20) {
  const entries = buffer.slice(-count);
  return {
    meta: getDiagnosticsMeta(),
    reliability: computeReliability(entries),
    latest: entries[entries.length - 1] ?? null,
    entries,
  };
}

// Exports ------------------------------------------------------------------

export function exportHealthJson(count = 20): string {
  return JSON.stringify(getDiagnosticsSnapshot(count), null, 2);
}

export function exportHealthCsv(count = 20): string {
  const rows = buffer.slice(-count);
  const meta = getDiagnosticsMeta();
  const header = [
    "timestamp",
    "status",
    "http_status",
    "latency_ms",
    "url",
    "message",
    "body_excerpt",
  ];
  const esc = (v: unknown) => {
    const s = v == null ? "" : String(v);
    return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
  };
  const metaLines = [
    `# exported_at=${meta.exportedAt}`,
    `# api_base=${meta.apiBase}`,
    `# env_api_base=${meta.envApiBase ?? ""}`,
    `# polling_health_ms=${meta.polling.healthMs}`,
    `# polling_metrics_ms=${meta.polling.metricsMs}`,
    `# threshold_latency_warn_ms=${meta.thresholds.latencyWarnMs}`,
    `# threshold_timeout_ms=${meta.thresholds.timeoutMs}`,
    `# threshold_failure_rate_pct=${meta.thresholds.failureRatePct}`,
    `# threshold_window_size=${meta.thresholds.windowSize}`,
  ];
  const lines = rows.map((r) =>
    [
      r.checkedAt ? new Date(r.checkedAt).toISOString() : "",
      r.status,
      r.httpStatus ?? "",
      r.latencyMs ?? "",
      r.url,
      r.message ?? "",
      r.bodyExcerpt ?? "",
    ]
      .map(esc)
      .join(","),
  );
  return [...metaLines, header.join(","), ...lines].join("\n");
}
