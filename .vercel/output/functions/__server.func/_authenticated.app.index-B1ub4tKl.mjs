import { r as require_jsx_runtime, t as useQuery } from "./_libs/react+tanstack__react-query.mjs";
import { g as Link } from "./_libs/@tanstack/react-router+[...].mjs";
import { c as leoJson } from "./_ssr/leo-client-D7U1wpIv.mjs";
import { i as TileSkeletonGrid, n as ErrorState } from "./_ssr/LoadingStates-BV5BSSWv.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/_authenticated.app.index-B1ub4tKl.js
var import_jsx_runtime = require_jsx_runtime();
function Dashboard() {
	const { data, isLoading, error, refetch } = useQuery({
		queryKey: ["metrics"],
		queryFn: () => leoJson("/api/v1/leo/metrics"),
		refetchInterval: 5e3,
		retry: 0
	});
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "p-6 md:p-10 max-w-6xl",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "eyebrow",
				children: "Overview"
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h1", {
				className: "mt-2 font-display text-3xl md:text-4xl font-bold",
				children: "Dashboard"
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "mt-2 text-sm text-muted-foreground",
				children: error ? "Backend unreachable." : isLoading ? "Loading metrics…" : "Live from your LEO runtime."
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "mt-10",
				children: isLoading ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(TileSkeletonGrid, {}) : error ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ErrorState, { onRetry: () => refetch() }) : /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "grid gap-px bg-border sm:grid-cols-2 lg:grid-cols-3",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Tile, {
							label: "Total requests",
							value: num(data?.leo_total_requests)
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Tile, {
							label: "Compute avoided",
							value: num(data?.leo_compute_avoided)
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Tile, {
							label: "Avoidance rate",
							value: pct(data?.leo_avoidance_rate_pct)
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Tile, {
							label: "Watts saved",
							value: num(data?.leo_gpu_watts_saved)
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Tile, {
							label: "Cache hit rate",
							value: pct(data?.leo_crystallization_hit_rate)
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Tile, {
							label: "Router",
							value: "Phi-3 Mini",
							small: true
						})
					]
				})
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mt-12",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "eyebrow",
					children: "Quick actions"
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "mt-4 grid gap-px bg-border md:grid-cols-3",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Action, {
							to: "/app/chat",
							title: "Start a chat",
							body: "OpenAI-compatible completions with LEO metadata."
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Action, {
							to: "/app/orchestrate",
							title: "Run orchestration",
							body: "Send a query through the router."
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Action, {
							to: "/app/embeddings",
							title: "Generate embeddings",
							body: "384-dim vectors, 100% local."
						})
					]
				})]
			})
		]
	});
}
function num(n) {
	if (n == null) return "—";
	if (n >= 1e6) return `${(n / 1e6).toFixed(2)}M`;
	if (n >= 1e3) return `${(n / 1e3).toFixed(1)}K`;
	return String(n);
}
function pct(n) {
	return n == null ? "—" : `${n.toFixed(1)}%`;
}
function Tile({ label, value, small }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "bg-background p-6",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: "eyebrow",
			children: label
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: `mt-3 font-display font-bold text-leo ${small ? "text-2xl" : "text-4xl"}`,
			children: value
		})]
	});
}
function Action({ to, title, body }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Link, {
		to,
		className: "bg-background p-6 hover:bg-surface transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-leo focus-visible:ring-inset",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "font-display text-lg font-bold",
			children: [
				title,
				" ",
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
					className: "text-leo",
					"aria-hidden": "true",
					children: "›"
				})
			]
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: "mt-1 text-sm text-muted-foreground",
			children: body
		})]
	});
}
//#endregion
export { Dashboard as component };
