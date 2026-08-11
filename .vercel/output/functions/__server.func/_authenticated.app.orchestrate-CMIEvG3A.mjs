import { o as __toESM } from "./_runtime.mjs";
import { i as require_react, r as require_jsx_runtime } from "./_libs/react+tanstack__react-query.mjs";
import { n as toast } from "./_libs/sonner.mjs";
import { c as leoJson } from "./_ssr/leo-client-D7U1wpIv.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/_authenticated.app.orchestrate-CMIEvG3A.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
function Page() {
	const [query, setQuery] = (0, import_react.useState)("");
	const [result, setResult] = (0, import_react.useState)(null);
	const [loading, setLoading] = (0, import_react.useState)(false);
	async function run() {
		if (!query.trim()) return;
		setLoading(true);
		setResult(null);
		try {
			setResult(await leoJson("/api/v1/leo/orchestrate", {
				method: "POST",
				body: JSON.stringify({ query })
			}));
		} catch (e) {
			toast.error(e instanceof Error ? e.message : "Failed");
		} finally {
			setLoading(false);
		}
	}
	const path = result?.x_leo_metadata?.resolved_by ?? result?.resolved_by;
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "p-10 max-w-5xl",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "eyebrow",
				children: "Runtime"
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h1", {
				className: "mt-2 font-display text-4xl font-bold",
				children: "Orchestrate"
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "mt-2 text-sm text-muted-foreground",
				children: "Send a query through Phi-3 → GraphRAG or Mistral."
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mt-8",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("textarea", {
					value: query,
					onChange: (e) => setQuery(e.target.value),
					rows: 4,
					placeholder: "How do I reset my password?",
					className: "w-full bg-input p-4 text-sm outline-none focus:ring-1 focus:ring-leo"
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
					onClick: run,
					disabled: loading,
					className: "mt-3 bg-leo px-5 py-3 text-sm font-semibold text-leo-foreground disabled:opacity-50",
					children: loading ? "Routing…" : "Run orchestration ›"
				})]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mt-12 grid gap-px bg-border md:grid-cols-3",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Node, {
						n: "01",
						label: "Phi-3 Router",
						active: !!result
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Node, {
						n: "02",
						label: "GraphRAG",
						active: path === "GraphRAG"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Node, {
						n: "03",
						label: "Mistral 7B",
						active: path === "Mistral"
					})
				]
			}),
			result && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mt-8 border border-border",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "border-b border-border bg-surface px-4 py-2 eyebrow",
					children: "Response"
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("pre", {
					className: "overflow-auto p-4 font-mono text-xs",
					children: JSON.stringify(result, null, 2)
				})]
			})
		]
	});
}
function Node({ n, label, active }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: `bg-background p-6 border-t-2 ${active ? "border-leo" : "border-transparent"}`,
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: "font-mono text-xs text-muted-foreground",
			children: n
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: `mt-3 font-display text-lg font-bold ${active ? "text-leo" : ""}`,
			children: label
		})]
	});
}
//#endregion
export { Page as component };
