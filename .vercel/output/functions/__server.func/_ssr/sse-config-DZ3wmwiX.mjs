import { o as __toESM } from "../_runtime.mjs";
import { i as require_react, r as require_jsx_runtime } from "../_libs/react+tanstack__react-query.mjs";
import { n as toast } from "../_libs/sonner.mjs";
import { a as getEnvApiBase, l as resetApiBase, n as getApiBase, r as getApiBaseSource, u as setApiBase } from "./leo-client-D7U1wpIv.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/sse-config-DZ3wmwiX.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
var STORAGE_KEY = "leo.health_history_v1";
var THRESHOLD_KEY = "leo.health_thresholds_v1";
var POLLING_KEY = "leo.health_polling_v1";
var DEFAULT_THRESHOLDS = {
	latencyWarnMs: 800,
	timeoutMs: 5e3,
	failureRatePct: 40,
	windowSize: 10,
	consecutiveFailLimit: 3,
	avgLatencyWarnMs: 800
};
function loadBuffer() {
	if (typeof window === "undefined") return [];
	try {
		const raw = window.localStorage.getItem(STORAGE_KEY);
		if (!raw) return [];
		const parsed = JSON.parse(raw);
		if (!Array.isArray(parsed)) return [];
		return parsed.slice(-60);
	} catch {
		return [];
	}
}
function persist() {
	if (typeof window === "undefined") return;
	try {
		window.localStorage.setItem(STORAGE_KEY, JSON.stringify(buffer));
	} catch {}
}
var buffer = loadBuffer();
var nextId = buffer.reduce((m, e) => Math.max(m, e.id), 0) + 1;
var listeners = /* @__PURE__ */ new Set();
function emit() {
	const snapshot = buffer.slice();
	listeners.forEach((l) => l(snapshot));
}
function pushHealthEntry(r) {
	const entry = {
		...r,
		id: nextId++
	};
	buffer = [...buffer, entry].slice(-60);
	persist();
	emit();
}
function getHealthHistory() {
	return buffer.slice();
}
function clearHealthHistory() {
	buffer = [];
	persist();
	emit();
}
/**
* Import previously exported health entries or a full debug report JSON.
* Accepts debug report ({history:[...]}), snapshot ({entries:[...]}), or a bare array.
*/
function importHealthEntries(input, mode = "merge") {
	const errors = [];
	let rawList = [];
	if (Array.isArray(input)) rawList = input;
	else if (input && typeof input === "object") {
		const o = input;
		if (Array.isArray(o.history)) rawList = o.history;
		else if (Array.isArray(o.entries)) rawList = o.entries;
		else errors.push("No `history` or `entries` array found in JSON.");
	} else errors.push("Expected JSON object or array.");
	const parsed = [];
	rawList.forEach((row, i) => {
		if (!row || typeof row !== "object") {
			errors.push(`row ${i}: not an object`);
			return;
		}
		const r = row;
		const atRaw = r.at ?? r.checkedAt;
		const checkedAt = typeof atRaw === "string" ? Date.parse(atRaw) : typeof atRaw === "number" ? atRaw : void 0;
		const status = typeof r.status === "string" ? r.status : void 0;
		if (!status) {
			errors.push(`row ${i}: missing status`);
			return;
		}
		parsed.push({
			id: nextId++,
			status,
			url: typeof r.url === "string" ? r.url : "",
			checkedAt,
			latencyMs: typeof r.latencyMs === "number" ? r.latencyMs : void 0,
			httpStatus: typeof r.httpStatus === "number" ? r.httpStatus : void 0,
			message: typeof r.message === "string" ? r.message : void 0,
			failureKind: r.failureKind,
			errorName: typeof r.errorName === "string" ? r.errorName : void 0,
			bodyExcerpt: typeof r.bodyExcerpt === "string" ? r.bodyExcerpt : void 0
		});
	});
	if (mode === "replace") buffer = parsed.slice(-60);
	else {
		const seen = new Set(buffer.map((e) => `${e.checkedAt}|${e.url}`));
		for (const e of parsed) {
			const k = `${e.checkedAt}|${e.url}`;
			if (seen.has(k)) continue;
			seen.add(k);
			buffer.push(e);
		}
		buffer = buffer.slice(-60);
	}
	persist();
	emit();
	return {
		imported: parsed.length,
		skipped: rawList.length - parsed.length,
		errors,
		replaced: mode === "replace"
	};
}
function useHealthHistory() {
	const [list, setList] = (0, import_react.useState)(() => buffer.slice());
	(0, import_react.useEffect)(() => {
		listeners.add(setList);
		return () => {
			listeners.delete(setList);
		};
	}, []);
	return list;
}
function getThresholds() {
	if (typeof window === "undefined") return DEFAULT_THRESHOLDS;
	try {
		const raw = window.localStorage.getItem(THRESHOLD_KEY);
		if (!raw) return DEFAULT_THRESHOLDS;
		return {
			...DEFAULT_THRESHOLDS,
			...JSON.parse(raw)
		};
	} catch {
		return DEFAULT_THRESHOLDS;
	}
}
function setThresholds(t) {
	if (typeof window === "undefined") return;
	window.localStorage.setItem(THRESHOLD_KEY, JSON.stringify(t));
	window.dispatchEvent(new CustomEvent("leo:thresholds-changed"));
}
function useThresholds() {
	const [t, setT] = (0, import_react.useState)(() => getThresholds());
	(0, import_react.useEffect)(() => {
		const on = () => setT(getThresholds());
		window.addEventListener("leo:thresholds-changed", on);
		return () => window.removeEventListener("leo:thresholds-changed", on);
	}, []);
	return [t, (next) => {
		setThresholds(next);
		setT(next);
	}];
}
function computeReliability(entries = buffer, t = getThresholds()) {
	const window = entries.slice(-t.windowSize);
	if (window.length === 0) return {
		level: "ok",
		failureRatePct: 0,
		slowSamples: 0,
		windowSize: 0,
		reasons: []
	};
	const failures = window.filter((e) => e.status !== "online").length;
	const slow = window.filter((e) => (e.latencyMs ?? 0) > t.latencyWarnMs).length;
	const failureRatePct = Math.round(failures / window.length * 100);
	const reasons = [];
	let level = "ok";
	if (failureRatePct >= t.failureRatePct) {
		level = "critical";
		reasons.push(`Failure rate ${failureRatePct}% ≥ ${t.failureRatePct}%`);
	}
	if (slow >= Math.ceil(window.length / 2)) {
		if (level !== "critical") level = "warn";
		reasons.push(`${slow}/${window.length} samples over ${t.latencyWarnMs}ms`);
	}
	return {
		level,
		failureRatePct,
		slowSamples: slow,
		windowSize: window.length,
		reasons
	};
}
var DEFAULT_POLLING = {
	healthMs: 15e3,
	metricsMs: 3e3
};
function getPollingIntervals() {
	if (typeof window === "undefined") return DEFAULT_POLLING;
	try {
		const raw = window.localStorage.getItem(POLLING_KEY);
		if (!raw) return DEFAULT_POLLING;
		return {
			...DEFAULT_POLLING,
			...JSON.parse(raw)
		};
	} catch {
		return DEFAULT_POLLING;
	}
}
function setPollingIntervals(p) {
	if (typeof window === "undefined") return;
	window.localStorage.setItem(POLLING_KEY, JSON.stringify(p));
	window.dispatchEvent(new CustomEvent("leo:polling-changed"));
}
function usePollingIntervals() {
	const [p, setP] = (0, import_react.useState)(() => getPollingIntervals());
	(0, import_react.useEffect)(() => {
		const on = () => setP(getPollingIntervals());
		window.addEventListener("leo:polling-changed", on);
		return () => window.removeEventListener("leo:polling-changed", on);
	}, []);
	return [p, (next) => {
		setPollingIntervals(next);
		setP(next);
	}];
}
function getDiagnosticsMeta() {
	return {
		exportedAt: (/* @__PURE__ */ new Date()).toISOString(),
		apiBase: getApiBase(),
		envApiBase: null,
		polling: getPollingIntervals(),
		thresholds: getThresholds(),
		userAgent: typeof navigator !== "undefined" ? navigator.userAgent : void 0
	};
}
function getDiagnosticsSnapshot(count = 20) {
	const entries = buffer.slice(-count);
	return {
		meta: getDiagnosticsMeta(),
		reliability: computeReliability(entries),
		latest: entries[entries.length - 1] ?? null,
		entries
	};
}
function exportHealthJson(count = 20) {
	return JSON.stringify(getDiagnosticsSnapshot(count), null, 2);
}
function exportHealthCsv(count = 20) {
	const rows = buffer.slice(-count);
	const meta = getDiagnosticsMeta();
	const header = [
		"timestamp",
		"status",
		"http_status",
		"latency_ms",
		"url",
		"message",
		"body_excerpt"
	];
	const esc = (v) => {
		const s = v == null ? "" : String(v);
		return /[",\n]/.test(s) ? `"${s.replace(/"/g, "\"\"")}"` : s;
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
		`# threshold_window_size=${meta.thresholds.windowSize}`
	];
	const lines = rows.map((r) => [
		r.checkedAt ? new Date(r.checkedAt).toISOString() : "",
		r.status,
		r.httpStatus ?? "",
		r.latencyMs ?? "",
		r.url,
		r.message ?? "",
		r.bodyExcerpt ?? ""
	].map(esc).join(","));
	return [
		...metaLines,
		header.join(","),
		...lines
	].join("\n");
}
var HEALTH_PATH = "/health";
var TIMEOUT_MS = 5e3;
function buildHealthUrl(base = getApiBase()) {
	return `${base.replace(/\/+$/, "")}${HEALTH_PATH}`;
}
function validateHealthPayload(raw) {
	const issues = [];
	if (typeof raw !== "object" || raw === null) return [{
		field: "(root)",
		message: "Response is not a JSON object"
	}];
	const obj = raw;
	if (!("status" in obj)) issues.push({
		field: "status",
		message: "Missing required field"
	});
	else if (typeof obj.status !== "string") issues.push({
		field: "status",
		message: `Expected string, got ${typeof obj.status}`
	});
	else if (![
		"ok",
		"healthy",
		"up"
	].includes(obj.status.toLowerCase())) issues.push({
		field: "status",
		message: `Unexpected value "${obj.status}"`
	});
	if ("version" in obj && typeof obj.version !== "string") issues.push({
		field: "version",
		message: `Expected string, got ${typeof obj.version}`
	});
	if ("uptime_s" in obj && typeof obj.uptime_s !== "number") issues.push({
		field: "uptime_s",
		message: `Expected number, got ${typeof obj.uptime_s}`
	});
	return issues;
}
async function checkBackendHealth(base = getApiBase()) {
	const url = buildHealthUrl(base);
	const started = performance.now();
	const controller = new AbortController();
	const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);
	try {
		const res = await fetch(url, {
			method: "GET",
			signal: controller.signal,
			headers: { Accept: "application/json" }
		});
		const latencyMs = Math.round(performance.now() - started);
		const text = await res.text().catch(() => "");
		const bodyExcerpt = text.length > 240 ? `${text.slice(0, 240)}…` : text;
		let schemaIssues;
		if (res.ok) try {
			schemaIssues = validateHealthPayload(JSON.parse(text));
		} catch {
			schemaIssues = [{
				field: "(root)",
				message: "Response is not valid JSON"
			}];
		}
		if (res.ok) return {
			status: "online",
			url,
			latencyMs,
			httpStatus: res.status,
			checkedAt: Date.now(),
			bodyExcerpt,
			schemaIssues
		};
		return {
			status: "error",
			url,
			latencyMs,
			httpStatus: res.status,
			message: `HTTP ${res.status}`,
			checkedAt: Date.now(),
			bodyExcerpt,
			failureKind: "http",
			hints: res.status === 404 ? [`The backend returned 404. Confirm it exposes GET /health at ${url}.`] : res.status >= 500 ? ["The backend crashed handling /health. Check server logs for the traceback."] : res.status === 401 || res.status === 403 ? ["/health should be public. Remove auth middleware for this route."] : void 0
		};
	} catch (err) {
		const latencyMs = Math.round(performance.now() - started);
		return {
			...classifyFetchError(err, url),
			latencyMs,
			checkedAt: Date.now()
		};
	} finally {
		clearTimeout(timer);
	}
}
/** Classify a fetch()-thrown error into a user-actionable HealthResult.
*  The browser deliberately hides CORS/network distinctions from JS for
*  security reasons — the error is always a generic TypeError("Failed to
*  fetch"). We infer the likely cause from context (page origin vs URL
*  scheme/host) and surface concrete remediation hints. */
function classifyFetchError(err, url) {
	const base = {
		status: "unreachable",
		url
	};
	if (err instanceof DOMException && err.name === "AbortError") return {
		...base,
		failureKind: "timeout",
		errorName: "AbortError",
		message: `Timed out after ${TIMEOUT_MS}ms — the backend didn't respond in time.`,
		hints: ["Confirm the backend process is running and listening on the port in the URL.", "If you're behind a tunnel, verify the tunnel is still active."]
	};
	const raw = err instanceof Error ? err.message : String(err);
	const name = err instanceof Error ? err.name : void 0;
	if (typeof window !== "undefined" && window.location.protocol === "https:" && url.startsWith("http://") && !/^http:\/\/(localhost|127\.0\.0\.1)/i.test(url)) return {
		...base,
		failureKind: "mixed-content",
		errorName: name,
		message: "Browser blocked the request: the page is HTTPS but the backend URL is HTTP.",
		hints: ["Serve the backend over HTTPS (deploy it, or expose it via a tunnel like Cloudflare/ngrok).", "Or open the frontend over HTTP for local testing."]
	};
	if (typeof window !== "undefined" && /^http:\/\/(localhost|127\.0\.0\.1)/i.test(url) && !/^(localhost|127\.0\.0\.1)/i.test(window.location.hostname)) return {
		...base,
		failureKind: "network",
		errorName: name,
		message: "This browser tab isn't on your laptop — it can't reach http://localhost.",
		hints: ["Expose your backend with a tunnel: `cloudflared tunnel --url http://localhost:8005`", "Then paste the public https://…trycloudflare.com URL into Settings."]
	};
	if (name === "TypeError" || /failed to fetch|networkerror/i.test(raw)) {
		const origin = typeof window !== "undefined" ? window.location.origin : "<frontend-origin>";
		return {
			...base,
			failureKind: "cors",
			errorName: name,
			message: `Fetch failed. Most likely CORS is blocking the request from ${origin}.`,
			hints: [
				`Add CORS headers on the backend so ${origin} is allowed. FastAPI:`,
				`  app.add_middleware(CORSMiddleware, allow_origins=["${origin}"], allow_methods=["*"], allow_headers=["*"])`,
				"Required response headers: Access-Control-Allow-Origin, Access-Control-Allow-Methods, Access-Control-Allow-Headers.",
				"The backend must also answer OPTIONS /health with 204 and the same headers.",
				"If it isn't CORS, the host/port may be wrong or the process isn't running."
			]
		};
	}
	return {
		...base,
		failureKind: "network",
		errorName: name,
		message: raw || "Network error"
	};
}
function useBackendHealth(intervalMs = 15e3) {
	const [result, setResult] = (0, import_react.useState)({
		status: "checking",
		url: buildHealthUrl()
	});
	const mounted = (0, import_react.useRef)(true);
	async function run() {
		if (!mounted.current) return;
		setResult((r) => ({
			...r,
			status: "checking",
			url: buildHealthUrl()
		}));
		const r = await checkBackendHealth();
		if (mounted.current) setResult(r);
		pushHealthEntry(r);
	}
	(0, import_react.useEffect)(() => {
		mounted.current = true;
		run();
		const id = intervalMs > 0 ? setInterval(run, intervalMs) : null;
		const onFocus = () => run();
		window.addEventListener("focus", onFocus);
		window.addEventListener("leo:api-base-changed", onFocus);
		return () => {
			mounted.current = false;
			if (id) clearInterval(id);
			window.removeEventListener("focus", onFocus);
			window.removeEventListener("leo:api-base-changed", onFocus);
		};
	}, [intervalMs]);
	return {
		...result,
		refresh: run
	};
}
var SOURCE_LABEL = {
	settings: "Settings override (localStorage)",
	env: "Environment variable (VITE_LEO_API_BASE_URL)",
	default: "Built-in default"
};
function formatAgo(ts) {
	if (!ts) return "never";
	const s = Math.round((Date.now() - ts) / 1e3);
	if (s < 5) return "just now";
	if (s < 60) return `${s}s ago`;
	if (s < 3600) return `${Math.round(s / 60)}m ago`;
	return `${Math.round(s / 3600)}h ago`;
}
function isLocalhostUrl(u) {
	return /^https?:\/\/(localhost|127\.0\.0\.1)(:\d+)?/i.test(u.trim());
}
function BackendHealthPanel() {
	const [polling] = usePollingIntervals();
	const h = useBackendHealth(polling.healthMs);
	const [base, setBase] = (0, import_react.useState)("");
	const [source, setSource] = (0, import_react.useState)("default");
	const [envUrl, setEnvUrl] = (0, import_react.useState)();
	const [lastSuccess, setLastSuccess] = (0, import_react.useState)(null);
	const [, force] = (0, import_react.useState)(0);
	(0, import_react.useEffect)(() => {
		const id = setInterval(() => force((x) => x + 1), 15e3);
		return () => clearInterval(id);
	}, []);
	(0, import_react.useEffect)(() => {
		setBase(getApiBase());
		setSource(getApiBaseSource());
		setEnvUrl(/* @__PURE__ */ getEnvApiBase());
		const onChange = () => {
			setBase(getApiBase());
			setSource(getApiBaseSource());
		};
		window.addEventListener("leo:api-base-changed", onChange);
		return () => window.removeEventListener("leo:api-base-changed", onChange);
	}, []);
	(0, import_react.useEffect)(() => {
		if (h.status === "online") setLastSuccess({
			at: h.checkedAt ?? Date.now(),
			latencyMs: h.latencyMs
		});
	}, [
		h.status,
		h.checkedAt,
		h.latencyMs
	]);
	function onReset() {
		resetApiBase();
		toast.success(envUrl ? `Reset — now using env var: ${envUrl}` : "Reset — using built-in default (http://localhost:8000)");
	}
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "space-y-6",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(StatusBlock, {
				health: h,
				lastSuccess
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(SourceBlock, {
				base,
				source,
				envUrl,
				onReset
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(UrlHelper, { onSaved: (u) => setBase(u) })
		]
	});
}
function StatusBlock({ health, lastSuccess }) {
	const dot = health.status === "online" ? "bg-leo" : health.status === "checking" ? "bg-yellow-400 animate-pulse" : health.status === "unreachable" ? "bg-red-500" : "bg-orange-400";
	const label = health.status === "online" ? "Online" : health.status === "checking" ? "Checking…" : health.status === "unreachable" ? "Unreachable" : "Error";
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "border border-border bg-background/60 p-4",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex flex-wrap items-center gap-3",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
						className: `inline-block h-2.5 w-2.5 rounded-full ${dot}`,
						"aria-hidden": true
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
						className: "font-semibold",
						role: "status",
						"aria-live": "polite",
						children: ["Backend ", label]
					}),
					health.latencyMs != null && health.status === "online" && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
						className: "text-xs text-muted-foreground",
						children: [
							"· ",
							health.latencyMs,
							"ms"
						]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
						type: "button",
						onClick: health.refresh,
						className: "ml-auto border border-border px-3 py-1 text-xs font-semibold hover:border-leo hover:text-leo focus:outline-none focus-visible:ring-2 focus-visible:ring-leo",
						children: "Re-check now"
					})
				]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("dl", {
				className: "mt-4 grid gap-x-6 gap-y-2 text-xs sm:grid-cols-[max-content_1fr]",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("dt", {
						className: "text-muted-foreground",
						children: "Request URL"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("dd", {
						className: "font-mono break-all",
						children: health.url
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("dt", {
						className: "text-muted-foreground",
						children: "Last success"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("dd", { children: lastSuccess ? `${formatAgo(lastSuccess.at)} (${lastSuccess.latencyMs ?? "?"}ms)` : "no successful check yet" }),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("dt", {
						className: "text-muted-foreground",
						children: "Last check"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("dd", { children: health.checkedAt ? formatAgo(health.checkedAt) : "—" }),
					health.httpStatus != null && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(import_jsx_runtime.Fragment, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("dt", {
						className: "text-muted-foreground",
						children: "HTTP status"
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("dd", { children: health.httpStatus })] })
				]
			}),
			health.status !== "online" && health.status !== "checking" && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mt-4 border-l-2 border-red-500 bg-red-500/5 p-3",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
						className: "text-xs font-semibold text-red-400",
						children: [health.failureKind ? `${health.failureKind.toUpperCase()} — ` : "", health.message ?? "Unknown error"]
					}),
					health.errorName && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "mt-1 font-mono text-[11px] text-muted-foreground",
						children: health.errorName
					}),
					health.hints && health.hints.length > 0 && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("ul", {
						className: "mt-3 space-y-1 text-xs text-muted-foreground",
						children: health.hints.map((hint, i) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", {
							className: "flex gap-2",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
								className: "text-leo",
								"aria-hidden": true,
								children: "→"
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("code", {
								className: "whitespace-pre-wrap break-words font-mono text-[11px]",
								children: hint
							})]
						}, i))
					}),
					health.bodyExcerpt && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("details", {
						className: "mt-3 text-xs",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("summary", {
							className: "cursor-pointer text-muted-foreground",
							children: "Response body"
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("pre", {
							className: "mt-2 overflow-x-auto bg-input p-2 font-mono text-[11px]",
							children: health.bodyExcerpt
						})]
					})
				]
			})
		]
	});
}
function SourceBlock({ base, source, envUrl, onReset }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "border border-border p-4",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "eyebrow",
				children: "Effective API base URL"
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("code", {
				className: "mt-2 block break-all font-mono text-sm",
				children: base || "—"
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
				className: "mt-2 text-xs text-muted-foreground",
				children: ["Source: ", /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
					className: "font-semibold text-foreground",
					children: SOURCE_LABEL[source]
				})]
			}),
			source === "settings" && envUrl && envUrl !== base && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
				className: "mt-1 text-xs text-orange-400",
				children: [
					"⚠ A Settings override is active. It shadows your env var",
					" ",
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("code", {
						className: "font-mono",
						children: envUrl
					}),
					"."
				]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
				type: "button",
				onClick: onReset,
				disabled: source !== "settings",
				className: "mt-3 border border-border px-4 py-2 text-xs font-semibold hover:border-leo hover:text-leo disabled:opacity-40 disabled:hover:border-border disabled:hover:text-foreground focus:outline-none focus-visible:ring-2 focus-visible:ring-leo",
				children: "Reset to defaults"
			}),
			source !== "settings" && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "mt-2 text-[11px] text-muted-foreground",
				children: "Nothing to reset — no Settings override is active."
			})
		]
	});
}
function UrlHelper({ onSaved }) {
	const [url, setUrl] = (0, import_react.useState)("");
	const [validating, setValidating] = (0, import_react.useState)(false);
	const [result, setResult] = (0, import_react.useState)(null);
	const abortRef = (0, import_react.useRef)(null);
	const isLocal = (0, import_react.useMemo)(() => url.trim() ? isLocalhostUrl(url) : false, [url]);
	const pageOnHttps = typeof window !== "undefined" && window.location.protocol === "https:";
	async function validate() {
		if (!url.trim()) {
			toast.error("Paste a URL first.");
			return;
		}
		abortRef.current?.abort();
		abortRef.current = new AbortController();
		setValidating(true);
		setResult(null);
		try {
			const r = await checkBackendHealth(url.trim());
			setResult(r);
			if (r.status === "online") toast.success(`Reachable (${r.latencyMs}ms)`);
			else toast.error(r.message ?? "Unreachable");
		} finally {
			setValidating(false);
		}
	}
	function save() {
		if (!url.trim()) return;
		setApiBase(url.trim());
		onSaved(url.trim());
		toast.success("API base saved.");
	}
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "border border-border p-4",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "eyebrow",
				children: "Paste & validate a backend URL"
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
				className: "mt-2 text-xs text-muted-foreground",
				children: [
					"Try a URL before committing to it. Health-check runs against",
					" ",
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("code", {
						className: "font-mono",
						children: "<url>/health"
					}),
					"."
				]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mt-3 flex flex-col gap-2 sm:flex-row",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("input", {
						value: url,
						onChange: (e) => setUrl(e.target.value),
						placeholder: "https://xxxx.trycloudflare.com",
						"aria-label": "Backend URL to validate",
						className: "flex-1 bg-input px-3 py-2 font-mono text-sm outline-none focus:ring-1 focus:ring-leo"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
						type: "button",
						onClick: validate,
						disabled: validating || !url.trim(),
						className: "border border-border px-4 py-2 text-xs font-semibold hover:border-leo hover:text-leo disabled:opacity-40 focus:outline-none focus-visible:ring-2 focus-visible:ring-leo",
						children: validating ? "Checking…" : "Validate"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
						type: "button",
						onClick: save,
						disabled: !url.trim() || result?.status !== "online",
						className: "bg-leo px-4 py-2 text-xs font-semibold text-leo-foreground disabled:opacity-40 focus:outline-none focus-visible:ring-2 focus-visible:ring-white",
						children: "Save as API base"
					})
				]
			}),
			isLocal && pageOnHttps && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mt-3 border-l-2 border-orange-400 bg-orange-400/5 p-3 text-xs",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "font-semibold text-orange-400",
						children: "You pasted a localhost URL."
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
						className: "mt-1 text-muted-foreground",
						children: [
							"This browser tab isn't running on your laptop, so ",
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("code", { children: "localhost" }),
							" can't resolve. Expose the backend with a tunnel and use its public https URL:"
						]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("pre", {
						className: "mt-2 overflow-x-auto bg-input p-2 font-mono text-[11px]",
						children: `cloudflared tunnel --url http://localhost:8005
# or
ngrok http 8005`
					})
				]
			}),
			result && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mt-3 text-xs",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", { children: [
						"Result:",
						" ",
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: result.status === "online" ? "font-semibold text-leo" : "font-semibold text-red-400",
							children: result.status
						}),
						result.httpStatus ? ` · HTTP ${result.httpStatus}` : "",
						result.latencyMs != null ? ` · ${result.latencyMs}ms` : ""
					] }),
					result.status !== "online" && result.message && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "mt-1 text-red-400",
						children: result.message
					}),
					result.hints && result.hints.length > 0 && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("ul", {
						className: "mt-2 space-y-1 text-muted-foreground",
						children: result.hints.map((h, i) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", {
							className: "flex gap-2",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
								className: "text-leo",
								"aria-hidden": true,
								children: "→"
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("code", {
								className: "whitespace-pre-wrap break-words font-mono text-[11px]",
								children: h
							})]
						}, i))
					})
				]
			})
		]
	});
}
var DEFAULT_SSE_CONFIG = {
	maxAttempts: 5,
	initialBackoffMs: 500,
	maxBackoffMs: 15e3
};
var KEY = "leo.sse.reconnect_v1";
var EVENT = "leo:sse-config-changed";
function clamp(n, lo, hi) {
	return Math.max(lo, Math.min(hi, n));
}
function sanitize(raw) {
	const cfg = {
		...DEFAULT_SSE_CONFIG,
		...raw
	};
	cfg.maxAttempts = clamp(Math.round(cfg.maxAttempts), 0, 50);
	cfg.initialBackoffMs = clamp(Math.round(cfg.initialBackoffMs), 100, 6e4);
	cfg.maxBackoffMs = clamp(Math.round(cfg.maxBackoffMs), cfg.initialBackoffMs, 3e5);
	return cfg;
}
function getSseConfig() {
	if (typeof window === "undefined") return { ...DEFAULT_SSE_CONFIG };
	try {
		const raw = window.localStorage.getItem(KEY);
		if (!raw) return { ...DEFAULT_SSE_CONFIG };
		return sanitize(JSON.parse(raw));
	} catch {
		return { ...DEFAULT_SSE_CONFIG };
	}
}
function setSseConfig(cfg) {
	if (typeof window === "undefined") return;
	const next = sanitize({
		...getSseConfig(),
		...cfg
	});
	window.localStorage.setItem(KEY, JSON.stringify(next));
	window.dispatchEvent(new CustomEvent(EVENT, { detail: next }));
}
function useSseConfig() {
	const [cfg, setCfg] = (0, import_react.useState)(() => getSseConfig());
	(0, import_react.useEffect)(() => {
		const handler = () => setCfg(getSseConfig());
		window.addEventListener(EVENT, handler);
		window.addEventListener("storage", handler);
		return () => {
			window.removeEventListener(EVENT, handler);
			window.removeEventListener("storage", handler);
		};
	}, []);
	return [cfg, setSseConfig];
}
//#endregion
export { useThresholds as C, useSseConfig as S, setSseConfig as _, checkBackendHealth as a, useHealthHistory as b, exportHealthCsv as c, getDiagnosticsSnapshot as d, getHealthHistory as f, pushHealthEntry as g, importHealthEntries as h, buildHealthUrl as i, exportHealthJson as l, getThresholds as m, DEFAULT_SSE_CONFIG as n, clearHealthHistory as o, getSseConfig as p, DEFAULT_THRESHOLDS as r, computeReliability as s, BackendHealthPanel as t, getDiagnosticsMeta as u, setThresholds as v, usePollingIntervals as x, useBackendHealth as y };
