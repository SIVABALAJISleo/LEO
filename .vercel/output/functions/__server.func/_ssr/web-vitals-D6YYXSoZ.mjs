import { t as reportLovableError } from "./lovable-error-reporting-2OGRNSh7.mjs";
import { a as x, i as b, n as T, r as W, t as S } from "../_libs/web-vitals.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/web-vitals-D6YYXSoZ.js
var KEY = "leo.telemetry.mode";
var RETENTION_KEY = "leo.telemetry.retention_days";
var QUEUE_KEY$1 = "leo.telemetry.queue";
var DEFAULT_RETENTION = 30;
var ESSENTIAL_KINDS = new Set(["runtime-error", "unhandled-rejection"]);
function isEssentialKind(kind) {
	return ESSENTIAL_KINDS.has(kind);
}
function getTelemetryMode() {
	if (typeof window === "undefined") return "full";
	const raw = window.localStorage.getItem(KEY);
	if (raw === "off" || raw === "errors-only" || raw === "full") return raw;
	return "full";
}
function setTelemetryMode(mode) {
	if (typeof window === "undefined") return;
	window.localStorage.setItem(KEY, mode);
	if (mode === "off" || mode === "errors-only") clearTelemetryQueue();
}
function getRetentionDays() {
	if (typeof window === "undefined") return DEFAULT_RETENTION;
	const raw = Number(window.localStorage.getItem(RETENTION_KEY));
	if (raw === 7 || raw === 30 || raw === 90 || raw === 0) return raw;
	return DEFAULT_RETENTION;
}
function setRetentionDays(days) {
	if (typeof window === "undefined") return;
	window.localStorage.setItem(RETENTION_KEY, String(days));
}
/** Wipe non-essential buffered telemetry events immediately. */
function clearTelemetryQueue() {
	if (typeof window === "undefined") return;
	const raw = window.localStorage.getItem(QUEUE_KEY$1);
	if (!raw) return;
	try {
		const arr = JSON.parse(raw);
		if (Array.isArray(arr)) {
			const kept = arr.filter((p) => isEssentialKind(typeof p.kind === "string" ? p.kind : ""));
			window.localStorage.setItem(QUEUE_KEY$1, JSON.stringify(kept));
			return;
		}
	} catch {}
	window.localStorage.removeItem(QUEUE_KEY$1);
}
/** Should a payload of the given `kind` be sent under the current mode? */
function shouldSendKind(kind) {
	if (isEssentialKind(kind)) return true;
	const mode = getTelemetryMode();
	if (mode === "off") return false;
	if (mode === "errors-only") return isEssentialKind(kind);
	return true;
}
var ENDPOINT = "/api/telemetry";
var QUEUE_KEY = "leo.telemetry.queue";
var MAX_QUEUE = 500;
var FLUSH_INTERVAL_MS = 15e3;
function loadQueue() {
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
function saveQueue(q) {
	if (typeof window === "undefined") return;
	try {
		const trimmed = q.length > MAX_QUEUE ? q.slice(q.length - MAX_QUEUE) : q;
		window.localStorage.setItem(QUEUE_KEY, JSON.stringify(trimmed));
	} catch {}
}
function enqueue(payload) {
	const q = loadQueue();
	q.push(payload);
	saveQueue(pruneQueue(q));
}
/**
* Drop non-essential (performance) events older than the configured
* retention window. Runtime errors and unhandled rejections are always kept.
*/
function pruneQueue(input) {
	const q = input ?? loadQueue();
	const days = getRetentionDays();
	if (days === 0) return q;
	const cutoff = Date.now() - days * 24 * 60 * 60 * 1e3;
	const kept = q.filter((p) => {
		if (isEssentialKind(typeof p.kind === "string" ? p.kind : "")) return true;
		return (typeof p.ts === "number" ? p.ts : 0) >= cutoff;
	});
	if (!input) saveQueue(kept);
	return kept;
}
async function sendBatch(batch) {
	const body = JSON.stringify({ events: batch });
	try {
		return (await fetch(ENDPOINT, {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body,
			keepalive: true
		})).ok;
	} catch {
		return false;
	}
}
var flushing = false;
async function flushTelemetry() {
	if (flushing) return;
	const q = pruneQueue();
	if (q.length === 0) return;
	if (typeof navigator !== "undefined" && navigator.onLine === false) return;
	getTelemetryMode();
	const toSend = q.filter((p) => shouldSendKind(typeof p.kind === "string" ? p.kind : ""));
	if (toSend.length === 0) return;
	flushing = true;
	try {
		const chunkSize = 50;
		let remaining = toSend;
		while (remaining.length > 0) {
			if (!await sendBatch(remaining.slice(0, chunkSize))) {
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
var DEFAULT_REPORTER = (payload) => {
	if (!shouldSendKind(typeof payload.kind === "string" ? payload.kind : "")) return;
	let sent = false;
	try {
		if ((typeof navigator === "undefined" || navigator.onLine !== false) && typeof navigator !== "undefined" && "sendBeacon" in navigator) {
			const blob = new Blob([JSON.stringify(payload)], { type: "application/json" });
			sent = navigator.sendBeacon(ENDPOINT, blob);
		}
	} catch {
		sent = false;
	}
	if (!sent) {
		enqueue(payload);
		flushTelemetry();
	}
};
var reporter = DEFAULT_REPORTER;
/**
* Emit a custom telemetry event through the same reporter/queue/beacon path
* as web vitals. Use for domain events like chat reconnects, optimistic
* rollbacks, and merge-banner changes. Auto-stamps `ts` and `path`.
*/
function reportTelemetry(payload) {
	reporter({
		ts: Date.now(),
		path: typeof window !== "undefined" ? window.location.pathname : "",
		...payload
	});
}
function sendMetric(metric) {
	reporter({
		kind: "web-vital",
		name: metric.name,
		value: Math.round(metric.value * 100) / 100,
		rating: metric.rating,
		id: metric.id,
		navigationType: metric.navigationType,
		path: typeof window !== "undefined" ? window.location.pathname : "",
		ts: Date.now()
	});
}
var installed = false;
function initWebVitals() {
	if (installed || typeof window === "undefined") return;
	installed = true;
	try {
		b(sendMetric);
		S(sendMetric);
		x(sendMetric);
		T(sendMetric);
		W(sendMetric);
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
			stack: event.error instanceof Error ? event.error.stack : void 0,
			path: window.location.pathname,
			ts: Date.now()
		});
		reportLovableError(event.error ?? new Error(event.message), { source: "window.onerror" });
	});
	window.addEventListener("unhandledrejection", (event) => {
		const reason = event.reason;
		reporter({
			kind: "unhandled-rejection",
			message: reason instanceof Error ? reason.message : String(reason),
			stack: reason instanceof Error ? reason.stack : void 0,
			path: window.location.pathname,
			ts: Date.now()
		});
		reportLovableError(reason, { source: "unhandledrejection" });
	});
	window.addEventListener("online", () => void flushTelemetry());
	window.addEventListener("visibilitychange", () => {
		if (document.visibilityState === "visible") flushTelemetry();
	});
	window.addEventListener("pagehide", () => {
		const q = loadQueue();
		if (q.length === 0) return;
		try {
			const blob = new Blob([JSON.stringify({ events: q })], { type: "application/json" });
			if (navigator.sendBeacon(ENDPOINT, blob)) saveQueue([]);
		} catch {}
	});
	setInterval(() => void flushTelemetry(), FLUSH_INTERVAL_MS);
	flushTelemetry();
}
//#endregion
export { setTelemetryMode as a, setRetentionDays as i, initWebVitals, getRetentionDays as n, pruneQueue, getTelemetryMode as r, reportTelemetry, clearTelemetryQueue as t };
