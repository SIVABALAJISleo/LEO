// User-facing telemetry mode + retention.
//   full        — vitals + runtime errors + unhandled rejections (default)
//   errors-only — drop performance vitals, keep runtime errors/rejections
//   off         — send nothing; also flush and stop queuing anything
//
// Retention controls how long buffered performance events sit in the offline
// queue before being pruned. Errors and unhandled rejections are ALWAYS kept
// regardless of retention — losing crash reports would defeat the point.
export type TelemetryMode = "full" | "errors-only" | "off";
export type RetentionDays = 7 | 30 | 90 | 0; // 0 = keep until sent

const KEY = "leo.telemetry.mode";
const RETENTION_KEY = "leo.telemetry.retention_days";
const QUEUE_KEY = "leo.telemetry.queue";
const DEFAULT_RETENTION: RetentionDays = 30;

const ESSENTIAL_KINDS = new Set(["runtime-error", "unhandled-rejection"]);

export function isEssentialKind(kind: string): boolean {
  return ESSENTIAL_KINDS.has(kind);
}

export function getTelemetryMode(): TelemetryMode {
  if (typeof window === "undefined") return "full";
  const raw = window.localStorage.getItem(KEY);
  if (raw === "off" || raw === "errors-only" || raw === "full") return raw;
  return "full";
}

export function setTelemetryMode(mode: TelemetryMode) {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(KEY, mode);
  if (mode === "off") {
    // Clear anything currently queued so opting out is immediate.
    window.localStorage.removeItem(QUEUE_KEY);
  }
}

export function getRetentionDays(): RetentionDays {
  if (typeof window === "undefined") return DEFAULT_RETENTION;
  const raw = Number(window.localStorage.getItem(RETENTION_KEY));
  if (raw === 7 || raw === 30 || raw === 90 || raw === 0) return raw;
  return DEFAULT_RETENTION;
}

export function setRetentionDays(days: RetentionDays) {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(RETENTION_KEY, String(days));
}

/** Wipe every buffered telemetry event immediately. */
export function clearTelemetryQueue() {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(QUEUE_KEY);
}

/** Should a payload of the given `kind` be sent under the current mode? */
export function shouldSendKind(kind: string): boolean {
  const mode = getTelemetryMode();
  if (mode === "off") return false;
  if (mode === "errors-only") return isEssentialKind(kind);
  return true;
}
