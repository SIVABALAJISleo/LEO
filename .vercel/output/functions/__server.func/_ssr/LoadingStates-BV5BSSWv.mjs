import { r as require_jsx_runtime } from "../_libs/react+tanstack__react-query.mjs";
import { r as WifiOff } from "../_libs/lucide-react.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/LoadingStates-BV5BSSWv.js
var import_jsx_runtime = require_jsx_runtime();
/** Simple animated skeleton block. */
function Skeleton({ className = "" }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
		className: `animate-pulse bg-surface ${className}`,
		"aria-hidden": "true",
		role: "presentation"
	});
}
/** Grid of metric-tile skeletons that mirrors the dashboard layout. */
function TileSkeletonGrid({ count = 6 }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
		className: "grid gap-px bg-border sm:grid-cols-2 lg:grid-cols-3",
		"aria-busy": "true",
		"aria-label": "Loading metrics",
		children: Array.from({ length: count }).map((_, i) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "bg-background p-6",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Skeleton, { className: "h-3 w-24" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Skeleton, { className: "mt-4 h-10 w-32" })]
		}, i))
	});
}
/** Row skeletons for list-style views (memory, KG results). */
function ListSkeleton({ rows = 5 }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
		"aria-busy": "true",
		"aria-label": "Loading",
		children: Array.from({ length: rows }).map((_, i) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "border-b border-border last:border-0 p-4",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Skeleton, { className: "h-4 w-3/4" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Skeleton, { className: "mt-2 h-3 w-1/2" })]
		}, i))
	});
}
/** Consistent error banner used across authenticated pages. */
function ErrorState({ title = "Backend unavailable", message, onRetry, icon: Icon = WifiOff }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		role: "alert",
		className: "border border-border bg-surface p-6 flex items-start gap-4",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Icon, {
			className: "h-5 w-5 text-leo shrink-0 mt-0.5",
			"aria-hidden": "true"
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "flex-1 min-w-0",
			children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "font-display font-bold",
					children: title
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "mt-1 text-sm text-muted-foreground",
					children: message ?? "Check that your LEO backend is running and the API base URL in Settings is correct."
				}),
				onRetry && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
					onClick: onRetry,
					className: "mt-4 border border-border px-4 py-2 text-xs font-semibold hover:border-leo focus:outline-none focus-visible:ring-2 focus-visible:ring-leo",
					children: "Retry"
				})
			]
		})]
	});
}
/** Empty state for lists with no results. */
function EmptyState({ title, body, action }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "border border-dashed border-border p-10 text-center",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "font-display text-lg font-bold",
				children: title
			}),
			body && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "mt-2 text-sm text-muted-foreground",
				children: body
			}),
			action && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "mt-4",
				children: action
			})
		]
	});
}
//#endregion
export { TileSkeletonGrid as i, ErrorState as n, ListSkeleton as r, EmptyState as t };
