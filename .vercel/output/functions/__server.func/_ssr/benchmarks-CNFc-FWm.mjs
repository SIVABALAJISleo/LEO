import { o as __toESM } from "../_runtime.mjs";
import { i as require_react, r as require_jsx_runtime, t as useQuery } from "../_libs/react+tanstack__react-query.mjs";
import { g as Link, v as useNavigate } from "../_libs/@tanstack/react-router+[...].mjs";
import { n as toast } from "../_libs/sonner.mjs";
import { a as getEnvApiBase, c as leoJson, n as getApiBase, o as getToken, r as getApiBaseSource, s as leoFetch } from "./leo-client-D7U1wpIv.mjs";
import { C as useThresholds, _ as setSseConfig, b as useHealthHistory, c as exportHealthCsv, d as getDiagnosticsSnapshot, f as getHealthHistory, g as pushHealthEntry, h as importHealthEntries, i as buildHealthUrl, l as exportHealthJson, m as getThresholds, n as DEFAULT_SSE_CONFIG, o as clearHealthHistory, p as getSseConfig, r as DEFAULT_THRESHOLDS$1, s as computeReliability, t as BackendHealthPanel, u as getDiagnosticsMeta, v as setThresholds, x as usePollingIntervals, y as useBackendHealth } from "./sse-config-DZ3wmwiX.mjs";
import { t as toPng } from "../_libs/html-to-image.mjs";
import { t as require_jspdf_node_min } from "../_libs/jspdf.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/benchmarks-CNFc-FWm.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
var import_jspdf_node_min = /* @__PURE__ */ __toESM(require_jspdf_node_min());
var DOT = {
	checking: "bg-yellow-400 animate-pulse",
	online: "bg-leo",
	unreachable: "bg-red-500",
	error: "bg-orange-400"
};
var LABEL = {
	checking: "Checking…",
	online: "Backend online",
	unreachable: "Backend unreachable",
	error: "Backend error"
};
function BackendStatusBadge({ compact = false }) {
	const [polling] = usePollingIntervals();
	const h = useBackendHealth(polling.healthMs);
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		role: "status",
		"aria-live": "polite",
		title: `${LABEL[h.status]} — ${h.url}${h.message ? ` (${h.message})` : ""}${h.latencyMs != null ? ` · ${h.latencyMs}ms` : ""}`,
		className: "inline-flex items-center gap-2 border border-border bg-background/60 px-3 py-1.5 text-xs font-medium",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
				className: `inline-block h-2 w-2 rounded-full ${DOT[h.status]}`,
				"aria-hidden": true
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { children: LABEL[h.status] }),
			!compact && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(import_jsx_runtime.Fragment, { children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
					className: "text-muted-foreground",
					children: "·"
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("code", {
					className: "max-w-[280px] truncate font-mono text-[11px] text-muted-foreground",
					"aria-label": "Request URL",
					children: h.url
				}),
				h.latencyMs != null && h.status === "online" && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
					className: "text-muted-foreground",
					children: [
						"· ",
						h.latencyMs,
						"ms"
					]
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
					type: "button",
					onClick: h.refresh,
					className: "ml-1 border border-border px-2 py-0.5 text-[11px] hover:border-leo hover:text-leo focus:outline-none focus-visible:ring-2 focus-visible:ring-leo",
					"aria-label": "Re-check backend health",
					children: "Retry"
				})
			] }),
			h.status !== "online" && h.status !== "checking" && h.message && !compact && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
				className: "ml-2 text-red-400",
				role: "alert",
				children: h.message
			})
		]
	});
}
function CurlBlock({ label, path, extra = "" }) {
	const [open, setOpen] = (0, import_react.useState)(false);
	const cmd = `curl -sS ${extra} -w '\\nHTTP %{http_code} · %{time_total}s\\n' -o - '${path === "/health" ? buildHealthUrl() : `${getApiBase().replace(/\/+$/, "")}${path}`}'`.replace(/\s+/g, " ").trim();
	async function copy() {
		try {
			await navigator.clipboard.writeText(cmd);
			toast.success("curl command copied to clipboard");
		} catch {
			toast.error("Clipboard blocked — select and copy manually");
		}
	}
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "inline-flex flex-col items-start gap-2",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
			type: "button",
			onClick: () => setOpen((v) => !v),
			className: "border border-border px-3 py-1.5 text-xs font-medium hover:border-leo hover:text-leo focus:outline-none focus-visible:ring-2 focus-visible:ring-leo",
			"aria-expanded": open,
			children: open ? `Hide curl (${label})` : `Generate curl for ${label}`
		}), open && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "w-full max-w-2xl border border-border bg-background/80 p-3",
			children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "mb-2 text-[11px] text-muted-foreground",
					children: "Run this from your laptop or tunnel host to test the exact URL the frontend calls:"
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("pre", {
					className: "overflow-auto whitespace-pre-wrap break-all rounded bg-black/40 p-3 font-mono text-[11px] text-leo",
					children: cmd
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "mt-2 flex gap-2",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
						type: "button",
						onClick: copy,
						className: "border border-border px-3 py-1 text-[11px] hover:border-leo hover:text-leo",
						children: "Copy"
					})
				})
			]
		})]
	});
}
function CurlHealthButton() {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CurlBlock, {
		label: "/health",
		path: "/health"
	});
}
function CurlMetricsButton() {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CurlBlock, {
		label: "/api/v1/leo/metrics",
		path: "/api/v1/leo/metrics",
		extra: "-H 'Accept: application/json'"
	});
}
function LatencyChart({ width = 560, height = 120 }) {
	const points = useHealthHistory().filter((h) => typeof h.latencyMs === "number");
	const pad = 8;
	const w = width;
	const h = height;
	const max = Math.max(50, ...points.map((p) => p.latencyMs ?? 0));
	const min = 0;
	const stepX = points.length > 1 ? (w - pad * 2) / (points.length - 1) : 0;
	const y = (v) => h - pad - (v - min) / Math.max(1, max - min) * (h - pad * 2);
	const path = points.map((p, i) => `${i === 0 ? "M" : "L"} ${pad + i * stepX} ${y(p.latencyMs ?? 0)}`).join(" ");
	const last = points[points.length - 1];
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "border border-border bg-background/60 p-4",
		role: "img",
		"aria-label": `Backend latency over last ${points.length} health checks`,
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "mb-2 flex items-baseline justify-between",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "eyebrow",
				children: "Live /health latency"
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "font-mono text-xs text-muted-foreground",
				children: [
					points.length,
					"/60 samples · max ",
					max,
					"ms",
					last?.latencyMs != null ? ` · last ${last.latencyMs}ms` : ""
				]
			})]
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("svg", {
			viewBox: `0 0 ${w} ${h}`,
			width: "100%",
			height: h,
			preserveAspectRatio: "none",
			className: "block",
			children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("line", {
					x1: pad,
					x2: w - pad,
					y1: h - pad,
					y2: h - pad,
					stroke: "currentColor",
					strokeOpacity: .15
				}),
				points.length > 0 && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(import_jsx_runtime.Fragment, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("path", {
					d: path,
					fill: "none",
					stroke: "#76B900",
					strokeWidth: 1.5
				}), points.map((p, i) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("circle", {
					cx: pad + i * stepX,
					cy: y(p.latencyMs ?? 0),
					r: 2,
					fill: p.status === "online" ? "#76B900" : p.status === "error" ? "#fb923c" : "#ef4444",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("title", { children: `${p.latencyMs}ms · ${p.status}${p.httpStatus ? ` · ${p.httpStatus}` : ""}` })
				}, p.id))] }),
				points.length === 0 && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("text", {
					x: w / 2,
					y: h / 2,
					textAnchor: "middle",
					className: "fill-muted-foreground",
					fontSize: "12",
					children: "Waiting for first /health sample…"
				})
			]
		})]
	});
}
var STATUS_COLOR = {
	online: "text-leo",
	error: "text-orange-400",
	unreachable: "text-red-400",
	checking: "text-muted-foreground"
};
function download(filename, content, mime) {
	const blob = new Blob([content], { type: mime });
	const url = URL.createObjectURL(blob);
	const a = document.createElement("a");
	a.href = url;
	a.download = filename;
	a.click();
	setTimeout(() => URL.revokeObjectURL(url), 1e3);
	toast.success(`Exported ${filename}`);
}
function DiagnosticsPanel() {
	const history = useHealthHistory();
	const rows = history.slice(-20).reverse();
	const [t, setT] = useThresholds();
	const report = computeReliability(history, t);
	const schemaIssues = history[history.length - 1]?.schemaIssues ?? [];
	const alertClass = report.level === "critical" ? "border-red-500 bg-red-500/10 text-red-300" : report.level === "warn" ? "border-orange-400 bg-orange-400/10 text-orange-200" : "border-border bg-background/60 text-muted-foreground";
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
		className: "border border-border bg-background/60",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("header", {
				className: "flex flex-wrap items-center justify-between gap-2 border-b border-border px-4 py-3",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "eyebrow",
					children: "Diagnostics"
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "text-xs text-muted-foreground",
					children: [
						"Last ",
						rows.length,
						" backend health checks · persisted locally"
					]
				})] }), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "flex flex-wrap gap-2",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
							type: "button",
							onClick: () => download(`leo-health-${Date.now()}.json`, exportHealthJson(20), "application/json"),
							className: "border border-border px-2 py-1 text-[11px] hover:border-leo hover:text-leo",
							children: "Export JSON"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
							type: "button",
							onClick: () => download(`leo-health-${Date.now()}.csv`, exportHealthCsv(20), "text/csv"),
							className: "border border-border px-2 py-1 text-[11px] hover:border-leo hover:text-leo",
							children: "Export CSV"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
							type: "button",
							onClick: async () => {
								const json = JSON.stringify(getDiagnosticsSnapshot(20), null, 2);
								try {
									await navigator.clipboard.writeText(json);
									toast.success("Diagnostics snapshot copied to clipboard");
								} catch {
									toast.error("Clipboard blocked — export JSON instead");
								}
							},
							className: "border border-border px-2 py-1 text-[11px] hover:border-leo hover:text-leo",
							children: "Copy snapshot"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
							type: "button",
							onClick: () => {
								if (confirm("Clear all persisted health samples?")) clearHealthHistory();
							},
							className: "border border-border px-2 py-1 text-[11px] text-muted-foreground hover:border-red-500 hover:text-red-400",
							children: "Clear"
						})
					]
				})]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: `border-b border-border px-4 py-3 text-xs ${alertClass}`,
				role: report.level === "critical" ? "alert" : "status",
				"aria-live": "polite",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "flex flex-wrap items-baseline justify-between gap-2",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("strong", {
						className: "uppercase tracking-wide",
						children: ["Reliability: ", report.level]
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
						className: "font-mono",
						children: [
							"failure ",
							report.failureRatePct,
							"% · slow ",
							report.slowSamples,
							"/",
							report.windowSize
						]
					})]
				}), report.reasons.length > 0 && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("ul", {
					className: "mt-1 list-inside list-disc",
					children: report.reasons.map((r) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("li", { children: r }, r))
				})]
			}),
			schemaIssues.length > 0 && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "border-b border-border bg-orange-400/10 px-4 py-3 text-xs text-orange-200",
				role: "alert",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("strong", { children: "/health schema warnings" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("ul", {
					className: "mt-1 list-inside list-disc",
					children: schemaIssues.map((s) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", { children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "font-mono",
							children: s.field
						}),
						": ",
						s.message
					] }, s.field))
				})]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("details", {
				className: "border-b border-border px-4 py-3 text-xs",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("summary", {
					className: "cursor-pointer text-muted-foreground",
					children: "Thresholds"
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "mt-3 grid grid-cols-2 gap-3",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(NumField, {
							label: "Latency warn (ms)",
							value: t.latencyWarnMs,
							onChange: (v) => setT({
								...t,
								latencyWarnMs: v
							})
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(NumField, {
							label: "Timeout (ms)",
							value: t.timeoutMs,
							onChange: (v) => setT({
								...t,
								timeoutMs: v
							})
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(NumField, {
							label: "Failure rate (%)",
							value: t.failureRatePct,
							onChange: (v) => setT({
								...t,
								failureRatePct: v
							})
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(NumField, {
							label: "Window size",
							value: t.windowSize,
							onChange: (v) => setT({
								...t,
								windowSize: v
							})
						})
					]
				})]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "max-h-[360px] overflow-auto",
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("table", {
					className: "w-full border-collapse text-xs",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("thead", {
						className: "sticky top-0 bg-background/95 text-left text-muted-foreground",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("tr", { children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("th", {
								className: "px-4 py-2 font-medium",
								children: "Time"
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("th", {
								className: "px-4 py-2 font-medium",
								children: "Status"
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("th", {
								className: "px-4 py-2 font-medium",
								children: "HTTP"
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("th", {
								className: "px-4 py-2 font-medium",
								children: "Latency"
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("th", {
								className: "px-4 py-2 font-medium",
								children: "Payload / message"
							})
						] })
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("tbody", { children: [rows.length === 0 && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("tr", { children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
						colSpan: 5,
						className: "px-4 py-6 text-center text-muted-foreground",
						children: "No health checks recorded yet."
					}) }), rows.map((r) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("tr", {
						className: "border-t border-border/60 align-top",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
								className: "whitespace-nowrap px-4 py-2 font-mono",
								children: r.checkedAt ? new Date(r.checkedAt).toLocaleTimeString() : "—"
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
								className: `px-4 py-2 font-medium ${STATUS_COLOR[r.status] ?? ""}`,
								children: r.status
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
								className: "px-4 py-2 font-mono",
								children: r.httpStatus ?? "—"
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
								className: "px-4 py-2 font-mono",
								children: r.latencyMs != null ? `${r.latencyMs}ms` : "—"
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
								className: "px-4 py-2 font-mono text-muted-foreground",
								children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
									className: "max-w-[520px] truncate",
									title: r.bodyExcerpt ?? r.message ?? "",
									children: r.bodyExcerpt ?? r.message ?? "—"
								})
							})
						]
					}, r.id))] })]
				})
			})
		]
	});
}
function NumField({ label, value, onChange }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("label", {
		className: "flex flex-col gap-1",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
			className: "text-[11px] text-muted-foreground",
			children: label
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("input", {
			type: "number",
			min: 0,
			value,
			onChange: (e) => onChange(Number(e.target.value) || 0),
			className: "border border-border bg-background px-2 py-1 font-mono text-xs focus:border-leo focus:outline-none"
		})]
	});
}
function formatHuman(iso) {
	try {
		const d = new Date(iso);
		const diff = Date.now() - d.getTime();
		const s = Math.round(diff / 1e3);
		const rel = s < 5 ? "just now" : s < 60 ? `${s}s ago` : s < 3600 ? `${Math.round(s / 60)}m ago` : s < 86400 ? `${Math.round(s / 3600)}h ago` : `${Math.round(s / 86400)}d ago`;
		return `${d.toLocaleString()} · ${rel}`;
	} catch {
		return iso;
	}
}
var HISTORY_KEY = "leo.diagnostics_history_v1";
var MAX_HISTORY = 10;
var REFRESH_OPTIONS = [
	0,
	2e3,
	5e3,
	1e4,
	3e4
];
function loadHistory() {
	if (typeof window === "undefined") return [];
	try {
		const raw = window.localStorage.getItem(HISTORY_KEY);
		if (!raw) return [];
		const p = JSON.parse(raw);
		return Array.isArray(p) ? p.slice(-10) : [];
	} catch {
		return [];
	}
}
function saveHistory(h) {
	try {
		window.localStorage.setItem(HISTORY_KEY, JSON.stringify(h.slice(-10)));
	} catch {}
}
async function probeDiagnostics(source, refreshMs) {
	const url = `${getApiBase()}/api/v1/leo/diagnostics`;
	const started = performance.now();
	const token = getToken();
	const headers = { Accept: "application/json" };
	if (token) headers["Authorization"] = `Bearer ${token}`;
	try {
		const controller = new AbortController();
		const timer = setTimeout(() => controller.abort(), 8e3);
		const res = await fetch(url, {
			headers,
			signal: controller.signal
		});
		clearTimeout(timer);
		const latency = Math.round(performance.now() - started);
		let data = null;
		let err;
		try {
			data = await res.json();
		} catch {
			err = "Invalid JSON response";
		}
		return {
			id: Date.now(),
			at: (/* @__PURE__ */ new Date()).toISOString(),
			ok: res.ok && !err,
			httpStatus: res.status,
			latencyMs: latency,
			data,
			error: !res.ok ? `HTTP ${res.status}` : err,
			source,
			refreshMs
		};
	} catch (e) {
		return {
			id: Date.now(),
			at: (/* @__PURE__ */ new Date()).toISOString(),
			ok: false,
			httpStatus: null,
			latencyMs: Math.round(performance.now() - started),
			data: null,
			error: e instanceof Error ? e.message : "Network error",
			source,
			refreshMs
		};
	}
}
function BackendDiagnosticsPanel() {
	const [history, setHistory] = (0, import_react.useState)(() => loadHistory());
	const [selectedId, setSelectedId] = (0, import_react.useState)(null);
	const [compareId, setCompareId] = (0, import_react.useState)(null);
	const [isFetching, setIsFetching] = (0, import_react.useState)(false);
	const [refreshMs, setRefreshMs] = (0, import_react.useState)(0);
	const timerRef = (0, import_react.useRef)(null);
	const latest = history[history.length - 1] ?? null;
	const selected = history.find((h) => h.id === selectedId) ?? latest;
	const compare = history.find((h) => h.id === compareId) ?? null;
	const prevErrRef = (0, import_react.useRef)(null);
	async function run(source = "manual") {
		setIsFetching(true);
		const entry = await probeDiagnostics(source, refreshMs || void 0);
		setHistory((prev) => {
			const next = [...prev, entry].slice(-10);
			saveHistory(next);
			return next;
		});
		if (refreshMs > 0 && entry.ok) {
			const errSig = entry.data?.last_error ? `${entry.data.last_error.type ?? ""}|${entry.data.last_error.message ?? ""}|${entry.data.last_error.at ?? ""}` : "";
			const prev = prevErrRef.current;
			if (prev !== null && prev !== errSig) if (errSig === "") toast.success("last_error cleared");
			else toast.error(`New backend error: ${entry.data?.last_error?.message ?? entry.data?.last_error?.type ?? "unknown"}`);
			prevErrRef.current = errSig;
		}
		setIsFetching(false);
	}
	(0, import_react.useEffect)(() => {
		if (history.length === 0) run("initial");
	}, []);
	(0, import_react.useEffect)(() => {
		if (timerRef.current) clearInterval(timerRef.current);
		if (refreshMs > 0) timerRef.current = setInterval(() => void run("auto"), refreshMs);
		return () => {
			if (timerRef.current) clearInterval(timerRef.current);
		};
	}, [refreshMs]);
	const copy = async () => {
		try {
			await navigator.clipboard.writeText(JSON.stringify(selected?.data ?? {}, null, 2));
			toast.success("Diagnostics copied");
		} catch {
			toast.error("Clipboard blocked");
		}
	};
	const download = () => {
		if (!selected?.data) {
			toast.error("No diagnostics payload to download");
			return;
		}
		const blob = new Blob([JSON.stringify(selected.data, null, 2)], { type: "application/json" });
		const url = URL.createObjectURL(blob);
		const a = document.createElement("a");
		a.href = url;
		a.download = `leo-diagnostics-${selected.at.replace(/[:.]/g, "-")}.json`;
		document.body.appendChild(a);
		a.click();
		a.remove();
		URL.revokeObjectURL(url);
	};
	const downloadCsv = () => {
		if (history.length === 0) {
			toast.error("No history to export");
			return;
		}
		const esc = (v) => {
			const s = v == null ? "" : String(v);
			return /[",\n]/.test(s) ? `"${s.replace(/"/g, "\"\"")}"` : s;
		};
		const header = [
			"timestamp",
			"ok",
			"http_status",
			"latency_ms",
			"environment",
			"models",
			"config",
			"last_error_type",
			"last_error_message",
			"last_error_route",
			"last_error_at",
			"error"
		];
		const metaLines = [
			`# exported_at=${(/* @__PURE__ */ new Date()).toISOString()}`,
			`# api_base=${getApiBase()}`,
			`# endpoint=/api/v1/leo/diagnostics`,
			`# count=${history.length}`
		];
		const rows = history.map((h) => [
			h.at,
			h.ok,
			h.httpStatus ?? "",
			h.latencyMs ?? "",
			h.data?.environment ? JSON.stringify(h.data.environment) : "",
			h.data?.models ? JSON.stringify(h.data.models) : "",
			h.data?.config ? JSON.stringify(h.data.config) : "",
			h.data?.last_error?.type ?? "",
			h.data?.last_error?.message ?? "",
			h.data?.last_error?.route ?? "",
			h.data?.last_error?.at ?? "",
			h.error ?? ""
		].map(esc).join(","));
		const csv = [
			...metaLines,
			header.join(","),
			...rows
		].join("\n");
		const blob = new Blob([csv], { type: "text/csv" });
		const url = URL.createObjectURL(blob);
		const a = document.createElement("a");
		a.href = url;
		a.download = `leo-diagnostics-history-${(/* @__PURE__ */ new Date()).toISOString().replace(/[:.]/g, "-")}.csv`;
		document.body.appendChild(a);
		a.click();
		a.remove();
		URL.revokeObjectURL(url);
	};
	const clearHistory = () => {
		setHistory([]);
		saveHistory([]);
		setSelectedId(null);
		setCompareId(null);
		prevErrRef.current = null;
		toast.success("Diagnostics history cleared");
	};
	const copyLatestJson = async () => {
		if (!latest?.data) {
			toast.error("No latest payload to copy");
			return;
		}
		try {
			await navigator.clipboard.writeText(JSON.stringify(latest.data, null, 2));
			toast.success("Latest diagnostics JSON copied");
		} catch {
			toast.error("Clipboard blocked");
		}
	};
	const buildDiffReport = () => {
		if (!compare || !selected) return null;
		const sections = [
			"environment",
			"models",
			"config",
			"last_error"
		].map((k) => {
			const a = JSON.stringify(compare.data?.[k] ?? null, null, 2);
			const b = JSON.stringify(selected.data?.[k] ?? null, null, 2);
			const lines = diffLines(a, b);
			return {
				key: k,
				changed: a !== b,
				lines
			};
		});
		return {
			meta: {
				exported_at: (/* @__PURE__ */ new Date()).toISOString(),
				api_base: getApiBase(),
				endpoint: "/api/v1/leo/diagnostics",
				baseline: {
					at: compare.at,
					source: compare.source,
					httpStatus: compare.httpStatus
				},
				current: {
					at: selected.at,
					source: selected.source,
					httpStatus: selected.httpStatus
				}
			},
			sections
		};
	};
	const exportDiffJson = () => {
		const report = buildDiffReport();
		if (!report) {
			toast.error("Set a compare baseline first (double-click a snapshot)");
			return;
		}
		const blob = new Blob([JSON.stringify(report, null, 2)], { type: "application/json" });
		const url = URL.createObjectURL(blob);
		const a = document.createElement("a");
		a.href = url;
		a.download = `leo-diagnostics-diff-${(/* @__PURE__ */ new Date()).toISOString().replace(/[:.]/g, "-")}.json`;
		document.body.appendChild(a);
		a.click();
		a.remove();
		URL.revokeObjectURL(url);
	};
	const exportDiffMarkdown = () => {
		const report = buildDiffReport();
		if (!report) {
			toast.error("Set a compare baseline first (double-click a snapshot)");
			return;
		}
		const { meta, sections } = report;
		const md = [];
		md.push(`# LEO Diagnostics Diff Report`);
		md.push("");
		md.push(`- Exported: \`${meta.exported_at}\``);
		md.push(`- API base: \`${meta.api_base}\``);
		md.push(`- Endpoint: \`${meta.endpoint}\``);
		md.push(`- Baseline: \`${meta.baseline.at}\` (source: ${meta.baseline.source}, HTTP ${meta.baseline.httpStatus ?? "n/a"})`);
		md.push(`- Current:  \`${meta.current.at}\` (source: ${meta.current.source}, HTTP ${meta.current.httpStatus ?? "n/a"})`);
		md.push("");
		for (const s of sections) {
			md.push(`## ${s.key} — ${s.changed ? "changed" : "unchanged"}`);
			md.push("");
			if (!s.changed) {
				md.push("_no changes_");
				md.push("");
				continue;
			}
			md.push("```diff");
			for (const ln of s.lines) {
				const prefix = ln.kind === "add" ? "+" : ln.kind === "del" ? "-" : " ";
				md.push(`${prefix} ${ln.text}`);
			}
			md.push("```");
			md.push("");
		}
		const blob = new Blob([md.join("\n")], { type: "text/markdown" });
		const url = URL.createObjectURL(blob);
		const a = document.createElement("a");
		a.href = url;
		a.download = `leo-diagnostics-diff-${(/* @__PURE__ */ new Date()).toISOString().replace(/[:.]/g, "-")}.md`;
		document.body.appendChild(a);
		a.click();
		a.remove();
		URL.revokeObjectURL(url);
	};
	const url = `${getApiBase()}/api/v1/leo/diagnostics`;
	const connOk = latest?.ok === true;
	const connWarn = latest && !latest.ok;
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
		className: "border border-border bg-background/60",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("header", {
				className: "flex flex-wrap items-center justify-between gap-2 border-b border-border px-4 py-3",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "min-w-0",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
							className: "eyebrow",
							children: "Backend /diagnostics"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
							className: "text-xs text-muted-foreground font-mono truncate max-w-[420px]",
							children: url
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
							className: "mt-1 flex items-center gap-2 text-[11px]",
							children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
								"aria-live": "polite",
								className: `inline-flex items-center gap-1 px-2 py-0.5 border ${connOk ? "border-green-500/40 bg-green-500/10 text-green-300" : connWarn ? "border-red-500/40 bg-red-500/10 text-red-300" : "border-border text-muted-foreground"}`,
								children: [
									connOk ? "● reachable" : connWarn ? "● unreachable" : "● unknown",
									latest?.httpStatus != null && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
										className: "font-mono",
										children: ["HTTP ", latest.httpStatus]
									}),
									latest?.latencyMs != null && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
										className: "font-mono",
										children: [latest.latencyMs, "ms"]
									})
								]
							})
						})
					]
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "flex flex-wrap items-center gap-2",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("label", {
							className: "inline-flex items-center gap-1 text-[11px] text-muted-foreground",
							children: ["Auto", /* @__PURE__ */ (0, import_jsx_runtime.jsx)("select", {
								value: refreshMs,
								onChange: (e) => setRefreshMs(Number(e.target.value)),
								className: "border border-border bg-background px-1 py-0.5 font-mono text-[11px] focus:border-leo focus:outline-none",
								"aria-label": "Auto-refresh interval",
								children: REFRESH_OPTIONS.map((o) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("option", {
									value: o,
									children: o === 0 ? "off" : `${o / 1e3}s`
								}, o))
							})]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
							type: "button",
							onClick: () => void run("manual"),
							disabled: isFetching,
							className: "border border-border px-2 py-1 text-[11px] hover:border-leo hover:text-leo disabled:opacity-50",
							children: isFetching ? "Fetching…" : "Refresh"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
							type: "button",
							onClick: copyLatestJson,
							disabled: !latest?.data,
							className: "border border-border px-2 py-1 text-[11px] hover:border-leo hover:text-leo disabled:opacity-50",
							title: "Copy latest /diagnostics JSON payload (including last_error)",
							children: "Copy JSON"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
							type: "button",
							onClick: copy,
							disabled: !selected?.data,
							className: "border border-border px-2 py-1 text-[11px] hover:border-leo hover:text-leo disabled:opacity-50",
							children: "Copy"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
							type: "button",
							onClick: download,
							disabled: !selected?.data,
							className: "border border-border px-2 py-1 text-[11px] hover:border-leo hover:text-leo disabled:opacity-50",
							children: "Download JSON"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
							type: "button",
							onClick: downloadCsv,
							disabled: history.length === 0,
							className: "border border-border px-2 py-1 text-[11px] hover:border-leo hover:text-leo disabled:opacity-50",
							children: "Download CSV"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
							type: "button",
							onClick: exportDiffJson,
							disabled: !compare || !selected,
							className: "border border-border px-2 py-1 text-[11px] hover:border-leo hover:text-leo disabled:opacity-50",
							title: "Export the current baseline↔current diff as JSON",
							children: "Export diff JSON"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
							type: "button",
							onClick: exportDiffMarkdown,
							disabled: !compare || !selected,
							className: "border border-border px-2 py-1 text-[11px] hover:border-leo hover:text-leo disabled:opacity-50",
							title: "Export the current baseline↔current diff as Markdown",
							children: "Export diff MD"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
							type: "button",
							onClick: clearHistory,
							disabled: history.length === 0,
							className: "border border-border px-2 py-1 text-[11px] hover:border-red-500/60 hover:text-red-300 disabled:opacity-50",
							children: "Clear"
						})
					]
				})]
			}),
			connWarn && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "border-b border-red-500/40 bg-red-500/10 px-4 py-2 text-[11px] text-red-200",
				role: "alert",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("strong", { children: "Unreachable:" }),
					" ",
					latest?.error ?? "unknown error",
					" — check that your backend is running and that ",
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("code", {
						className: "font-mono",
						children: "/api/v1/leo/diagnostics"
					}),
					" exists."
				]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "grid gap-0 border-b border-border md:grid-cols-[220px_1fr]",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "border-b border-border md:border-b-0 md:border-r md:border-border",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "px-3 py-2 text-[11px] uppercase tracking-wide text-muted-foreground",
							children: [
								"History (",
								history.length,
								"/",
								MAX_HISTORY,
								")"
							]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("ul", {
							className: "max-h-[300px] overflow-auto",
							children: [history.length === 0 && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("li", {
								className: "px-3 py-2 text-[11px] text-muted-foreground",
								children: "No snapshots yet."
							}), history.slice().reverse().map((h) => {
								const isSel = (selectedId ?? latest?.id) === h.id;
								const isCmp = compareId === h.id;
								return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("li", { children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("button", {
									type: "button",
									onClick: () => setSelectedId(h.id),
									onDoubleClick: () => setCompareId(h.id === compareId ? null : h.id),
									className: `flex w-full items-center justify-between gap-2 border-l-2 px-3 py-1.5 text-left text-[11px] font-mono hover:bg-muted/30 ${isSel ? "border-leo bg-muted/20" : isCmp ? "border-orange-400" : "border-transparent"}`,
									title: "Click to view · Double-click to set as compare baseline",
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
										className: "flex min-w-0 flex-col",
										children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
											className: "truncate",
											children: new Date(h.at).toLocaleTimeString()
										}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
											className: "text-[10px] opacity-60 normal-case",
											children: [h.source, h.source === "auto" && h.refreshMs ? ` · ${h.refreshMs / 1e3}s` : ""]
										})]
									}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
										className: h.ok ? "text-green-400" : "text-red-400",
										children: h.httpStatus ?? "ERR"
									})]
								}) }, h.id);
							})]
						}),
						history.length >= 2 && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "border-t border-border px-3 py-2 text-[10px] text-muted-foreground",
							children: ["Double-click a row to set compare baseline", compare && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
								type: "button",
								onClick: () => setCompareId(null),
								className: "ml-2 underline hover:text-leo",
								children: "clear"
							})]
						})
					]
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "px-4 py-3 text-xs",
					"aria-live": "polite",
					children: !selected ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "text-muted-foreground",
						children: "No diagnostics yet — click Refresh."
					}) : /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(import_jsx_runtime.Fragment, { children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "mb-2 flex flex-wrap items-center gap-3 text-[11px] text-muted-foreground",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", { children: [
								"Snapshot: ",
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
									className: "font-mono",
									children: formatHuman(selected.at)
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
									className: "ml-1 opacity-70",
									children: [
										"· source: ",
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
											className: "font-mono",
											children: selected.source
										}),
										selected.source === "auto" && selected.refreshMs ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(import_jsx_runtime.Fragment, { children: [
											" ",
											"· every ",
											/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
												className: "font-mono",
												children: [selected.refreshMs / 1e3, "s"]
											})
										] }) : null
									]
								})
							] }), compare && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", { children: [
								"vs baseline: ",
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
									className: "font-mono",
									children: formatHuman(compare.at)
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
									className: "ml-1 opacity-70",
									children: ["· source: ", /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
										className: "font-mono",
										children: compare.source
									})]
								})
							] })]
						}),
						selected.data?.last_error && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "mb-3 border border-orange-400/40 bg-orange-400/10 p-3 text-orange-100",
							role: "alert",
							children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
									className: "flex items-baseline justify-between gap-2",
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("strong", {
										className: "uppercase tracking-wide",
										children: "Last error"
									}), selected.data.last_error.at && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
										className: "font-mono text-[11px]",
										children: selected.data.last_error.at
									})]
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
									className: "mt-1 font-mono",
									children: [selected.data.last_error.type ? `${selected.data.last_error.type}: ` : "", selected.data.last_error.message ?? "(no message)"]
								}),
								selected.data.last_error.route && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
									className: "mt-1 font-mono text-[11px] opacity-80",
									children: ["route: ", selected.data.last_error.route]
								}),
								selected.data.last_error.traceback && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("details", {
									className: "mt-2",
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("summary", {
										className: "cursor-pointer text-[11px] opacity-80",
										children: "Traceback"
									}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("pre", {
										className: "mt-2 max-h-64 overflow-auto whitespace-pre-wrap font-mono text-[11px]",
										children: selected.data.last_error.traceback
									})]
								})
							]
						}),
						compare ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(DiffView, {
							baseline: compare.data,
							current: selected.data
						}) : selected.data ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("pre", {
							className: "max-h-[360px] overflow-auto whitespace-pre-wrap font-mono text-[11px] text-muted-foreground",
							children: JSON.stringify({
								environment: selected.data.environment,
								models: selected.data.models,
								config: selected.data.config
							}, null, 2)
						}) : /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
							className: "text-red-300",
							children: ["No payload — ", selected.error]
						})
					] })
				})]
			})
		]
	});
}
function DiffView({ baseline, current }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
		className: "space-y-3",
		children: [
			"environment",
			"models",
			"config",
			"last_error"
		].map((k) => {
			const a = JSON.stringify(baseline?.[k] ?? null, null, 2);
			const b = JSON.stringify(current?.[k] ?? null, null, 2);
			const same = a === b;
			return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "border border-border",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: `flex items-center justify-between border-b border-border px-2 py-1 text-[11px] uppercase tracking-wide ${same ? "text-muted-foreground" : "text-orange-300"}`,
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { children: k }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { children: same ? "unchanged" : "changed" })]
				}), !same && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "bg-background font-mono text-[11px] max-h-72 overflow-auto",
					children: diffLines(a, b).map((ln, i) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: ln.kind === "add" ? "bg-green-500/10 text-green-300 px-2" : ln.kind === "del" ? "bg-red-500/10 text-red-300 px-2" : "text-muted-foreground px-2",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "select-none opacity-60 mr-2",
							children: ln.kind === "add" ? "+" : ln.kind === "del" ? "-" : " "
						}), ln.text || "\xA0"]
					}, i))
				})]
			}, k);
		})
	});
}
function diffLines(aText, bText) {
	const a = aText.split("\n");
	const b = bText.split("\n");
	const n = a.length, m = b.length;
	const dp = Array.from({ length: n + 1 }, () => new Array(m + 1).fill(0));
	for (let i = n - 1; i >= 0; i--) for (let j = m - 1; j >= 0; j--) dp[i][j] = a[i] === b[j] ? dp[i + 1][j + 1] + 1 : Math.max(dp[i + 1][j], dp[i][j + 1]);
	const out = [];
	let i = 0, j = 0;
	while (i < n && j < m) if (a[i] === b[j]) {
		out.push({
			kind: "eq",
			text: a[i]
		});
		i++;
		j++;
	} else if (dp[i + 1][j] >= dp[i][j + 1]) {
		out.push({
			kind: "del",
			text: a[i]
		});
		i++;
	} else {
		out.push({
			kind: "add",
			text: b[j]
		});
		j++;
	}
	while (i < n) out.push({
		kind: "del",
		text: a[i++]
	});
	while (j < m) out.push({
		kind: "add",
		text: b[j++]
	});
	return out;
}
var KEY$6 = "leo.bench.history";
var MAX = 50;
function read$4() {
	if (typeof window === "undefined") return [];
	try {
		const raw = window.localStorage.getItem(KEY$6);
		return raw ? JSON.parse(raw) : [];
	} catch {
		return [];
	}
}
function write$1(runs) {
	if (typeof window === "undefined") return;
	try {
		window.localStorage.setItem(KEY$6, JSON.stringify(runs.slice(0, MAX)));
		window.dispatchEvent(new CustomEvent("leo:bench-history"));
	} catch {}
}
function saveRun(run) {
	write$1([run, ...read$4()]);
}
function validateRow(raw, rowIndex) {
	if (!raw || typeof raw !== "object") return {
		ok: false,
		issue: {
			rowIndex,
			status: "invalid",
			reason: "not an object"
		}
	};
	const r = raw;
	const missing = [];
	if (typeof r.id !== "string" || !r.id) missing.push("id");
	if (typeof r.timestamp !== "string" || !r.timestamp) missing.push("timestamp");
	for (const k of [
		"throughputRps",
		"p50Ms",
		"p95Ms",
		"p99Ms",
		"errorRatePct"
	]) {
		const v = r[k];
		if (typeof v !== "number" || Number.isNaN(v)) missing.push(k);
	}
	if (missing.length) return {
		ok: false,
		issue: {
			rowIndex,
			status: "invalid",
			reason: `missing/invalid: ${missing.join(", ")}`,
			id: typeof r.id === "string" ? r.id : void 0
		}
	};
	return {
		ok: true,
		run: r
	};
}
function importRuns(incoming, strategy = "merge") {
	const issues = [];
	const valid = [];
	incoming.forEach((raw, i) => {
		const res = validateRow(raw, i);
		if (res.ok) valid.push(res.run);
		else issues.push(res.issue);
	});
	if (strategy === "replace") {
		write$1(valid);
		valid.forEach((r, i) => issues.push({
			rowIndex: i,
			status: "merged",
			id: r.id
		}));
		return {
			added: valid.length,
			skipped: 0,
			invalid: issues.filter((x) => x.status === "invalid").length,
			total: valid.length,
			issues
		};
	}
	const current = read$4();
	const seen = new Set(current.map((r) => r.id));
	let added = 0;
	let skipped = 0;
	for (let i = 0; i < valid.length; i++) {
		const r = valid[i];
		if (seen.has(r.id)) {
			skipped += 1;
			issues.push({
				rowIndex: i,
				status: "duplicate",
				id: r.id,
				reason: "id already in history"
			});
		} else {
			seen.add(r.id);
			current.push(r);
			added += 1;
			issues.push({
				rowIndex: i,
				status: "merged",
				id: r.id
			});
		}
	}
	current.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
	write$1(current);
	return {
		added,
		skipped,
		invalid: issues.filter((x) => x.status === "invalid").length,
		total: current.length,
		issues
	};
}
var SCHEMA_FIELDS = [
	{
		name: "id",
		type: "string",
		required: true
	},
	{
		name: "timestamp",
		type: "string",
		required: true
	},
	{
		name: "apiBase",
		type: "string",
		required: false
	},
	{
		name: "path",
		type: "string",
		required: false
	},
	{
		name: "totalRequests",
		type: "number",
		required: false
	},
	{
		name: "concurrency",
		type: "number",
		required: false
	},
	{
		name: "durationMs",
		type: "number",
		required: false
	},
	{
		name: "errors",
		type: "number",
		required: false
	},
	{
		name: "errorRatePct",
		type: "number",
		required: true
	},
	{
		name: "throughputRps",
		type: "number",
		required: true
	},
	{
		name: "p50Ms",
		type: "number",
		required: true
	},
	{
		name: "p95Ms",
		type: "number",
		required: true
	},
	{
		name: "p99Ms",
		type: "number",
		required: true
	},
	{
		name: "minMs",
		type: "number",
		required: false
	},
	{
		name: "maxMs",
		type: "number",
		required: false
	},
	{
		name: "meanMs",
		type: "number",
		required: false
	}
];
function validateSchema(text, name) {
	const trimmed = text.trim();
	const looksCsv = name.toLowerCase().endsWith(".csv") || !trimmed.startsWith("[") && !trimmed.startsWith("{");
	const issues = [];
	let detected = [];
	let rowCount = 0;
	const format = looksCsv ? "csv" : "json";
	try {
		if (looksCsv) {
			const lines = trimmed.split(/\r?\n/).filter((l) => l.length > 0);
			if (lines.length < 2) {
				issues.push({
					field: "*",
					severity: "error",
					message: "CSV needs a header row and at least one data row."
				});
				return {
					ok: false,
					format,
					detectedFields: [],
					issues,
					rowCount: 0
				};
			}
			detected = splitCsvLine(lines[0]);
			rowCount = lines.length - 1;
		} else {
			const data = JSON.parse(trimmed);
			const arr = Array.isArray(data) ? data : Array.isArray(data.runs) ? data.runs : [data];
			rowCount = arr.length;
			const first = arr.find((x) => x && typeof x === "object");
			detected = first ? Object.keys(first) : [];
			if (!first) issues.push({
				field: "*",
				severity: "error",
				message: "No object rows found in JSON payload."
			});
		}
	} catch (e) {
		issues.push({
			field: "*",
			severity: "error",
			message: `Parse failed: ${e.message}`
		});
		return {
			ok: false,
			format,
			detectedFields: [],
			issues,
			rowCount: 0
		};
	}
	const detectedSet = new Set(detected);
	for (const f of SCHEMA_FIELDS) if (!detectedSet.has(f.name)) if (f.required) issues.push({
		field: f.name,
		severity: "error",
		message: `Missing required ${f.type} column/field "${f.name}".`
	});
	else issues.push({
		field: f.name,
		severity: "warning",
		message: `Optional field "${f.name}" not present — will default.`
	});
	const known = new Set(SCHEMA_FIELDS.map((f) => f.name));
	for (const d of detected) if (!known.has(d)) issues.push({
		field: d,
		severity: "warning",
		message: `Unknown field "${d}" will be ignored.`
	});
	return {
		ok: !issues.some((i) => i.severity === "error"),
		format,
		detectedFields: detected,
		issues,
		rowCount
	};
}
function parseImportedFile(text, name) {
	const trimmed = text.trim();
	if (name.toLowerCase().endsWith(".csv") || !trimmed.startsWith("[") && !trimmed.startsWith("{")) return parseCsv(trimmed);
	const data = JSON.parse(trimmed);
	if (Array.isArray(data)) return data;
	if (data && typeof data === "object" && Array.isArray(data.runs)) return data.runs;
	return [data];
}
function parseCsv(text) {
	const lines = text.split(/\r?\n/).filter((l) => l.length > 0);
	if (lines.length < 2) return [];
	const header = splitCsvLine(lines[0]);
	const numericKeys = new Set([
		"totalRequests",
		"concurrency",
		"durationMs",
		"errors",
		"errorRatePct",
		"throughputRps",
		"p50Ms",
		"p95Ms",
		"p99Ms",
		"minMs",
		"maxMs",
		"meanMs"
	]);
	return lines.slice(1).map((line) => {
		const cells = splitCsvLine(line);
		const obj = {};
		header.forEach((h, i) => {
			const v = cells[i] ?? "";
			obj[h] = numericKeys.has(h) ? Number(v) : v;
		});
		return obj;
	});
}
function splitCsvLine(line) {
	const out = [];
	let cur = "";
	let inQ = false;
	for (let i = 0; i < line.length; i++) {
		const c = line[i];
		if (inQ) if (c === "\"" && line[i + 1] === "\"") {
			cur += "\"";
			i++;
		} else if (c === "\"") inQ = false;
		else cur += c;
		else if (c === ",") {
			out.push(cur);
			cur = "";
		} else if (c === "\"") inQ = true;
		else cur += c;
	}
	out.push(cur);
	return out;
}
function clearHistory() {
	write$1([]);
}
var CSV_COLS = [
	"id",
	"timestamp",
	"apiBase",
	"path",
	"totalRequests",
	"concurrency",
	"durationMs",
	"errors",
	"errorRatePct",
	"throughputRps",
	"p50Ms",
	"p95Ms",
	"p99Ms",
	"minMs",
	"maxMs",
	"meanMs"
];
function runsToCsv(runs) {
	const esc = (v) => {
		const s = v == null ? "" : String(v);
		return /[",\n]/.test(s) ? `"${s.replace(/"/g, "\"\"")}"` : s;
	};
	return [CSV_COLS.join(","), ...runs.map((r) => CSV_COLS.map((k) => esc(r[k])).join(","))].join("\n");
}
function downloadRuns(runs, format) {
	if (typeof window === "undefined" || runs.length === 0) return;
	const isCsv = format === "csv";
	const body = isCsv ? runsToCsv(runs) : JSON.stringify(runs, null, 2);
	const blob = new Blob([body], { type: isCsv ? "text/csv;charset=utf-8" : "application/json" });
	const url = URL.createObjectURL(blob);
	const a = document.createElement("a");
	a.href = url;
	a.download = `leo-bench-history-${Date.now()}.${format}`;
	a.click();
	URL.revokeObjectURL(url);
}
var TEMPLATE_ROW = {
	id: "example-run-0001",
	timestamp: "2026-01-01T00:00:00.000Z",
	apiBase: "http://localhost:8005",
	path: "/api/v1/leo/metrics",
	totalRequests: 200,
	concurrency: 8,
	durationMs: 4200,
	errors: 0,
	errorRatePct: 0,
	throughputRps: 47.6,
	p50Ms: 18.2,
	p95Ms: 42.1,
	p99Ms: 61.3,
	minMs: 11.4,
	maxMs: 88.7,
	meanMs: 22.9
};
function downloadTemplate(format) {
	if (typeof window === "undefined") return;
	const body = format === "csv" ? runsToCsv([TEMPLATE_ROW]) : JSON.stringify({
		$schema: "leo-bench-history v1",
		note: "Every row needs `id` (string) and `throughputRps` (number). Timestamps are ISO-8601. All *Ms/*Rps/*Pct fields are numeric.",
		runs: [TEMPLATE_ROW]
	}, null, 2);
	const blob = new Blob([body], { type: format === "csv" ? "text/csv;charset=utf-8" : "application/json" });
	const url = URL.createObjectURL(blob);
	const a = document.createElement("a");
	a.href = url;
	a.download = `leo-bench-template.${format}`;
	a.click();
	URL.revokeObjectURL(url);
}
function useBenchmarkHistory() {
	const [runs, setRuns] = (0, import_react.useState)([]);
	(0, import_react.useEffect)(() => {
		setRuns(read$4());
		const on = () => setRuns(read$4());
		window.addEventListener("leo:bench-history", on);
		window.addEventListener("storage", on);
		return () => {
			window.removeEventListener("leo:bench-history", on);
			window.removeEventListener("storage", on);
		};
	}, []);
	return runs;
}
var NVIDIA_PRESETS = {
	"h100-sxm": {
		label: "NVIDIA H100 SXM",
		fp16_tflops: 989,
		mem_gb: 80,
		mem_bw_gbs: 3350,
		tdp_w: 700,
		ref_rps: 1e3
	},
	"a100-80": {
		label: "NVIDIA A100 80GB",
		fp16_tflops: 312,
		mem_gb: 80,
		mem_bw_gbs: 2039,
		tdp_w: 400,
		ref_rps: 600
	},
	l4: {
		label: "NVIDIA L4",
		fp16_tflops: 121,
		mem_gb: 24,
		mem_bw_gbs: 300,
		tdp_w: 72,
		ref_rps: 250
	},
	"rtx-4090": {
		label: "NVIDIA RTX 4090",
		fp16_tflops: 330,
		mem_gb: 24,
		mem_bw_gbs: 1008,
		tdp_w: 450,
		ref_rps: 500
	},
	t4: {
		label: "NVIDIA T4",
		fp16_tflops: 65,
		mem_gb: 16,
		mem_bw_gbs: 320,
		tdp_w: 70,
		ref_rps: 150
	}
};
var REF_KEY = "leo.nvidia_ref";
function useNvidiaRef() {
	const [preset, setPreset] = (0, import_react.useState)("h100-sxm");
	const [ref, setRef] = (0, import_react.useState)(NVIDIA_PRESETS["h100-sxm"]);
	(0, import_react.useEffect)(() => {
		if (typeof window === "undefined") return;
		try {
			const raw = window.localStorage.getItem(REF_KEY);
			if (raw) {
				const parsed = JSON.parse(raw);
				setPreset(parsed.preset);
				setRef(parsed.ref);
			}
		} catch {}
	}, []);
	function save(next, nextPreset = preset) {
		setRef(next);
		setPreset(nextPreset);
		try {
			window.localStorage.setItem(REF_KEY, JSON.stringify({
				preset: nextPreset,
				ref: next
			}));
		} catch {}
	}
	return [
		ref,
		(r) => save(r, "custom"),
		preset,
		(id) => {
			if (id === "custom") save(ref, "custom");
			else save(NVIDIA_PRESETS[id] ?? ref, id);
		}
	];
}
var DEFAULT_PROFILE = {
	laptop: "Lenovo IdeaPad Slim 3 15IAH8",
	cpu: "Intel Core i5-12450H (12th Gen)",
	cores: 8,
	threads: 12,
	ram_gb: 16,
	igpu: "Intel UHD Graphics (Alder Lake)",
	igpu_tflops_fp16: .4,
	storage: "512 GB NVMe SSD",
	tdp_w: 45
};
var STORAGE_KEY = "leo.hw_profile";
function HardwareProfileCard({ liveRps, avoidanceRatePct, wattsSaved, selectedRun }) {
	const [p, setP] = (0, import_react.useState)(DEFAULT_PROFILE);
	const [editing, setEditing] = (0, import_react.useState)(false);
	const [showMath, setShowMath] = (0, import_react.useState)(true);
	const [ref, setRef, presetId, setPresetId] = useNvidiaRef();
	(0, import_react.useEffect)(() => {
		if (typeof window === "undefined") return;
		try {
			const raw = window.localStorage.getItem(STORAGE_KEY);
			if (raw) setP({
				...DEFAULT_PROFILE,
				...JSON.parse(raw)
			});
		} catch {}
	}, []);
	function save(next) {
		setP(next);
		try {
			window.localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
		} catch {}
	}
	const effRpsSource = selectedRun ? {
		rps: selectedRun.throughputRps,
		label: `benchmark @ ${new Date(selectedRun.timestamp).toLocaleTimeString()}`
	} : liveRps != null ? {
		rps: liveRps,
		label: "last run rps"
	} : null;
	const tflopsRatioPct = p.igpu_tflops_fp16 / ref.fp16_tflops * 100;
	const memRatioPct = p.ram_gb / ref.mem_gb * 100;
	const tdpRatioPct = p.tdp_w / ref.tdp_w * 100;
	const avoidance = avoidanceRatePct ?? 0;
	const effRps = effRpsSource ? effRpsSource.rps * (1 + avoidance / 100) : void 0;
	const throughputRatioPct = effRps ? effRps / ref.ref_rps * 100 : void 0;
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
		"aria-labelledby": "hw-profile-title",
		className: "border border-border bg-background p-6",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex items-start justify-between gap-4",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "eyebrow",
						children: "Hardware profile"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
						id: "hw-profile-title",
						className: "mt-1 font-display text-2xl font-bold",
						children: p.laptop
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
						className: "mt-1 text-xs text-muted-foreground",
						children: ["Compared against ", /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "font-mono text-leo",
							children: ref.label
						})]
					})
				] }), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "flex gap-2",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
						type: "button",
						onClick: () => setShowMath((v) => !v),
						className: "border border-border px-3 py-1.5 text-xs hover:border-leo hover:text-leo focus:outline-none focus-visible:ring-2 focus-visible:ring-leo",
						children: showMath ? "Hide math" : "Show math"
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
						type: "button",
						onClick: () => setEditing((v) => !v),
						className: "border border-border px-3 py-1.5 text-xs hover:border-leo hover:text-leo focus:outline-none focus-visible:ring-2 focus-visible:ring-leo",
						children: editing ? "Done" : "Edit"
					})]
				})]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mt-4 border border-border/60 bg-muted/20 p-4",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "flex items-center justify-between gap-3",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "text-[11px] uppercase tracking-wide text-muted-foreground",
						children: "Reference NVIDIA figure"
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("select", {
						value: presetId,
						onChange: (e) => setPresetId(e.target.value),
						className: "border border-border bg-background px-2 py-1 font-mono text-xs focus:border-leo focus:outline-none",
						"aria-label": "NVIDIA reference preset",
						children: [Object.entries(NVIDIA_PRESETS).map(([id, r]) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("option", {
							value: id,
							children: r.label
						}, id)), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("option", {
							value: "custom",
							children: "Custom"
						})]
					})]
				}), editing && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "mt-3 grid gap-2 text-xs sm:grid-cols-2 lg:grid-cols-3",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(RefField, {
							label: "Label",
							value: ref.label,
							onChange: (v) => setRef({
								...ref,
								label: v
							})
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(RefNum, {
							label: "FP16 TFLOPS",
							value: ref.fp16_tflops,
							onChange: (v) => setRef({
								...ref,
								fp16_tflops: v
							})
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(RefNum, {
							label: "Memory (GB)",
							value: ref.mem_gb,
							onChange: (v) => setRef({
								...ref,
								mem_gb: v
							})
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(RefNum, {
							label: "Mem BW (GB/s)",
							value: ref.mem_bw_gbs,
							onChange: (v) => setRef({
								...ref,
								mem_bw_gbs: v
							})
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(RefNum, {
							label: "TDP (W)",
							value: ref.tdp_w,
							onChange: (v) => setRef({
								...ref,
								tdp_w: v
							})
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(RefNum, {
							label: "Reference RPS",
							value: ref.ref_rps,
							onChange: (v) => setRef({
								...ref,
								ref_rps: v
							})
						})
					]
				})]
			}),
			editing && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mt-4 grid gap-3 border border-border/60 bg-muted/20 p-4 text-xs sm:grid-cols-2",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(RefField, {
						label: "Laptop",
						value: p.laptop,
						onChange: (v) => save({
							...p,
							laptop: v
						})
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(RefField, {
						label: "CPU",
						value: p.cpu,
						onChange: (v) => save({
							...p,
							cpu: v
						})
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(RefNum, {
						label: "Cores",
						value: p.cores,
						onChange: (v) => save({
							...p,
							cores: v
						})
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(RefNum, {
						label: "Threads",
						value: p.threads,
						onChange: (v) => save({
							...p,
							threads: v
						})
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(RefNum, {
						label: "RAM (GB)",
						value: p.ram_gb,
						onChange: (v) => save({
							...p,
							ram_gb: v
						})
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(RefField, {
						label: "iGPU",
						value: p.igpu,
						onChange: (v) => save({
							...p,
							igpu: v
						})
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(RefNum, {
						label: "iGPU FP16 TFLOPS",
						value: p.igpu_tflops_fp16,
						step: .1,
						onChange: (v) => save({
							...p,
							igpu_tflops_fp16: v
						})
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(RefField, {
						label: "Storage",
						value: p.storage,
						onChange: (v) => save({
							...p,
							storage: v
						})
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(RefNum, {
						label: "TDP (W)",
						value: p.tdp_w,
						onChange: (v) => save({
							...p,
							tdp_w: v
						})
					})
				]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("dl", {
				className: "mt-6 grid gap-px bg-border sm:grid-cols-2 lg:grid-cols-3",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Spec, {
						label: "CPU / cores",
						value: `${p.cpu} · ${p.cores}C/${p.threads}T`
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Spec, {
						label: "RAM",
						value: `${p.ram_gb} GB`
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Spec, {
						label: "iGPU",
						value: p.igpu
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Spec, {
						label: "Storage",
						value: p.storage
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Spec, {
						label: "TDP",
						value: `${p.tdp_w} W`
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Spec, {
						label: "iGPU FP16",
						value: `${p.igpu_tflops_fp16.toFixed(2)} TFLOPS`
					})
				]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mt-6",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "eyebrow",
						children: "Documented ratio vs reference"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "mt-3 grid gap-px bg-border sm:grid-cols-2 lg:grid-cols-4",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Ratio, {
								label: "FP16 compute",
								pct: tflopsRatioPct,
								formula: `${p.igpu_tflops_fp16} ÷ ${ref.fp16_tflops} × 100`,
								showMath
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Ratio, {
								label: "Memory",
								pct: memRatioPct,
								formula: `${p.ram_gb} ÷ ${ref.mem_gb} × 100`,
								showMath
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Ratio, {
								label: "Power draw",
								pct: tdpRatioPct,
								formula: `${p.tdp_w} ÷ ${ref.tdp_w} × 100`,
								invert: true,
								showMath
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Ratio, {
								label: "Effective RPS*",
								pct: throughputRatioPct,
								formula: effRpsSource ? `${effRpsSource.rps.toFixed(2)} × (1 + ${avoidance.toFixed(1)}/100) ÷ ${ref.ref_rps} × 100` : "Run a benchmark",
								showMath
							})
						]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
						className: "mt-3 text-[11px] text-muted-foreground",
						children: [
							"* Effective RPS = measured rps × (1 + avoidance rate). Source:",
							" ",
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
								className: "font-mono",
								children: effRpsSource?.label ?? "n/a"
							}),
							". Reference RPS is a configurable nominal baseline — edit above to match your target hardware's real serving rate."
						]
					}),
					wattsSaved != null && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
						className: "mt-1 text-[11px] text-muted-foreground",
						children: [
							"Live watts saved by avoidance:",
							" ",
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
								className: "text-leo",
								children: [wattsSaved.toLocaleString(), " W"]
							})
						]
					})
				]
			})
		]
	});
}
function Spec({ label, value }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "bg-background p-4",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("dt", {
			className: "text-[11px] uppercase tracking-wide text-muted-foreground",
			children: label
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("dd", {
			className: "mt-1 truncate font-mono text-sm",
			children: value
		})]
	});
}
function Ratio({ label, pct, formula, invert, showMath }) {
	const display = pct == null ? "—" : `${pct < .1 ? pct.toFixed(3) : pct.toFixed(2)}%`;
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "bg-background p-4",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "text-[11px] uppercase tracking-wide text-muted-foreground",
				children: label
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: `mt-1 font-display text-2xl font-bold ${pct != null && (invert ? pct < 100 : pct > 5) ? "text-leo" : "text-foreground"}`,
				children: display
			}),
			showMath && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mt-2 font-mono text-[10px] leading-relaxed text-muted-foreground",
				children: [formula, pct != null && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "mt-0.5 text-leo/80",
					children: [
						"= ",
						pct.toFixed(4),
						"%"
					]
				})]
			})
		]
	});
}
function RefField({ label, value, onChange }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("label", {
		className: "flex flex-col gap-1",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
			className: "text-[11px] uppercase tracking-wide text-muted-foreground",
			children: label
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("input", {
			value,
			onChange: (e) => onChange(e.target.value),
			className: "border border-border bg-background px-2 py-1 font-mono text-xs focus:border-leo focus:outline-none"
		})]
	});
}
function RefNum({ label, value, step = 1, onChange }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("label", {
		className: "flex flex-col gap-1",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
			className: "text-[11px] uppercase tracking-wide text-muted-foreground",
			children: label
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("input", {
			type: "number",
			step,
			value,
			onChange: (e) => onChange(Number(e.target.value) || 0),
			className: "border border-border bg-background px-2 py-1 font-mono text-xs focus:border-leo focus:outline-none"
		})]
	});
}
var KEY$5 = "leo.bench.chartOptions";
var DEFAULTS = {
	rangeBuckets: 120,
	smoothingWindow: 1,
	showLatency: true,
	showThroughput: true
};
function read$3() {
	if (typeof window === "undefined") return DEFAULTS;
	try {
		const raw = window.localStorage.getItem(KEY$5);
		if (!raw) return DEFAULTS;
		const parsed = JSON.parse(raw);
		return {
			...DEFAULTS,
			...parsed
		};
	} catch {
		return DEFAULTS;
	}
}
function write(opts) {
	if (typeof window === "undefined") return;
	try {
		window.localStorage.setItem(KEY$5, JSON.stringify(opts));
		window.dispatchEvent(new CustomEvent("leo:chart-options"));
	} catch {}
}
function useChartOptions() {
	const [opts, setOpts] = (0, import_react.useState)(DEFAULTS);
	(0, import_react.useEffect)(() => {
		setOpts(read$3());
		const on = () => setOpts(read$3());
		window.addEventListener("leo:chart-options", on);
		window.addEventListener("storage", on);
		return () => {
			window.removeEventListener("leo:chart-options", on);
			window.removeEventListener("storage", on);
		};
	}, []);
	return [opts, (patch) => {
		const next = {
			...opts,
			...patch
		};
		setOpts(next);
		write(next);
	}];
}
function smoothSeries(values, window) {
	if (window <= 1 || values.length === 0) return values;
	const w = Math.min(window, values.length);
	const half = Math.floor(w / 2);
	const out = new Array(values.length);
	for (let i = 0; i < values.length; i++) {
		let sum = 0;
		let count = 0;
		for (let j = i - half; j <= i + half; j++) if (j >= 0 && j < values.length) {
			sum += values[j];
			count += 1;
		}
		out[i] = count ? sum / count : 0;
	}
	return out;
}
var KEY$4 = "leo.sse.log_v1";
var EVENT$2 = "leo:sse-log-changed";
function load$1() {
	if (typeof window === "undefined") return [];
	try {
		const raw = window.localStorage.getItem(KEY$4);
		if (!raw) return [];
		const parsed = JSON.parse(raw);
		return Array.isArray(parsed) ? parsed.slice(-200) : [];
	} catch {
		return [];
	}
}
var buffer = load$1();
var nextId = buffer.reduce((m, e) => Math.max(m, e.id), 0) + 1;
function persist$1() {
	if (typeof window === "undefined") return;
	try {
		window.localStorage.setItem(KEY$4, JSON.stringify(buffer));
		window.dispatchEvent(new CustomEvent(EVENT$2));
	} catch {}
}
function pushSseLog(entry) {
	buffer = [...buffer, {
		id: nextId++,
		at: entry.at ?? Date.now(),
		...entry
	}].slice(-200);
	persist$1();
}
function getSseLog() {
	return buffer.slice();
}
function clearSseLog() {
	buffer = [];
	persist$1();
}
function useSseLog() {
	const [list, setList] = (0, import_react.useState)(() => buffer.slice());
	(0, import_react.useEffect)(() => {
		const on = () => setList(buffer.slice());
		window.addEventListener(EVENT$2, on);
		window.addEventListener("storage", on);
		return () => {
			window.removeEventListener(EVENT$2, on);
			window.removeEventListener("storage", on);
		};
	}, []);
	return list;
}
var TRANSPORT_KEY$1 = "leo.bench.transportMode";
var DIAG_KEY$3 = "leo.bench.sse-diag";
function loadDiag() {
	if (typeof window === "undefined") return null;
	try {
		const raw = window.localStorage.getItem(DIAG_KEY$3);
		return raw ? JSON.parse(raw) : null;
	} catch {
		return null;
	}
}
function saveDiag(d) {
	if (typeof window === "undefined") return;
	try {
		window.localStorage.setItem(DIAG_KEY$3, JSON.stringify(d));
	} catch {}
}
function loadTransportMode() {
	if (typeof window === "undefined") return "auto";
	const v = window.localStorage.getItem(TRANSPORT_KEY$1);
	return v === "sse-only" || v === "polling-only" ? v : "auto";
}
var MIX_PRESETS = [
	{
		id: "metrics-only",
		label: "Metrics only",
		description: "Single lightweight endpoint. Baseline latency.",
		paths: [{
			path: "/api/v1/leo/metrics",
			weight: 1
		}]
	},
	{
		id: "inference-heavy",
		label: "Inference heavy (H100-style)",
		description: "70% metrics / 30% health — approximates hot cache serving.",
		paths: [{
			path: "/api/v1/leo/metrics",
			weight: 7
		}, {
			path: "/health",
			weight: 3
		}]
	},
	{
		id: "mixed-training",
		label: "Mixed training (A100-style)",
		description: "50/50 across metrics and diagnostics — bursty pattern.",
		paths: [{
			path: "/api/v1/leo/metrics",
			weight: 5
		}, {
			path: "/api/v1/leo/diagnostics",
			weight: 5
		}]
	},
	{
		id: "edge-inference",
		label: "Edge inference (L4-style)",
		description: "Small requests dominated by /health checks.",
		paths: [{
			path: "/health",
			weight: 8
		}, {
			path: "/api/v1/leo/metrics",
			weight: 2
		}]
	}
];
function percentile$2(sorted, p) {
	if (sorted.length === 0) return 0;
	return sorted[Math.min(sorted.length - 1, Math.floor(p / 100 * sorted.length))];
}
function pickPath(mix) {
	const total = mix.reduce((s, m) => s + m.weight, 0);
	let r = Math.random() * total;
	for (const m of mix) {
		r -= m.weight;
		if (r <= 0) return m.path;
	}
	return mix[0].path;
}
function BenchmarkRunner({ onResult, onLiveRun }) {
	const [mode, setMode] = (0, import_react.useState)("count");
	const [total, setTotal] = (0, import_react.useState)(200);
	const [durationSec, setDurationSec] = (0, import_react.useState)(30);
	const [concurrency, setConcurrency] = (0, import_react.useState)(8);
	const [warmupSec, setWarmupSec] = (0, import_react.useState)(2);
	const [mixId, setMixId] = (0, import_react.useState)(MIX_PRESETS[0].id);
	const mix = MIX_PRESETS.find((m) => m.id === mixId) ?? MIX_PRESETS[0];
	const [chartOpts, setChartOpts] = useChartOptions();
	const [running, setRunning] = (0, import_react.useState)(false);
	const [phase, setPhase] = (0, import_react.useState)("idle");
	const [progress, setProgress] = (0, import_react.useState)(0);
	const [result, setResult] = (0, import_react.useState)(null);
	const [buckets, setBuckets] = (0, import_react.useState)([]);
	const [live, setLive] = (0, import_react.useState)([]);
	const [streamStatus, setStreamStatus] = (0, import_react.useState)("idle");
	const [reconnectAttempts, setReconnectAttempts] = (0, import_react.useState)(0);
	const [lastEventAt, setLastEventAt] = (0, import_react.useState)(null);
	const [lastEventDelta, setLastEventDelta] = (0, import_react.useState)(0);
	const [lastError, setLastError] = (0, import_react.useState)(null);
	const [transport, setTransport] = (0, import_react.useState)("sse");
	const [transportMode, setTransportMode] = (0, import_react.useState)("auto");
	const [perfSnapshot, setPerfSnapshot] = (0, import_react.useState)({
		renders: 0,
		lastMs: 0
	});
	const renderCountRef = (0, import_react.useRef)(0);
	const lastCommitRef = (0, import_react.useRef)(performance.now());
	const lastRenderMsRef = (0, import_react.useRef)(0);
	{
		const now = performance.now();
		lastRenderMsRef.current = now - lastCommitRef.current;
		lastCommitRef.current = now;
		renderCountRef.current += 1;
	}
	const samplesRef = (0, import_react.useRef)([]);
	const abortRef = (0, import_react.useRef)(null);
	const tickRef = (0, import_react.useRef)(null);
	const startRef = (0, import_react.useRef)(0);
	const diagPersistRef = (0, import_react.useRef)(null);
	(0, import_react.useEffect)(() => {
		setTransportMode(loadTransportMode());
		const d = loadDiag();
		if (d) {
			setLastEventAt(d.lastEventAt);
			setLastError(d.lastError);
			setReconnectAttempts(d.reconnectAttempts);
			setTransport(d.transport);
			setStreamStatus(d.status === "open" ? "closed" : d.status);
		}
		const onModeChange = () => setTransportMode(loadTransportMode());
		window.addEventListener("leo:transport-mode-changed", onModeChange);
		return () => window.removeEventListener("leo:transport-mode-changed", onModeChange);
	}, []);
	(0, import_react.useEffect)(() => {
		const id = window.setInterval(() => {
			setPerfSnapshot({
				renders: renderCountRef.current,
				lastMs: lastRenderMsRef.current
			});
		}, 500);
		return () => window.clearInterval(id);
	}, []);
	(0, import_react.useEffect)(() => {
		if (!running || lastEventAt == null) return;
		const id = window.setInterval(() => {
			setLastEventDelta(Date.now() - lastEventAt);
		}, 500);
		return () => window.clearInterval(id);
	}, [running, lastEventAt]);
	(0, import_react.useEffect)(() => {
		if (!running) return;
		let es = null;
		let pollTimer = null;
		let recoveryTimer = null;
		let disposed = false;
		let attempts = 0;
		let retryTimer = null;
		let fatalErrorStreak = 0;
		const base = getApiBase() || "";
		const sseUrl = `${base}/api/v1/leo/metrics/stream`;
		const pollUrl = `${base}/api/v1/leo/metrics`;
		const sseCfg = (() => {
			try {
				const raw = typeof window !== "undefined" ? window.localStorage.getItem("leo.sse.reconnect_v1") : null;
				const parsed = raw ? JSON.parse(raw) : {};
				return {
					maxAttempts: Number.isFinite(parsed.maxAttempts) ? parsed.maxAttempts : 5,
					initialBackoffMs: Number.isFinite(parsed.initialBackoffMs) ? parsed.initialBackoffMs : 500,
					maxBackoffMs: Number.isFinite(parsed.maxBackoffMs) ? parsed.maxBackoffMs : 15e3
				};
			} catch {
				return {
					maxAttempts: 5,
					initialBackoffMs: 500,
					maxBackoffMs: 15e3
				};
			}
		})();
		const MAX_SSE_ATTEMPTS = sseCfg.maxAttempts;
		const classifyError = (readyState) => {
			if (readyState === 2) return ++fatalErrorStreak >= 2 ? "fatal" : "soft";
			fatalErrorStreak = 0;
			return "soft";
		};
		const applyMetric = (d) => {
			setLastEventAt(Date.now());
			setLive((prev) => [...prev, {
				t: (performance.now() - startRef.current) / 1e3,
				rps60: typeof d.leo_rps_60s === "number" ? d.leo_rps_60s : void 0,
				total: typeof d.leo_total_requests === "number" ? d.leo_total_requests : void 0
			}].slice(-240));
		};
		const stopPolling = () => {
			if (pollTimer != null) {
				window.clearInterval(pollTimer);
				pollTimer = null;
			}
			if (recoveryTimer != null) {
				window.clearInterval(recoveryTimer);
				recoveryTimer = null;
			}
		};
		const startPolling = (reason) => {
			setTransport("polling");
			setStreamStatus("polling");
			if (reason) setLastError(reason);
			const tick = async () => {
				if (disposed) return;
				try {
					const res = await fetch(pollUrl, { cache: "no-store" });
					if (!res.ok) throw new Error(`HTTP ${res.status}`);
					applyMetric(await res.json());
					setLastError(null);
				} catch (e) {
					setLastError(e.message);
				}
			};
			tick();
			pollTimer = window.setInterval(tick, 2e3);
			if (transportMode === "auto" && recoveryTimer == null) recoveryTimer = window.setInterval(() => {
				if (disposed) return;
				try {
					const probe = new EventSource(sseUrl, { withCredentials: false });
					const probeTimeout = window.setTimeout(() => {
						try {
							probe.close();
						} catch {}
					}, 3e3);
					probe.onopen = () => {
						window.clearTimeout(probeTimeout);
						try {
							probe.close();
						} catch {}
						if (disposed) return;
						toast.success("SSE recovered — switching back from polling");
						pushSseLog({
							kind: "polling-recover",
							message: "SSE recovered, resuming stream",
							transport: "sse"
						});
						stopPolling();
						attempts = 0;
						fatalErrorStreak = 0;
						setReconnectAttempts(0);
						connect();
					};
					probe.onerror = () => {
						window.clearTimeout(probeTimeout);
						try {
							probe.close();
						} catch {}
					};
				} catch {}
			}, 2e4);
		};
		const connect = () => {
			if (disposed) return;
			pushSseLog({
				kind: "connect",
				message: `Opening EventSource ${sseUrl}`
			});
			try {
				es = new EventSource(sseUrl, { withCredentials: false });
			} catch (e) {
				setLastError(e.message);
				pushSseLog({
					kind: "error",
					message: `Constructor threw: ${e.message}`
				});
				scheduleRetry("soft");
				return;
			}
			es.onopen = () => {
				if (disposed) return;
				attempts = 0;
				fatalErrorStreak = 0;
				setReconnectAttempts(0);
				setTransport("sse");
				setStreamStatus("open");
				setLastError(null);
				pushSseLog({
					kind: "open",
					message: "SSE connection established",
					transport: "sse"
				});
			};
			es.addEventListener("metrics", (ev) => {
				try {
					applyMetric(JSON.parse(ev.data));
				} catch (e) {
					setLastError("parse: " + e.message);
					pushSseLog({
						kind: "error",
						message: `Parse error: ${e.message}`
					});
				}
			});
			es.onerror = () => {
				if (disposed) return;
				const rs = es?.readyState;
				setLastError(`SSE error (readyState=${rs ?? "?"})`);
				pushSseLog({
					kind: "error",
					message: "SSE error event",
					readyState: rs ?? null
				});
				try {
					es?.close();
				} catch {}
				scheduleRetry(classifyError(rs));
			};
		};
		const scheduleRetry = (severity) => {
			if (disposed) return;
			attempts += 1;
			setReconnectAttempts(attempts);
			if (severity === "fatal" || attempts > MAX_SSE_ATTEMPTS) {
				if (transportMode === "sse-only") {
					setStreamStatus("error");
					setLastError("SSE unreachable and polling fallback disabled by user.");
					pushSseLog({
						kind: "error",
						message: "SSE-only mode: giving up after exhausting attempts",
						attempt: attempts
					});
					return;
				}
				toast.warning(severity === "fatal" ? "SSE returned fatal error — switching to 2s polling" : "SSE unavailable — falling back to 2s polling");
				pushSseLog({
					kind: "polling-start",
					message: severity === "fatal" ? "Fatal SSE error — falling back to polling" : `Exhausted ${MAX_SSE_ATTEMPTS} attempts — falling back to polling`,
					attempt: attempts,
					transport: "polling"
				});
				startPolling();
				return;
			}
			setStreamStatus("reconnecting");
			const delay = Math.min(sseCfg.maxBackoffMs, sseCfg.initialBackoffMs * 2 ** Math.min(attempts, 6));
			pushSseLog({
				kind: "reconnect",
				message: `Reconnect scheduled (severity=${severity})`,
				attempt: attempts,
				backoffMs: delay
			});
			retryTimer = window.setTimeout(connect, delay);
		};
		if (transportMode === "polling-only") startPolling("Forced by user (Polling-only mode).");
		else connect();
		return () => {
			disposed = true;
			if (retryTimer != null) window.clearTimeout(retryTimer);
			stopPolling();
			try {
				es?.close();
			} catch {}
			setStreamStatus("closed");
		};
	}, [running, transportMode]);
	(0, import_react.useEffect)(() => {
		if (diagPersistRef.current != null) window.clearTimeout(diagPersistRef.current);
		diagPersistRef.current = window.setTimeout(() => {
			saveDiag({
				lastEventAt,
				lastError,
				reconnectAttempts,
				transport,
				status: streamStatus,
				savedAt: Date.now()
			});
		}, 250);
		return () => {
			if (diagPersistRef.current != null) window.clearTimeout(diagPersistRef.current);
		};
	}, [
		lastEventAt,
		lastError,
		reconnectAttempts,
		transport,
		streamStatus
	]);
	const changeTransportMode = (0, import_react.useCallback)((m) => {
		setTransportMode(m);
		try {
			window.localStorage.setItem(TRANSPORT_KEY$1, m);
		} catch {}
	}, []);
	(0, import_react.useEffect)(() => {
		if (!running) return;
		tickRef.current = window.setInterval(() => {
			const s = samplesRef.current;
			const map = /* @__PURE__ */ new Map();
			for (const x of s) {
				const tSec = Math.floor(x.t);
				const b = map.get(tSec) ?? {
					tSec,
					count: 0,
					sumMs: 0,
					errors: 0
				};
				if (x.ok) {
					b.count += 1;
					b.sumMs += x.latencyMs;
				} else b.errors += 1;
				map.set(tSec, b);
			}
			setBuckets(Array.from(map.values()).sort((a, b) => a.tSec - b.tSec));
		}, 250);
		return () => {
			if (tickRef.current != null) window.clearInterval(tickRef.current);
		};
	}, [running]);
	async function run() {
		if (running) return;
		setRunning(true);
		setResult(null);
		setProgress(0);
		setBuckets([]);
		setLive([]);
		setPhase("warmup");
		samplesRef.current = [];
		const controller = new AbortController();
		abortRef.current = controller;
		const warmupUntil = performance.now() + Math.max(0, warmupSec) * 1e3;
		const warmupWorker = async () => {
			while (performance.now() < warmupUntil && !controller.signal.aborted) try {
				const res = await leoFetch(pickPath(mix.paths), { signal: controller.signal });
				try {
					await res.text();
				} catch {}
			} catch {}
		};
		if (warmupSec > 0) await Promise.all(Array.from({ length: concurrency }, () => warmupWorker()));
		if (controller.signal.aborted) {
			finalize(controller, 0, 0, [], performance.now());
			return;
		}
		setPhase("measure");
		const latencies = [];
		let errors = 0;
		let completed = 0;
		const started = performance.now();
		startRef.current = started;
		const stopAt = mode === "duration" ? started + durationSec * 1e3 : Infinity;
		const worker = async () => {
			while (!controller.signal.aborted) {
				if (mode === "count" && completed + errors >= total) break;
				if (mode === "duration" && performance.now() >= stopAt) break;
				const t0 = performance.now();
				try {
					const res = await leoFetch(pickPath(mix.paths), { signal: controller.signal });
					const dt = performance.now() - t0;
					const ok = res.ok;
					samplesRef.current.push({
						t: (t0 - started) / 1e3,
						latencyMs: dt,
						ok
					});
					if (ok) {
						latencies.push(dt);
						completed += 1;
					} else errors += 1;
					try {
						await res.text();
					} catch {}
				} catch {
					errors += 1;
					samplesRef.current.push({
						t: (performance.now() - started) / 1e3,
						latencyMs: performance.now() - t0,
						ok: false
					});
				}
				if (mode === "count") setProgress(completed + errors);
				else setProgress(Math.min(100, (performance.now() - started) / (durationSec * 1e3) * 100));
			}
		};
		try {
			await Promise.all(Array.from({ length: concurrency }, () => worker()));
		} finally {
			finalize(controller, completed, errors, latencies, started);
		}
	}
	function finalize(controller, completed, errors, latencies, started) {
		const durationMs = performance.now() - started;
		const sorted = [...latencies].sort((a, b) => a - b);
		const sum = sorted.reduce((a, b) => a + b, 0);
		const totalReq = latencies.length + errors;
		const label = mix.paths.length === 1 ? mix.paths[0].path : `mix:${mix.id}`;
		const r = {
			id: `${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
			timestamp: (/* @__PURE__ */ new Date()).toISOString(),
			apiBase: getApiBase(),
			path: label,
			totalRequests: totalReq,
			concurrency,
			durationMs,
			errors,
			errorRatePct: totalReq ? errors / totalReq * 100 : 0,
			throughputRps: durationMs > 0 ? latencies.length / durationMs * 1e3 : 0,
			p50Ms: percentile$2(sorted, 50),
			p95Ms: percentile$2(sorted, 95),
			p99Ms: percentile$2(sorted, 99),
			minMs: sorted[0] ?? 0,
			maxMs: sorted[sorted.length - 1] ?? 0,
			meanMs: sorted.length ? sum / sorted.length : 0
		};
		setResult(r);
		setPhase("done");
		if (totalReq > 0) {
			saveRun(r);
			onResult?.(r);
			onLiveRun?.(r.throughputRps);
			if (r.errorRatePct > 50) toast.error(`Benchmark: ${r.errors}/${totalReq} failed`);
			else toast.success(`Benchmark done · ${r.throughputRps.toFixed(1)} rps`);
		}
		setRunning(false);
		abortRef.current = null;
	}
	function stop() {
		abortRef.current?.abort();
	}
	function exportJson() {
		if (!result) return;
		const payload = {
			...result,
			config: {
				mode,
				total,
				durationSec,
				concurrency,
				warmupSec,
				mix
			},
			userAgent: typeof navigator !== "undefined" ? navigator.userAgent : "",
			buckets,
			liveMetrics: live
		};
		const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
		const url = URL.createObjectURL(blob);
		const a = document.createElement("a");
		a.href = url;
		a.download = `leo-benchmark-${Date.now()}.json`;
		a.click();
		URL.revokeObjectURL(url);
	}
	const progressPct = mode === "count" ? progress / Math.max(1, total) * 100 : Math.min(100, progress);
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
		"aria-labelledby": "bench-runner-title",
		className: "border border-border bg-background p-6",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "eyebrow",
				children: "Load test"
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
				id: "bench-runner-title",
				className: "mt-1 font-display text-2xl font-bold",
				children: "Benchmark run"
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
				className: "mt-1 text-xs text-muted-foreground",
				children: [
					"Configurable load against",
					" ",
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
						className: "font-mono text-leo",
						children: getApiBase() || "(no backend)"
					}),
					". Live server counters stream over SSE from ",
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
						className: "font-mono",
						children: "/api/v1/leo/metrics/stream"
					}),
					"."
				]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("label", {
						className: "flex flex-col gap-1 text-xs",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "uppercase tracking-wide text-muted-foreground",
							children: "Mode"
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("select", {
							value: mode,
							onChange: (e) => setMode(e.target.value),
							disabled: running,
							className: "border border-border bg-background px-2 py-1 font-mono text-xs focus:border-leo focus:outline-none",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("option", {
								value: "count",
								children: "Fixed requests"
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("option", {
								value: "duration",
								children: "Fixed duration"
							})]
						})]
					}),
					mode === "count" ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("label", {
						className: "flex flex-col gap-1 text-xs",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "uppercase tracking-wide text-muted-foreground",
							children: "Total requests"
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("input", {
							type: "number",
							min: 1,
							max: 5e3,
							value: total,
							disabled: running,
							onChange: (e) => setTotal(Math.min(5e3, Math.max(1, Number(e.target.value) || 1))),
							className: "border border-border bg-background px-2 py-1 font-mono text-xs focus:border-leo focus:outline-none"
						})]
					}) : /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("label", {
						className: "flex flex-col gap-1 text-xs",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "uppercase tracking-wide text-muted-foreground",
							children: "Duration (s)"
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("input", {
							type: "number",
							min: 1,
							max: 600,
							value: durationSec,
							disabled: running,
							onChange: (e) => setDurationSec(Math.min(600, Math.max(1, Number(e.target.value) || 1))),
							className: "border border-border bg-background px-2 py-1 font-mono text-xs focus:border-leo focus:outline-none"
						})]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("label", {
						className: "flex flex-col gap-1 text-xs",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "uppercase tracking-wide text-muted-foreground",
							children: "Concurrency"
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("input", {
							type: "number",
							min: 1,
							max: 64,
							value: concurrency,
							disabled: running,
							onChange: (e) => setConcurrency(Math.min(64, Math.max(1, Number(e.target.value) || 1))),
							className: "border border-border bg-background px-2 py-1 font-mono text-xs focus:border-leo focus:outline-none"
						})]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("label", {
						className: "flex flex-col gap-1 text-xs",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "uppercase tracking-wide text-muted-foreground",
							children: "Warm-up (s)"
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("input", {
							type: "number",
							min: 0,
							max: 60,
							value: warmupSec,
							disabled: running,
							onChange: (e) => setWarmupSec(Math.min(60, Math.max(0, Number(e.target.value) || 0))),
							className: "border border-border bg-background px-2 py-1 font-mono text-xs focus:border-leo focus:outline-none"
						})]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("label", {
						className: "flex flex-col gap-1 text-xs sm:col-span-2",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
								className: "uppercase tracking-wide text-muted-foreground",
								children: "Request mix"
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("select", {
								value: mixId,
								onChange: (e) => setMixId(e.target.value),
								disabled: running,
								className: "border border-border bg-background px-2 py-1 font-mono text-xs focus:border-leo focus:outline-none",
								children: MIX_PRESETS.map((p) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("option", {
									value: p.id,
									children: p.label
								}, p.id))
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
								className: "text-[10px] text-muted-foreground",
								children: mix.description
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
								className: "font-mono text-[10px] text-muted-foreground",
								children: mix.paths.map((p) => `${p.path} × ${p.weight}`).join("  ·  ")
							})
						]
					})
				]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mt-4 flex flex-wrap items-center gap-3",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
						type: "button",
						onClick: run,
						disabled: running,
						className: "border border-leo bg-leo px-4 py-2 text-xs font-semibold text-primary-foreground hover:bg-leo/90 disabled:opacity-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-leo",
						children: running ? phase === "warmup" ? "Warming up…" : "Running…" : "Run benchmark"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
						type: "button",
						onClick: stop,
						disabled: !running,
						className: "border border-border px-4 py-2 text-xs hover:border-leo hover:text-leo disabled:opacity-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-leo",
						children: "Stop"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
						type: "button",
						onClick: exportJson,
						disabled: !result,
						className: "border border-border px-4 py-2 text-xs hover:border-leo hover:text-leo disabled:opacity-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-leo",
						children: "Export JSON"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("fieldset", {
						className: "inline-flex items-stretch border border-border text-[10px]",
						"aria-label": "Live-metrics transport mode",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("legend", {
							className: "sr-only",
							children: "Live-metrics transport mode"
						}), [
							"auto",
							"sse-only",
							"polling-only"
						].map((m) => {
							const active = transportMode === m;
							return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("button", {
								type: "button",
								onClick: () => changeTransportMode(m),
								className: `px-2 py-1 border-l first:border-l-0 border-border font-mono focus:outline-none focus-visible:ring-2 focus-visible:ring-leo ${active ? "bg-leo/20 text-leo" : "text-muted-foreground hover:text-leo"}`,
								"aria-pressed": active,
								title: m === "auto" ? "Prefer SSE, auto-fallback to 2s polling after repeated errors" : m === "sse-only" ? "Force EventSource; do not fall back to polling" : "Skip EventSource; poll /api/v1/leo/metrics every 2s",
								children: [m === "auto" ? "Auto" : m === "sse-only" ? "SSE" : "Poll", active && (m === "sse-only" && transport === "sse" || m === "polling-only" && transport === "polling" || m === "auto" && running) ? " •" : ""]
							}, m);
						})]
					}),
					running && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
						className: "font-mono text-xs text-muted-foreground",
						"aria-live": "polite",
						children: phase === "warmup" ? `warmup ${warmupSec}s` : mode === "count" ? `${progress}/${total}` : `${progressPct.toFixed(0)}%`
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
						className: `ml-auto font-mono text-[10px] ${streamStatus === "open" ? "text-leo" : streamStatus === "error" ? "text-destructive" : streamStatus === "polling" ? "text-yellow-600" : "text-muted-foreground"}`,
						"aria-live": "polite",
						children: [
							transport === "sse" ? "SSE" : "POLL",
							": ",
							streamStatus,
							streamStatus === "reconnecting" && reconnectAttempts > 0 ? ` · attempt ${reconnectAttempts}` : ""
						]
					})
				]
			}),
			(running || live.length > 0) && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mt-4 grid gap-3 border border-border bg-muted/10 p-3 text-[11px] sm:grid-cols-2 lg:grid-cols-4",
				role: "region",
				"aria-label": "Stream and render diagnostics",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(DiagStat, {
						label: "Transport",
						value: transport === "sse" ? "Server-Sent Events" : "Polling (2s)",
						tone: transport === "sse" ? "leo" : "warn"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(DiagStat, {
						label: "Stream state",
						value: `${streamStatus}${reconnectAttempts > 0 ? ` · ${reconnectAttempts} retries` : ""}`,
						tone: streamStatus === "open" ? "leo" : streamStatus === "reconnecting" || streamStatus === "polling" ? "warn" : streamStatus === "error" ? "err" : "muted"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(DiagStat, {
						label: "Last event",
						value: lastEventAt == null ? "—" : `${(lastEventDelta / 1e3).toFixed(1)}s ago`,
						tone: lastEventDelta > 5e3 ? "warn" : "muted"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(DiagStat, {
						label: "Render commits",
						value: `${perfSnapshot.renders} · Δ${perfSnapshot.lastMs.toFixed(0)}ms`,
						tone: perfSnapshot.lastMs > 100 ? "warn" : "muted"
					}),
					lastError && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "sm:col-span-2 lg:col-span-4 border-t border-border/60 pt-2 font-mono text-destructive",
						children: ["error: ", lastError]
					})
				]
			}),
			running && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "mt-3 h-1 w-full bg-border",
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "h-full bg-leo transition-[width]",
					style: { width: `${progressPct}%` }
				})
			}),
			(running || buckets.length > 0) && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(import_jsx_runtime.Fragment, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("fieldset", {
				className: "mt-6 inline-flex flex-wrap items-center gap-3 border border-border bg-background/60 px-3 py-2 text-[11px]",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("legend", {
						className: "px-1 text-[10px] uppercase tracking-wide text-muted-foreground",
						children: "Chart options"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("label", {
						className: "inline-flex items-center gap-1",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "text-muted-foreground",
							children: "Range"
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("select", {
							value: chartOpts.rangeBuckets,
							onChange: (e) => setChartOpts({ rangeBuckets: Number(e.target.value) }),
							className: "border border-border bg-background px-2 py-0.5 font-mono focus:border-leo focus:outline-none",
							"aria-label": "Chart range",
							children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("option", {
									value: 30,
									children: "last 30s"
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("option", {
									value: 60,
									children: "last 60s"
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("option", {
									value: 120,
									children: "last 120s"
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("option", {
									value: 0,
									children: "all"
								})
							]
						})]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("label", {
						className: "inline-flex items-center gap-1",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "text-muted-foreground",
							children: "Smoothing"
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("select", {
							value: chartOpts.smoothingWindow,
							onChange: (e) => setChartOpts({ smoothingWindow: Number(e.target.value) }),
							className: "border border-border bg-background px-2 py-0.5 font-mono focus:border-leo focus:outline-none",
							"aria-label": "Smoothing window",
							children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("option", {
									value: 1,
									children: "off"
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("option", {
									value: 3,
									children: "3-pt"
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("option", {
									value: 5,
									children: "5-pt"
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("option", {
									value: 7,
									children: "7-pt"
								})
							]
						})]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("label", {
						className: "inline-flex items-center gap-1",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("input", {
							type: "checkbox",
							checked: chartOpts.showLatency,
							onChange: (e) => setChartOpts({ showLatency: e.target.checked })
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { children: "Latency" })]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("label", {
						className: "inline-flex items-center gap-1",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("input", {
							type: "checkbox",
							checked: chartOpts.showThroughput,
							onChange: (e) => setChartOpts({ showThroughput: e.target.checked })
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { children: "Throughput" })]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
						className: "text-muted-foreground",
						children: "saved automatically"
					})
				]
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: `mt-3 grid gap-6 ${chartOpts.showLatency && chartOpts.showThroughput ? "lg:grid-cols-2" : ""}`,
				children: [chartOpts.showLatency && /* @__PURE__ */ (0, import_jsx_runtime.jsx)(LiveChart, {
					title: "Latency (mean per 1s bucket)",
					buckets,
					kind: "latency",
					rangeBuckets: chartOpts.rangeBuckets,
					smoothingWindow: chartOpts.smoothingWindow
				}), chartOpts.showThroughput && /* @__PURE__ */ (0, import_jsx_runtime.jsx)(LiveChart, {
					title: "Throughput (req/s per 1s bucket)",
					buckets,
					kind: "throughput",
					rangeBuckets: chartOpts.rangeBuckets,
					smoothingWindow: chartOpts.smoothingWindow
				})]
			})] }),
			live.length > 0 && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mt-6 border border-border bg-muted/10 p-4",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "eyebrow",
					children: "Live server counters (SSE)"
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "mt-2 grid gap-3 text-xs sm:grid-cols-3",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(LiveStat, {
							label: "Server rps (60s)",
							value: live[live.length - 1]?.rps60?.toFixed(2) ?? "—"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(LiveStat, {
							label: "Server total",
							value: live[live.length - 1]?.total?.toLocaleString() ?? "—"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(LiveStat, {
							label: "Samples",
							value: String(live.length)
						})
					]
				})]
			}),
			result && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mt-6 grid gap-px bg-border sm:grid-cols-2 lg:grid-cols-4",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Stat$1, {
						label: "Throughput",
						value: `${result.throughputRps.toFixed(1)} rps`,
						highlight: true
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Stat$1, {
						label: "Error rate",
						value: `${result.errorRatePct.toFixed(2)}%`
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Stat$1, {
						label: "Requests",
						value: `${result.totalRequests}`
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Stat$1, {
						label: "Duration",
						value: `${(result.durationMs / 1e3).toFixed(2)}s`
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Stat$1, {
						label: "p50",
						value: `${result.p50Ms.toFixed(1)} ms`
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Stat$1, {
						label: "p95",
						value: `${result.p95Ms.toFixed(1)} ms`,
						highlight: true
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Stat$1, {
						label: "p99",
						value: `${result.p99Ms.toFixed(1)} ms`,
						highlight: true
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Stat$1, {
						label: "min / max",
						value: `${result.minMs.toFixed(0)} / ${result.maxMs.toFixed(0)} ms`
					})
				]
			})
		]
	});
}
function Stat$1({ label, value, highlight }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "bg-background p-4",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: "text-[11px] uppercase tracking-wide text-muted-foreground",
			children: label
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: `mt-1 font-display text-xl font-bold ${highlight ? "text-leo" : "text-foreground"}`,
			children: value
		})]
	});
}
function LiveStat({ label, value }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
		className: "text-[11px] uppercase tracking-wide text-muted-foreground",
		children: label
	}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
		className: "mt-1 font-mono text-lg text-leo",
		children: value
	})] });
}
var LiveChart = (0, import_react.memo)(function LiveChart({ title, buckets, kind, rangeBuckets = 120, smoothingWindow = 1 }) {
	const w = 480;
	const h = 140;
	const pad = 24;
	const visible = (0, import_react.useMemo)(() => {
		if (rangeBuckets <= 0) return buckets;
		return buckets.length > rangeBuckets ? buckets.slice(-rangeBuckets) : buckets;
	}, [buckets, rangeBuckets]);
	const { values, points, max, stepX } = (0, import_react.useMemo)(() => {
		const vals = smoothSeries(visible.map((b) => kind === "latency" ? b.count > 0 ? b.sumMs / b.count : 0 : b.count), smoothingWindow);
		const mx = Math.max(1, ...vals);
		const step = visible.length > 1 ? (w - pad * 2) / (visible.length - 1) : 0;
		return {
			values: vals,
			points: vals.map((v, i) => {
				const x = pad + i * step;
				const y = h - pad - v / mx * (h - pad * 2);
				return `${x.toFixed(1)},${y.toFixed(1)}`;
			}).join(" "),
			max: mx,
			stepX: step
		};
	}, [
		visible,
		kind,
		smoothingWindow
	]);
	const unit = kind === "latency" ? "ms" : "rps";
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("figure", {
		className: "border border-border bg-background p-4",
		"aria-label": title,
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("figcaption", {
				className: "mb-2 flex items-baseline justify-between",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
					className: "text-[11px] uppercase tracking-wide text-muted-foreground",
					children: title
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
					className: "font-mono text-xs text-leo",
					children: [
						"peak ",
						max.toFixed(kind === "latency" ? 1 : 0),
						" ",
						unit,
						smoothingWindow > 1 ? ` · smooth ${smoothingWindow}` : ""
					]
				})]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("svg", {
				viewBox: `0 0 ${w} ${h}`,
				preserveAspectRatio: "none",
				className: "h-32 w-full",
				role: "img",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("line", {
						x1: pad,
						y1: h - pad,
						x2: w - pad,
						y2: h - pad,
						stroke: "currentColor",
						opacity: "0.2"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("line", {
						x1: pad,
						y1: pad,
						x2: pad,
						y2: h - pad,
						stroke: "currentColor",
						opacity: "0.2"
					}),
					points && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("polyline", {
						points,
						fill: "none",
						stroke: "#76B900",
						strokeWidth: "1.5",
						strokeLinejoin: "round"
					}),
					values.map((v, i) => {
						return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("circle", {
							cx: pad + i * stepX,
							cy: h - pad - v / max * (h - pad * 2),
							r: "1.5",
							fill: "#76B900"
						}, i);
					})
				]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mt-1 flex justify-between text-[10px] text-muted-foreground",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { children: "0s" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { children: visible.length > 0 ? `${visible[visible.length - 1].tSec}s` : "—" })]
			})
		]
	});
}, (prev, next) => {
	if (prev.kind !== next.kind || prev.title !== next.title || prev.rangeBuckets !== next.rangeBuckets || prev.smoothingWindow !== next.smoothingWindow) return false;
	const a = prev.buckets;
	const b = next.buckets;
	if (a.length !== b.length) return false;
	if (a.length === 0) return true;
	const la = a[a.length - 1];
	const lb = b[b.length - 1];
	return la.tSec === lb.tSec && la.count === lb.count && la.sumMs === lb.sumMs && la.errors === lb.errors;
});
function DiagStat({ label, value, tone = "muted" }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
		className: "text-[10px] uppercase tracking-wide text-muted-foreground",
		children: label
	}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
		className: `mt-0.5 font-mono ${tone === "leo" ? "text-leo" : tone === "warn" ? "text-yellow-600" : tone === "err" ? "text-destructive" : "text-foreground"}`,
		children: value
	})] });
}
function toB64Url$1(s) {
	return (typeof btoa !== "undefined" ? btoa(unescape(encodeURIComponent(s))) : "").replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}
function fromB64Url$1(s) {
	const b64 = s.replace(/-/g, "+").replace(/_/g, "/") + "===".slice((s.length + 3) % 4);
	return typeof atob !== "undefined" ? decodeURIComponent(escape(atob(b64))) : "";
}
function encodeRunShare(run) {
	return toB64Url$1(JSON.stringify(run));
}
function encodeComparisonShare(base, target) {
	return toB64Url$1(JSON.stringify({
		b: base,
		t: target
	}));
}
function decodeRunShare(payload) {
	try {
		return JSON.parse(fromB64Url$1(payload));
	} catch {
		return null;
	}
}
function decodeComparisonShare(payload) {
	try {
		const p = JSON.parse(fromB64Url$1(payload));
		return {
			base: p.b,
			target: p.t
		};
	} catch {
		return null;
	}
}
function buildShareUrl(kind, payload) {
	if (typeof window === "undefined") return "";
	const u = new URL(window.location.href);
	u.searchParams.delete("run");
	u.searchParams.delete("compare");
	u.searchParams.set(kind, payload);
	return u.toString();
}
function readShareParams() {
	if (typeof window === "undefined") return {
		run: null,
		compare: null
	};
	const u = new URL(window.location.href);
	const runP = u.searchParams.get("run");
	const cmpP = u.searchParams.get("compare");
	return {
		run: runP ? decodeRunShare(runP) : null,
		compare: cmpP ? decodeComparisonShare(cmpP) : null
	};
}
var COLS = [
	{
		key: "timestamp",
		label: "When"
	},
	{
		key: "path",
		label: "Path"
	},
	{
		key: "totalRequests",
		label: "N",
		num: true
	},
	{
		key: "concurrency",
		label: "C",
		num: true
	},
	{
		key: "throughputRps",
		label: "rps",
		num: true
	},
	{
		key: "p50Ms",
		label: "p50",
		num: true
	},
	{
		key: "p95Ms",
		label: "p95",
		num: true
	},
	{
		key: "p99Ms",
		label: "p99",
		num: true
	},
	{
		key: "errorRatePct",
		label: "err%",
		num: true
	}
];
function BenchmarkHistory({ selectedId, onSelect }) {
	const runs = useBenchmarkHistory();
	const [sortKey, setSortKey] = (0, import_react.useState)("timestamp");
	const [dir, setDir] = (0, import_react.useState)("desc");
	const sorted = (0, import_react.useMemo)(() => {
		const arr = [...runs];
		arr.sort((a, b) => {
			const av = a[sortKey];
			const bv = b[sortKey];
			const cmp = typeof av === "number" && typeof bv === "number" ? av - bv : String(av).localeCompare(String(bv));
			return dir === "asc" ? cmp : -cmp;
		});
		return arr;
	}, [
		runs,
		sortKey,
		dir
	]);
	function toggle(k) {
		if (k === sortKey) setDir(dir === "asc" ? "desc" : "asc");
		else {
			setSortKey(k);
			setDir(k === "timestamp" ? "desc" : "desc");
		}
	}
	const fileRef = (0, import_react.useRef)(null);
	const [importReport, setImportReport] = (0, import_react.useState)(null);
	const [schemaReport, setSchemaReport] = (0, import_react.useState)(null);
	async function onImportFile(e) {
		const file = e.target.files?.[0];
		e.target.value = "";
		if (!file) return;
		try {
			const text = await file.text();
			const schema = validateSchema(text, file.name);
			setSchemaReport({
				...schema,
				fileName: file.name
			});
			if (!schema.ok) {
				const errs = schema.issues.filter((i) => i.severity === "error").length;
				toast.error(`Schema check failed — ${errs} error${errs === 1 ? "" : "s"}. See details below.`);
				setImportReport(null);
				return;
			}
			const parsed = parseImportedFile(text, file.name);
			if (parsed.length === 0) {
				toast.error("No benchmark runs found in file");
				setImportReport({
					added: 0,
					skipped: 0,
					invalid: 0,
					total: 0,
					issues: [],
					fileName: file.name
				});
				return;
			}
			const res = importRuns(parsed, "merge");
			setImportReport({
				...res,
				fileName: file.name
			});
			const parts = [`${res.added} merged`];
			if (res.skipped) parts.push(`${res.skipped} duplicate`);
			if (res.invalid) parts.push(`${res.invalid} invalid`);
			const msg = `Import: ${parts.join(" · ")}`;
			if (res.invalid > 0) toast.warning(msg);
			else toast.success(msg);
		} catch (err) {
			toast.error("Import failed: " + err.message);
			setImportReport({
				added: 0,
				skipped: 0,
				invalid: 1,
				total: 0,
				issues: [{
					rowIndex: 0,
					status: "invalid",
					reason: err.message
				}],
				fileName: file.name
			});
		}
	}
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
		"aria-labelledby": "bench-history-title",
		className: "border border-border bg-background p-6",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex flex-wrap items-center justify-between gap-3",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "eyebrow",
						children: "History"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
						id: "bench-history-title",
						className: "mt-1 font-display text-2xl font-bold",
						children: "Saved benchmark runs"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "mt-1 text-xs text-muted-foreground",
						children: "Click a row to link the Hardware profile ratio to that run."
					})
				] }), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "flex flex-wrap gap-2",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("input", {
							ref: fileRef,
							type: "file",
							accept: ".json,.csv,application/json,text/csv",
							onChange: onImportFile,
							className: "hidden",
							"aria-label": "Import benchmark history file"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
							type: "button",
							onClick: () => fileRef.current?.click(),
							className: "border border-leo/60 px-3 py-1.5 text-xs text-leo hover:bg-leo/10 focus:outline-none focus-visible:ring-2 focus-visible:ring-leo",
							children: "Import JSON / CSV"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "inline-flex items-stretch border border-border text-xs",
							role: "group",
							"aria-label": "Download import template",
							children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
									className: "px-2 py-1.5 text-muted-foreground",
									children: "Template"
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
									type: "button",
									onClick: () => downloadTemplate("json"),
									className: "border-l border-border px-2 py-1.5 hover:border-leo hover:text-leo focus:outline-none focus-visible:ring-2 focus-visible:ring-leo",
									title: "Download an example JSON matching the import schema",
									children: "JSON"
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
									type: "button",
									onClick: () => downloadTemplate("csv"),
									className: "border-l border-border px-2 py-1.5 hover:border-leo hover:text-leo focus:outline-none focus-visible:ring-2 focus-visible:ring-leo",
									title: "Download an example CSV matching the import schema",
									children: "CSV"
								})
							]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
							type: "button",
							onClick: async () => {
								const sel = runs.find((r) => r.id === selectedId);
								if (!sel) {
									toast.error("Select a run first");
									return;
								}
								const url = buildShareUrl("run", encodeRunShare(sel));
								try {
									await navigator.clipboard.writeText(url);
									toast.success("Run share link copied");
								} catch {
									toast.error("Copy failed");
								}
							},
							disabled: !selectedId,
							className: "border border-border px-3 py-1.5 text-xs hover:border-leo hover:text-leo disabled:opacity-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-leo",
							children: "Share selected"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
							type: "button",
							onClick: () => downloadRuns(runs, "json"),
							disabled: runs.length === 0,
							className: "border border-border px-3 py-1.5 text-xs hover:border-leo hover:text-leo disabled:opacity-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-leo",
							children: "Export JSON"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
							type: "button",
							onClick: () => downloadRuns(runs, "csv"),
							disabled: runs.length === 0,
							className: "border border-border px-3 py-1.5 text-xs hover:border-leo hover:text-leo disabled:opacity-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-leo",
							children: "Export CSV"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
							type: "button",
							onClick: () => {
								clearHistory();
								onSelect?.(null);
							},
							disabled: runs.length === 0,
							className: "border border-border px-3 py-1.5 text-xs hover:border-destructive hover:text-destructive disabled:opacity-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-destructive",
							children: "Clear"
						})
					]
				})]
			}),
			schemaReport && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				role: "status",
				"aria-live": "polite",
				className: `mt-4 border p-3 text-xs ${schemaReport.ok ? "border-border bg-muted/10" : "border-destructive/60 bg-destructive/10 text-destructive"}`,
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "flex flex-wrap items-baseline justify-between gap-2",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
								className: "eyebrow",
								children: "Schema check"
							}),
							" ",
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
								className: "font-mono text-muted-foreground",
								children: schemaReport.fileName
							}),
							" ",
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
								className: "font-mono text-[10px] uppercase text-muted-foreground",
								children: schemaReport.format
							})
						] }), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "flex items-center gap-3 font-mono",
							children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", { children: [schemaReport.rowCount, " rows"] }),
								/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", { children: [schemaReport.detectedFields.length, " fields"] }),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
									className: schemaReport.ok ? "text-leo" : "text-destructive",
									children: schemaReport.ok ? "OK" : "FAIL"
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
									type: "button",
									onClick: () => setSchemaReport(null),
									className: "text-muted-foreground hover:text-leo focus:outline-none focus-visible:ring-2 focus-visible:ring-leo",
									"aria-label": "Dismiss schema report",
									children: "×"
								})
							]
						})]
					}),
					schemaReport.issues.length > 0 && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("ul", {
						className: "mt-2 space-y-0.5 font-mono text-[11px]",
						children: [schemaReport.issues.slice(0, 30).map((iss, i) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", {
							className: iss.severity === "error" ? "text-destructive" : "text-yellow-600",
							children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
									className: "mr-1 uppercase",
									children: [
										"[",
										iss.severity,
										"]"
									]
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
									className: "mr-1",
									children: [iss.field, ":"]
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
									className: "text-muted-foreground",
									children: iss.message
								})
							]
						}, i)), schemaReport.issues.length > 30 && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", {
							className: "text-[10px] text-muted-foreground",
							children: [
								"… ",
								schemaReport.issues.length - 30,
								" more issues suppressed."
							]
						})]
					}),
					schemaReport.detectedFields.length > 0 && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
						className: "mt-2 text-[10px] text-muted-foreground",
						children: [
							"Detected fields:",
							" ",
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
								className: "font-mono",
								children: schemaReport.detectedFields.join(", ")
							})
						]
					})
				]
			}),
			importReport && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				role: "status",
				"aria-live": "polite",
				className: "mt-4 border border-border bg-muted/10 p-3 text-xs",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "flex flex-wrap items-baseline justify-between gap-2",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "eyebrow",
							children: "Import report"
						}),
						" ",
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "font-mono text-muted-foreground",
							children: importReport.fileName
						})
					] }), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "flex gap-3 font-mono",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
								className: "text-leo",
								children: [importReport.added, " merged"]
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
								className: "text-muted-foreground",
								children: [importReport.skipped, " duplicate"]
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
								className: importReport.invalid ? "text-destructive" : "text-muted-foreground",
								children: [importReport.invalid, " invalid"]
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
								type: "button",
								onClick: () => setImportReport(null),
								className: "text-muted-foreground hover:text-leo focus:outline-none focus-visible:ring-2 focus-visible:ring-leo",
								"aria-label": "Dismiss import report",
								children: "×"
							})
						]
					})]
				}), importReport.issues.length > 0 && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("details", {
					className: "mt-2",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("summary", {
						className: "cursor-pointer text-[11px] uppercase tracking-wide text-muted-foreground hover:text-leo",
						children: [
							"Row-level details (",
							importReport.issues.length,
							")"
						]
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "mt-2 max-h-48 overflow-y-auto",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("table", {
							className: "w-full text-[11px]",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("thead", {
								className: "text-muted-foreground",
								children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("tr", { children: [
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("th", {
										className: "text-left px-2 py-1",
										children: "Row"
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("th", {
										className: "text-left px-2 py-1",
										children: "Status"
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("th", {
										className: "text-left px-2 py-1",
										children: "ID"
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("th", {
										className: "text-left px-2 py-1",
										children: "Reason"
									})
								] })
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("tbody", { children: importReport.issues.slice(0, 200).map((iss, i) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("tr", {
								className: "border-t border-border/40",
								children: [
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
										className: "px-2 py-1 font-mono",
										children: iss.rowIndex + 1
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
										className: `px-2 py-1 font-mono ${iss.status === "invalid" ? "text-destructive" : iss.status === "duplicate" ? "text-yellow-600" : "text-leo"}`,
										children: iss.status
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
										className: "px-2 py-1 font-mono truncate max-w-[180px]",
										title: iss.id ?? "",
										children: iss.id ?? "—"
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
										className: "px-2 py-1 text-muted-foreground",
										children: iss.reason ?? ""
									})
								]
							}, i)) })]
						}), importReport.issues.length > 200 && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
							className: "mt-2 text-[10px] text-muted-foreground",
							children: [
								"Showing first 200 of ",
								importReport.issues.length,
								" rows."
							]
						})]
					})]
				})]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "mt-4 overflow-x-auto",
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("table", {
					className: "w-full min-w-[720px] border-collapse text-xs",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("thead", { children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("tr", {
						className: "border-b border-border text-[11px] uppercase tracking-wide text-muted-foreground",
						children: COLS.map((c) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("th", {
							scope: "col",
							className: `px-3 py-2 ${c.num ? "text-right" : "text-left"}`,
							children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("button", {
								type: "button",
								onClick: () => toggle(c.key),
								className: "inline-flex items-center gap-1 hover:text-leo focus:outline-none focus-visible:ring-2 focus-visible:ring-leo",
								"aria-sort": sortKey === c.key ? dir === "asc" ? "ascending" : "descending" : "none",
								children: [c.label, sortKey === c.key && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
									"aria-hidden": true,
									children: dir === "asc" ? "↑" : "↓"
								})]
							})
						}, c.key))
					}) }), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("tbody", { children: [sorted.length === 0 && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("tr", { children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
						colSpan: COLS.length,
						className: "px-3 py-6 text-center text-muted-foreground",
						children: "No runs yet. Run a benchmark to populate history."
					}) }), sorted.map((r) => {
						const isSel = r.id === selectedId;
						return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("tr", {
							onClick: () => onSelect?.(isSel ? null : r),
							className: `cursor-pointer border-b border-border/60 hover:bg-muted/30 ${isSel ? "bg-leo/10" : ""}`,
							children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
									className: "px-3 py-2 font-mono",
									children: new Date(r.timestamp).toLocaleString()
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
									className: "px-3 py-2 font-mono truncate max-w-[200px]",
									title: r.path,
									children: r.path
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
									className: "px-3 py-2 text-right font-mono",
									children: r.totalRequests
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
									className: "px-3 py-2 text-right font-mono",
									children: r.concurrency
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
									className: "px-3 py-2 text-right font-mono text-leo",
									children: r.throughputRps.toFixed(1)
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
									className: "px-3 py-2 text-right font-mono",
									children: r.p50Ms.toFixed(1)
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
									className: "px-3 py-2 text-right font-mono",
									children: r.p95Ms.toFixed(1)
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
									className: "px-3 py-2 text-right font-mono",
									children: r.p99Ms.toFixed(1)
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
									className: `px-3 py-2 text-right font-mono ${r.errorRatePct > 5 ? "text-destructive" : ""}`,
									children: r.errorRatePct.toFixed(2)
								})
							]
						}, r.id);
					})] })]
				})
			})
		]
	});
}
var KEY$3 = "leo.bench.thresholds";
var DEFAULT_THRESHOLDS = {
	enabled: true,
	p50PctIncrease: 15,
	p95PctIncrease: 20,
	p99PctIncrease: 25,
	errorRateAbsPct: 2,
	throughputPctDrop: 15
};
function read$2() {
	if (typeof window === "undefined") return DEFAULT_THRESHOLDS;
	try {
		const raw = window.localStorage.getItem(KEY$3);
		return raw ? {
			...DEFAULT_THRESHOLDS,
			...JSON.parse(raw)
		} : DEFAULT_THRESHOLDS;
	} catch {
		return DEFAULT_THRESHOLDS;
	}
}
function useRegressionThresholds() {
	const [t, setT] = (0, import_react.useState)(DEFAULT_THRESHOLDS);
	(0, import_react.useEffect)(() => {
		setT(read$2());
		const on = () => setT(read$2());
		window.addEventListener("leo:thresholds", on);
		window.addEventListener("storage", on);
		return () => {
			window.removeEventListener("leo:thresholds", on);
			window.removeEventListener("storage", on);
		};
	}, []);
	const save = (next) => {
		setT(next);
		try {
			window.localStorage.setItem(KEY$3, JSON.stringify(next));
			window.dispatchEvent(new CustomEvent("leo:thresholds"));
		} catch {}
	};
	return [t, save];
}
function evaluateRegressions(base, target, t) {
	if (!base || !target || !t.enabled) return [];
	const findings = [];
	const pct = (a, b) => a === 0 ? b === 0 ? 0 : 100 : (b - a) / Math.abs(a) * 100;
	const checks = [
		{
			metric: "p50",
			label: "p50 latency",
			delta: pct(base.p50Ms, target.p50Ms),
			breach: t.p50PctIncrease,
			triggered: pct(base.p50Ms, target.p50Ms) > t.p50PctIncrease
		},
		{
			metric: "p95",
			label: "p95 latency",
			delta: pct(base.p95Ms, target.p95Ms),
			breach: t.p95PctIncrease,
			triggered: pct(base.p95Ms, target.p95Ms) > t.p95PctIncrease
		},
		{
			metric: "p99",
			label: "p99 latency",
			delta: pct(base.p99Ms, target.p99Ms),
			breach: t.p99PctIncrease,
			triggered: pct(base.p99Ms, target.p99Ms) > t.p99PctIncrease
		},
		{
			metric: "throughput",
			label: "throughput",
			delta: pct(base.throughputRps, target.throughputRps),
			breach: -t.throughputPctDrop,
			triggered: pct(base.throughputRps, target.throughputRps) < -t.throughputPctDrop
		},
		{
			metric: "errorRate",
			label: "error rate",
			delta: target.errorRatePct - base.errorRatePct,
			breach: t.errorRateAbsPct,
			triggered: target.errorRatePct >= t.errorRateAbsPct && target.errorRatePct > base.errorRatePct
		}
	];
	for (const c of checks) {
		if (!c.triggered) continue;
		const mag = Math.abs(c.delta) / Math.max(1, Math.abs(c.breach));
		findings.push({
			metric: c.metric,
			label: c.label,
			base: c.metric === "throughput" ? base.throughputRps : c.metric === "errorRate" ? base.errorRatePct : base[`${c.metric}Ms`],
			target: c.metric === "throughput" ? target.throughputRps : c.metric === "errorRate" ? target.errorRatePct : target[`${c.metric}Ms`],
			delta: c.delta,
			breach: c.breach,
			severity: mag >= 2 ? "critical" : "warn"
		});
	}
	return findings;
}
var METRICS = [
	{
		key: "throughputRps",
		label: "Throughput",
		unit: "rps",
		higherIsWorse: false,
		fmt: (v) => v.toFixed(1)
	},
	{
		key: "p50Ms",
		label: "p50",
		unit: "ms",
		higherIsWorse: true,
		fmt: (v) => v.toFixed(1)
	},
	{
		key: "p95Ms",
		label: "p95",
		unit: "ms",
		higherIsWorse: true,
		fmt: (v) => v.toFixed(1)
	},
	{
		key: "p99Ms",
		label: "p99",
		unit: "ms",
		higherIsWorse: true,
		fmt: (v) => v.toFixed(1)
	},
	{
		key: "meanMs",
		label: "mean",
		unit: "ms",
		higherIsWorse: true,
		fmt: (v) => v.toFixed(1)
	},
	{
		key: "errorRatePct",
		label: "Error rate",
		unit: "%",
		higherIsWorse: true,
		fmt: (v) => v.toFixed(2)
	}
];
function pctDelta(a, b) {
	if (a === 0) return b === 0 ? 0 : 100;
	return (b - a) / Math.abs(a) * 100;
}
function BenchmarkComparison({ presetBase, presetTarget } = {}) {
	const runs = useBenchmarkHistory();
	const [baseId, setBaseId] = (0, import_react.useState)("");
	const [targetId, setTargetId] = (0, import_react.useState)("");
	const [thresholds] = useRegressionThresholds();
	const cardRef = (0, import_react.useRef)(null);
	const options = (0, import_react.useMemo)(() => {
		const map = /* @__PURE__ */ new Map();
		for (const r of runs) map.set(r.id, r);
		if (presetBase) map.set(presetBase.id, presetBase);
		if (presetTarget) map.set(presetTarget.id, presetTarget);
		return [...map.values()].sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
	}, [
		runs,
		presetBase,
		presetTarget
	]);
	const base = options.find((r) => r.id === baseId) ?? presetBase ?? options[1] ?? null;
	const target = options.find((r) => r.id === targetId) ?? presetTarget ?? options[0] ?? null;
	const rows = (0, import_react.useMemo)(() => {
		if (!base || !target) return [];
		return METRICS.map((m) => {
			const a = Number(base[m.key] ?? 0);
			const b = Number(target[m.key] ?? 0);
			const delta = pctDelta(a, b);
			return {
				m,
				a,
				b,
				delta,
				improved: m.higherIsWorse ? delta < 0 : delta > 0,
				changed: Math.abs(delta) > .5
			};
		});
	}, [base, target]);
	const findings = (0, import_react.useMemo)(() => evaluateRegressions(base, target, thresholds), [
		base,
		target,
		thresholds
	]);
	const lastKeyRef = (0, import_react.useRef)("");
	(0, import_react.useEffect)(() => {
		if (!base || !target || findings.length === 0) return;
		const key = `${base.id}::${target.id}`;
		if (lastKeyRef.current === key) return;
		lastKeyRef.current = key;
		const critical = findings.filter((f) => f.severity === "critical").length;
		const msg = `Regression detected: ${findings.length} metric${findings.length > 1 ? "s" : ""} breached thresholds${critical > 0 ? ` (${critical} critical)` : ""}`;
		if (critical > 0) toast.error(msg);
		else toast.warning(msg);
	}, [
		findings,
		base,
		target
	]);
	async function copyShareLink() {
		if (!base || !target) return;
		const url = buildShareUrl("compare", encodeComparisonShare(base, target));
		try {
			await navigator.clipboard.writeText(url);
			toast.success("Share link copied");
		} catch {
			toast.error("Copy failed — link: " + url.slice(0, 60) + "…");
		}
	}
	const [exporting, setExporting] = (0, import_react.useState)(null);
	const [exportProgress, setExportProgress] = (0, import_react.useState)(null);
	const [lastExportError, setLastExportError] = (0, import_react.useState)(null);
	const [retryAttempts, setRetryAttempts] = (0, import_react.useState)({
		png: 0,
		pdf: 0
	});
	const cancelRef = (0, import_react.useRef)(null);
	(0, import_react.useEffect)(() => {
		if (!exportProgress) return;
		const id = window.setInterval(() => {
			setExportProgress((p) => p ? {
				...p,
				elapsedMs: Date.now() - p.startedAt
			} : p);
		}, 200);
		return () => window.clearInterval(id);
	}, [exportProgress?.startedAt, exportProgress]);
	function cancelExport() {
		if (cancelRef.current) cancelRef.current.cancelled = true;
		setExportProgress(null);
		setExporting(null);
		toast.message("Export cancelled");
	}
	function assertReady(kind) {
		if (!base || !target) return "Select both a baseline and target run before exporting.";
		if (options.length < 2) return "Save at least two benchmark runs to export a comparison.";
		if (!cardRef.current) return "Comparison card isn't mounted yet — try again in a moment.";
		const rect = cardRef.current.getBoundingClientRect();
		if (rect.width < 40 || rect.height < 40) return "Comparison card isn't fully rendered yet. Scroll it into view and retry.";
		if (rows.length === 0) return "No metric rows available to render.";
		return null;
	}
	async function exportPng() {
		const err = assertReady("png");
		if (err) {
			setLastExportError({
				kind: "png",
				reason: err,
				at: Date.now()
			});
			toast.error(err);
			return;
		}
		setExporting("png");
		const token = { cancelled: false };
		cancelRef.current = token;
		setExportProgress({
			kind: "png",
			startedAt: Date.now(),
			elapsedMs: 0,
			step: "waiting for layout"
		});
		const tid = toast.loading("Rendering PNG…");
		try {
			await new Promise((r) => requestAnimationFrame(() => r(null)));
			if (token.cancelled) throw new Error("cancelled");
			setExportProgress((p) => p ? {
				...p,
				step: "rasterizing"
			} : p);
			const dataUrl = await toPng(cardRef.current, {
				pixelRatio: 2,
				backgroundColor: getComputedStyle(document.body).backgroundColor || "#0a0a0a",
				cacheBust: true
			});
			if (token.cancelled) throw new Error("cancelled");
			setExportProgress((p) => p ? {
				...p,
				step: "downloading"
			} : p);
			const a = document.createElement("a");
			a.href = dataUrl;
			a.download = `leo-comparison-${Date.now()}.png`;
			a.click();
			setLastExportError(null);
			setRetryAttempts((r) => ({
				...r,
				png: 0
			}));
			toast.success("Comparison exported as PNG", { id: tid });
		} catch (e) {
			const reason = e.message || "unknown error";
			if (reason !== "cancelled") {
				setLastExportError({
					kind: "png",
					reason,
					at: Date.now()
				});
				setRetryAttempts((r) => ({
					...r,
					png: r.png + 1
				}));
				toast.error("PNG export failed: " + reason, { id: tid });
			} else toast.dismiss(tid);
		} finally {
			cancelRef.current = null;
			setExporting(null);
			setExportProgress(null);
		}
	}
	function printPdf() {
		const err = assertReady("pdf");
		if (err) {
			setLastExportError({
				kind: "pdf",
				reason: err,
				at: Date.now()
			});
			toast.error(err);
			return;
		}
		setExporting("pdf");
		setExportProgress({
			kind: "pdf",
			startedAt: Date.now(),
			elapsedMs: 0,
			step: "opening print dialog"
		});
		const token = { cancelled: false };
		cancelRef.current = token;
		const style = document.createElement("style");
		style.setAttribute("data-bench-print", "1");
		style.textContent = `
      @media print {
        body * { visibility: hidden !important; }
        [data-bench-compare-card], [data-bench-compare-card] * { visibility: visible !important; }
        [data-bench-compare-card] { position: absolute !important; left: 0; top: 0; width: 100%; padding: 24px; }
        [data-print-hide] { display: none !important; }
      }
    `;
		document.head.appendChild(style);
		const cleanup = () => {
			style.remove();
			cancelRef.current = null;
			setExporting(null);
			setExportProgress(null);
			window.removeEventListener("afterprint", cleanup);
		};
		window.addEventListener("afterprint", cleanup);
		try {
			window.print();
			if (token.cancelled) throw new Error("cancelled");
			setLastExportError(null);
			setRetryAttempts((r) => ({
				...r,
				pdf: 0
			}));
		} catch (e) {
			const reason = e.message || "unknown error";
			if (reason !== "cancelled") {
				setLastExportError({
					kind: "pdf",
					reason,
					at: Date.now()
				});
				setRetryAttempts((r) => ({
					...r,
					pdf: r.pdf + 1
				}));
				toast.error("Print failed: " + reason);
			}
			cleanup();
		}
	}
	function retryLastExport() {
		if (!lastExportError) return;
		const kind = lastExportError.kind;
		const attempts = retryAttempts[kind];
		const delay = Math.min(8e3, 500 * 2 ** Math.min(attempts, 4));
		const fallback = kind === "pdf" && attempts >= 2;
		if (fallback) toast.message(`PDF failed ${attempts}× — falling back to PNG in ${Math.round(delay / 100) / 10}s`);
		else toast.message(`Retrying ${kind.toUpperCase()} in ${Math.round(delay / 100) / 10}s (attempt ${attempts + 1})`);
		window.setTimeout(() => {
			if (fallback) exportPng();
			else if (kind === "png") exportPng();
			else printPdf();
		}, delay);
	}
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
		"aria-labelledby": "bench-compare-title",
		className: "border border-border bg-background p-6",
		"data-bench-compare-card": true,
		ref: cardRef,
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex flex-wrap items-center justify-between gap-3",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "eyebrow",
						children: "Compare"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
						id: "bench-compare-title",
						className: "mt-1 font-display text-2xl font-bold",
						children: "Run-to-run comparison"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "mt-1 text-xs text-muted-foreground",
						children: "Green = improvement, red = regression. Deltas are percentage change from baseline to target."
					})
				] }), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "flex flex-wrap gap-2",
					"data-print-hide": true,
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
							type: "button",
							onClick: copyShareLink,
							disabled: !base || !target,
							className: "border border-border px-3 py-1.5 text-xs hover:border-leo hover:text-leo disabled:opacity-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-leo",
							children: "Copy share link"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
							type: "button",
							onClick: exportPng,
							disabled: !base || !target || exporting !== null,
							className: "border border-border px-3 py-1.5 text-xs hover:border-leo hover:text-leo disabled:opacity-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-leo",
							children: exporting === "png" ? "Rendering…" : "Export PNG"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
							type: "button",
							onClick: printPdf,
							disabled: !base || !target || exporting !== null,
							className: "border border-border px-3 py-1.5 text-xs hover:border-leo hover:text-leo disabled:opacity-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-leo",
							children: exporting === "pdf" ? "Preparing…" : "Print / Save PDF"
						})
					]
				})]
			}),
			exportProgress && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				role: "status",
				"aria-live": "polite",
				"data-print-hide": true,
				className: "mt-4 border border-leo/40 bg-leo/5 p-3 text-xs",
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "flex flex-wrap items-center justify-between gap-3",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "min-w-0 flex-1",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
								className: "flex items-baseline gap-2",
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
									className: "font-semibold text-leo",
									children: ["Exporting ", exportProgress.kind.toUpperCase()]
								}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
									className: "font-mono text-muted-foreground",
									children: [
										exportProgress.step,
										" · ",
										(exportProgress.elapsedMs / 1e3).toFixed(1),
										"s"
									]
								})]
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
								className: "mt-2 h-1 w-full overflow-hidden bg-border",
								children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", { className: "h-full w-1/3 animate-pulse bg-leo" })
							}),
							exportProgress.elapsedMs > 8e3 && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
								className: "mt-1 text-[10px] text-yellow-600",
								children: "Taking longer than expected — the browser may be blocked. Cancel and retry if it looks stuck."
							})
						]
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
						type: "button",
						onClick: cancelExport,
						className: "border border-destructive/60 px-3 py-1.5 text-destructive hover:bg-destructive/10 focus:outline-none focus-visible:ring-2 focus-visible:ring-destructive",
						children: "Cancel"
					})]
				})
			}),
			lastExportError && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				role: "alert",
				"aria-live": "assertive",
				"data-print-hide": true,
				className: "mt-4 border border-destructive/60 bg-destructive/10 p-3 text-xs text-destructive",
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "flex flex-wrap items-start justify-between gap-3",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "min-w-0",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
								className: "font-semibold",
								children: lastExportError.kind === "png" ? "PNG export failed" : "PDF export failed"
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
								className: "mt-1 font-mono break-words text-[11px] opacity-80",
								children: lastExportError.reason
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
								className: "mt-1 text-[10px] opacity-70",
								children: [
									"Common fixes: scroll the card into view, wait for charts to finish rendering, or reduce the browser zoom then retry.",
									lastExportError.kind === "pdf" && retryAttempts.pdf >= 2 && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(import_jsx_runtime.Fragment, { children: [
										" ",
										"After 2 PDF failures the next retry falls back to ",
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)("b", { children: "PNG (image-only)" }),
										"."
									] }),
									retryAttempts[lastExportError.kind] > 0 && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(import_jsx_runtime.Fragment, { children: [" · attempt ", retryAttempts[lastExportError.kind]] })
								]
							})
						]
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "flex gap-2",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
							type: "button",
							onClick: retryLastExport,
							disabled: exporting !== null,
							className: "border border-destructive/70 px-3 py-1.5 hover:bg-destructive/20 disabled:opacity-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-destructive",
							children: exporting ? "Retrying…" : `Retry ${lastExportError.kind.toUpperCase()}`
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
							type: "button",
							onClick: () => setLastExportError(null),
							className: "border border-border px-3 py-1.5 text-muted-foreground hover:text-foreground focus:outline-none focus-visible:ring-2 focus-visible:ring-leo",
							"aria-label": "Dismiss export error",
							children: "Dismiss"
						})]
					})]
				})
			}),
			options.length < 2 ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "mt-6 text-xs text-muted-foreground",
				children: "Save at least two benchmark runs to compare."
			}) : /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(import_jsx_runtime.Fragment, { children: [
				findings.length > 0 && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					role: "alert",
					"aria-live": "polite",
					className: `mt-4 border p-3 text-xs ${findings.some((f) => f.severity === "critical") ? "border-destructive bg-destructive/10 text-destructive" : "border-yellow-500/60 bg-yellow-500/10 text-yellow-600"}`,
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
						className: "font-semibold uppercase tracking-wide",
						children: "⚠ Regression threshold breached"
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("ul", {
						className: "mt-2 space-y-0.5",
						children: findings.map((f) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", {
							className: "font-mono",
							children: [
								f.label,
								": ",
								f.base.toFixed(1),
								" → ",
								f.target.toFixed(1),
								" (",
								f.delta > 0 ? "+" : "",
								f.delta.toFixed(1),
								"%) breaches ",
								Math.abs(f.breach),
								f.metric === "errorRate" ? "%" : "%",
								" threshold (",
								f.severity,
								")"
							]
						}, f.metric))
					})]
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "mt-4 grid gap-3 sm:grid-cols-2",
					"data-print-hide": true,
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(RunPicker, {
						label: "Baseline",
						value: base?.id ?? "",
						onChange: setBaseId,
						options
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(RunPicker, {
						label: "Target",
						value: target?.id ?? "",
						onChange: setTargetId,
						options
					})]
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-3",
					children: rows.map(({ m, a, b, delta, improved, changed }) => {
						const color = !changed ? "text-muted-foreground" : improved ? "text-leo" : "text-destructive";
						const arrow = !changed ? "→" : delta > 0 ? "▲" : "▼";
						const maxAbs = Math.max(Math.abs(a), Math.abs(b), 1);
						const aPct = Math.abs(a) / maxAbs * 100;
						const bPct = Math.abs(b) / maxAbs * 100;
						return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "border border-border bg-muted/10 p-3",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
								className: "flex items-baseline justify-between",
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
									className: "text-[11px] uppercase tracking-wide text-muted-foreground",
									children: m.label
								}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
									className: `font-mono text-xs ${color}`,
									children: [
										arrow,
										" ",
										delta > 0 ? "+" : "",
										delta.toFixed(1),
										"%"
									]
								})]
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
								className: "mt-2 space-y-1.5",
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(BarRow, {
									label: "base",
									value: m.fmt(a),
									unit: m.unit,
									pct: aPct,
									muted: true
								}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(BarRow, {
									label: "target",
									value: m.fmt(b),
									unit: m.unit,
									pct: bPct,
									color
								})]
							})]
						}, m.key);
					})
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "mt-6 text-[11px] text-muted-foreground",
					children: [
						"Baseline: ",
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "font-mono",
							children: base?.path
						}),
						" ·",
						" ",
						base && new Date(base.timestamp).toLocaleString(),
						" → Target:",
						" ",
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "font-mono",
							children: target?.path
						}),
						" ·",
						" ",
						target && new Date(target.timestamp).toLocaleString()
					]
				})
			] })
		]
	});
}
function RunPicker({ label, value, onChange, options }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("label", {
		className: "flex flex-col gap-1 text-xs",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
			className: "uppercase tracking-wide text-muted-foreground",
			children: label
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("select", {
			value,
			onChange: (e) => onChange(e.target.value),
			className: "border border-border bg-background px-2 py-1 font-mono text-xs focus:border-leo focus:outline-none",
			children: options.map((r) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("option", {
				value: r.id,
				children: [
					new Date(r.timestamp).toLocaleString(),
					" · ",
					r.path,
					" · ",
					r.throughputRps.toFixed(1),
					" rps"
				]
			}, r.id))
		})]
	});
}
function BarRow({ label, value, unit, pct, muted, color }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "flex items-baseline justify-between text-[10px]",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
			className: "uppercase tracking-wide text-muted-foreground",
			children: label
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
			className: `font-mono ${color ?? (muted ? "text-muted-foreground" : "text-foreground")}`,
			children: [
				value,
				" ",
				unit
			]
		})]
	}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
		className: "mt-0.5 h-1 w-full bg-border",
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: `h-full ${muted ? "bg-muted-foreground/40" : "bg-leo"}`,
			style: { width: `${Math.min(100, pct)}%` }
		})
	})] });
}
function RegressionThresholdsCard() {
	const [t, setT] = useRegressionThresholds();
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
		"aria-labelledby": "thresholds-title",
		className: "border border-border bg-background p-6",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex flex-wrap items-center justify-between gap-3",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "eyebrow",
						children: "Alerts"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
						id: "thresholds-title",
						className: "mt-1 font-display text-2xl font-bold",
						children: "Regression thresholds"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "mt-1 text-xs text-muted-foreground",
						children: "When a comparison exceeds these tolerances vs. the baseline, the UI surfaces an inline banner and a toast."
					})
				] }), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("label", {
					className: "inline-flex items-center gap-2 text-xs",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("input", {
						type: "checkbox",
						checked: t.enabled,
						onChange: (e) => setT({
							...t,
							enabled: e.target.checked
						}),
						className: "h-4 w-4 accent-[#76B900]"
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
						className: "uppercase tracking-wide",
						children: t.enabled ? "Enabled" : "Disabled"
					})]
				})]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Field, {
						label: "p50 increase %",
						value: t.p50PctIncrease,
						onChange: (v) => setT({
							...t,
							p50PctIncrease: v
						})
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Field, {
						label: "p95 increase %",
						value: t.p95PctIncrease,
						onChange: (v) => setT({
							...t,
							p95PctIncrease: v
						})
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Field, {
						label: "p99 increase %",
						value: t.p99PctIncrease,
						onChange: (v) => setT({
							...t,
							p99PctIncrease: v
						})
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Field, {
						label: "throughput drop %",
						value: t.throughputPctDrop,
						onChange: (v) => setT({
							...t,
							throughputPctDrop: v
						})
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Field, {
						label: "error rate abs %",
						value: t.errorRateAbsPct,
						onChange: (v) => setT({
							...t,
							errorRateAbsPct: v
						}),
						step: .1
					})
				]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
				type: "button",
				onClick: () => setT(DEFAULT_THRESHOLDS),
				className: "mt-4 border border-border px-3 py-1.5 text-xs hover:border-leo hover:text-leo focus:outline-none focus-visible:ring-2 focus-visible:ring-leo",
				children: "Reset defaults"
			})
		]
	});
}
function Field({ label, value, onChange, step = 1 }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("label", {
		className: "flex flex-col gap-1 text-xs",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
			className: "uppercase tracking-wide text-muted-foreground",
			children: label
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("input", {
			type: "number",
			min: 0,
			step,
			value,
			onChange: (e) => onChange(Math.max(0, Number(e.target.value) || 0)),
			className: "border border-border bg-background px-2 py-1 font-mono text-xs focus:border-leo focus:outline-none"
		})]
	});
}
function CopyDebugReportButton() {
	const [busy, setBusy] = (0, import_react.useState)(false);
	async function copy() {
		setBusy(true);
		try {
			const history = getHealthHistory().slice(-30);
			const lastError = [...history].reverse().find((e) => e.status !== "online" && e.status !== "checking") ?? null;
			const report = {
				generatedAt: (/* @__PURE__ */ new Date()).toISOString(),
				apiBase: {
					effective: getApiBase(),
					source: getApiBaseSource(),
					env: /* @__PURE__ */ getEnvApiBase() ?? null
				},
				meta: getDiagnosticsMeta(),
				reliability: computeReliability(history),
				lastError: lastError ? {
					at: lastError.checkedAt ? new Date(lastError.checkedAt).toISOString() : null,
					status: lastError.status,
					failureKind: lastError.failureKind,
					httpStatus: lastError.httpStatus,
					errorName: lastError.errorName,
					message: lastError.message,
					hints: lastError.hints,
					url: lastError.url
				} : null,
				history: history.map((e) => ({
					at: e.checkedAt ? new Date(e.checkedAt).toISOString() : null,
					status: e.status,
					latencyMs: e.latencyMs,
					httpStatus: e.httpStatus,
					failureKind: e.failureKind,
					message: e.message,
					url: e.url
				}))
			};
			const json = JSON.stringify(report, null, 2);
			await navigator.clipboard.writeText(json);
			toast.success("Debug report copied to clipboard");
		} catch (err) {
			toast.error(err instanceof Error ? err.message : "Copy failed");
		} finally {
			setBusy(false);
		}
	}
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
		type: "button",
		onClick: copy,
		disabled: busy,
		className: "border border-border px-3 py-1.5 text-xs font-semibold hover:border-leo hover:text-leo disabled:opacity-40 focus:outline-none focus-visible:ring-2 focus-visible:ring-leo",
		children: busy ? "Copying…" : "Copy debug report"
	});
}
var KEY$2 = "leo.health_alert_timeline_v1";
var EVENT$1 = "leo:health-alert-timeline-changed";
function load() {
	if (typeof window === "undefined") return [];
	try {
		const raw = window.localStorage.getItem(KEY$2);
		if (!raw) return [];
		const parsed = JSON.parse(raw);
		return Array.isArray(parsed) ? parsed.slice(-200) : [];
	} catch {
		return [];
	}
}
function persist(events) {
	if (typeof window === "undefined") return;
	try {
		window.localStorage.setItem(KEY$2, JSON.stringify(events.slice(-200)));
		window.dispatchEvent(new CustomEvent(EVENT$1));
	} catch {}
}
function getAlertTimeline() {
	return load();
}
function clearAlertTimeline() {
	persist([]);
}
/** Called by HealthDegradationAlert whenever the level transitions. */
function recordAlertTransition(nextLevel, reasons) {
	const events = load();
	const open = events.length && events[events.length - 1].endedAt === null ? events[events.length - 1] : null;
	if (nextLevel === "ok") {
		if (open) {
			open.endedAt = Date.now();
			open.lastReasons = reasons.length ? reasons : open.lastReasons;
			persist(events);
		}
		return;
	}
	if (open) {
		if (nextLevel === "critical" && open.peakLevel !== "critical") open.peakLevel = "critical";
		open.lastReasons = reasons;
		persist(events);
		return;
	}
	events.push({
		id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
		level: nextLevel,
		startedAt: Date.now(),
		endedAt: null,
		startReasons: reasons,
		peakLevel: nextLevel,
		lastReasons: reasons
	});
	persist(events);
}
function useAlertTimeline() {
	const [events, setEvents] = (0, import_react.useState)(() => load());
	(0, import_react.useEffect)(() => {
		const handler = () => setEvents(load());
		window.addEventListener(EVENT$1, handler);
		window.addEventListener("storage", handler);
		return () => {
			window.removeEventListener(EVENT$1, handler);
			window.removeEventListener("storage", handler);
		};
	}, []);
	return events;
}
var SSE_DIAG_KEY$1 = "leo.bench.sse-diag";
var CORS_RESULT_KEY$3 = "leo.cors.last_result";
function readJson$1(key) {
	if (typeof window === "undefined") return null;
	try {
		const raw = window.localStorage.getItem(key);
		return raw ? JSON.parse(raw) : null;
	} catch {
		return null;
	}
}
function buildDebugReport() {
	const history = getHealthHistory().slice(-30);
	return {
		generatedAt: (/* @__PURE__ */ new Date()).toISOString(),
		apiBase: {
			effective: getApiBase(),
			source: getApiBaseSource(),
			env: /* @__PURE__ */ getEnvApiBase() ?? null
		},
		meta: getDiagnosticsMeta(),
		thresholds: getThresholds(),
		sseConfig: getSseConfig(),
		reliability: computeReliability(history),
		sseDiagnostic: readJson$1(SSE_DIAG_KEY$1),
		sseLog: getSseLog(),
		alertTimeline: getAlertTimeline(),
		corsPreflight: readJson$1(CORS_RESULT_KEY$3),
		history
	};
}
function ExportDebugReportButton() {
	function download() {
		try {
			const report = buildDebugReport();
			const blob = new Blob([JSON.stringify(report, null, 2)], { type: "application/json" });
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
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
		type: "button",
		onClick: download,
		className: "border border-border px-3 py-1.5 text-xs font-semibold hover:border-leo hover:text-leo focus:outline-none focus-visible:ring-2 focus-visible:ring-leo",
		children: "Export debug report"
	});
}
var N = 30;
function HealthHistoryChart() {
	const history = useHealthHistory();
	const timeline = useAlertTimeline();
	const slice = (0, import_react.useMemo)(() => history.slice(-30), [history]);
	const maxLatency = (0, import_react.useMemo)(() => Math.max(100, ...slice.map((e) => e.latencyMs ?? 0)), [slice]);
	const okCount = slice.filter((e) => e.status === "online").length;
	const failCount = slice.filter((e) => e.status !== "online" && e.status !== "checking").length;
	const avgLatency = (() => {
		const oks = slice.filter((e) => e.status === "online" && typeof e.latencyMs === "number");
		if (!oks.length) return null;
		return Math.round(oks.reduce((s, e) => s + (e.latencyMs ?? 0), 0) / oks.length);
	})();
	const timeExtent = (0, import_react.useMemo)(() => {
		const times = slice.map((e) => e.checkedAt ?? 0).filter((t) => t > 0);
		if (times.length < 2) return null;
		return {
			start: times[0],
			end: times[times.length - 1]
		};
	}, [slice]);
	const overlapping = (0, import_react.useMemo)(() => {
		if (!timeExtent) return [];
		const now = Date.now();
		return timeline.filter((ep) => {
			const s = ep.startedAt;
			return (ep.endedAt ?? now) >= timeExtent.start && s <= timeExtent.end;
		});
	}, [timeline, timeExtent]);
	function pctFor(ts) {
		if (!timeExtent) return 0;
		const span = Math.max(1, timeExtent.end - timeExtent.start);
		return Math.max(0, Math.min(100, (ts - timeExtent.start) / span * 100));
	}
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		id: "health-history-chart",
		className: "border border-border p-4",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex flex-wrap items-baseline justify-between gap-2",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
					className: "eyebrow",
					children: [
						"Last ",
						N,
						" health checks"
					]
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "mt-1 text-xs text-muted-foreground",
					children: "Bar height = latency · color = status · shaded band = alert episode"
				})] }), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "flex gap-4 text-xs",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Stat, {
							label: "OK",
							value: okCount,
							tone: "ok"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Stat, {
							label: "Fail",
							value: failCount,
							tone: "fail"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Stat, {
							label: "Avg",
							value: avgLatency != null ? `${avgLatency}ms` : "—"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Stat, {
							label: "Alerts",
							value: overlapping.length,
							tone: overlapping.length ? "fail" : void 0
						})
					]
				})]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "relative mt-4 h-24",
				role: "img",
				"aria-label": `Latency history for last ${slice.length} checks with ${overlapping.length} alert episodes overlaid`,
				children: [timeExtent && overlapping.length > 0 && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "pointer-events-none absolute inset-0 z-0",
					children: overlapping.map((ep) => {
						const startPct = pctFor(ep.startedAt);
						const endPct = pctFor(ep.endedAt ?? Date.now());
						const widthPct = Math.max(.5, endPct - startPct);
						const isCritical = ep.peakLevel === "critical";
						const bg = isCritical ? "bg-red-500/15" : "bg-yellow-400/15";
						const border = isCritical ? "border-red-500/60" : "border-yellow-400/60";
						const title = `${isCritical ? "Critical" : "Warn"} · ${new Date(ep.startedAt).toLocaleTimeString()}${ep.endedAt ? ` → ${new Date(ep.endedAt).toLocaleTimeString()}` : " (ongoing)"}${ep.lastReasons.length ? "\n" + ep.lastReasons.join("\n") : ""}`;
						return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
							className: `absolute top-0 bottom-0 border-x ${bg} ${border}`,
							style: {
								left: `${startPct}%`,
								width: `${widthPct}%`
							},
							title
						}, ep.id);
					})
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "relative z-10 flex h-full items-end gap-1",
					children: [
						slice.length === 0 && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "w-full text-center text-xs text-muted-foreground",
							children: "No checks yet — waiting for first poll."
						}),
						slice.map((e) => {
							const ok = e.status === "online";
							const height = e.latencyMs != null ? Math.max(4, Math.round(e.latencyMs / maxLatency * 96)) : 96;
							const color = ok ? "bg-leo" : e.status === "checking" ? "bg-yellow-400" : "bg-red-500";
							const title = [
								e.checkedAt ? new Date(e.checkedAt).toLocaleTimeString() : "",
								e.status,
								e.latencyMs != null ? `${e.latencyMs}ms` : "",
								e.httpStatus ? `HTTP ${e.httpStatus}` : "",
								e.message ?? ""
							].filter(Boolean).join(" · ");
							return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
								className: `flex-1 ${color} transition-all hover:opacity-80`,
								style: {
									height: `${height}%`,
									minWidth: 4
								},
								title
							}, e.id);
						}),
						slice.length > 0 && Array.from({ length: N - slice.length }).map((_, i) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
							className: "h-1 flex-1 bg-border/40",
							style: { minWidth: 4 }
						}, `pad-${i}`))
					]
				})]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mt-2 flex justify-between text-[10px] text-muted-foreground",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { children: "older" }),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", { children: [
						"0–",
						maxLatency,
						"ms range"
					] }),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { children: "newest" })
				]
			}),
			overlapping.length > 0 && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("ul", {
				className: "mt-3 space-y-1 border-t border-border pt-2 text-[11px]",
				children: overlapping.map((ep) => {
					const dot = ep.peakLevel === "critical" ? "bg-red-500" : "bg-yellow-400";
					const duration = Math.round(((ep.endedAt ?? Date.now()) - ep.startedAt) / 1e3);
					return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", {
						className: "flex items-start gap-2",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { className: `mt-1 inline-block h-2 w-2 shrink-0 ${dot}` }), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
							className: "flex-1",
							children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
									className: "font-semibold uppercase tracking-wide",
									children: ep.peakLevel
								}),
								" ",
								/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
									className: "text-muted-foreground",
									children: [new Date(ep.startedAt).toLocaleTimeString(), ep.endedAt ? ` → ${new Date(ep.endedAt).toLocaleTimeString()} (${duration}s)` : " · ongoing"]
								}),
								ep.lastReasons.length > 0 && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
									className: "ml-1 text-muted-foreground",
									children: ["— ", ep.lastReasons.join("; ")]
								})
							]
						})]
					}, ep.id);
				})
			})
		]
	});
}
function Stat({ label, value, tone }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "text-right",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: "text-[10px] uppercase tracking-wide text-muted-foreground",
			children: label
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: `font-mono text-sm font-semibold ${tone === "ok" ? "text-leo" : tone === "fail" ? "text-red-400" : "text-foreground"}`,
			children: value
		})]
	});
}
var DIAG_KEY$2 = "leo.bench.sse-diag";
var TRANSPORT_KEY = "leo.bench.transportMode";
function read$1() {
	if (typeof window === "undefined") return null;
	try {
		const raw = window.localStorage.getItem(DIAG_KEY$2);
		return raw ? JSON.parse(raw) : null;
	} catch {
		return null;
	}
}
function loadMode() {
	if (typeof window === "undefined") return "auto";
	const v = window.localStorage.getItem(TRANSPORT_KEY);
	return v === "sse-only" || v === "polling-only" ? v : "auto";
}
function formatAgo(ts) {
	if (!ts) return "never";
	const s = Math.round((Date.now() - ts) / 1e3);
	if (s < 2) return "just now";
	if (s < 60) return `${s}s ago`;
	if (s < 3600) return `${Math.round(s / 60)}m ago`;
	return `${Math.round(s / 3600)}h ago`;
}
function SseStatusWidget() {
	const [diag, setDiag] = (0, import_react.useState)(() => read$1());
	const [mode, setMode] = (0, import_react.useState)(() => loadMode());
	const [, tick] = (0, import_react.useState)(0);
	(0, import_react.useEffect)(() => {
		const id = setInterval(() => {
			setDiag(read$1());
			tick((n) => n + 1);
		}, 1e3);
		const onModeChange = () => setMode(loadMode());
		window.addEventListener("leo:transport-mode-changed", onModeChange);
		return () => {
			clearInterval(id);
			window.removeEventListener("leo:transport-mode-changed", onModeChange);
		};
	}, []);
	function changeMode(next) {
		setMode(next);
		try {
			window.localStorage.setItem(TRANSPORT_KEY, next);
		} catch {}
		window.dispatchEvent(new CustomEvent("leo:transport-mode-changed", { detail: next }));
	}
	const status = diag?.status ?? "idle";
	const transport = diag?.transport ?? "sse";
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "border border-border p-4",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex flex-wrap items-center gap-3",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
						className: `inline-block h-2.5 w-2.5 rounded-full ${status === "open" ? "bg-leo" : status === "polling" ? "bg-blue-400" : status === "reconnecting" ? "bg-yellow-400 animate-pulse" : status === "error" ? "bg-red-500" : "bg-muted-foreground/40"}`,
						"aria-hidden": true
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
						className: "font-semibold",
						role: "status",
						"aria-live": "polite",
						children: ["SSE ", status]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
						className: "text-xs text-muted-foreground",
						children: ["· transport: ", /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "font-mono text-foreground",
							children: transport
						})]
					})
				]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("fieldset", {
				className: "mt-4 flex flex-wrap gap-1.5",
				"aria-label": "Force transport mode for benchmark stream",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("legend", {
					className: "sr-only",
					children: "Force transport mode"
				}), [
					{
						id: "auto",
						label: "Auto",
						hint: "SSE with automatic polling fallback"
					},
					{
						id: "sse-only",
						label: "SSE only",
						hint: "Force EventSource; no fallback"
					},
					{
						id: "polling-only",
						label: "Polling only",
						hint: "Skip SSE entirely"
					}
				].map((m) => {
					const active = mode === m.id;
					return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
						type: "button",
						onClick: () => changeMode(m.id),
						"aria-pressed": active,
						title: m.hint,
						className: "px-2.5 py-1 text-[11px] font-semibold uppercase tracking-wide transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-white " + (active ? "bg-leo text-leo-foreground" : "border border-border text-muted-foreground hover:text-foreground"),
						children: m.label
					}, m.id);
				})]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "mt-1 text-[10px] text-muted-foreground",
				children: "Applies to the next (or in-flight) benchmark stream."
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("dl", {
				className: "mt-4 grid gap-x-6 gap-y-2 text-xs sm:grid-cols-[max-content_1fr]",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("dt", {
						className: "text-muted-foreground",
						children: "Last event"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("dd", { children: formatAgo(diag?.lastEventAt) }),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("dt", {
						className: "text-muted-foreground",
						children: "Reconnect attempts"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("dd", {
						className: "font-mono",
						children: diag?.reconnectAttempts ?? 0
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("dt", {
						className: "text-muted-foreground",
						children: "Diagnostics saved"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("dd", { children: formatAgo(diag?.savedAt) })
				]
			}),
			diag?.lastError && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mt-3 border-l-2 border-red-500 bg-red-500/5 p-3 text-xs",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "font-semibold text-red-400",
					children: "Last SSE error"
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "mt-1 font-mono text-[11px] break-words",
					children: diag.lastError
				})]
			}),
			!diag && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "mt-3 text-xs text-muted-foreground",
				children: "No SSE session yet — start a benchmark run to open the stream."
			})
		]
	});
}
var PATH_PRESETS = [
	"/health",
	"/api/v1/leo/metrics",
	"/api/v1/leo/diagnostics",
	"/api/v1/leo/chat"
];
var METHODS = [
	"GET",
	"POST",
	"PUT",
	"PATCH",
	"DELETE"
];
async function runPreflight(base, path, method, reqHeaders) {
	const cleanPath = path.startsWith("/") ? path : `/${path}`;
	const url = `${base.replace(/\/+$/, "")}${cleanPath}`;
	const origin = typeof window !== "undefined" ? window.location.origin : "*";
	const started = performance.now();
	const controller = new AbortController();
	const timer = setTimeout(() => controller.abort(), 5e3);
	try {
		const res = await fetch(url, {
			method: "OPTIONS",
			signal: controller.signal,
			headers: {
				Origin: origin,
				"Access-Control-Request-Method": method,
				"Access-Control-Request-Headers": reqHeaders.join(", ")
			}
		});
		const latencyMs = Math.round(performance.now() - started);
		const rawHeaders = [];
		res.headers.forEach((v, k) => rawHeaders.push([k, v]));
		const allowOrigin = res.headers.get("access-control-allow-origin");
		const allowMethods = res.headers.get("access-control-allow-methods");
		const allowHeaders = res.headers.get("access-control-allow-headers");
		const checks = [];
		if (!allowOrigin) checks.push({
			header: "Access-Control-Allow-Origin",
			received: null,
			kind: "fail",
			note: `Missing. Must be "${origin}" or "*".`
		});
		else if (allowOrigin === "*" || allowOrigin === origin) checks.push({
			header: "Access-Control-Allow-Origin",
			received: allowOrigin,
			kind: allowOrigin === "*" ? "warn" : "ok",
			note: allowOrigin === "*" ? "Wildcard works but blocks credentialed requests." : "Origin allowed."
		});
		else checks.push({
			header: "Access-Control-Allow-Origin",
			received: allowOrigin,
			kind: "fail",
			note: `Does not match request origin "${origin}".`
		});
		const methodsList = (allowMethods ?? "").toLowerCase().split(/[,\s]+/).filter(Boolean);
		if (!allowMethods) checks.push({
			header: "Access-Control-Allow-Methods",
			received: null,
			kind: "fail",
			note: `Missing. Must include ${method}.`
		});
		else if (!methodsList.includes(method.toLowerCase()) && !methodsList.includes("*")) checks.push({
			header: "Access-Control-Allow-Methods",
			received: allowMethods,
			kind: "fail",
			note: `${method} not listed.`
		});
		else checks.push({
			header: "Access-Control-Allow-Methods",
			received: allowMethods,
			kind: "ok",
			note: `${method} allowed.`
		});
		const headersList = (allowHeaders ?? "").toLowerCase().split(/[,\s]+/).filter(Boolean);
		const missing = reqHeaders.filter((h) => !headersList.includes(h.toLowerCase()) && !headersList.includes("*"));
		if (!allowHeaders) checks.push({
			header: "Access-Control-Allow-Headers",
			received: null,
			kind: reqHeaders.length ? "fail" : "warn",
			note: reqHeaders.length ? `Missing. Add ${reqHeaders.join(", ")}.` : "Not sent — fine if the client doesn't send extra headers."
		});
		else if (missing.length) checks.push({
			header: "Access-Control-Allow-Headers",
			received: allowHeaders,
			kind: "fail",
			note: `Missing: ${missing.join(", ")}`
		});
		else checks.push({
			header: "Access-Control-Allow-Headers",
			received: allowHeaders,
			kind: "ok",
			note: "All requested headers allowed."
		});
		clearTimeout(timer);
		return {
			url,
			origin,
			method,
			ok: res.ok && checks.every((c) => c.kind !== "fail"),
			httpStatus: res.status,
			latencyMs,
			checks,
			rawHeaders
		};
	} catch (err) {
		clearTimeout(timer);
		return {
			url,
			origin,
			method,
			ok: false,
			checks: [],
			rawHeaders: [],
			error: err instanceof Error ? err.name === "AbortError" ? "Preflight timed out after 5s" : `${err.name}: ${err.message}` : String(err)
		};
	}
}
function buildCurl(url, origin, method, headers, verbose = false) {
	const q = (s) => `'${s.replace(/'/g, `'\\''`)}'`;
	const lines = [
		`curl ${verbose ? "-i -sS" : "-sS -o /dev/null -D -"} -X OPTIONS ${q(url)} \\`,
		`  -H ${q(`Origin: ${origin}`)} \\`,
		`  -H ${q(`Access-Control-Request-Method: ${method}`)}`
	];
	if (headers.length) {
		lines[lines.length - 1] += " \\";
		lines.push(`  -H ${q(`Access-Control-Request-Headers: ${headers.join(", ")}`)}`);
	}
	return lines.join("\n");
}
var CORS_RESULT_KEY$2 = "leo.cors.last_result";
function CorsPreflightTester() {
	const [running, setRunning] = (0, import_react.useState)(false);
	const [result, setResult] = (0, import_react.useState)(() => {
		if (typeof window === "undefined") return null;
		try {
			const raw = window.localStorage.getItem(CORS_RESULT_KEY$2);
			return raw ? JSON.parse(raw) : null;
		} catch {
			return null;
		}
	});
	const [showCurl, setShowCurl] = (0, import_react.useState)(false);
	const [path, setPath] = (0, import_react.useState)("/health");
	const [method, setMethod] = (0, import_react.useState)("GET");
	const [headersInput, setHeadersInput] = (0, import_react.useState)("content-type, authorization");
	const base = getApiBase();
	const origin = typeof window !== "undefined" ? window.location.origin : "*";
	const reqHeaders = (0, import_react.useMemo)(() => headersInput.split(",").map((s) => s.trim().toLowerCase()).filter(Boolean), [headersInput]);
	const cleanPath = path.startsWith("/") ? path : `/${path}`;
	const fullUrl = `${base.replace(/\/+$/, "")}${cleanPath}`;
	const curl = buildCurl(fullUrl, origin, method, reqHeaders);
	const curlVerbose = buildCurl(fullUrl, origin, method, reqHeaders, true);
	const missingSummary = (0, import_react.useMemo)(() => {
		if (!result || !result.checks.length) return null;
		const failing = result.checks.filter((c) => c.kind === "fail");
		if (!failing.length) return null;
		return failing.map((c) => c.header.replace(/^Access-Control-Allow-/, "Allow-"));
	}, [result]);
	async function run() {
		setRunning(true);
		try {
			const r = await runPreflight(base, path, method, reqHeaders);
			setResult(r);
			try {
				window.localStorage.setItem(CORS_RESULT_KEY$2, JSON.stringify(r));
			} catch {}
			if (r.ok) toast.success("CORS preflight passed");
			else toast.error(r.error ?? "CORS preflight failed");
		} finally {
			setRunning(false);
		}
	}
	async function copy(text, label) {
		try {
			await navigator.clipboard.writeText(text);
			toast.success(`${label} copied`);
		} catch {
			toast.error("Clipboard blocked — select and copy manually");
		}
	}
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "border border-border p-4",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex flex-wrap items-baseline justify-between gap-2",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "eyebrow",
					children: "CORS preflight tester"
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
					className: "mt-1 text-xs text-muted-foreground",
					children: [
						"Pick any path + method to send an OPTIONS preflight against",
						" ",
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("code", {
							className: "font-mono",
							children: base
						}),
						"."
					]
				})] }), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "flex flex-wrap gap-2",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
						type: "button",
						onClick: () => setShowCurl((s) => !s),
						className: "border border-border px-3 py-1.5 text-xs font-semibold hover:bg-input focus:outline-none focus-visible:ring-2 focus-visible:ring-white",
						"aria-expanded": showCurl,
						children: showCurl ? "Hide curl" : "Show curl"
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
						type: "button",
						onClick: run,
						disabled: running,
						className: "bg-leo px-3 py-1.5 text-xs font-semibold text-leo-foreground disabled:opacity-40 focus:outline-none focus-visible:ring-2 focus-visible:ring-white",
						children: running ? "Testing…" : "Test CORS preflight"
					})]
				})]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mt-4 grid gap-3 text-xs sm:grid-cols-[1fr_auto]",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("label", {
						className: "flex flex-col gap-1",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
								className: "text-muted-foreground",
								children: "Path"
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("input", {
								list: "cors-path-presets",
								value: path,
								onChange: (e) => setPath(e.target.value),
								className: "border border-border bg-background px-2 py-1 font-mono focus:border-leo focus:outline-none",
								placeholder: "/api/v1/leo/chat",
								"aria-label": "Request path"
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("datalist", {
								id: "cors-path-presets",
								children: PATH_PRESETS.map((p) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("option", { value: p }, p))
							})
						]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("label", {
						className: "flex flex-col gap-1",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "text-muted-foreground",
							children: "Method"
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("select", {
							value: method,
							onChange: (e) => setMethod(e.target.value),
							className: "border border-border bg-background px-2 py-1 font-mono focus:border-leo focus:outline-none",
							"aria-label": "Request method",
							children: METHODS.map((m) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("option", {
								value: m,
								children: m
							}, m))
						})]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("label", {
						className: "flex flex-col gap-1 sm:col-span-2",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "text-muted-foreground",
							children: "Request headers (comma-separated)"
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("input", {
							value: headersInput,
							onChange: (e) => setHeadersInput(e.target.value),
							className: "border border-border bg-background px-2 py-1 font-mono focus:border-leo focus:outline-none",
							placeholder: "content-type, authorization",
							"aria-label": "Access-Control-Request-Headers list"
						})]
					})
				]
			}),
			showCurl && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mt-4 space-y-3 text-xs",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "flex items-center justify-between gap-2",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "eyebrow",
						children: "Headers only"
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
						type: "button",
						onClick: () => copy(curl, "curl command"),
						className: "border border-border px-2 py-0.5 text-[11px] font-semibold hover:bg-input focus:outline-none focus-visible:ring-2 focus-visible:ring-white",
						children: "Copy"
					})]
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("pre", {
					className: "mt-1 overflow-x-auto bg-input p-2 font-mono text-[11px] whitespace-pre",
					children: curl
				})] }), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "flex items-center justify-between gap-2",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "eyebrow",
						children: "Verbose (with body)"
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
						type: "button",
						onClick: () => copy(curlVerbose, "verbose curl command"),
						className: "border border-border px-2 py-0.5 text-[11px] font-semibold hover:bg-input focus:outline-none focus-visible:ring-2 focus-visible:ring-white",
						children: "Copy"
					})]
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("pre", {
					className: "mt-1 overflow-x-auto bg-input p-2 font-mono text-[11px] whitespace-pre",
					children: curlVerbose
				})] })]
			}),
			result && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mt-4 space-y-3 text-xs",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", { children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: result.ok ? "font-semibold text-leo" : "font-semibold text-red-400",
							children: result.ok ? "PASS" : "FAIL"
						}),
						" · ",
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("code", {
							className: "font-mono",
							children: result.method
						}),
						" ",
						result.url,
						result.httpStatus != null && ` · HTTP ${result.httpStatus}`,
						result.latencyMs != null && ` · ${result.latencyMs}ms`
					] }),
					missingSummary && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						role: "alert",
						className: "border-l-2 border-red-500 bg-red-500/5 p-3",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
							className: "font-semibold text-red-400",
							children: ["Missing / mismatched: ", missingSummary.join(" · ")]
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "mt-1 text-muted-foreground",
							children: "Add these to your backend CORS config so the browser accepts the preflight."
						})]
					}),
					result.error && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "border-l-2 border-red-500 bg-red-500/5 p-3",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "font-semibold text-red-400",
							children: result.error
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "mt-1 text-muted-foreground",
							children: "Common causes: server not running, OPTIONS handler missing, or no CORS headers."
						})]
					}),
					result.checks.length > 0 && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("ul", {
						className: "space-y-2",
						children: result.checks.map((c) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", {
							className: "border border-border p-2",
							children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
									className: "flex items-center gap-2",
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
										className: c.kind === "ok" ? "text-leo" : c.kind === "warn" ? "text-orange-400" : "text-red-400",
										"aria-hidden": true,
										children: c.kind === "ok" ? "✓" : c.kind === "warn" ? "!" : "✗"
									}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("code", {
										className: "font-mono text-[11px]",
										children: c.header
									})]
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
									className: "mt-1 pl-6 text-muted-foreground",
									children: c.note
								}),
								c.received != null && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
									className: "mt-1 pl-6 font-mono text-[11px] break-all",
									children: ["received: ", c.received]
								})
							]
						}, c.header))
					}),
					result.rawHeaders.length > 0 && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("details", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("summary", {
						className: "cursor-pointer text-muted-foreground",
						children: "All response headers"
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("pre", {
						className: "mt-2 overflow-x-auto bg-input p-2 font-mono text-[11px]",
						children: result.rawHeaders.map(([k, v]) => `${k}: ${v}`).join("\n")
					})] })
				]
			})
		]
	});
}
function HealthDegradationAlert() {
	const history = useHealthHistory();
	const [thresholds] = useThresholds();
	const lastLevel = (0, import_react.useRef)("ok");
	const [alert, setAlert] = (0, import_react.useState)(null);
	(0, import_react.useEffect)(() => {
		const window = history.slice(-30);
		if (window.length === 0) return;
		let consecutive = 0;
		for (let i = window.length - 1; i >= 0; i--) if (window[i].status !== "online") consecutive++;
		else break;
		const latencies = window.filter((e) => typeof e.latencyMs === "number" && e.status === "online").map((e) => e.latencyMs);
		const avg = latencies.length ? Math.round(latencies.reduce((a, b) => a + b, 0) / latencies.length) : 0;
		const over = latencies.filter((l) => l > thresholds.latencyWarnMs).length;
		const reasons = [];
		let level = "ok";
		if (consecutive >= thresholds.consecutiveFailLimit) {
			level = "critical";
			reasons.push(`${consecutive} consecutive failed health checks (limit ${thresholds.consecutiveFailLimit})`);
		}
		if (latencies.length >= 5 && avg > thresholds.avgLatencyWarnMs) {
			if (level !== "critical") level = "warn";
			reasons.push(`Avg latency ${avg}ms over last ${latencies.length} samples (> ${thresholds.avgLatencyWarnMs}ms)`);
		}
		if (over >= Math.ceil(latencies.length / 2) && latencies.length >= 6) {
			if (level !== "critical") level = "warn";
			reasons.push(`${over}/${latencies.length} slow samples over ${thresholds.latencyWarnMs}ms`);
		}
		setAlert(level === "ok" ? null : {
			level,
			reasons
		});
		if (level !== lastLevel.current) {
			if (level === "critical") toast.error("Backend degraded — " + reasons[0]);
			else if (level === "warn") toast.warning("Backend slow — " + reasons[0]);
			else toast.success("Backend recovered");
			lastLevel.current = level;
			recordAlertTransition(level, reasons);
		} else if (level !== "ok") recordAlertTransition(level, reasons);
	}, [history, thresholds]);
	if (!alert) return null;
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		role: "alert",
		"aria-live": "assertive",
		className: `border-l-2 p-3 text-xs ${alert.level === "critical" ? "border-red-500 bg-red-500/5 text-red-300" : "border-yellow-500 bg-yellow-500/5 text-yellow-200"}`,
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
			className: "font-semibold uppercase tracking-wide",
			children: alert.level === "critical" ? "Health degraded" : "Health warning"
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("ul", {
			className: "mt-1 list-inside list-disc space-y-0.5",
			children: alert.reasons.map((r) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("li", { children: r }, r))
		})]
	});
}
var DIAG_KEY$1 = "leo.bench.sse-diag";
function readDiag() {
	if (typeof window === "undefined") return null;
	try {
		const raw = window.localStorage.getItem(DIAG_KEY$1);
		return raw ? JSON.parse(raw) : null;
	} catch {
		return null;
	}
}
function diagnose(diag, base, recentFailures, recentCorsHint, recentMixedContent, everOnline) {
	const pageHttps = typeof window !== "undefined" && window.location.protocol === "https:";
	const baseHttp = base.startsWith("http://");
	const isLocal = /localhost|127\.0\.0\.1|0\.0\.0\.0/.test(base);
	const err = (diag?.lastError ?? "").toLowerCase();
	if (!diag || diag.status === "idle") return {
		id: "idle",
		title: "No SSE session yet",
		confidence: "low",
		why: ["Start a benchmark run to open the EventSource stream."],
		fix: [{
			text: "Open Benchmark runner",
			href: "/benchmarks"
		}]
	};
	if (diag.status === "open" && recentFailures === 0) return {
		id: "healthy",
		title: "Stream healthy",
		confidence: "high",
		why: ["EventSource is open and health checks are passing."],
		fix: []
	};
	if (pageHttps && baseHttp) return {
		id: "mixed-content",
		title: "Mixed content blocked",
		confidence: "high",
		why: ["Page is https but VITE_LEO_API_BASE_URL is http.", "Browsers silently block EventSource across this boundary."],
		fix: [{ text: "Use an https tunnel URL (Cloudflare Tunnel or ngrok)" }, {
			text: "Update base URL in Settings",
			href: "/app/settings"
		}]
	};
	if (recentCorsHint || err.includes("cors") || err.includes("access-control")) return {
		id: "cors",
		title: "CORS blocking the stream",
		confidence: "high",
		why: ["Recent health checks or SSE errors mention CORS.", "EventSource requires Access-Control-Allow-Origin on the SSE response."],
		fix: [{ text: "Run the CORS preflight tester below and copy the curl output" }, { text: "Add CORSMiddleware(allow_origins=[…], allow_methods=['*']) to FastAPI" }]
	};
	if (recentMixedContent) return {
		id: "mixed-content",
		title: "Mixed content blocked",
		confidence: "high",
		why: ["Health checks flagged mixed-content."],
		fix: [{ text: "Serve the backend over https" }]
	};
	if (!everOnline && isLocal && typeof window !== "undefined" && window.location.hostname !== "localhost") return {
		id: "tunnel",
		title: "Localhost base URL not reachable from this origin",
		confidence: "high",
		why: [`Base URL "${base}" points at localhost but this app is served from ${window.location.hostname}.`, "The preview environment cannot reach your laptop directly."],
		fix: [{ text: "Start a Cloudflare Tunnel or ngrok tunnel to your backend" }, {
			text: "Paste the public tunnel URL into Settings",
			href: "/app/settings"
		}]
	};
	if (!everOnline && recentFailures > 0) return {
		id: "wrong-base",
		title: "Base URL never responded successfully",
		confidence: "medium",
		why: [`No successful /health response from "${base}".`, "DNS resolves but the endpoint returns nothing usable, or the path is wrong."],
		fix: [{ text: "Verify the URL and port match your running backend" }, { text: "Reset to defaults in the Backend health panel" }]
	};
	return {
		id: "network",
		title: "Transient network / server issue",
		confidence: recentFailures > 3 ? "medium" : "low",
		why: [`Reconnect attempts: ${diag.reconnectAttempts}.`, diag.lastError ? `Last error: ${diag.lastError}` : "Connection drops without a clear error."],
		fix: [{ text: "Check backend logs for crashes or timeouts" }, { text: "Use the manual Re-run checks button to resample" }]
	};
}
function SseFailureDiagnostic() {
	const history = useHealthHistory();
	const [diag, setDiag] = (0, import_react.useState)(() => readDiag());
	const navigate = useNavigate();
	(0, import_react.useEffect)(() => {
		const id = setInterval(() => setDiag(readDiag()), 2e3);
		return () => clearInterval(id);
	}, []);
	async function copyAndConfigure() {
		const suggestion = [
			`# LEO effective API base URL`,
			`VITE_LEO_API_BASE_URL=${getApiBase()}`,
			``,
			`# Recommended update:`,
			`# 1. Replace with your public backend URL (https:// tunnel if page is https).`,
			`# 2. Save in Settings — the new value will override any env default.`
		].join("\n");
		try {
			await navigator.clipboard.writeText(suggestion);
			toast.success("Copied API base + settings hint");
		} catch {
			toast.error("Clipboard blocked — opening Settings anyway");
		}
		navigate({
			to: "/app/settings",
			search: { apiBase: getApiBase() }
		});
	}
	const base = getApiBase();
	const source = getApiBaseSource();
	const recent = history.slice(-10);
	const recentFailures = recent.filter((e) => e.status !== "online").length;
	const cause = diagnose(diag, base, recentFailures, recent.some((e) => e.failureKind === "cors"), recent.some((e) => e.failureKind === "mixed-content"), history.some((e) => e.status === "online"));
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: `border-l-2 ${cause.id === "healthy" ? "border-leo/40" : cause.id === "idle" ? "border-border" : "border-yellow-500/50"} p-4`,
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex flex-wrap items-baseline justify-between gap-2",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "eyebrow",
					children: "SSE failure diagnostic"
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
					className: "text-[10px] uppercase tracking-wide text-muted-foreground",
					children: ["confidence: ", cause.confidence]
				})]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "mt-2 text-sm font-semibold",
				children: cause.title
			}),
			cause.why.length > 0 && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("ul", {
				className: "mt-2 space-y-1 text-xs text-muted-foreground",
				children: cause.why.map((w) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", { children: ["• ", w] }, w))
			}),
			cause.fix.length > 0 && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mt-3",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "text-[11px] font-semibold uppercase tracking-wide text-muted-foreground",
					children: "Next steps"
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("ol", {
					className: "mt-1 space-y-1 text-xs",
					children: cause.fix.map((f, i) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", { children: [
						i + 1,
						".",
						" ",
						f.href ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Link, {
							to: f.href,
							className: "text-leo underline underline-offset-2 hover:text-leo/80",
							children: f.text
						}) : f.text
					] }, i))
				})]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mt-3 flex flex-wrap items-center justify-between gap-2",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
					className: "text-[10px] text-muted-foreground",
					children: [
						"base: ",
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("code", {
							className: "font-mono",
							children: base
						}),
						" · source: ",
						source
					]
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
					type: "button",
					onClick: copyAndConfigure,
					className: "border border-leo bg-leo/10 px-3 py-1 text-[11px] font-semibold text-leo hover:bg-leo/20 focus:outline-none focus-visible:ring-2 focus-visible:ring-leo",
					children: "Copy URL & configure ›"
				})]
			})
		]
	});
}
var CORS_RESULT_KEY$1 = "leo.cors.last_result";
var SSE_DIAG_KEY = "leo.bench.sse-diag";
function applyThresholds(input) {
	if (!input || typeof input !== "object") return false;
	const t = input;
	if (![
		"latencyWarnMs",
		"timeoutMs",
		"failureRatePct",
		"windowSize",
		"consecutiveFailLimit",
		"avgLatencyWarnMs"
	].some((k) => typeof t[k] === "number")) return false;
	setThresholds({
		...DEFAULT_THRESHOLDS$1,
		...t
	});
	return true;
}
function applySseConfig(input) {
	if (!input || typeof input !== "object") return false;
	const c = input;
	if (!(typeof c.maxAttempts === "number" || typeof c.initialBackoffMs === "number" || typeof c.maxBackoffMs === "number")) return false;
	setSseConfig({
		...DEFAULT_SSE_CONFIG,
		...c
	});
	return true;
}
function ImportDebugReportButton() {
	const [open, setOpen] = (0, import_react.useState)(false);
	const [text, setText] = (0, import_react.useState)("");
	const [mode, setMode] = (0, import_react.useState)("merge");
	const [summary, setSummary] = (0, import_react.useState)(null);
	const fileRef = (0, import_react.useRef)(null);
	function apply(raw) {
		let parsed;
		try {
			parsed = JSON.parse(raw);
		} catch (e) {
			toast.error("Invalid JSON: " + (e instanceof Error ? e.message : "parse failed"));
			return;
		}
		const notes = [];
		const report = importHealthEntries(parsed, mode);
		let thresholdsApplied = false;
		let sseApplied = false;
		let corsApplied = false;
		let sseDiagApplied = false;
		if (parsed && typeof parsed === "object") {
			const o = parsed;
			thresholdsApplied = applyThresholds(o.thresholds ?? (o.meta && typeof o.meta === "object" ? o.meta.thresholds : void 0));
			sseApplied = applySseConfig(o.sseConfig ?? o.sseReconnect ?? (o.meta && typeof o.meta === "object" ? o.meta.sseReconnect : void 0));
			if (o.corsPreflight && typeof o.corsPreflight === "object") try {
				window.localStorage.setItem(CORS_RESULT_KEY$1, JSON.stringify(o.corsPreflight));
				corsApplied = true;
			} catch {
				notes.push("Failed to restore CORS result (storage quota).");
			}
			if (o.sseDiagnostic && typeof o.sseDiagnostic === "object") try {
				window.localStorage.setItem(SSE_DIAG_KEY, JSON.stringify(o.sseDiagnostic));
				sseDiagApplied = true;
			} catch {
				notes.push("Failed to restore SSE diagnostic snapshot.");
			}
		}
		setSummary({
			history: report,
			thresholds: thresholdsApplied,
			sseConfig: sseApplied,
			corsResult: corsApplied,
			sseDiag: sseDiagApplied,
			notes
		});
		const restoredParts = [
			report.imported > 0 ? `${report.imported} history entries` : null,
			thresholdsApplied ? "thresholds" : null,
			sseApplied ? "SSE settings" : null,
			corsApplied ? "CORS result" : null,
			sseDiagApplied ? "SSE diagnostic" : null
		].filter(Boolean);
		if (restoredParts.length) toast.success(`Restored ${restoredParts.join(", ")}`);
		else toast.error("Nothing recognizable to import");
	}
	async function onFile(f) {
		const raw = await f.text();
		setText(raw);
		apply(raw);
	}
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(import_jsx_runtime.Fragment, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
		type: "button",
		onClick: () => setOpen((s) => !s),
		className: "border border-border px-3 py-1.5 text-xs font-semibold hover:border-leo hover:text-leo focus:outline-none focus-visible:ring-2 focus-visible:ring-leo",
		"aria-expanded": open,
		children: open ? "Close import" : "Import debug report"
	}), open && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "mt-3 w-full border border-border bg-background/60 p-4",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "eyebrow",
				children: "Import debug report"
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "mt-1 text-xs text-muted-foreground",
				children: "Paste a previously exported debug report JSON or upload a file. Restores health history, thresholds, CORS preflight result, and SSE reconnect settings in one click."
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mt-3 flex flex-wrap items-center gap-3 text-xs",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("label", {
						className: "inline-flex items-center gap-1",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("input", {
							type: "radio",
							name: "import-mode",
							checked: mode === "merge",
							onChange: () => setMode("merge")
						}), "Merge history (dedupe by timestamp+url)"]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("label", {
						className: "inline-flex items-center gap-1",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("input", {
							type: "radio",
							name: "import-mode",
							checked: mode === "replace",
							onChange: () => setMode("replace")
						}), "Replace history"]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("input", {
						ref: fileRef,
						type: "file",
						accept: "application/json,.json",
						onChange: (e) => {
							const f = e.target.files?.[0];
							if (f) onFile(f);
						},
						className: "text-xs"
					})
				]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("textarea", {
				value: text,
				onChange: (e) => setText(e.target.value),
				placeholder: "{\"history\":[…],\"thresholds\":{…},\"sseConfig\":{…},\"corsPreflight\":{…}}",
				spellCheck: false,
				className: "mt-3 h-32 w-full resize-y border border-border bg-background p-2 font-mono text-[11px] focus:border-leo focus:outline-none"
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mt-3 flex flex-wrap gap-2",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
					type: "button",
					onClick: () => apply(text),
					disabled: !text.trim(),
					className: "bg-leo px-3 py-1.5 text-xs font-semibold text-leo-foreground disabled:opacity-40 focus:outline-none focus-visible:ring-2 focus-visible:ring-white",
					children: "Import & restore"
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
					type: "button",
					onClick: () => {
						setText("");
						setSummary(null);
						if (fileRef.current) fileRef.current.value = "";
					},
					className: "border border-border px-3 py-1.5 text-xs font-semibold hover:bg-input",
					children: "Clear"
				})]
			}),
			summary && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mt-4 border-l-2 border-leo/60 bg-input/30 p-3 text-xs",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "font-semibold",
						children: "Restore summary"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("ul", {
						className: "mt-2 space-y-0.5 font-mono text-[11px]",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", { children: [
								"· history: imported ",
								summary.history?.imported ?? 0,
								", skipped",
								" ",
								summary.history?.skipped ?? 0,
								" (",
								summary.history?.replaced ? "replaced" : "merged",
								")"
							] }),
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", { children: ["· thresholds: ", summary.thresholds ? "restored" : "not present"] }),
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", { children: ["· SSE reconnect settings: ", summary.sseConfig ? "restored" : "not present"] }),
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", { children: ["· CORS preflight result: ", summary.corsResult ? "restored" : "not present"] }),
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", { children: ["· SSE diagnostic snapshot: ", summary.sseDiag ? "restored" : "not present"] })
						]
					}),
					(summary.history?.errors.length ?? 0) > 0 && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("details", {
						className: "mt-2",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("summary", {
							className: "cursor-pointer text-red-400",
							children: [summary.history.errors.length, " history parse error(s)"]
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("ul", {
							className: "mt-1 space-y-0.5 font-mono text-[11px]",
							children: summary.history.errors.slice(0, 20).map((e, i) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", { children: ["· ", e] }, i))
						})]
					}),
					summary.notes.length > 0 && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("ul", {
						className: "mt-2 space-y-0.5 text-yellow-400",
						children: summary.notes.map((n, i) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", { children: ["! ", n] }, i))
					})
				]
			})
		]
	})] });
}
function csvEscape(v) {
	if (v === null || v === void 0) return "";
	const s = String(v);
	if (/[",\r\n]/.test(s)) return `"${s.replace(/"/g, "\"\"")}"`;
	return s;
}
function toCsv(rows) {
	return rows.map((r) => r.map(csvEscape).join(",")).join("\r\n") + "\r\n";
}
function percentile$1(sorted, p) {
	if (!sorted.length) return 0;
	return sorted[Math.min(sorted.length - 1, Math.floor(p / 100 * sorted.length))];
}
function ExportHealthCsvButton() {
	function download() {
		try {
			const history = getHealthHistory();
			if (!history.length) {
				toast.error("No health checks recorded yet");
				return;
			}
			const latencies = history.map((h) => typeof h.latencyMs === "number" ? h.latencyMs : null).filter((n) => n !== null).sort((a, b) => a - b);
			const rel = computeReliability(history);
			const online = history.filter((h) => h.status === "online").length;
			const offline = history.length - online;
			const timeline = getAlertTimeline();
			const summary = [
				["# LEO health history export"],
				["generatedAt", (/* @__PURE__ */ new Date()).toISOString()],
				["apiBase", getApiBase()],
				["samples", history.length],
				["online", online],
				["offline", offline],
				["failureRatePct", rel.failureRatePct.toFixed(2)],
				["reliabilityLevel", rel.level],
				["latency_p50_ms", percentile$1(latencies, 50)],
				["latency_p95_ms", percentile$1(latencies, 95)],
				["latency_p99_ms", percentile$1(latencies, 99)],
				["latency_avg_ms", latencies.length ? Math.round(latencies.reduce((a, b) => a + b, 0) / latencies.length) : 0],
				["alert_episodes", timeline.length],
				[]
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
				"bodyExcerpt"
			];
			const rows = history.map((h) => [
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
				h.bodyExcerpt ?? ""
			]);
			const alertHeader = [
				"episode_id",
				"level",
				"peakLevel",
				"startedAtIso",
				"endedAtIso",
				"durationSec",
				"startReasons",
				"lastReasons"
			];
			const now = Date.now();
			const alertRows = timeline.map((ep) => [
				ep.id,
				ep.level,
				ep.peakLevel,
				new Date(ep.startedAt).toISOString(),
				ep.endedAt ? new Date(ep.endedAt).toISOString() : "",
				Math.round(((ep.endedAt ?? now) - ep.startedAt) / 1e3),
				ep.startReasons.join("; "),
				ep.lastReasons.join("; ")
			]);
			const csv = toCsv(summary) + toCsv([header, ...rows]) + "\r\n" + toCsv([["# alert episodes"]]) + toCsv([alertHeader, ...alertRows]);
			const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
			const url = URL.createObjectURL(blob);
			const a = document.createElement("a");
			a.href = url;
			a.download = `leo-health-history-${Date.now()}.csv`;
			document.body.appendChild(a);
			a.click();
			a.remove();
			URL.revokeObjectURL(url);
			toast.success(`Health CSV exported (${history.length} rows, ${timeline.length} alert episodes)`);
		} catch (err) {
			toast.error(err instanceof Error ? err.message : "CSV export failed");
		}
	}
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
		type: "button",
		onClick: download,
		className: "border border-border px-3 py-1.5 text-xs font-semibold hover:border-leo hover:text-leo focus:outline-none focus-visible:ring-2 focus-visible:ring-leo",
		children: "Export health CSV"
	});
}
var DEFAULT_BURST_CONFIG = {
	count: 5,
	intervalMs: 400,
	path: "/health"
};
var KEY$1 = "leo.burst.config_v1";
var LAST_KEY = "leo.burst.last_run_v1";
var EVENT = "leo:burst-config-changed";
var LAST_EVENT = "leo:burst-last-run-changed";
function clamp(n, lo, hi) {
	return Math.max(lo, Math.min(hi, Math.round(n)));
}
function sanitize(raw) {
	const c = {
		...DEFAULT_BURST_CONFIG,
		...raw
	};
	c.count = clamp(c.count, 1, 100);
	c.intervalMs = clamp(c.intervalMs, 0, 6e4);
	c.path = typeof c.path === "string" && c.path.trim() ? c.path.trim() : DEFAULT_BURST_CONFIG.path;
	if (!c.path.startsWith("/")) c.path = "/" + c.path;
	return c;
}
function getBurstConfig() {
	if (typeof window === "undefined") return { ...DEFAULT_BURST_CONFIG };
	try {
		const raw = window.localStorage.getItem(KEY$1);
		if (!raw) return { ...DEFAULT_BURST_CONFIG };
		return sanitize(JSON.parse(raw));
	} catch {
		return { ...DEFAULT_BURST_CONFIG };
	}
}
function setBurstConfig(cfg) {
	if (typeof window === "undefined") return;
	const next = sanitize({
		...getBurstConfig(),
		...cfg
	});
	window.localStorage.setItem(KEY$1, JSON.stringify(next));
	window.dispatchEvent(new CustomEvent(EVENT, { detail: next }));
}
function useBurstConfig() {
	const [cfg, setCfg] = (0, import_react.useState)(() => getBurstConfig());
	(0, import_react.useEffect)(() => {
		const on = () => setCfg(getBurstConfig());
		window.addEventListener(EVENT, on);
		window.addEventListener("storage", on);
		return () => {
			window.removeEventListener(EVENT, on);
			window.removeEventListener("storage", on);
		};
	}, []);
	return [cfg, setBurstConfig];
}
function getLastRunBurstConfig() {
	if (typeof window === "undefined") return null;
	try {
		const raw = window.localStorage.getItem(LAST_KEY);
		if (!raw) return null;
		return sanitize(JSON.parse(raw));
	} catch {
		return null;
	}
}
function recordLastRunBurstConfig(cfg) {
	if (typeof window === "undefined") return;
	try {
		window.localStorage.setItem(LAST_KEY, JSON.stringify(sanitize(cfg)));
		window.dispatchEvent(new CustomEvent(LAST_EVENT, { detail: cfg }));
	} catch {}
}
function useLastRunBurstConfig() {
	const [cfg, setCfg] = (0, import_react.useState)(() => getLastRunBurstConfig());
	(0, import_react.useEffect)(() => {
		const on = () => setCfg(getLastRunBurstConfig());
		window.addEventListener(LAST_EVENT, on);
		window.addEventListener("storage", on);
		return () => {
			window.removeEventListener(LAST_EVENT, on);
			window.removeEventListener("storage", on);
		};
	}, []);
	return cfg;
}
var TIMEOUT_MS = 5e3;
async function probe(path) {
	const url = `${getApiBase().replace(/\/+$/, "")}${path.startsWith("/") ? path : "/" + path}`;
	const started = performance.now();
	const controller = new AbortController();
	const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);
	try {
		const res = await fetch(url, {
			method: "GET",
			signal: controller.signal
		});
		const latencyMs = Math.round(performance.now() - started);
		const text = await res.text().catch(() => "");
		const bodyExcerpt = text.length > 240 ? text.slice(0, 240) + "…" : text;
		return {
			status: res.ok ? "online" : "error",
			url,
			latencyMs,
			httpStatus: res.status,
			checkedAt: Date.now(),
			bodyExcerpt,
			message: res.ok ? void 0 : `HTTP ${res.status}`,
			failureKind: res.ok ? void 0 : "http"
		};
	} catch (err) {
		const latencyMs = Math.round(performance.now() - started);
		const isAbort = err instanceof DOMException && err.name === "AbortError";
		return {
			status: "unreachable",
			url,
			latencyMs,
			checkedAt: Date.now(),
			failureKind: isAbort ? "timeout" : "network",
			errorName: err instanceof Error ? err.name : "Error",
			message: err instanceof Error ? err.message : String(err)
		};
	} finally {
		clearTimeout(timer);
	}
}
function BurstHealthCheckButton() {
	const [cfg, setCfg] = useBurstConfig();
	const lastRun = useLastRunBurstConfig();
	const [open, setOpen] = (0, import_react.useState)(false);
	const [running, setRunning] = (0, import_react.useState)(false);
	const [progress, setProgress] = (0, import_react.useState)(0);
	const [progressTotal, setProgressTotal] = (0, import_react.useState)(0);
	const cancelRef = (0, import_react.useRef)(false);
	async function runWith(runCfg) {
		if (running) {
			cancelRef.current = true;
			return;
		}
		setRunning(true);
		cancelRef.current = false;
		setProgress(0);
		setProgressTotal(runCfg.count);
		recordLastRunBurstConfig(runCfg);
		let fails = 0;
		for (let i = 0; i < runCfg.count; i++) {
			if (cancelRef.current) break;
			const r = await probe(runCfg.path);
			pushHealthEntry(r);
			if (r.status !== "online") fails++;
			setProgress(i + 1);
			if (i < runCfg.count - 1 && runCfg.intervalMs > 0) await new Promise((res) => setTimeout(res, runCfg.intervalMs));
		}
		setRunning(false);
		if (cancelRef.current) toast.message("Burst cancelled");
		else if (fails === 0) toast.success(`Ran ${runCfg.count} checks on ${runCfg.path} — all online`);
		else toast.error(`Ran ${runCfg.count} checks on ${runCfg.path} — ${fails} failed`);
	}
	const run = () => runWith(cfg);
	const runAgain = () => lastRun && runWith(lastRun);
	const runAgainTitle = lastRun ? `Replay last run: ${lastRun.count}× ${lastRun.path} @ ${lastRun.intervalMs}ms` : "No previous burst run yet";
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "inline-flex flex-wrap items-center gap-2",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
				type: "button",
				onClick: run,
				"aria-live": "polite",
				className: "border border-leo bg-leo/10 px-3 py-1.5 text-xs font-semibold text-leo hover:bg-leo/20 focus:outline-none focus-visible:ring-2 focus-visible:ring-leo",
				children: running ? `Running ${progress}/${progressTotal}…` : "Run health checks now"
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("button", {
				type: "button",
				onClick: runAgain,
				disabled: !lastRun || running,
				"aria-label": "Run again with last used burst config",
				title: runAgainTitle,
				className: "border border-border px-3 py-1.5 text-xs font-semibold hover:border-leo hover:text-leo focus:outline-none focus-visible:ring-2 focus-visible:ring-leo disabled:opacity-40 disabled:cursor-not-allowed",
				children: ["↻ Run again", lastRun && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
					className: "ml-1 font-mono text-[10px] text-muted-foreground",
					children: [
						lastRun.count,
						"× ",
						lastRun.path
					]
				})]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
				type: "button",
				onClick: () => setOpen((s) => !s),
				"aria-expanded": open,
				title: "Configure burst count, interval, and path",
				className: "border border-border px-2 py-1.5 text-xs font-semibold hover:border-leo hover:text-leo focus:outline-none focus-visible:ring-2 focus-visible:ring-leo",
				children: "⚙ Burst"
			}),
			open && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("fieldset", {
				className: "mt-2 flex w-full flex-wrap items-end gap-3 border border-border bg-background/60 px-3 py-2 text-xs",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("legend", {
						className: "px-1 text-[11px] uppercase tracking-wide text-muted-foreground",
						children: "Burst config"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("label", {
						className: "flex flex-col gap-1",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "text-muted-foreground",
							children: "Count (1–100)"
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("input", {
							type: "number",
							min: 1,
							max: 100,
							value: cfg.count,
							onChange: (e) => setCfg({ count: Number(e.target.value) }),
							className: "w-20 border border-border bg-background px-2 py-1 font-mono text-xs focus:border-leo focus:outline-none"
						})]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("label", {
						className: "flex flex-col gap-1",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "text-muted-foreground",
							children: "Interval (ms)"
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("input", {
							type: "number",
							min: 0,
							max: 6e4,
							step: 50,
							value: cfg.intervalMs,
							onChange: (e) => setCfg({ intervalMs: Number(e.target.value) }),
							className: "w-24 border border-border bg-background px-2 py-1 font-mono text-xs focus:border-leo focus:outline-none"
						})]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("label", {
						className: "flex flex-col gap-1",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
								className: "text-muted-foreground",
								children: "Path"
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("input", {
								type: "text",
								value: cfg.path,
								onChange: (e) => setCfg({ path: e.target.value }),
								placeholder: "/health",
								spellCheck: false,
								list: "burst-path-presets",
								className: "w-56 border border-border bg-background px-2 py-1 font-mono text-xs focus:border-leo focus:outline-none"
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("datalist", {
								id: "burst-path-presets",
								children: [
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("option", { value: "/health" }),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("option", { value: "/api/v1/leo/metrics" }),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("option", { value: "/api/v1/leo/diagnostics" })
								]
							})
						]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
						type: "button",
						onClick: () => setCfg(DEFAULT_BURST_CONFIG),
						className: "border border-border px-2 py-1 text-xs hover:border-leo hover:text-leo",
						children: "Reset"
					})
				]
			})
		]
	});
}
var KEY = "leo.cors.last_result";
function readSnapshot() {
	if (typeof window === "undefined") return null;
	try {
		const raw = window.localStorage.getItem(KEY);
		return raw ? JSON.parse(raw) : null;
	} catch {
		return null;
	}
}
function deriveConfig(snap) {
	const received = new Map(snap.rawHeaders.map(([k, v]) => [k.toLowerCase(), v]));
	const parseList = (v) => (v ?? "").split(/[,\s]+/).map((s) => s.trim()).filter(Boolean);
	const methodsRecv = parseList(received.get("access-control-allow-methods"));
	const headersRecv = parseList(received.get("access-control-allow-headers"));
	const methods = Array.from(new Set([
		...methodsRecv,
		snap.method,
		"GET",
		"POST",
		"OPTIONS"
	].map((m) => m.toUpperCase()))).filter((m) => m !== "*");
	const requested = snap.checks.filter((c) => c.header === "Access-Control-Allow-Headers").flatMap((c) => {
		const missing = (c.note ?? "").match(/Missing:\s*(.*)$/i)?.[1];
		return missing ? missing.split(/,\s*/) : [];
	});
	const headers = Array.from(new Set([
		...headersRecv,
		...requested,
		"Content-Type",
		"Authorization"
	].map((h) => h.trim()))).filter((h) => h && h !== "*");
	return {
		origin: snap.origin,
		methods,
		headers
	};
}
function snippet(fw, cfg) {
	const originJson = JSON.stringify(cfg.origin);
	const methodsJson = JSON.stringify(cfg.methods);
	const headersJson = JSON.stringify(cfg.headers);
	const headersCsv = cfg.headers.join(", ");
	const methodsCsv = cfg.methods.join(", ");
	switch (fw) {
		case "express": return `import cors from "cors";

app.use(cors({
  origin: ${originJson},
  methods: ${methodsJson},
  allowedHeaders: ${headersJson},
  credentials: false,
  maxAge: 86400,
}));

// Ensure OPTIONS preflight succeeds for every route:
app.options("*", cors());`;
		case "nest": return `// main.ts
app.enableCors({
  origin: ${originJson},
  methods: ${methodsJson},
  allowedHeaders: ${headersJson},
  credentials: false,
  maxAge: 86400,
});`;
		case "fastapi": return `from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[${originJson}],
    allow_methods=${JSON.stringify(cfg.methods)},
    allow_headers=${JSON.stringify(cfg.headers)},
    allow_credentials=False,
    max_age=86400,
)`;
		case "vite": return `// vite.config.ts — proxy the frontend dev server to your backend
// so the browser never sees a cross-origin request in dev.
export default defineConfig({
  server: {
    proxy: {
      "/api": {
        target: "http://localhost:8005",
        changeOrigin: true,
        secure: false,
      },
      "/health": {
        target: "http://localhost:8005",
        changeOrigin: true,
        secure: false,
      },
    },
  },
});`;
		case "generic": return `# Response headers your backend MUST send on every response
# (and on the OPTIONS preflight):

Access-Control-Allow-Origin: ${cfg.origin}
Access-Control-Allow-Methods: ${methodsCsv}
Access-Control-Allow-Headers: ${headersCsv}
Access-Control-Max-Age: 86400

# Preflight (OPTIONS) must return 204 with the headers above.`;
	}
}
var TABS = [
	{
		id: "express",
		label: "Express"
	},
	{
		id: "nest",
		label: "NestJS"
	},
	{
		id: "fastapi",
		label: "FastAPI"
	},
	{
		id: "vite",
		label: "Vite proxy"
	},
	{
		id: "generic",
		label: "Generic"
	}
];
function CorsSnippetsPanel() {
	const [snap, setSnap] = (0, import_react.useState)(() => readSnapshot());
	const [tab, setTab] = (0, import_react.useState)("fastapi");
	(0, import_react.useEffect)(() => {
		const handler = () => setSnap(readSnapshot());
		window.addEventListener("storage", handler);
		const id = setInterval(handler, 2e3);
		return () => {
			window.removeEventListener("storage", handler);
			clearInterval(id);
		};
	}, []);
	if (!snap) return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "border border-border p-4",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
			className: "eyebrow",
			children: "Backend CORS snippets"
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
			className: "mt-2 text-xs text-muted-foreground",
			children: "Run a preflight above first — the exact allow-headers, methods, and origin will be filled in here."
		})]
	});
	const cfg = deriveConfig(snap);
	const code = snippet(tab, cfg);
	async function copy() {
		try {
			await navigator.clipboard.writeText(code);
			toast.success(`${TABS.find((t) => t.id === tab)?.label} snippet copied`);
		} catch {
			toast.error("Clipboard blocked — select and copy manually");
		}
	}
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "border border-border p-4",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex flex-wrap items-baseline justify-between gap-2",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "eyebrow",
					children: "Backend CORS snippets"
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
					className: "mt-1 text-xs text-muted-foreground",
					children: [
						"Generated from your last preflight (",
						snap.method,
						" ",
						snap.url,
						")."
					]
				})] }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
					type: "button",
					onClick: copy,
					className: "border border-border px-3 py-1 text-[11px] font-semibold hover:border-leo hover:text-leo focus:outline-none focus-visible:ring-2 focus-visible:ring-leo",
					children: "Copy snippet"
				})]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				role: "tablist",
				"aria-label": "Framework",
				className: "mt-3 flex flex-wrap gap-1",
				children: TABS.map((t) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
					role: "tab",
					"aria-selected": tab === t.id,
					type: "button",
					onClick: () => setTab(t.id),
					className: "border px-2 py-0.5 text-[11px] font-semibold focus:outline-none focus-visible:ring-2 focus-visible:ring-leo " + (tab === t.id ? "border-leo bg-leo/10 text-leo" : "border-border hover:border-leo hover:text-leo"),
					children: t.label
				}, t.id))
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mt-3 grid gap-1 text-[11px] text-muted-foreground sm:grid-cols-3",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", { children: ["origin: ", /* @__PURE__ */ (0, import_jsx_runtime.jsx)("code", {
						className: "font-mono text-foreground",
						children: cfg.origin
					})] }),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", { children: ["methods: ", /* @__PURE__ */ (0, import_jsx_runtime.jsx)("code", {
						className: "font-mono text-foreground",
						children: cfg.methods.join(", ")
					})] }),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", { children: ["headers: ", /* @__PURE__ */ (0, import_jsx_runtime.jsx)("code", {
						className: "font-mono text-foreground",
						children: cfg.headers.join(", ")
					})] })
				]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("pre", {
				className: "mt-3 overflow-x-auto bg-input p-3 font-mono text-[11px] whitespace-pre",
				children: code
			})
		]
	});
}
var RANGE_MS = {
	"1h": 60 * 6e4,
	"24h": 1440 * 6e4,
	"7d": 10080 * 6e4,
	all: null
};
function fmtTime(ts) {
	return new Date(ts).toLocaleString();
}
function fmtDuration$1(ms) {
	if (ms < 1e3) return `${ms}ms`;
	const s = Math.round(ms / 1e3);
	if (s < 60) return `${s}s`;
	const m = Math.floor(s / 60);
	const rs = s % 60;
	if (m < 60) return rs ? `${m}m ${rs}s` : `${m}m`;
	const h = Math.floor(m / 60);
	const rm = m % 60;
	return rm ? `${h}h ${rm}m` : `${h}h`;
}
function HealthAlertTimeline() {
	const events = useAlertTimeline();
	const [range, setRange] = (0, import_react.useState)("24h");
	const [level, setLevel] = (0, import_react.useState)("all");
	const [query, setQuery] = (0, import_react.useState)("");
	const filtered = (0, import_react.useMemo)(() => {
		const cutoff = RANGE_MS[range];
		const now = Date.now();
		const q = query.trim().toLowerCase();
		return events.filter((e) => {
			if (cutoff !== null && (e.endedAt ?? now) < now - cutoff) return false;
			if (level !== "all" && e.peakLevel !== level) return false;
			if (q) {
				if (![...e.startReasons, ...e.lastReasons].join(" ").toLowerCase().includes(q)) return false;
			}
			return true;
		}).slice().reverse();
	}, [
		events,
		range,
		level,
		query
	]);
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "border border-border p-4",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex flex-wrap items-baseline justify-between gap-2",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "eyebrow",
					children: "Alert timeline"
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "mt-1 text-xs text-muted-foreground",
					children: "Every warn/critical episode with start, end, and thresholds exceeded."
				})] }), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "flex flex-wrap items-center gap-2",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("fieldset", {
						className: "flex gap-1",
						"aria-label": "Filter timeline by time range",
						children: Object.keys(RANGE_MS).map((r) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
							type: "button",
							onClick: () => setRange(r),
							"aria-pressed": range === r,
							className: "border px-2 py-0.5 text-[11px] font-semibold focus:outline-none focus-visible:ring-2 focus-visible:ring-leo " + (range === r ? "border-leo bg-leo/10 text-leo" : "border-border hover:border-leo hover:text-leo"),
							children: r === "all" ? "All" : r
						}, r))
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
						type: "button",
						onClick: () => {
							clearAlertTimeline();
							toast.success("Alert timeline cleared");
						},
						className: "border border-border px-2 py-0.5 text-[11px] font-semibold hover:border-red-500 hover:text-red-400 focus:outline-none focus-visible:ring-2 focus-visible:ring-red-500",
						children: "Clear"
					})]
				})]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mt-3 flex flex-wrap items-center gap-2",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("fieldset", {
						className: "flex gap-1",
						"aria-label": "Filter timeline by level",
						children: [
							"all",
							"warn",
							"critical"
						].map((l) => {
							const active = level === l;
							return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
								type: "button",
								onClick: () => setLevel(l),
								"aria-pressed": active,
								className: `border border-border px-2 py-0.5 text-[11px] font-semibold uppercase focus:outline-none focus-visible:ring-2 focus-visible:ring-leo ${l === "critical" ? active ? "border-red-500 bg-red-500/10 text-red-300" : "hover:border-red-500 hover:text-red-400" : l === "warn" ? active ? "border-yellow-400 bg-yellow-400/10 text-yellow-200" : "hover:border-yellow-400 hover:text-yellow-200" : active ? "border-leo bg-leo/10 text-leo" : "hover:border-leo hover:text-leo"}`,
								children: l
							}, l);
						})
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("label", {
						className: "flex flex-1 min-w-[180px] items-center gap-2 text-xs",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "sr-only",
							children: "Search alert reasons"
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("input", {
							type: "search",
							value: query,
							onChange: (e) => setQuery(e.target.value),
							placeholder: "Search reasons (e.g. latency, 500, cors)…",
							className: "w-full border border-border bg-background px-2 py-1 font-mono text-xs focus:border-leo focus:outline-none"
						})]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
						className: "text-[11px] text-muted-foreground",
						children: [
							filtered.length,
							"/",
							events.length
						]
					})
				]
			}),
			filtered.length === 0 ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "mt-4 text-xs text-muted-foreground",
				children: "No alerts match these filters. Try widening the range or clearing the search."
			}) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)("ul", {
				className: "mt-4 space-y-2",
				"aria-live": "polite",
				children: filtered.map((e) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(TimelineRow, { event: e }, e.id))
			})
		]
	});
}
function TimelineRow({ event }) {
	const ended = event.endedAt ?? null;
	const duration = ended ? ended - event.startedAt : Date.now() - event.startedAt;
	const isCritical = event.peakLevel === "critical";
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", {
		className: "border-l-2 p-2 text-xs " + (isCritical ? "border-red-500 bg-red-500/5" : "border-yellow-500 bg-yellow-500/5"),
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex flex-wrap items-baseline justify-between gap-2",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
					className: "font-semibold uppercase tracking-wide " + (isCritical ? "text-red-400" : "text-yellow-200"),
					children: [isCritical ? "Critical" : "Warn", ended ? "" : " · ongoing"]
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "font-mono text-[11px] text-muted-foreground",
					children: fmtDuration$1(duration)
				})]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
				className: "mt-1 text-[11px] text-muted-foreground",
				children: [
					fmtTime(event.startedAt),
					" → ",
					ended ? fmtTime(ended) : "now"
				]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("ul", {
				className: "mt-1 list-inside list-disc space-y-0.5",
				children: (event.lastReasons.length ? event.lastReasons : event.startReasons).map((r) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("li", { children: r }, r))
			})
		]
	});
}
var KIND_STYLES = {
	connect: "text-muted-foreground",
	open: "text-leo",
	error: "text-red-400",
	reconnect: "text-yellow-400",
	"polling-start": "text-yellow-400",
	"polling-recover": "text-leo",
	closed: "text-muted-foreground",
	info: "text-muted-foreground"
};
function formatEntry(e) {
	const bits = [
		new Date(e.at).toISOString(),
		e.kind.toUpperCase(),
		e.message
	];
	if (e.attempt != null) bits.push(`attempt=${e.attempt}`);
	if (e.backoffMs != null) bits.push(`backoff=${e.backoffMs}ms`);
	if (e.transport) bits.push(`transport=${e.transport}`);
	if (e.readyState != null) bits.push(`readyState=${e.readyState}`);
	return bits.join(" · ");
}
function SseDiagnosticsLog() {
	const log = useSseLog();
	const [filter, setFilter] = (0, import_react.useState)("all");
	const filtered = (0, import_react.useMemo)(() => filter === "all" ? log : log.filter((e) => e.kind === filter), [log, filter]);
	async function copyAll() {
		const text = filtered.map(formatEntry).join("\n");
		if (!text) {
			toast.error("No SSE log entries to copy");
			return;
		}
		try {
			await navigator.clipboard.writeText(text);
			toast.success(`Copied ${filtered.length} log entries`);
		} catch {
			toast.error("Clipboard write failed");
		}
	}
	async function copyOne(e) {
		try {
			await navigator.clipboard.writeText(formatEntry(e));
			toast.success("Entry copied");
		} catch {
			toast.error("Clipboard write failed");
		}
	}
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "border border-border p-4",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "flex flex-wrap items-baseline justify-between gap-2",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "eyebrow",
				children: "SSE diagnostics log"
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
				className: "mt-1 text-xs text-muted-foreground",
				children: [
					"Last ",
					log.length,
					" lifecycle events · reconnect attempts, backoff, errors"
				]
			})] }), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex flex-wrap items-center gap-2 text-xs",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("select", {
						value: filter,
						onChange: (e) => setFilter(e.target.value),
						className: "border border-border bg-background px-2 py-1 font-mono text-xs focus:border-leo focus:outline-none",
						"aria-label": "Filter SSE log entries",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("option", {
								value: "all",
								children: "all"
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("option", {
								value: "open",
								children: "open"
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("option", {
								value: "error",
								children: "error"
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("option", {
								value: "reconnect",
								children: "reconnect"
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("option", {
								value: "polling-start",
								children: "polling-start"
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("option", {
								value: "polling-recover",
								children: "polling-recover"
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("option", {
								value: "connect",
								children: "connect"
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("option", {
								value: "closed",
								children: "closed"
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("option", {
								value: "info",
								children: "info"
							})
						]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
						type: "button",
						onClick: copyAll,
						className: "border border-border px-2 py-1 text-xs font-semibold hover:border-leo hover:text-leo",
						children: "Copy all"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
						type: "button",
						onClick: () => {
							clearSseLog();
							toast.message("SSE log cleared");
						},
						className: "border border-border px-2 py-1 text-xs font-semibold hover:border-red-400 hover:text-red-400",
						children: "Clear"
					})
				]
			})]
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: "mt-3 max-h-72 overflow-y-auto border border-border bg-background/60 font-mono text-[11px]",
			children: filtered.length === 0 ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "p-3 text-muted-foreground",
				children: "No SSE events recorded yet. Start the benchmark runner to capture stream lifecycle."
			}) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)("ul", {
				className: "divide-y divide-border/60",
				children: filtered.slice().reverse().map((e) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", {
					className: "flex items-start gap-2 p-2",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "w-20 shrink-0 text-muted-foreground",
							children: new Date(e.at).toLocaleTimeString()
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: `w-24 shrink-0 font-semibold ${KIND_STYLES[e.kind]}`,
							children: e.kind
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
							className: "flex-1 break-all",
							children: [
								e.message,
								e.attempt != null && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
									className: "ml-2 text-muted-foreground",
									children: ["attempt=", e.attempt]
								}),
								e.backoffMs != null && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
									className: "ml-2 text-muted-foreground",
									children: [
										"backoff=",
										e.backoffMs,
										"ms"
									]
								}),
								e.transport && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
									className: "ml-2 text-muted-foreground",
									children: ["transport=", e.transport]
								}),
								e.readyState != null && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
									className: "ml-2 text-muted-foreground",
									children: ["rs=", e.readyState]
								})
							]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
							type: "button",
							onClick: () => copyOne(e),
							className: "shrink-0 border border-border px-1.5 py-0.5 text-[10px] hover:border-leo hover:text-leo",
							title: "Copy this entry",
							children: "copy"
						})
					]
				}, e.id))
			})
		})]
	});
}
var DIAG_KEY = "leo.bench.sse-diag";
function read() {
	if (typeof window === "undefined") return null;
	try {
		const raw = window.localStorage.getItem(DIAG_KEY);
		return raw ? JSON.parse(raw) : null;
	} catch {
		return null;
	}
}
function SseLiveIndicator() {
	const [diag, setDiag] = (0, import_react.useState)(() => read());
	const log = useSseLog();
	(0, import_react.useEffect)(() => {
		const id = setInterval(() => setDiag(read()), 1e3);
		return () => clearInterval(id);
	}, []);
	const status = diag?.status ?? "idle";
	const attempts = diag?.reconnectAttempts ?? 0;
	const backoff = [...log].reverse().find((e) => e.kind === "reconnect")?.backoffMs;
	const styles = {
		open: "border-leo bg-leo/10 text-leo",
		polling: "border-blue-400 bg-blue-400/10 text-blue-300",
		reconnecting: "border-yellow-400 bg-yellow-400/10 text-yellow-300",
		error: "border-red-500 bg-red-500/10 text-red-300",
		closed: "border-border text-muted-foreground",
		idle: "border-border text-muted-foreground"
	};
	const pulse = status === "reconnecting" ? "animate-pulse" : "";
	const label = status === "open" ? "SSE open" : status === "polling" ? "SSE → polling" : status === "reconnecting" ? "SSE reconnecting" : status === "error" ? "SSE error" : status === "closed" ? "SSE closed" : "SSE idle";
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
		role: "status",
		"aria-live": "polite",
		title: diag?.lastError ? `Last error: ${diag.lastError}` : "Live SSE benchmark stream status",
		className: `inline-flex items-center gap-2 border px-2.5 py-1 text-[11px] font-semibold uppercase tracking-wide ${styles[status] ?? styles.idle} ${pulse}`,
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
				className: `inline-block h-1.5 w-1.5 rounded-full ${status === "open" ? "bg-leo" : status === "polling" ? "bg-blue-400" : status === "reconnecting" ? "bg-yellow-400" : status === "error" ? "bg-red-500" : "bg-muted-foreground/60"}`,
				"aria-hidden": true
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { children: label }),
			status === "reconnecting" && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
				className: "font-mono normal-case tracking-normal text-[10px] text-foreground/80",
				children: [
					"attempt ",
					attempts,
					backoff != null ? ` · ${backoff}ms` : ""
				]
			}),
			status !== "reconnecting" && attempts > 0 && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
				className: "font-mono normal-case tracking-normal text-[10px] text-foreground/60",
				children: [attempts, " retries"]
			})
		]
	});
}
var CORS_RESULT_KEY = "leo.cors.last_result";
var SSE_LOG_KEY = "leo.sse.log_v1";
function toB64Url(s) {
	return (typeof btoa !== "undefined" ? btoa(unescape(encodeURIComponent(s))) : "").replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}
