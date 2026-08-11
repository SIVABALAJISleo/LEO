import { o as __toESM } from "../_runtime.mjs";
import { i as require_react, r as require_jsx_runtime } from "../_libs/react+tanstack__react-query.mjs";
import { g as Link, v as useNavigate } from "../_libs/@tanstack/react-router+[...].mjs";
import { n as toast } from "../_libs/sonner.mjs";
import { n as useAuth } from "./auth-context-DXoMsQvX.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/login-BB1XtBhM.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
function LoginPage() {
	const auth = useAuth();
	const navigate = useNavigate();
	const [email, setEmail] = (0, import_react.useState)("");
	const [password, setPassword] = (0, import_react.useState)("");
	const [manualToken, setManualToken] = (0, import_react.useState)("");
	const [loading, setLoading] = (0, import_react.useState)(false);
	async function onSubmit(e) {
		e.preventDefault();
		setLoading(true);
		try {
			await auth.login(email, password);
			navigate({ to: "/app" });
		} catch (err) {
			toast.error(err instanceof Error ? err.message : "Login failed");
		} finally {
			setLoading(false);
		}
	}
	function useToken() {
		if (!manualToken.trim()) return;
		auth.setSession(manualToken.trim(), { email: email || "developer" });
		navigate({ to: "/app" });
	}
	function directAdminLogin() {
		auth.setSession("admin-auto-session", {
			email: "admin@leo.ai",
			username: "admin",
			permissions: ["admin"]
		});
		toast.success("Signed in as Admin");
		navigate({ to: "/app" });
	}
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "mx-auto max-w-md px-6 py-24",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "eyebrow",
				children: "Console"
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h1", {
				className: "mt-3 font-display text-4xl font-bold",
				children: "Sign in"
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "mt-2 text-sm text-muted-foreground",
				children: "Access your LEO AI runtime."
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
				type: "button",
				onClick: directAdminLogin,
				className: "mt-6 w-full bg-leo px-4 py-3 text-sm font-bold text-leo-foreground shadow-md hover:brightness-110",
				children: "⚡ Direct Login as Admin (Bypass Sign In)"
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "relative my-6 text-center text-xs text-muted-foreground uppercase tracking-widest before:absolute before:left-0 before:top-1/2 before:w-5/12 before:border-t before:border-border after:absolute after:right-0 after:top-1/2 after:w-5/12 after:border-t after:border-border",
				children: "Or"
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("form", {
				onSubmit,
				className: "space-y-4",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Field, {
						label: "Email",
						type: "email",
						value: email,
						onChange: setEmail
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Field, {
						label: "Password",
						type: "password",
						value: password,
						onChange: setPassword
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
						disabled: loading,
						className: "w-full border border-border px-4 py-3 text-sm font-semibold hover:border-leo disabled:opacity-60",
						children: loading ? "Signing in…" : "Sign in with Credentials ›"
					})
				]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mt-8 border-t border-border pt-6",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
						className: "eyebrow",
						children: "Have a JWT?"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "mt-2 text-xs text-muted-foreground",
						children: "Paste your existing bearer token to skip the login endpoint."
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("input", {
						value: manualToken,
						onChange: (e) => setManualToken(e.target.value),
						placeholder: "eyJhbGciOi...",
						className: "mt-3 w-full bg-input px-3 py-2 font-mono text-xs"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
						type: "button",
						onClick: useToken,
						className: "mt-3 w-full border border-border px-4 py-2 text-sm hover:border-leo",
						children: "Use token ›"
					})
				]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
				className: "mt-8 text-sm text-muted-foreground",
				children: [
					"No account?",
					" ",
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Link, {
						to: "/signup",
						className: "text-leo",
						children: "Create one ›"
					})
				]
			})
		]
	});
}
function Field({ label, type, value, onChange }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("label", {
		className: "block",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
			className: "eyebrow",
			children: label
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("input", {
			required: true,
			type,
			value,
			onChange: (e) => onChange(e.target.value),
			className: "mt-2 w-full bg-input px-3 py-3 text-sm outline-none focus:ring-1 focus:ring-leo"
		})]
	});
}
//#endregion
export { LoginPage as component };
