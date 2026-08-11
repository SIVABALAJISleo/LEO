import { r as require_jsx_runtime } from "../_libs/react+tanstack__react-query.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/docs-DL2CviJs.js
var import_jsx_runtime = require_jsx_runtime();
var endpoints = [
	[
		"POST",
		"/v1/chat/completions",
		"OpenAI-compatible chat",
		"450ms avg"
	],
	[
		"POST",
		"/v1/embeddings",
		"384-dim local embeddings",
		"2-5ms"
	],
	[
		"POST",
		"/api/v1/leo/orchestrate",
		"Router → GraphRAG or Mistral",
		"varies"
	],
	[
		"GET",
		"/api/v1/leo/metrics",
		"Live runtime metrics",
		"1ms"
	],
	[
		"POST",
		"/api/v1/memory",
		"Store or query semantic memory",
		"3ms"
	],
	[
		"POST",
		"/api/v1/kg/query",
		"Knowledge graph 2-hop query",
		"6ms"
	],
	[
		"POST",
		"/api/v1/security/*",
		"RBAC, audit, keys",
		"-"
	]
];
function DocsPage() {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "mx-auto max-w-[1440px] px-6 py-24",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "eyebrow",
				children: "Documentation"
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h1", {
				className: "mt-3 font-display text-5xl font-bold md:text-6xl",
				children: "Build with LEO."
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
				className: "mt-4 max-w-2xl text-muted-foreground",
				children: [
					"Full reference lives in",
					" ",
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("code", {
						className: "text-leo",
						children: "LEO_AI_BACKEND_API_DOCUMENTATION.md"
					}),
					", plus an OpenAPI 3.0 spec you can import into Postman or generate SDKs from."
				]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mt-16",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "eyebrow mb-4",
					children: "Key endpoints"
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "border border-border",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("table", {
						className: "w-full text-sm",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("thead", { children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("tr", {
							className: "border-b border-border bg-surface text-left",
							children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("th", {
									className: "p-4 font-mono text-xs",
									children: "Method"
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("th", {
									className: "p-4 font-mono text-xs",
									children: "Path"
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("th", {
									className: "p-4 font-mono text-xs",
									children: "Description"
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("th", {
									className: "p-4 font-mono text-xs text-right",
									children: "Latency"
								})
							]
						}) }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("tbody", { children: endpoints.map(([m, p, d, l]) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("tr", {
							className: "border-b border-border last:border-0 hover:bg-surface transition-colors",
							children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
									className: "p-4",
									children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
										className: "inline-block bg-leo px-2 py-0.5 font-mono text-xs font-bold text-leo-foreground",
										children: m
									})
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
									className: "p-4 font-mono",
									children: p
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
									className: "p-4 text-muted-foreground",
									children: d
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
									className: "p-4 text-right font-mono text-xs text-leo",
									children: l
								})
							]
						}, p)) })]
					})
				})]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mt-16 grid gap-px bg-border md:grid-cols-3",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "bg-background p-8",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
								className: "eyebrow",
								children: "Auth"
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
								className: "mt-3 font-mono text-xs text-muted-foreground",
								children: "Authorization: Bearer <JWT>"
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
								className: "mt-2 text-sm text-muted-foreground",
								children: "JWT with RBAC scopes: orchestrate, memory, kg, security, admin."
							})
						]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "bg-background p-8",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
							className: "eyebrow",
							children: "Rate limits"
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "mt-3 text-sm text-muted-foreground",
							children: "Global 600/60s. Chat 100/min. Embeddings 1000/min. Memory/KG 500/min."
						})]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "bg-background p-8",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
							className: "eyebrow",
							children: "SDK"
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "mt-3 text-sm text-muted-foreground",
							children: "Any OpenAI SDK works out of the box. Point base URL at your LEO deployment."
						})]
					})
				]
			})
		]
	});
}
//#endregion
export { DocsPage as component };
