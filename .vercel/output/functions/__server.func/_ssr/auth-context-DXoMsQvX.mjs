import { o as __toESM } from "../_runtime.mjs";
import { i as require_react, r as require_jsx_runtime } from "../_libs/react+tanstack__react-query.mjs";
import { v as useNavigate } from "../_libs/@tanstack/react-router+[...].mjs";
import { c as leoJson, f as setToken, o as getToken, p as setUnauthorizedHandler } from "./leo-client-D7U1wpIv.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/auth-context-DXoMsQvX.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
var AuthContext = (0, import_react.createContext)(null);
function AuthProvider({ children }) {
	const [token, setTokenState] = (0, import_react.useState)(null);
	const [user, setUser] = (0, import_react.useState)(null);
	const navigate = useNavigate();
	const DEFAULT_ADMIN_USER = {
		email: "admin@leo.ai",
		username: "admin",
		permissions: ["admin"]
	};
	(0, import_react.useEffect)(() => {
		const t = getToken();
		if (t) {
			setTokenState(t);
			try {
				const stored = window.localStorage.getItem("leo.user");
				if (stored) setUser(JSON.parse(stored));
				else setUser(DEFAULT_ADMIN_USER);
			} catch {
				setUser(DEFAULT_ADMIN_USER);
			}
		}
	}, []);
	(0, import_react.useEffect)(() => {
		setUnauthorizedHandler(() => {
			setTokenState(null);
			setUser(null);
			if (typeof window !== "undefined") window.localStorage.removeItem("leo.user");
			navigate({ to: "/login" });
		});
		return () => setUnauthorizedHandler(null);
	}, [navigate]);
	const value = (0, import_react.useMemo)(() => ({
		token,
		user,
		isAuthenticated: !!token,
		setSession(newToken, newUser) {
			setToken(newToken);
			setTokenState(newToken);
			if (newUser !== void 0) {
				setUser(newUser);
				if (typeof window !== "undefined") if (newUser) window.localStorage.setItem("leo.user", JSON.stringify(newUser));
				else window.localStorage.removeItem("leo.user");
			}
		},
		async login(email, password) {
			const res = await leoJson("/api/v1/auth/login", {
				method: "POST",
				body: JSON.stringify({
					email,
					password
				})
			});
			const tk = res.access_token ?? res.token;
			if (!tk) throw new Error("No token returned");
			this.setSession(tk, res.user ?? { email });
		},
		async signup(email, password) {
			const res = await leoJson("/api/v1/auth/signup", {
				method: "POST",
				body: JSON.stringify({
					email,
					password
				})
			});
			const tk = res.access_token ?? res.token;
			if (tk) this.setSession(tk, res.user ?? { email });
		},
		logout() {
			setToken(null);
			setTokenState(null);
			setUser(null);
			if (typeof window !== "undefined") window.localStorage.removeItem("leo.user");
		}
	}), [token, user]);
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(AuthContext.Provider, {
		value,
		children
	});
}
function useAuth() {
	const ctx = (0, import_react.useContext)(AuthContext);
	if (!ctx) throw new Error("useAuth must be used within AuthProvider");
	return ctx;
}
//#endregion
export { useAuth as n, AuthProvider as t };
