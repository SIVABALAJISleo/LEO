import { o as __toESM } from "./_runtime.mjs";
import { i as require_react, r as require_jsx_runtime } from "./_libs/react+tanstack__react-query.mjs";
import { n as toast } from "./_libs/sonner.mjs";
import { c as leoJson } from "./_ssr/leo-client-D7U1wpIv.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/_authenticated.app.knowledge-graph-BUl3wR2q.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
function Page() {
	const [q, setQ] = (0, import_react.useState)("");
	const [result, setResult] = (0, import_react.useState)(null);
	const [loading, setLoading] = (0, import_react.useState)(false);
	async function run() {
		if (!q.trim()) return;
		setLoading(true);
		try {
			setResult(await leoJson("/api/v1/kg/query", {
				method: "POST",
				body: JSON.stringify({
					query: q,
					hops: 2
				})
			}));
		} catch (e) {
			toast.error(e instanceof Error ? e.message : "Failed");
		} finally {
			setLoading(false);
		}
	}
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "p-10 max-w-5xl",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "eyebrow",
				children: "Runtime"
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h1", {
				className: "mt-2 font-display text-4xl font-bold",
				children: "Knowledge Graph"
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "mt-2 text-sm text-muted-foreground",
				children: "2-hop traversal over 50K+ entities."
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mt-8 flex gap-2",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("input", {
					value: q,
					onChange: (e) => setQ(e.target.value),
					placeholder: "Entity or query…",
					className: "flex-1 bg-input px-3 py-2.5 text-sm outline-none focus:ring-1 focus:ring-leo"
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
					onClick: run,
					disabled: loading,
					className: "bg-leo px-5 py-2.5 text-sm font-semibold text-leo-foreground disabled:opacity-50",
					children: loading ? "Traversing…" : "Query ›"
				})]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mt-6 grid gap-px bg-border md:grid-cols-3",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Stat, {
						label: "Entities",
						v: "50K+"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Stat, {
						label: "Relationships",
						v: "120K+"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Stat, {
						label: "2-hop latency",
						v: "6ms"
					})
				]
			}),
			result && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mt-8 border border-border",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "border-b border-border bg-surface px-4 py-2 eyebrow",
					children: "Result"
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("pre", {
					className: "overflow-auto p-4 font-mono text-xs",
					children: JSON.stringify(result, null, 2)
				})]
			})
		]
	});
}
function Stat({ label, v }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "bg-background p-5",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: "eyebrow",
			children: label
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: "mt-2 font-display text-2xl font-bold text-leo",
			children: v
		})]
	});
}
//#endregion
export { Page as component };
