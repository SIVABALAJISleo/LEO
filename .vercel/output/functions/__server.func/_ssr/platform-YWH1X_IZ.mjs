import { r as require_jsx_runtime } from "../_libs/react+tanstack__react-query.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/platform-YWH1X_IZ.js
var import_jsx_runtime = require_jsx_runtime();
function PlatformPage() {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "mx-auto max-w-[1440px] px-6 py-24",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "eyebrow",
				children: "Platform"
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h1", {
				className: "mt-3 max-w-4xl font-display text-5xl font-bold md:text-7xl",
				children: "Every request takes the fastest path."
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "mt-6 max-w-2xl text-lg text-muted-foreground",
				children: "LEO orchestrates a router, a graph, and a full LLM. Simple questions never touch a 7B model."
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mt-20 grid gap-px bg-border md:grid-cols-3",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Step, {
						n: "01",
						title: "Phi-3 Mini Router",
						latency: "10 ms",
						body: "Classifies intent. Simple → GraphRAG. Complex → Mistral 7B."
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Step, {
						n: "02",
						title: "GraphRAG",
						latency: "2.3 ms",
						body: "50K+ entities, 2-hop traversal on ChromaDB + FAISS + SQLite."
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Step, {
						n: "03",
						title: "Mistral 7B",
						latency: "1500 ms",
						body: "Full generation for novel queries. Speculative decoding on iGPU."
					})
				]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mt-20 grid gap-px bg-border md:grid-cols-2",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Card, {
						title: "OpenVINO acceleration",
						body: "Intel CPU + integrated GPU execution. Heterogeneous scheduling across cores and EUs."
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Card, {
						title: "GGUF memory-mapped models",
						body: "Weights stream from disk. Zero copy. Small RAM footprint."
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Card, {
						title: "Semantic cache",
						body: "Crystallized answers with 82.5% hit rate. Compute skipped for known queries."
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Card, {
						title: "OpenAI-compatible API",
						body: "/v1/chat/completions and /v1/embeddings as drop-in replacements."
					})
				]
			})
		]
	});
}
function Step({ n, title, latency, body }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "bg-background p-8",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex items-baseline justify-between",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "font-mono text-xs text-muted-foreground",
					children: n
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "font-mono text-xs text-leo",
					children: latency
				})]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h3", {
				className: "mt-6 font-display text-2xl font-bold",
				children: title
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "mt-3 text-sm text-muted-foreground leading-relaxed",
				children: body
			})
		]
	});
}
function Card({ title, body }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "bg-background p-8 hover:bg-surface transition-colors",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h3", {
			className: "font-display text-xl font-bold",
			children: title
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
			className: "mt-3 text-sm text-muted-foreground leading-relaxed",
			children: body
		})]
	});
}
//#endregion
export { PlatformPage as component };
