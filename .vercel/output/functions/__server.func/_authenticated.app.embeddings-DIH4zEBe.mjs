import { o as __toESM } from "./_runtime.mjs";
import { i as require_react, r as require_jsx_runtime } from "./_libs/react+tanstack__react-query.mjs";
import { n as toast } from "./_libs/sonner.mjs";
import { c as leoJson } from "./_ssr/leo-client-D7U1wpIv.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/_authenticated.app.embeddings-DIH4zEBe.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
function Page() {
	const [text, setText] = (0, import_react.useState)("");
	const [vec, setVec] = (0, import_react.useState)(null);
	const [loading, setLoading] = (0, import_react.useState)(false);
	async function run() {
		if (!text.trim()) return;
		setLoading(true);
		try {
			const r = await leoJson("/v1/embeddings", {
				method: "POST",
				body: JSON.stringify({
					input: text,
					model: "leo-embed"
				})
			});
			setVec(r?.data?.[0]?.embedding ?? r?.embedding ?? null);
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
				children: "Embeddings"
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "mt-2 text-sm text-muted-foreground",
				children: "384-dim local vectors. 2–5ms."
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("textarea", {
				value: text,
				onChange: (e) => setText(e.target.value),
				rows: 4,
				placeholder: "Enter text to embed…",
				className: "mt-8 w-full bg-input p-4 text-sm outline-none focus:ring-1 focus:ring-leo"
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
				onClick: run,
				disabled: loading,
				className: "mt-3 bg-leo px-5 py-3 text-sm font-semibold text-leo-foreground disabled:opacity-50",
				children: loading ? "Embedding…" : "Generate ›"
			}),
			vec && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mt-8 border border-border",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "border-b border-border bg-surface px-4 py-2 eyebrow flex justify-between",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { children: "Vector" }), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", { children: [vec.length, " dims"] })]
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("pre", {
					className: "max-h-80 overflow-auto p-4 font-mono text-[11px]",
					children: [
						"[",
						vec.slice(0, 32).map((n) => n.toFixed(4)).join(", "),
						vec.length > 32 ? ", …" : "",
						"]"
					]
				})]
			})
		]
	});
}
//#endregion
export { Page as component };
