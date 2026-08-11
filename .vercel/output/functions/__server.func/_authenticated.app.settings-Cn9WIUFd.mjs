import { o as __toESM } from "./_runtime.mjs";
import { i as require_react, r as require_jsx_runtime } from "./_libs/react+tanstack__react-query.mjs";
import { n as toast } from "./_libs/sonner.mjs";
import { d as setDebugMode, i as getDebugMode, n as getApiBase, u as setApiBase } from "./_ssr/leo-client-D7U1wpIv.mjs";
import { a as setTelemetryMode, i as setRetentionDays, n as getRetentionDays, pruneQueue, r as getTelemetryMode, t as clearTelemetryQueue } from "./_ssr/web-vitals-D6YYXSoZ.mjs";
import { l as getSyncPath, m as pullAndMerge, u as isSyncEnabled, v as setSyncEnabled, y as setSyncPath } from "./_ssr/chat-history-D5ztPwzC.mjs";
import { t as Route } from "./_authenticated.app.settings-DHmZrBWt.mjs";
import { C as useThresholds, S as useSseConfig, a as checkBackendHealth, n as DEFAULT_SSE_CONFIG, r as DEFAULT_THRESHOLDS, t as BackendHealthPanel } from "./_ssr/sse-config-DZ3wmwiX.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/_authenticated.app.settings-Cn9WIUFd.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
var KEY = "leo.api_base_presets";
var ACTIVE_KEY = "leo.api_base_preset_active";
var DEFAULT_PRESETS = [
	{
		kind: "local",
		label: "Local",
		url: "http://localhost:8005",
		hint: "Python backend running on your machine (dev only)."
	},
	{
		kind: "tunnel",
		label: "Tunnel",
		url: "",
		hint: "Public ngrok / Cloudflare Tunnel URL exposing your laptop backend."
	},
	{
		kind: "deployed",
		label: "Deployed",
		url: "",
		hint: "Production LEO backend (e.g. https://api.yourdomain.com)."
	}
];
function getPresets() {
	if (typeof window === "undefined") return DEFAULT_PRESETS;
	try {
		const raw = window.localStorage.getItem(KEY);
		if (!raw) return DEFAULT_PRESETS;
		const parsed = JSON.parse(raw);
		return DEFAULT_PRESETS.map((d) => parsed.find((p) => p.kind === d.kind) ?? d);
	} catch {
		return DEFAULT_PRESETS;
	}
}
function savePresets(list) {
	if (typeof window === "undefined") return;
	window.localStorage.setItem(KEY, JSON.stringify(list));
}
function getActivePresetKind() {
	if (typeof window === "undefined") return "local";
	return window.localStorage.getItem(ACTIVE_KEY) || detectKind(getApiBase());
}
function activatePreset(kind) {
	const preset = getPresets().find((p) => p.kind === kind);
	if (!preset || !preset.url) throw new Error(`No URL configured for ${kind}`);
	setApiBase(preset.url);
	if (typeof window !== "undefined") {
		window.localStorage.setItem(ACTIVE_KEY, kind);
		window.dispatchEvent(new CustomEvent("leo:api-base-changed", { detail: preset.url }));
	}
}
function updatePresetUrl(kind, url) {
	savePresets(getPresets().map((p) => p.kind === kind ? {
		...p,
		url
	} : p));
}
function detectKind(url) {
	if (/localhost|127\.0\.0\.1/.test(url)) return "local";
	if (/\.ngrok|\.trycloudflare\.com|\.loca\.lt/.test(url)) return "tunnel";
	if (/^https?:\/\//.test(url)) return "deployed";
	return "custom";
}
function BackendSwitcher() {
	const [presets, setPresets] = (0, import_react.useState)([]);
	const [active, setActive] = (0, import_react.useState)("local");
	(0, import_react.useEffect)(() => {
		setPresets(getPresets());
		setActive(getActivePresetKind());
	}, []);
	async function switchTo(kind) {
		const p = presets.find((x) => x.kind === kind);
		if (!p?.url) {
			toast.error(`No URL saved for "${kind}". Paste one below first.`);
			return;
		}
		try {
			activatePreset(kind);
			setActive(kind);
			toast.message(`Switched to ${kind} — pinging ${p.url}…`);
			const h = await checkBackendHealth(p.url);
			if (h.status === "online") toast.success(`${kind} backend online (${h.latencyMs}ms)`);
			else toast.error(`${kind} backend ${h.status}: ${h.message ?? h.httpStatus ?? ""}`);
		} catch (e) {
			toast.error(e instanceof Error ? e.message : "Failed to switch");
		}
	}
	function updateUrl(kind, url) {
		updatePresetUrl(kind, url);
		setPresets(getPresets());
	}
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [
		/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
			className: "eyebrow",
			children: "Backend switcher"
		}),
		/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
			className: "mt-2 font-display text-2xl font-bold",
			children: "One-click environment"
		}),
		/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
			className: "mt-2 text-sm text-muted-foreground",
			children: "Swap between your local laptop backend, a public tunnel (ngrok / Cloudflare), or a deployed production URL. Health is verified after each switch."
		}),
		/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: "mt-4 grid gap-3 sm:grid-cols-3",
			role: "radiogroup",
			"aria-label": "Backend preset",
			children: presets.map((p) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("button", {
				type: "button",
				role: "radio",
				"aria-checked": active === p.kind,
				onClick: () => switchTo(p.kind),
				className: `border p-4 text-left focus:outline-none focus-visible:ring-2 focus-visible:ring-leo ${active === p.kind ? "border-leo bg-leo/10" : "border-border hover:border-leo"}`,
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "flex items-center justify-between",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "font-display text-lg font-bold",
							children: p.label
						}), active === p.kind && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "text-[10px] font-bold uppercase tracking-wider text-leo",
							children: "Active"
						})]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "mt-1 text-xs text-muted-foreground",
						children: p.hint
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("code", {
						className: "mt-2 block truncate font-mono text-[11px] text-foreground/80",
						children: p.url || "— not set —"
					})
				]
			}, p.kind))
		}),
		/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: "mt-6 space-y-3",
			children: presets.map((p) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("label", {
				className: "block",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
					className: "eyebrow",
					children: [p.label, " URL"]
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("input", {
					value: p.url,
					onChange: (e) => updateUrl(p.kind, e.target.value),
					placeholder: p.kind === "local" ? "http://localhost:8005" : p.kind === "tunnel" ? "https://xxxx.ngrok-free.app" : "https://api.yourdomain.com",
					className: "mt-1 w-full bg-input px-3 py-2 font-mono text-sm outline-none focus:ring-1 focus:ring-leo",
					"aria-label": `${p.label} backend URL`
				})]
			}, p.kind))
		}),
		/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("details", {
			className: "mt-6 border border-border p-4 text-sm",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("summary", {
				className: "cursor-pointer font-semibold",
				children: "Tunnel setup (expose your laptop backend to the preview)"
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mt-3 space-y-3 text-muted-foreground",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "font-semibold text-foreground",
						children: "Option A — Cloudflare Tunnel (free, no signup)"
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("pre", {
						className: "mt-1 overflow-x-auto bg-input p-3 font-mono text-xs",
						children: `# 1. Install
brew install cloudflared        # macOS
winget install --id Cloudflare.cloudflared   # Windows

# 2. Start your Python backend on 8005, then:
cloudflared tunnel --url http://localhost:8005

# 3. Copy the https://<random>.trycloudflare.com URL
#    into the "Tunnel" field above and click Tunnel.`
					})] }),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "font-semibold text-foreground",
						children: "Option B — ngrok"
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("pre", {
						className: "mt-1 overflow-x-auto bg-input p-3 font-mono text-xs",
						children: `# 1. Install & auth
brew install ngrok/ngrok/ngrok
ngrok config add-authtoken <YOUR_TOKEN>

# 2. Start tunnel
ngrok http 8005

# 3. Paste the https://xxxx.ngrok-free.app URL
#    into the "Tunnel" field above.`
					})] }),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "text-xs",
						children: "Make sure your Python backend enables CORS for the frontend origin (Lovable preview or your deployed domain)."
					})
				]
			})]
		})
	] });
}
function HealthDegradationSettings() {
	const [t, setT] = useThresholds();
	function reset() {
		setT(DEFAULT_THRESHOLDS);
		toast.success("Thresholds reset to defaults");
	}
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "border border-border p-4",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "eyebrow",
				children: "Health degradation thresholds"
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "mt-1 text-xs text-muted-foreground",
				children: "Trigger the degradation alert when any of these limits are exceeded. Persisted per browser."
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mt-4 grid gap-3 text-xs sm:grid-cols-2",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(NumField, {
						label: "Consecutive failures",
						value: t.consecutiveFailLimit,
						min: 1,
						max: 30,
						onChange: (v) => setT({
							...t,
							consecutiveFailLimit: v
						})
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(NumField, {
						label: "Single-sample latency warn (ms)",
						value: t.latencyWarnMs,
						min: 50,
						max: 3e4,
						step: 50,
						onChange: (v) => setT({
							...t,
							latencyWarnMs: v
						})
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(NumField, {
						label: "Avg latency warn (ms)",
						value: t.avgLatencyWarnMs,
						min: 50,
						max: 3e4,
						step: 50,
						onChange: (v) => setT({
							...t,
							avgLatencyWarnMs: v
						})
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(NumField, {
						label: "Failure rate % (over window)",
						value: t.failureRatePct,
						min: 1,
						max: 100,
						onChange: (v) => setT({
							...t,
							failureRatePct: v
						})
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(NumField, {
						label: "Window size (samples)",
						value: t.windowSize,
						min: 2,
						max: 60,
						onChange: (v) => setT({
							...t,
							windowSize: v
						})
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(NumField, {
						label: "Timeout (ms)",
						value: t.timeoutMs,
						min: 500,
						max: 6e4,
						step: 500,
						onChange: (v) => setT({
							...t,
							timeoutMs: v
						})
					})
				]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
				type: "button",
				onClick: reset,
				className: "mt-4 border border-border px-3 py-1.5 text-xs font-semibold hover:border-leo hover:text-leo focus:outline-none focus-visible:ring-2 focus-visible:ring-leo",
				children: "Reset to defaults"
			})
		]
	});
}
function NumField({ label, value, onChange, min, max, step = 1 }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("label", {
		className: "flex flex-col gap-1",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
			className: "text-muted-foreground",
			children: label
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("input", {
			type: "number",
			value,
			min,
			max,
			step,
			onChange: (e) => {
				const n = Number(e.target.value);
				if (Number.isFinite(n)) onChange(Math.max(min, Math.min(max, n)));
			},
			className: "border border-border bg-background px-2 py-1 font-mono focus:border-leo focus:outline-none"
		})]
	});
}
function SseReconnectSettings() {
	const [cfg, setCfg] = useSseConfig();
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "border border-border p-4",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "eyebrow",
				children: "SSE reconnect behavior"
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "mt-1 text-xs text-muted-foreground",
				children: "Controls the live-metrics stream retry loop on /benchmarks."
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mt-4 grid gap-3 text-xs sm:grid-cols-3",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Field, {
						label: "Max attempts",
						hint: "After this many retries the stream falls back to polling.",
						min: 0,
						max: 50,
						step: 1,
						value: cfg.maxAttempts,
						onChange: (v) => setCfg({ maxAttempts: v })
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Field, {
						label: "Initial backoff (ms)",
						hint: "Delay before the first retry; doubles each attempt.",
						min: 100,
						max: 6e4,
						step: 100,
						value: cfg.initialBackoffMs,
						onChange: (v) => setCfg({ initialBackoffMs: v })
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Field, {
						label: "Max backoff (ms)",
						hint: "Upper cap on exponential backoff between retries.",
						min: cfg.initialBackoffMs,
						max: 3e5,
						step: 500,
						value: cfg.maxBackoffMs,
						onChange: (v) => setCfg({ maxBackoffMs: v })
					})
				]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "mt-4 flex flex-wrap gap-2",
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
					type: "button",
					onClick: () => {
						setCfg({ ...DEFAULT_SSE_CONFIG });
						toast.success("SSE reconnect reset to defaults");
					},
					className: "border border-border px-3 py-1.5 text-xs font-semibold hover:border-leo hover:text-leo focus:outline-none focus-visible:ring-2 focus-visible:ring-leo",
					children: "Reset to defaults"
				})
			})
		]
	});
}
function Field({ label, hint, min, max, step, value, onChange }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("label", {
		className: "flex flex-col gap-1",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
				className: "text-muted-foreground",
				children: label
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("input", {
				type: "number",
				min,
				max,
				step,
				value,
				onChange: (e) => {
					const v = Number(e.target.value);
					if (Number.isFinite(v)) onChange(v);
				},
				className: "border border-border bg-background px-2 py-1 font-mono focus:border-leo focus:outline-none"
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
				className: "text-[10px] text-muted-foreground",
				children: hint
			})
		]
	});
}
function Page() {
	const search = Route.useSearch();
	const [base, setBase] = (0, import_react.useState)("");
	const [debug, setDebug] = (0, import_react.useState)("off");
	const [syncOn, setSyncOn] = (0, import_react.useState)(false);
	const [syncPath, setSyncPathState] = (0, import_react.useState)("");
	const [telemetry, setTelemetry] = (0, import_react.useState)("full");
	const [retention, setRetention] = (0, import_react.useState)(30);
	(0, import_react.useEffect)(() => {
		setBase(search.apiBase ?? getApiBase());
		setDebug(getDebugMode());
		setSyncOn(isSyncEnabled());
		setSyncPathState(getSyncPath());
		setTelemetry(getTelemetryMode());
		setRetention(getRetentionDays());
		if (search.apiBase) toast.message("Prefilled API base — review and save to apply");
	}, [search.apiBase]);
	function saveBase() {
		setApiBase(base.trim() || "http://localhost:8000");
		toast.success("API base updated");
	}
	function saveDebug(mode) {
		setDebug(mode);
		setDebugMode(mode);
		toast.success(mode === "off" ? "Debug logging disabled" : `Debug logging: ${mode} — open the browser console`);
	}
	async function toggleSync(on) {
		setSyncOn(on);
		setSyncEnabled(on);
		if (on) {
			toast.message("Syncing chat history with LEO backend…");
			try {
				const merged = await pullAndMerge();
				toast.success(`Chat sync enabled — ${merged.length} conversation(s) merged.`);
			} catch {
				toast.error("Sync enabled, but initial pull failed. Check backend URL.");
			}
		} else toast.success("Chat sync disabled. History stays on this device only.");
	}
	function saveSyncPath() {
		setSyncPath(syncPath.trim());
		toast.success("Chat sync path saved.");
	}
	function saveTelemetry(mode) {
		setTelemetry(mode);
		setTelemetryMode(mode);
		if (mode === "off") toast.success("Telemetry disabled. Nothing will be sent.");
		else if (mode === "errors-only") toast.success("Telemetry limited to runtime errors only.");
		else toast.success("Full telemetry enabled.");
	}
	function saveRetention(days) {
		setRetention(days);
		setRetentionDays(days);
		const remaining = pruneQueue();
		if (days === 0) toast.success("Retention set to forever. Nothing will be auto-pruned.");
		else toast.success(`Retention set to ${days} days. ${remaining.length} event(s) remain buffered (errors always kept).`);
	}
	function clearNow() {
		clearTelemetryQueue();
		toast.success("Buffered telemetry cleared. Future errors will still be reported.");
	}
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "p-10 max-w-2xl",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "eyebrow",
				children: "Configuration"
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h1", {
				className: "mt-2 font-display text-4xl font-bold",
				children: "Settings"
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
				className: "mt-8",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "eyebrow",
					children: "Connectivity"
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "mt-4",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(BackendHealthPanel, {})
				})]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
				className: "mt-8",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("label", {
						className: "block",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "eyebrow",
							children: "API base URL"
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("input", {
							value: base,
							onChange: (e) => setBase(e.target.value),
							placeholder: "http://localhost:8000",
							"aria-label": "LEO backend API base URL",
							className: "mt-2 w-full bg-input px-3 py-3 font-mono text-sm outline-none focus:ring-1 focus:ring-leo"
						})]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "mt-2 text-xs text-muted-foreground",
						children: "Point the console at any LEO deployment. Stored locally."
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
						onClick: saveBase,
						className: "mt-4 bg-leo px-5 py-3 text-sm font-semibold text-leo-foreground focus:outline-none focus-visible:ring-2 focus-visible:ring-white",
						children: "Save ›"
					})
				]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("section", {
				className: "mt-12 border-t border-border pt-8",
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(BackendSwitcher, {})
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
				className: "mt-12 border-t border-border pt-8",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "eyebrow",
						children: "Chat history"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
						className: "mt-2 font-display text-2xl font-bold",
						children: "Sync across devices"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "mt-2 text-sm text-muted-foreground",
						children: "When enabled, conversation logs are pushed to and pulled from your LEO backend so they appear on every browser you sign into. When disabled, history stays on this device only."
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("label", {
						className: "mt-4 flex items-center gap-3 cursor-pointer",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("input", {
							type: "checkbox",
							checked: syncOn,
							onChange: (e) => toggleSync(e.target.checked),
							className: "h-4 w-4 accent-leo focus:outline-none focus-visible:ring-2 focus-visible:ring-leo",
							"aria-label": "Enable server-side chat history sync"
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
							className: "text-sm",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
								className: "font-semibold",
								children: "Enable server sync"
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
								className: "ml-2 text-muted-foreground",
								children: "(POST/GET/DELETE against your backend)"
							})]
						})]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("label", {
						className: "mt-4 block",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "eyebrow",
							children: "Sync endpoint path"
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("input", {
							value: syncPath,
							onChange: (e) => setSyncPathState(e.target.value),
							placeholder: "/api/v1/chat/sessions",
							"aria-label": "Chat sync endpoint path",
							disabled: !syncOn,
							className: "mt-2 w-full bg-input px-3 py-3 font-mono text-sm outline-none focus:ring-1 focus:ring-leo disabled:opacity-50"
						})]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
						onClick: saveSyncPath,
						disabled: !syncOn,
						className: "mt-3 border border-border px-4 py-2 text-xs font-semibold hover:border-leo hover:text-leo disabled:opacity-40 focus:outline-none focus-visible:ring-2 focus-visible:ring-leo",
						children: "Save path"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
						className: "mt-3 text-xs text-muted-foreground",
						children: [
							"Backend contract: ",
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("code", {
								className: "text-foreground",
								children: "GET"
							}),
							" returns",
							" ",
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("code", {
								className: "text-foreground",
								children: "{ sessions: ChatSession[] }"
							}),
							";",
							" ",
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("code", {
								className: "text-foreground",
								children: "POST"
							}),
							" body",
							" ",
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("code", {
								className: "text-foreground",
								children: "{ session }"
							}),
							" upserts;",
							" ",
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("code", {
								className: "text-foreground",
								children: "DELETE /:id"
							}),
							" removes."
						]
					})
				]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
				className: "mt-12 border-t border-border pt-8",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "eyebrow",
						children: "Privacy"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
						className: "mt-2 font-display text-2xl font-bold",
						children: "Telemetry"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "mt-2 text-sm text-muted-foreground",
						children: "LEO collects anonymous performance metrics (Web Vitals) and runtime error reports to catch regressions. Choose how much to share. Turning telemetry off also stops all offline buffering."
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("fieldset", {
						className: "mt-4 space-y-2",
						"aria-label": "Telemetry mode",
						children: [
							{
								v: "full",
								label: "Full",
								desc: "Web Vitals + runtime errors + unhandled rejections"
							},
							{
								v: "errors-only",
								label: "Errors only",
								desc: "Skip performance metrics. Keep runtime errors so crashes stay reportable."
							},
							{
								v: "off",
								label: "Off",
								desc: "Nothing is sent. Nothing is buffered."
							}
						].map(({ v, label, desc }) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("label", {
							className: `flex cursor-pointer items-start gap-3 border p-3 text-sm ${telemetry === v ? "border-leo bg-leo/5" : "border-border hover:border-leo"}`,
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("input", {
								type: "radio",
								name: "telemetry",
								value: v,
								checked: telemetry === v,
								onChange: () => saveTelemetry(v),
								className: "mt-0.5 h-4 w-4 accent-leo"
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
								className: "font-semibold",
								children: label
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
								className: "ml-1 text-muted-foreground",
								children: ["— ", desc]
							})] })]
						}, v))
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "mt-6 border-t border-border/60 pt-6",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
								className: "eyebrow",
								children: "Data retention"
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
								className: "mt-2 text-sm text-muted-foreground",
								children: "How long buffered performance events stay on this device before being pruned. Runtime errors and unhandled rejections are always preserved regardless of this setting so crashes remain reportable."
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("fieldset", {
								className: "mt-4 flex flex-wrap gap-2",
								"aria-label": "Telemetry retention window",
								children: [
									{
										v: 7,
										label: "7 days"
									},
									{
										v: 30,
										label: "30 days"
									},
									{
										v: 90,
										label: "90 days"
									},
									{
										v: 0,
										label: "Forever"
									}
								].map(({ v, label }) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("label", {
									className: `cursor-pointer border px-4 py-2 text-sm font-semibold ${retention === v ? "border-leo bg-leo/10 text-leo" : "border-border hover:border-leo"}`,
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("input", {
										type: "radio",
										name: "retention",
										value: v,
										checked: retention === v,
										onChange: () => saveRetention(v),
										className: "sr-only"
									}), label]
								}, v))
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
								type: "button",
								onClick: clearNow,
								className: "mt-4 border border-border px-4 py-2 text-xs font-semibold hover:border-destructive hover:text-destructive focus:outline-none focus-visible:ring-2 focus-visible:ring-leo",
								"data-testid": "telemetry-clear-now",
								children: "Clear buffered telemetry now"
							})
						]
					})
				]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
				className: "mt-12 border-t border-border pt-8",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "eyebrow",
						children: "Monitoring"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
						className: "mt-2 font-display text-2xl font-bold",
						children: "Health degradation alert"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "mt-2 text-sm text-muted-foreground",
						children: "Tune when the /benchmarks banner and toast raise a degradation warning."
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
						className: "mt-4",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(HealthDegradationSettings, {})
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
						className: "mt-4",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(SseReconnectSettings, {})
					})
				]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
				className: "mt-12 border-t border-border pt-8",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "eyebrow",
						children: "Debug"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
						className: "mt-2 font-display text-2xl font-bold",
						children: "Request logging"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "mt-2 text-sm text-muted-foreground",
						children: "Log every backend request in the browser console. Secrets (Authorization header, passwords, tokens) are automatically redacted."
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("fieldset", {
						className: "mt-4 flex flex-wrap gap-2",
						"aria-label": "Debug logging mode",
						children: [
							"off",
							"basic",
							"verbose"
						].map((m) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("label", {
							className: `cursor-pointer border px-4 py-2 text-sm font-semibold ${debug === m ? "border-leo bg-leo/10 text-leo" : "border-border hover:border-leo"}`,
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("input", {
								type: "radio",
								name: "debug",
								value: m,
								checked: debug === m,
								onChange: () => saveDebug(m),
								className: "sr-only"
							}), m === "off" ? "Off" : m === "basic" ? "Basic (headers)" : "Verbose (+ bodies)"]
						}, m))
					})
				]
			})
		]
	});
}
//#endregion
export { Page as component };
