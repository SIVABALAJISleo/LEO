import { o as __toESM } from "./_runtime.mjs";
import { i as require_react, r as require_jsx_runtime } from "./_libs/react+tanstack__react-query.mjs";
import { f as Outlet, g as Link, l as useRouterState, v as useNavigate } from "./_libs/@tanstack/react-router+[...].mjs";
import { n as useAuth } from "./_ssr/auth-context-DXoMsQvX.mjs";
import { A as Brain, O as Database, T as GitBranch, _ as Menu, c as Shield, g as MessageSquare, h as Network, j as Activity, l as Settings, n as X, s as Sparkles, v as LogOut, x as LayoutDashboard } from "./_libs/lucide-react.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/_authenticated.app-Bap1tEa2.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
var nav = [
	{
		to: "/app",
		label: "Dashboard",
		icon: LayoutDashboard,
		exact: true
	},
	{
		to: "/app/chat",
		label: "Chat",
		icon: MessageSquare
	},
	{
		to: "/app/orchestrate",
		label: "Orchestrate",
		icon: GitBranch
	},
	{
		to: "/app/memory",
		label: "Memory",
		icon: Brain
	},
	{
		to: "/app/knowledge-graph",
		label: "Knowledge Graph",
		icon: Network
	},
	{
		to: "/app/embeddings",
		label: "Embeddings",
		icon: Sparkles
	},
	{
		to: "/app/benchmarks",
		label: "Benchmarks",
		icon: Activity
	},
	{
		to: "/app/security",
		label: "Security",
		icon: Shield
	},
	{
		to: "/app/settings",
		label: "Settings",
		icon: Settings
	}
];
function AppShell({ children }) {
	const pathname = useRouterState({ select: (s) => s.location.pathname });
	const auth = useAuth();
	const navigate = useNavigate();
	const [mobileOpen, setMobileOpen] = (0, import_react.useState)(false);
	function isActive(to, exact) {
		return exact ? pathname === to : pathname === to || pathname.startsWith(to + "/");
	}
	function logout() {
		auth.logout();
		navigate({ to: "/login" });
	}
	const sidebar = /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(import_jsx_runtime.Fragment, { children: [
		/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Link, {
			to: "/",
			className: "flex items-center gap-2 border-b border-border px-6 py-4 font-display text-lg font-bold focus:outline-none focus-visible:ring-2 focus-visible:ring-leo",
			"aria-label": "LEO AI home",
			children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
					className: "text-leo",
					children: "LEO"
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { children: "AI" }),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
					className: "ml-auto font-mono text-[10px] uppercase tracking-widest text-muted-foreground",
					children: "Console"
				})
			]
		}),
		/* @__PURE__ */ (0, import_jsx_runtime.jsx)("nav", {
			className: "flex-1 py-4",
			"aria-label": "Console navigation",
			children: nav.map((n) => {
				const active = isActive(n.to, n.exact);
				return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Link, {
					to: n.to,
					onClick: () => setMobileOpen(false),
					"aria-current": active ? "page" : void 0,
					className: `flex items-center gap-3 border-l-2 px-6 py-2.5 text-sm transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-leo focus-visible:ring-inset ${active ? "border-leo bg-background text-foreground" : "border-transparent text-muted-foreground hover:text-foreground hover:bg-background/50"}`,
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(n.icon, {
						className: "h-4 w-4",
						"aria-hidden": "true"
					}), n.label]
				}, n.to);
			})
		}),
		/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "border-t border-border p-4",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mb-3 flex items-center gap-2 text-xs",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Database, {
					className: "h-3 w-3 text-leo",
					"aria-hidden": "true"
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
					className: "truncate text-muted-foreground",
					children: auth.user?.email ?? "signed in"
				})]
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("button", {
				onClick: logout,
				className: "flex w-full items-center gap-2 border border-border px-3 py-2 text-xs hover:border-leo focus:outline-none focus-visible:ring-2 focus-visible:ring-leo",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(LogOut, {
					className: "h-3 w-3",
					"aria-hidden": "true"
				}), " Sign out"]
			})]
		})
	] });
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "flex min-h-dvh bg-background",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "md:hidden fixed top-0 left-0 right-0 z-40 flex items-center justify-between border-b border-border bg-background px-4 h-14",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Link, {
					to: "/app",
					className: "font-display text-lg font-bold",
					"aria-label": "LEO AI console home",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
						className: "text-leo",
						children: "LEO"
					}), " AI"]
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
					onClick: () => setMobileOpen(true),
					"aria-label": "Open navigation menu",
					"aria-expanded": mobileOpen,
					className: "p-2 focus:outline-none focus-visible:ring-2 focus-visible:ring-leo",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Menu, {
						className: "h-5 w-5",
						"aria-hidden": "true"
					})
				})]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("aside", {
				className: "hidden md:flex w-60 shrink-0 border-r border-border bg-surface flex-col",
				"aria-label": "Console sidebar",
				children: sidebar
			}),
			mobileOpen && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "md:hidden fixed inset-0 z-50 flex",
				role: "dialog",
				"aria-modal": "true",
				"aria-label": "Console navigation",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "absolute inset-0 bg-black/60",
					onClick: () => setMobileOpen(false),
					"aria-hidden": "true"
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("aside", {
					className: "relative w-72 max-w-[85vw] border-r border-border bg-surface flex flex-col",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
						onClick: () => setMobileOpen(false),
						"aria-label": "Close navigation menu",
						className: "absolute top-3 right-3 p-2 focus:outline-none focus-visible:ring-2 focus-visible:ring-leo",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(X, {
							className: "h-5 w-5",
							"aria-hidden": "true"
						})
					}), sidebar]
				})]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("main", {
				className: "flex-1 min-w-0 pt-14 md:pt-0",
				id: "main",
				children
			})
		]
	});
}
var SplitComponent = () => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(AppShell, { children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Outlet, {}) });
//#endregion
export { SplitComponent as component };
