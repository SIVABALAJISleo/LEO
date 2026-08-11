import { m as createFileRoute, p as lazyRouteComponent } from "./_libs/@tanstack/react-router+[...].mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/_authenticated.app.settings-DHmZrBWt.js
var $$splitComponentImporter = () => import("./_authenticated.app.settings-Cn9WIUFd.mjs");
var Route = createFileRoute("/_authenticated/app/settings")({
	head: () => ({ meta: [{ title: "Settings — LEO AI" }] }),
	validateSearch: (search) => ({ apiBase: typeof search.apiBase === "string" ? search.apiBase : void 0 }),
	component: lazyRouteComponent($$splitComponentImporter, "component")
});
//#endregion
export { Route as t };
