import { r as require_jsx_runtime } from "../_libs/react+tanstack__react-query.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/features-CtfXJGmd.js
var import_jsx_runtime = require_jsx_runtime();
var features = [
	["Local LLM inference", "OpenVINO + GGUF mmap. Runs Mistral 7B and smaller on Intel CPU + iGPU."],
	["Multi-model routing", "Phi-3 Mini router selects the cheapest correct path for every query."],
	["Semantic memory", "Episodic, semantic, working, reflection, failure, procedural memory types."],
	["Knowledge graph", "50K+ entities, 120K+ relationships. 2-hop queries in ~6ms."],
	["Real benchmarks", "Measured latency, watts, throughput. Never simulated."],
	["CPU + iGPU heterogeneous", "Work spreads across CPU cores and integrated graphics EUs."],
	["Document understanding", "PDF, DOCX, code files ingested into semantic memory + KG."],
	["Code assistance", "Native code understanding path with FSM-guided generation."],
	["Modular plugins", "Plugin architecture for custom retrievers, tools, and post-processors."],
	["OpenAI-compatible", "/v1/chat/completions and /v1/embeddings drop-in endpoints."],
	["RBAC + JWT auth", "Role-based access, per-endpoint rate limits, audit trail."],
	["Observability", "Prometheus-style metrics, per-request LEO metadata for cost tracking."]
];
function FeaturesPage() {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "mx-auto max-w-[1440px] px-6 py-24",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "eyebrow",
				children: "Features"
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h1", {
				className: "mt-3 font-display text-5xl font-bold md:text-6xl",
				children: "Built for real workloads."
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "mt-16 grid gap-px bg-border md:grid-cols-2 lg:grid-cols-3",
				children: features.map(([t, d]) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "bg-background p-8 hover:bg-surface transition-colors",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h3", {
						className: "font-display text-lg font-bold",
						children: t
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "mt-2 text-sm text-muted-foreground leading-relaxed",
						children: d
					})]
				}, t))
			})
		]
	});
}
//#endregion
export { FeaturesPage as component };
