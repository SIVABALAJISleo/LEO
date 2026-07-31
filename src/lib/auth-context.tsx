import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import { useNavigate } from "@tanstack/react-router";
import { getToken, setToken, leoJson, setUnauthorizedHandler } from "./leo-client";

type User = { id?: string; email?: string; username?: string; permissions?: string[] };

type AuthState = {
  token: string | null;
  user: User | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string) => Promise<void>;
  logout: () => void;
  setSession: (token: string, user?: User | null) => void;
};

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setTokenState] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    // Attempt to hydrate session via HttpOnly cookie
    leoJson<User>("/api/v1/auth/me")
      .then((userData) => {
        setUser(userData);
        setTokenState("cookie-session-active");
      })
      .catch(() => {
        // No valid session cookie found
        setUser(null);
        setTokenState(null);
        if (typeof window !== "undefined") window.localStorage.removeItem("leo.user");
      });
  }, []);

  useEffect(() => {
    // Global 401 handler: clear session and bounce to login.
    setUnauthorizedHandler(() => {
      setTokenState(null);
      setUser(null);
      if (typeof window !== "undefined") window.localStorage.removeItem("leo.user");
      navigate({ to: "/login" });
    });
    return () => setUnauthorizedHandler(null);
  }, [navigate]);

  const value = useMemo<AuthState>(
    () => ({
      token,
      user,
      isAuthenticated: !!token,
      setSession(newToken, newUser) {
        setToken(newToken);
        setTokenState(newToken);
        if (newUser !== undefined) {
          setUser(newUser);
          if (typeof window !== "undefined") {
            if (newUser) window.localStorage.setItem("leo.user", JSON.stringify(newUser));
            else window.localStorage.removeItem("leo.user");
          }
        }
      },
      async login(email, password) {
        const res = await leoJson<{ user?: User }>("/api/v1/auth/login", {
          method: "POST",
          body: JSON.stringify({ email, password }),
        });
        this.setSession("cookie-session-active", res.user ?? { email });
      },
      async signup(email, password) {
        const res = await leoJson<{ user?: User }>("/api/v1/auth/signup", {
          method: "POST",
          body: JSON.stringify({ email, password }),
        });
        this.setSession("cookie-session-active", res.user ?? { email });
      },
      logout() {
        setToken(null);
        setTokenState(null);
        setUser(null);
        if (typeof window !== "undefined") window.localStorage.removeItem("leo.user");
      },
    }),
    [token, user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
