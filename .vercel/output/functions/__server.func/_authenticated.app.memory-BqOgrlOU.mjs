import { o as __toESM } from "./_runtime.mjs";
import { i as require_react, r as require_jsx_runtime, t as useQuery } from "./_libs/react+tanstack__react-query.mjs";
import { n as toast } from "./_libs/sonner.mjs";
import { c as leoJson } from "./_ssr/leo-client-D7U1wpIv.mjs";
import { n as ErrorState, r as ListSkeleton, t as EmptyState } from "./_ssr/LoadingStates-BV5BSSWv.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/_authenticated.app.memory-BqOgrlOU.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
var TYPES = [
	"episodic",
	"semantic",
	"working",
	"reflection",
	"failure",
	"procedural"
];
function Page() {
	const [type, setType] = (0, import_react.useState)("semantic");
	const [content, setContent] = (0, import_react.useState)("");
	const [busy, setBusy] = (0, import_react.useState)(false);
	const { data, refetch, isLoading, error } = useQuery({
		queryKey: ["memory", type],
		queryFn: () => leoJson(`/api/v1/memory?type=${type}`),
		staleTime: 3e4,
		gcTime: 10 * 6e4,
		placeholderData: (prev) => prev,
		retry: 0
	});
	async function add() {
		if (!content.trim() || busy) return;
		setBusy(true);
		try {
			await leoJson("/api/v1/memory", {
				method: "POST",
				body: JSON.stringify({
					type,
					content
				})
			});
			setContent("");
			toast.success("Memory stored");
			refetch();
		} catch (e) {
			toast.error(e instanceof Error ? e.message : "Failed to store memory");
		} finally {
			setBusy(false);
		}
	}
	const rows = Array.isArray(data) ? data : data?.items ?? data?.results ?? [];
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "p-6 md:p-10 max-w-5xl",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "eyebrow",
				children: "Runtime"
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h1", {
				className: "mt-2 font-display text-3xl md:text-4xl font-bold",
				children: "Semantic Memory"
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "mt-6 flex flex-wrap gap-1",
				role: "tablist",
				"aria-label": "Memory type",
				children: TYPES.map((t) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
					role: "tab",
					"aria-selected": t === type,
					onClick: () => setType(t),
					className: `px-3 py-1.5 text-xs font-mono uppercase tracking-wide border focus:outline-none focus-visible:ring-2 focus-visible:ring-leo ${t === type ? "border-leo text-leo" : "border-border text-muted-foreground hover:border-foreground"}`,
					children: t
				}, t))
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("form", {
				onSubmit: (e) => {
					e.preventDefault();
					add();
				},
				className: "mt-6 flex flex-col sm:flex-row gap-2",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("label", {
						className: "sr-only",
						htmlFor: "mem-content",
						children: [
							"New ",
							type,
							" memory"
						]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("input", {
						id: "mem-content",
						value: content,
						onChange: (e) => setContent(e.target.value),
						placeholder: `Store new ${type} memory…`,
						className: "flex-1 bg-input px-3 py-2 text-sm outline-none focus:ring-1 focus:ring-leo"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
						type: "submit",
						disabled: busy || !content.trim(),
						className: "bg-leo px-4 py-2 text-sm font-semibold text-leo-foreground disabled:opacity-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-leo",
						children: busy ? "Storing…" : "Store ›"
					})
				]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mt-8 border border-border",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "border-b border-border bg-surface px-4 py-2 eyebrow flex justify-between",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", { children: [type, " memories"] }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
						"aria-label": `${rows.length} entries`,
						children: rows.length
					})]
				}), isLoading && !data ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ListSkeleton, {}) : error ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "p-4",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ErrorState, { onRetry: () => refetch() })
				}) : rows.length === 0 ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(EmptyState, {
					title: "No entries yet",
					body: `Store your first ${type} memory above.`
				}) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)("ul", { children: rows.map((r, i) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("li", {
					className: "border-b border-border last:border-0 p-4 text-sm",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", { children: typeof r === "string" ? r : r?.content ?? JSON.stringify(r) })
				}, i)) })]
			})
		]
	});
}
//#endregion
export { Page as component };
