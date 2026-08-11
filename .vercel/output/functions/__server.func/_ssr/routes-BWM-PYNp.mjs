import { r as require_jsx_runtime } from "../_libs/react+tanstack__react-query.mjs";
import { g as Link } from "../_libs/@tanstack/react-router+[...].mjs";
import { E as Gauge, O as Database, S as Layers, T as GitBranch, h as Network, k as Cpu, t as Zap, y as Lock } from "../_libs/lucide-react.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/routes-BWM-PYNp.js
var import_jsx_runtime = require_jsx_runtime();
var leo_hero_default = "/assets/leo-hero-9kfEUp5P.jpg";
function Home() {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [
		/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
			className: "relative overflow-hidden border-b border-border",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "absolute inset-0 opacity-70",
				style: {
					backgroundImage: `linear-gradient(180deg, oklch(0 0 0 / 0.4) 0%, oklch(0 0 0 / 0.95) 100%), url(${leo_hero_default})`,
					backgroundSize: "cover",
					backgroundPosition: "center"
				}
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "relative mx-auto max-w-[1440px] px-6 pt-24 pb-32 md:pt-32 md:pb-44",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "eyebrow",
						children: "Introducing LEO AI"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("h1", {
						className: "mt-4 max-w-4xl font-display text-5xl font-bold leading-[1.02] md:text-7xl lg:text-[104px]",
						children: ["Full-power AI on ", /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "text-leo",
							children: "ordinary hardware."
						})]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "mt-6 max-w-2xl text-lg text-muted-foreground md:text-xl",
						children: "LEO AI is a local-first inference runtime that runs research-grade models on Intel CPU + iGPU — with semantic caching, adaptive routing, and OpenVINO acceleration. No cloud. No premium GPUs."
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "mt-10 flex flex-wrap gap-3",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Link, {
							to: "/signup",
							className: "inline-flex items-center gap-2 bg-leo px-6 py-4 text-sm font-semibold text-leo-foreground hover:brightness-110",
							children: ["Get LEO AI ", /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { children: "›" })]
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Link, {
							to: "/platform",
							className: "inline-flex items-center gap-2 border border-border px-6 py-4 text-sm font-semibold hover:border-leo",
							children: ["Explore the platform ", /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { children: "›" })]
						})]
					})
				]
			})]
		}),
		/* @__PURE__ */ (0, import_jsx_runtime.jsx)("section", {
			className: "border-b border-border bg-surface",
			children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mx-auto grid max-w-[1440px] grid-cols-2 gap-px bg-border md:grid-cols-4",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Stat, {
						value: "99.3%",
						label: "Compute avoided"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Stat, {
						value: "490 kW",
						label: "GPU watts saved"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Stat, {
						value: "1.72M",
						label: "Requests served"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Stat, {
						value: "2.3 ms",
						label: "GraphRAG latency"
					})
				]
			})
		}),
		/* @__PURE__ */ (0, import_jsx_runtime.jsx)("section", {
			className: "border-b border-border",
			children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mx-auto max-w-[1440px] px-6 py-24",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "eyebrow",
						children: "The runtime"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
						className: "mt-3 max-w-3xl font-display text-4xl font-bold md:text-6xl",
						children: "Three ideas that make LEO fast."
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "mt-14 grid gap-px bg-border md:grid-cols-3",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Pillar, {
								icon: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Lock, {}),
								title: "Local-first",
								body: "Models run on your machine. Your data never leaves the device. Full offline inference with mmap'd GGUF weights."
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Pillar, {
								icon: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Cpu, {}),
								title: "CPU + iGPU heterogeneous",
								body: "Intel OpenVINO scheduling spreads work across CPU cores and integrated graphics. Real gains on commodity chips."
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Pillar, {
								icon: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Network, {}),
								title: "Semantic routing",
								body: "A Phi-3 router picks GraphRAG or Mistral 7B per query. 99.3% of requests bypass heavy compute."
							})
						]
					})
				]
			})
		}),
		/* @__PURE__ */ (0, import_jsx_runtime.jsx)("section", {
			className: "border-b border-border bg-surface",
			children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mx-auto max-w-[1440px] px-6 py-24",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "flex items-end justify-between gap-6 flex-wrap",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "eyebrow",
						children: "Capabilities"
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
						className: "mt-3 font-display text-4xl font-bold md:text-5xl",
						children: "Everything in one runtime."
					})] }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Link, {
						to: "/features",
						className: "text-sm font-semibold text-leo hover:brightness-110",
						children: "All features ›"
					})]
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "mt-12 grid gap-px bg-border sm:grid-cols-2 lg:grid-cols-4",
					children: [
						{
							i: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Zap, {}),
							t: "Local LLM inference",
							d: "GGUF mmap, speculative decoding."
						},
						{
							i: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(GitBranch, {}),
							t: "Multi-model routing",
							d: "Phi-3 router, Mistral fallback."
						},
						{
							i: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Database, {}),
							t: "Semantic memory",
							d: "6 memory types, ChromaDB + FAISS."
						},
						{
							i: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Layers, {}),
							t: "Knowledge graph",
							d: "50K+ entities, 2-hop in 6ms."
						},
						{
							i: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Gauge, {}),
							t: "Real benchmarks",
							d: "Measured, not simulated."
						},
						{
							i: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Cpu, {}),
							t: "OpenVINO",
							d: "Intel CPU + iGPU acceleration."
						},
						{
							i: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Lock, {}),
							t: "RBAC + JWT",
							d: "Rate limits, permissions, audit."
						},
						{
							i: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Network, {}),
							t: "OpenAI-compatible",
							d: "/v1/chat/completions drop-in."
						}
					].map((c) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "group bg-background p-6 transition-colors hover:bg-surface-2",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
								className: "text-leo",
								children: c.i
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
								className: "mt-4 font-display text-lg font-semibold",
								children: c.t
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
								className: "mt-1 text-sm text-muted-foreground",
								children: c.d
							})
						]
					}, c.t))
				})]
			})
		}),
		/* @__PURE__ */ (0, import_jsx_runtime.jsx)("section", {
			className: "border-b border-border",
			children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mx-auto max-w-[1440px] px-6 py-24 md:py-32",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "eyebrow",
						children: "Start building"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
						className: "mt-3 max-w-3xl font-display text-5xl font-bold md:text-7xl",
						children: "Ship AI that runs anywhere."
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "mt-6 max-w-xl text-muted-foreground",
						children: "OpenAI-compatible endpoints. JWT auth. Ready in minutes."
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "mt-10 flex flex-wrap gap-3",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Link, {
							to: "/signup",
							className: "bg-leo px-6 py-4 text-sm font-semibold text-leo-foreground hover:brightness-110",
							children: "Create an account ›"
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Link, {
							to: "/docs",
							className: "border border-border px-6 py-4 text-sm font-semibold hover:border-leo",
							children: "Read the docs ›"
						})]
					})
				]
			})
		})
	] });
}
function Stat({ value, label }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "bg-background px-6 py-10",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: "font-display text-4xl font-bold text-leo md:text-5xl",
			children: value
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: "mt-2 text-xs uppercase tracking-widest text-muted-foreground",
			children: label
		})]
	});
}
function Pillar({ icon, title, body }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "bg-background p-8 transition-colors hover:bg-surface",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "text-leo",
				children: icon
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h3", {
				className: "mt-6 font-display text-2xl font-bold",
				children: title
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "mt-3 text-sm leading-relaxed text-muted-foreground",
				children: body
			})
		]
	});
}
//#endregion
export { Home as component };
