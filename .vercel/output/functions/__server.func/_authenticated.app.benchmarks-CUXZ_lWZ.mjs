import { r as require_jsx_runtime, t as useQuery } from "./_libs/react+tanstack__react-query.mjs";
import { c as leoJson } from "./_ssr/leo-client-D7U1wpIv.mjs";
import { i as TileSkeletonGrid, n as ErrorState } from "./_ssr/LoadingStates-BV5BSSWv.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/_authenticated.app.benchmarks-CUXZ_lWZ.js
var import_jsx_runtime = require_jsx_runtime();
function Page() {
	const { data, error, isLoading, refetch, isFetching } = useQuery({
		queryKey: ["app-metrics"],
		queryFn: () => leoJson("/api/v1/leo/metrics"),
		refetchInterval: 3e3,
		staleTime: 2e3,
		gcTime: 10 * 6e4,
		placeholderData: (prev) => prev,
		retry: 0
	});
	const entries = data ? Object.entries(data) : [];
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "p-6 md:p-10 max-w-6xl",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "eyebrow",
				children: "Observability"
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h1", {
				className: "mt-2 font-display text-3xl md:text-4xl font-bold",
				children: "Live Benchmarks"
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "mt-2 text-sm text-muted-foreground",
				"aria-live": "polite",
				children: error ? "Backend unreachable." : isLoading ? "Loading…" : isFetching ? "Refreshing…" : "Refreshing every 3s."
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "mt-8",
				children: isLoading && !data ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(TileSkeletonGrid, { count: 9 }) : error ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ErrorState, { onRetry: () => refetch() }) : /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "grid gap-px bg-border sm:grid-cols-2 lg:grid-cols-3",
					children: [entries.map(([k, v]) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "bg-background p-6",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
							className: "eyebrow truncate",
							children: k.replace(/^leo_/, "").replace(/_/g, " ")
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
							className: "mt-3 font-display text-3xl font-bold text-leo truncate",
							children: typeof v === "number" ? v.toLocaleString() : String(v)
						})]
					}, k)), entries.length === 0 && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
						className: "bg-background p-6 text-sm text-muted-foreground",
						children: "No data."
					})]
				})
			})
		]
	});
}
//#endregion
export { Page as component };
