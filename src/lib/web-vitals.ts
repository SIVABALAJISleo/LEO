// Web Vitals collection + runtime error reporting with offline buffering.
// Metrics/errors queue to localStorage when the network is down (or the
// beacon fails) and flush on `online`, on interval, and on `visibilitychange`.
import { onCLS, onINP, onLCP, onFCP, onTTFB, type Metric } from "web-vitals";
import { reportLovableError } from "./lovable-error-reporting";
import {
  getTelemetryMode,
  shouldSendKind,
  getRetentionDays,
  isEssentialKind,
} from "./telemetry-prefs";

type Payload = Record<string, unknown>;
type Reporter = (payload: Payload) => void;

const ENDPOINT = "/api/telemetry";
const QUEUE_KEY = "leo.telemetry.queue";
const MAX_QUEUE = 500; // hard cap on buffered events
const FLUSH_INTERVAL_MS = 15_000;

function loadQueue(): Payload[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = window.localStorage.getItem(QUEUE_KEY);
    if (!raw) return [];
    const arr = JSON.parse(raw);
    return Array.isArray(arr) ? arr : [];
  } catch {
    return [];
  }
}

function saveQueue(q: Payload[]) {
  if (typeof window === "undefined") return;
  try {
    const trimmed = q.length > MAX_QUEUE ? q.slice(q.length - MAX_QUEUE) : q;
    window.localStorage.setItem(QUEUE_KEY, JSON.stringify(trimmed));
  } catch {
    /* quota exceeded or private mode — drop silently */
  }
}

function enqueue(payload: Payload) {
  const q = loadQueue();
  q.push(payload);
  saveQueue(pruneQueue(q));
}

/**
 * Drop non-essential (performance) events older than the configured
 * retention window. Runtime errors and unhandled rejections are always kept.
 */
export function pruneQueue(input?: Payload[]): Payload[] {
  const q = input ?? loadQueue();
  const days = getRetentionDays();
  if (days === 0) return q;
  const cutoff = Date.now() - days * 24 * 60 * 60 * 1000;
  const kept = q.filter((p) => {
    const kind = typeof p.kind === "string" ? p.kind : "";
    if (isEssentialKind(kind)) return true;
    const ts = typeof p.ts === "number" ? p.ts : 0;
    return ts >= cutoff;
  });
  if (!input) saveQueue(kept);
  return kept;
}

async function sendBatch(batch: Payload[]): Promise<boolean> {
  const body = JSON.stringify({ events: batch });
  // Prefer keepalive fetch so we get a proper success/failure signal.
  try {
    const res = await fetch(ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body,
      keepalive: true,
    });
    return res.ok;
  } catch {
    return false;
  }
}

let flushing = false;
export async function flushTelemetry(): Promise<void> {
  if (flushing) return;
  if (getTelemetryMode() === "off") return;
  if (typeof navigator !== "undefined" && navigator.onLine === false) return;
  const q = pruneQueue();
  if (q.length === 0) return;
  flushing = true;
  try {
    // Send in chunks of 50 so a big backlog doesn't blow up a single request.
    const chunkSize = 50;
    let remaining = q.slice();
    while (remaining.length > 0) {
      const chunk = remaining.slice(0, chunkSize);
      const ok = await sendBatch(chunk);
      if (!ok) {
        // stop; keep whatever's left for next attempt
        saveQueue(remaining);
        return;
      }
      remaining = remaining.slice(chunkSize);
      saveQueue(remaining);
    }
  } finally {
    flushing = false;
  }
}

const DEFAULT_REPORTER: Reporter = (payload) => {
  const kind = typeof payload.kind === "string" ? payload.kind : "";
  if (!shouldSendKind(kind)) return; // respect user telemetry opt-out
  if (import.meta.env.DEV) {
    console.info("[LEO vitals]", payload);
  }
  // Fast-path: try beacon so we don't block the main thread. If offline or
  // sendBeacon returns false, fall back to the offline queue + flush loop.
  let sent = false;
  try {
    const online = typeof navigator === "undefined" || navigator.onLine !== false;
    if (online && typeof navigator !== "undefined" && "sendBeacon" in navigator) {
      const blob = new Blob([JSON.stringify(payload)], { type: "application/json" });
      sent = navigator.sendBeacon(ENDPOINT, blob);
    }
  } catch {
    sent = false;
  }
  if (!sent) {
    enqueue(payload);
    // Try an async fetch flush shortly — beacon may have failed for size,
    // fetch with keepalive often works when beacon doesn't.
    void flushTelemetry();
  }
};

let reporter: Reporter = DEFAULT_REPORTER;
export function setVitalsReporter(fn: Reporter) {
  reporter = fn;
}

/**
 * Emit a custom telemetry event through the same reporter/queue/beacon path
 * as web vitals. Use for domain events like chat reconnects, optimistic
 * rollbacks, and merge-banner changes. Auto-stamps `ts` and `path`.
 */
export function reportTelemetry(payload: Payload) {
  reporter({
    ts: Date.now(),
    path: typeof window !== "undefined" ? window.location.pathname : "",
    ...payload,
  });
}

function sendMetric(metric: Metric) {
  reporter({
    kind: "web-vital",
    name: metric.name,
    value: Math.round(metric.value * 100) / 100,
    rating: metric.rating,
    id: metric.id,
    navigationType: metric.navigationType,
    path: typeof window !== "undefined" ? window.location.pathname : "",
    ts: Date.now(),
  });
}

let installed = false;
export function initWebVitals() {
  if (installed || typeof window === "undefined") return;
  installed = true;

  try {
    onCLS(sendMetric);
    onINP(sendMetric);
    onLCP(sendMetric);
    onFCP(sendMetric);
    onTTFB(sendMetric);
  } catch (err) {
    console.warn("[LEO vitals] init failed", err);
  }

  window.addEventListener("error", (event) => {
    reporter({
      kind: "runtime-error",
      message: event.message,
      filename: event.filename,
      lineno: event.lineno,
      colno: event.colno,
      stack: event.error instanceof Error ? event.error.stack : undefined,
      path: window.location.pathname,
      ts: Date.now(),
    });
    reportLovableError(event.error ?? new Error(event.message), {
      source: "window.onerror",
    });
  });

  window.addEventListener("unhandledrejection", (event) => {
    const reason = event.reason;
    reporter({
      kind: "unhandled-rejection",
      message: reason instanceof Error ? reason.message : String(reason),
      stack: reason instanceof Error ? reason.stack : undefined,
      path: window.location.pathname,
      ts: Date.now(),
    });
    reportLovableError(reason, { source: "unhandledrejection" });
  });

  // Flush the offline queue when the network comes back or the tab regains
  // focus / is being hidden.
  window.addEventListener("online", () => void flushTelemetry());
  window.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "visible") void flushTelemetry();
  });
  window.addEventListener("pagehide", () => {
    // Best-effort final drain using beacon.
    const q = loadQueue();
    if (q.length === 0) return;
    try {
      const blob = new Blob([JSON.stringify({ events: q })], { type: "application/json" });
      if (navigator.sendBeacon(ENDPOINT, blob)) saveQueue([]);
    } catch {
      /* ignore */
    }
  });
  // Periodic flush for long-lived tabs.
  setInterval(() => void flushTelemetry(), FLUSH_INTERVAL_MS);
  // Kick off an initial flush in case we're picking up queued events from a
  // previous session.
  void flushTelemetry();
}