function fromB64Url(s) {
	const b64 = s.replace(/-/g, "+").replace(/_/g, "/") + "===".slice((s.length + 3) % 4);
	return typeof atob !== "undefined" ? decodeURIComponent(escape(atob(b64))) : "";
}
function readJson(key) {
	if (typeof window === "undefined") return null;
	try {
		const raw = window.localStorage.getItem(key);
		return raw ? JSON.parse(raw) : null;
	} catch {
		return null;
	}
}
function buildPermalinkState() {
	return {
		v: 1,
		generatedAt: (/* @__PURE__ */ new Date()).toISOString(),
		thresholds: getThresholds(),
		history: getHealthHistory(),
		sseConfig: getSseConfig(),
		sseLog: getSseLog(),
		corsResult: readJson(CORS_RESULT_KEY)
	};
}
function encodePermalinkState(state) {
	return toB64Url(JSON.stringify(state));
}
function decodePermalinkState(payload) {
	try {
		const obj = JSON.parse(fromB64Url(payload));
		if (!obj || obj.v !== 1) return null;
		return obj;
	} catch {
		return null;
	}
}
function buildPermalinkUrl(state = buildPermalinkState()) {
	if (typeof window === "undefined") return "";
	const u = new URL(window.location.href);
	u.searchParams.delete("state");
	u.searchParams.set("state", encodePermalinkState(state));
	return u.toString();
}
/** Apply a decoded permalink to local storage. Replaces existing state. */
function applyPermalinkState(state) {
	const summary = {
		thresholds: false,
		history: 0,
		sseConfig: false,
		sseLog: 0,
		corsResult: false
	};
	if (state.thresholds && typeof state.thresholds === "object") {
		setThresholds({
			...DEFAULT_THRESHOLDS$1,
			...state.thresholds
		});
		summary.thresholds = true;
	}
	if (Array.isArray(state.history)) summary.history = importHealthEntries(state.history, "replace").imported;
	if (state.sseConfig && typeof state.sseConfig === "object") {
		setSseConfig({
			...DEFAULT_SSE_CONFIG,
			...state.sseConfig
		});
		summary.sseConfig = true;
	}
	if (Array.isArray(state.sseLog) && typeof window !== "undefined") try {
		window.localStorage.setItem(SSE_LOG_KEY, JSON.stringify(state.sseLog.slice(-200)));
		window.dispatchEvent(new CustomEvent("leo:sse-log-changed"));
		summary.sseLog = state.sseLog.length;
	} catch {}
	if (state.corsResult && typeof window !== "undefined") try {
		window.localStorage.setItem(CORS_RESULT_KEY, JSON.stringify(state.corsResult));
		summary.corsResult = true;
	} catch {}
	return summary;
}
function readPermalinkFromUrl() {
	if (typeof window === "undefined") return null;
	const p = new URL(window.location.href).searchParams.get("state");
	return p ? decodePermalinkState(p) : null;
}
function clearPermalinkFromUrl() {
	if (typeof window === "undefined") return;
	const u = new URL(window.location.href);
	u.searchParams.delete("state");
	window.history.replaceState({}, "", u.toString());
}
function PermalinkButton() {
	async function copy() {
		try {
			const url = buildPermalinkUrl();
			await navigator.clipboard.writeText(url);
			const len = url.length;
			toast.success(`Permalink copied (${len.toLocaleString()} chars)`);
		} catch (err) {
			toast.error(err instanceof Error ? err.message : "Copy failed");
		}
	}
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
		type: "button",
		onClick: copy,
		title: "Copy a URL that restores current thresholds, health history, CORS result, SSE settings, and sseLog",
		className: "border border-border px-3 py-1.5 text-xs font-semibold hover:border-leo hover:text-leo focus:outline-none focus-visible:ring-2 focus-visible:ring-leo",
		children: "Copy permalink"
	});
}
function percentile(sorted, p) {
	if (!sorted.length) return null;
	return sorted[Math.min(sorted.length - 1, Math.floor(p / 100 * sorted.length))];
}
function fmtDuration(ms) {
	if (ms < 1e3) return `${ms}ms`;
	const s = Math.round(ms / 1e3);
	if (s < 60) return `${s}s`;
	return `${Math.floor(s / 60)}m ${s % 60}s`;
}
function GeneratePdfReportButton() {
	const [busy, setBusy] = (0, import_react.useState)(false);
	async function generate() {
		setBusy(true);
		try {
			const doc = new import_jspdf_node_min.default({
				unit: "pt",
				format: "a4"
			});
			const pageW = doc.internal.pageSize.getWidth();
			const pageH = doc.internal.pageSize.getHeight();
			const margin = 36;
			let y = margin;
			doc.setFont("helvetica", "bold");
			doc.setFontSize(18);
			doc.text("LEO AI — Benchmarks report", margin, y);
			y += 22;
			doc.setFont("helvetica", "normal");
			doc.setFontSize(10);
			doc.setTextColor(120);
			doc.text(`Generated ${(/* @__PURE__ */ new Date()).toLocaleString()}`, margin, y);
			y += 14;
			doc.text(`API base: ${getApiBase()}`, margin, y);
			y += 20;
			doc.setTextColor(0);
			const chartEl = document.getElementById("health-history-chart");
			if (chartEl) try {
				const dataUrl = await toPng(chartEl, {
					pixelRatio: 2,
					backgroundColor: "#0a0a0a",
					cacheBust: true
				});
				const imgW = pageW - margin * 2;
				const imgH = chartEl.clientHeight / chartEl.clientWidth * imgW;
				doc.addImage(dataUrl, "PNG", margin, y, imgW, imgH);
				y += imgH + 16;
			} catch (err) {
				doc.setTextColor(180, 0, 0);
				doc.text("Chart snapshot failed: " + (err instanceof Error ? err.message : "unknown"), margin, y);
				y += 16;
				doc.setTextColor(0);
			}
			else {
				doc.setTextColor(120);
				doc.text("Health history chart not on page — skipped.", margin, y);
				y += 16;
				doc.setTextColor(0);
			}
			const history = getHealthHistory();
			const reliability = computeReliability(history);
			const thresholds = getThresholds();
			const okCount = history.filter((h) => h.status === "online").length;
			const failCount = history.filter((h) => h.status !== "online" && h.status !== "checking").length;
			const latencies = history.filter((h) => h.status === "online" && typeof h.latencyMs === "number").map((h) => h.latencyMs).sort((a, b) => a - b);
			const avgLatency = latencies.length ? Math.round(latencies.reduce((s, n) => s + n, 0) / latencies.length) : null;
			const rows = [
				["Samples", String(history.length)],
				["Online", String(okCount)],
				["Failures", String(failCount)],
				["Failure rate", `${reliability.failureRatePct.toFixed(1)}%`],
				["Reliability level", reliability.level],
				["p50 latency", latencies.length ? `${percentile(latencies, 50)}ms` : "—"],
				["p95 latency", latencies.length ? `${percentile(latencies, 95)}ms` : "—"],
				["p99 latency", latencies.length ? `${percentile(latencies, 99)}ms` : "—"],
				["Avg latency", avgLatency != null ? `${avgLatency}ms` : "—"],
				["Thresholds", `latencyWarn=${thresholds.latencyWarnMs}ms, avgLatencyWarn=${thresholds.avgLatencyWarnMs}ms, failRate=${thresholds.failureRatePct}%, consecutive=${thresholds.consecutiveFailLimit}`]
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
				doc.text(String(v), 176, y, { maxWidth: pageW - margin * 2 - 140 });
				y += 14;
			}
			y += 10;
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
			} else for (const ep of alerts.slice(-40).reverse()) {
				if (y > pageH - margin) {
					doc.addPage();
					y = margin;
				}
				const dur = (ep.endedAt ?? Date.now()) - ep.startedAt;
				const line1 = `[${ep.peakLevel.toUpperCase()}] ${new Date(ep.startedAt).toLocaleString()} → ${ep.endedAt ? new Date(ep.endedAt).toLocaleString() : "ongoing"} · ${fmtDuration(dur)}`;
				doc.text(line1, margin, y, { maxWidth: pageW - margin * 2 });
				y += 12;
				const reasons = ep.lastReasons.length ? ep.lastReasons : ep.startReasons;
				if (reasons.length) {
					doc.setTextColor(120);
					doc.text("· " + reasons.join("; "), 48, y, { maxWidth: pageW - margin * 2 - 12 });
					doc.setTextColor(0);
					y += 12;
				}
			}
			y += 6;
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
			} else for (const e of log.slice(-120)) {
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
					e.transport ? `t=${e.transport}` : ""
				].filter(Boolean).join(" · ");
				doc.text(bits, margin, y, { maxWidth: pageW - margin * 2 });
				y += 10;
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
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
		type: "button",
		onClick: generate,
		disabled: busy,
		className: "border border-border px-3 py-1.5 text-xs font-semibold hover:border-leo hover:text-leo focus:outline-none focus-visible:ring-2 focus-visible:ring-leo disabled:opacity-50",
		children: busy ? "Generating PDF…" : "Generate PDF report"
	});
}
function BenchmarksPage() {
	const [polling, setPolling] = usePollingIntervals();
	const health = useBackendHealth(polling.healthMs);
	const [liveRps, setLiveRps] = (0, import_react.useState)(void 0);
	const [selectedRun, setSelectedRun] = (0, import_react.useState)(null);
	const shared = (0, import_react.useMemo)(() => readShareParams(), []);
	(0, import_react.useEffect)(() => {
		if (shared.run && !selectedRun) setSelectedRun(shared.run);
		if (shared.run || shared.compare) toast.message("Loaded shared benchmark from link");
		const permalink = readPermalinkFromUrl();
		if (permalink) {
			const summary = applyPermalinkState(permalink);
			clearPermalinkFromUrl();
			toast.success(`Permalink applied · history=${summary.history} · thresholds=${summary.thresholds ? "✓" : "—"} · sseLog=${summary.sseLog} · cors=${summary.corsResult ? "✓" : "—"}`);
		}
	}, []);
	const { data, isLoading, error, refetch, isFetching } = useQuery({
		queryKey: ["public-metrics"],
		queryFn: () => leoJson("/api/v1/leo/metrics"),
		retry: 4,
		retryDelay: (attempt) => Math.min(8e3, 500 * 2 ** attempt),
		refetchOnWindowFocus: false,
		refetchInterval: polling.metricsMs > 0 ? polling.metricsMs : false
	});
	const m = data ?? {
		leo_total_requests: 172e4,
		leo_compute_avoided: 1707960,
		leo_avoidance_rate_pct: 99.3,
		leo_gpu_watts_saved: 49e4,
		leo_crystallization_hit_rate: 82.5
	};
	async function rerunChecks() {
		toast.message("Re-running checks…");
		const [, m2] = await Promise.all([health.refresh(), refetch()]);
		if (m2.error) toast.error("Metrics check failed");
		else toast.success("Checks complete");
	}
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "mx-auto max-w-[1440px] px-6 py-24",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "eyebrow",
				children: "Benchmarks"
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h1", {
				className: "mt-3 font-display text-5xl font-bold md:text-6xl",
				children: "Measured, not simulated."
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mt-4 flex flex-wrap items-center gap-4",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(BackendStatusBadge, {}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(SseLiveIndicator, {}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
						type: "button",
						onClick: rerunChecks,
						disabled: isFetching || health.status === "checking",
						className: "border border-leo bg-leo/10 px-3 py-1.5 text-xs font-medium text-leo hover:bg-leo/20 disabled:opacity-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-leo",
						children: isFetching || health.status === "checking" ? "Running…" : "Re-run checks"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CurlHealthButton, {}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CurlMetricsButton, {}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CopyDebugReportButton, {}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(ExportDebugReportButton, {}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(ExportHealthCsvButton, {}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(ImportDebugReportButton, {}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(BurstHealthCheckButton, {}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(PermalinkButton, {}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(GeneratePdfReportButton, {})
				]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "mt-4",
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(HealthDegradationAlert, {})
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("fieldset", {
				className: "mt-4 inline-flex flex-wrap items-center gap-3 border border-border bg-background/60 px-3 py-2 text-xs",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("legend", {
						className: "px-1 text-[11px] uppercase tracking-wide text-muted-foreground",
						children: "Polling"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(IntervalField, {
						label: "/health",
						value: polling.healthMs,
						onChange: (v) => setPolling({
							...polling,
							healthMs: v
						})
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(IntervalField, {
						label: "/metrics",
						value: polling.metricsMs,
						onChange: (v) => setPolling({
							...polling,
							metricsMs: v
						})
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
						className: "text-muted-foreground",
						children: "0 = off"
					})
				]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "mt-4 max-w-2xl text-muted-foreground",
				"aria-live": "polite",
				children: isLoading ? "Fetching live metrics… (auto-retrying with backoff)" : error ? "Showing reference figures (backend offline after retries)." : isFetching ? "Refreshing metrics…" : "Live from your LEO runtime."
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mt-16 grid gap-px bg-border md:grid-cols-2 lg:grid-cols-3",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Big, {
						label: "Total requests",
						value: fmt(m.leo_total_requests)
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Big, {
						label: "Compute avoided",
						value: fmt(m.leo_compute_avoided)
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Big, {
						label: "Avoidance rate",
						value: `${(m.leo_avoidance_rate_pct ?? 0).toFixed(1)}%`
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Big, {
						label: "GPU watts saved",
						value: fmt(m.leo_gpu_watts_saved)
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Big, {
						label: "Cache hit rate",
						value: `${(m.leo_crystallization_hit_rate ?? 0).toFixed(1)}%`
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Big, {
						label: "Router latency",
						value: "10 ms"
					})
				]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mt-16 grid gap-8 lg:grid-cols-2",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(LatencyChart, {}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(DiagnosticsPanel, {})]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "mt-8",
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(BackendDiagnosticsPanel, {})
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "mt-8",
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(BackendHealthPanel, {})
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mt-8 grid gap-8 lg:grid-cols-2",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(HealthHistoryChart, {}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(SseStatusWidget, {})]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mt-8 grid gap-8 lg:grid-cols-2",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(SseFailureDiagnostic, {}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CorsPreflightTester, {})]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "mt-8",
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CorsSnippetsPanel, {})
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "mt-8",
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(HealthAlertTimeline, {})
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "mt-8",
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(SseDiagnosticsLog, {})
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mt-8 grid gap-8",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(HardwareProfileCard, {
						liveRps,
						avoidanceRatePct: m.leo_avoidance_rate_pct,
						wattsSaved: m.leo_gpu_watts_saved,
						selectedRun
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(BenchmarkRunner, { onResult: (run) => {
						setLiveRps(run.throughputRps);
						setSelectedRun(run);
					} }),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(BenchmarkHistory, {
						selectedId: selectedRun?.id ?? null,
						onSelect: (r) => setSelectedRun(r)
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(BenchmarkComparison, {
						presetBase: shared.compare?.base ?? null,
						presetTarget: shared.compare?.target ?? null
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(RegressionThresholdsCard, {})
				]
			})
		]
	});
}
function fmt(n) {
	if (!n) return "—";
	if (n >= 1e6) return `${(n / 1e6).toFixed(2)}M`;
	if (n >= 1e3) return `${(n / 1e3).toFixed(1)}K`;
	return `${n}`;
}
function Big({ label, value }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "bg-background p-10",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: "eyebrow",
			children: label
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: "mt-4 font-display text-5xl font-bold text-leo md:text-6xl",
			children: value
		})]
	});
}
function IntervalField({ label, value, onChange }) {
	const options = [
		0,
		1e3,
		3e3,
		5e3,
		15e3,
		3e4,
		6e4
	];
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("label", {
		className: "inline-flex items-center gap-1",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
			className: "text-muted-foreground",
			children: label
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("select", {
			value: options.includes(value) ? value : 0,
			onChange: (e) => onChange(Number(e.target.value)),
			className: "border border-border bg-background px-2 py-1 font-mono text-xs focus:border-leo focus:outline-none",
			"aria-label": `Polling interval for ${label}`,
			children: options.map((o) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("option", {
				value: o,
				children: o === 0 ? "off" : o < 1e3 ? `${o}ms` : `${o / 1e3}s`
			}, o))
		})]
	});
}
//#endregion
export { BenchmarksPage as component };
