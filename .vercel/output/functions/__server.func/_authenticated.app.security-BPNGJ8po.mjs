import { r as require_jsx_runtime } from "./_libs/react+tanstack__react-query.mjs";
import { n as useAuth } from "./_ssr/auth-context-DXoMsQvX.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/_authenticated.app.security-BPNGJ8po.js
var import_jsx_runtime = require_jsx_runtime();
function Page() {
	const { user, token } = useAuth();
	const scopes = user?.permissions ?? [
		"orchestrate",
		"memory",
		"kg"
	];
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "p-10 max-w-4xl",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "eyebrow",
				children: "Access"
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h1", {
				className: "mt-2 font-display text-4xl font-bold",
				children: "Security"
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mt-8 grid gap-px bg-border md:grid-cols-2",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Card, {
					title: "Session",
					body: user?.email ?? "Unknown"
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Card, {
					title: "Auth",
					body: "JWT Bearer"
				})]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mt-8 border border-border",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "border-b border-border bg-surface px-4 py-2 eyebrow",
					children: "Scopes"
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "p-4 flex flex-wrap gap-2",
					children: scopes.map((s) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
						className: "border border-leo px-2 py-1 font-mono text-xs text-leo",
						children: s
					}, s))
				})]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mt-8 border border-border",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "border-b border-border bg-surface px-4 py-2 eyebrow",
					children: "Rate limits"
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("ul", {
					className: "p-4 text-sm space-y-1 font-mono text-xs",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", { children: ["Global: ", /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "text-leo",
							children: "600 req / 60s"
						})] }),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", { children: ["Chat: ", /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "text-leo",
							children: "100 req / min"
						})] }),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", { children: ["Embeddings: ", /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "text-leo",
							children: "1000 req / min"
						})] }),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", { children: ["Memory/KG: ", /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "text-leo",
							children: "500 req / min"
						})] })
					]
				})]
			}),
			token && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("details", {
				className: "mt-8 border border-border",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("summary", {
					className: "cursor-pointer bg-surface px-4 py-2 eyebrow",
					children: "JWT token"
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("pre", {
					className: "overflow-auto p-4 font-mono text-[11px] break-all",
					children: token
				})]
			})
		]
	});
}
function Card({ title, body }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "bg-background p-5",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: "eyebrow",
			children: title
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: "mt-2 font-display text-lg font-bold",
			children: body
		})]
	});
}
//#endregion
export { Page as component };
