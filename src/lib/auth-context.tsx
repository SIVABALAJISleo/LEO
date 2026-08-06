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

const defaultUser: User = {
  id: "admin-mock-id",
  email: "admin@hyper.local",
  username: "admin",
  permissions: ["orchestrate"],
};

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setTokenState] = useState<string | null>("AUDIT_MODE_TOKEN");
  const [user, setUser] = useState<User | null>(defaultUser);
  const navigate = useNavigate();

  useEffect(() => {
    if (typeof window !== "undefined") {
      window.localStorage.setItem("leo.user", JSON.stringify(defaultUser));
    }
  }, []);

  useEffect(() => {
    // Global 401 handler
    setUnauthorizedHandler(() => {
      // In bypass mode, we prevent redirecting back to login
      console.warn("Unauthorized API request intercepted, keeping bypass session active.");
    });
    return () => setUnauthorizedHandler(null);
  }, []);

  const value = useMemo<AuthState>(
    () => ({
      token,
      user,
      isAuthenticated: true, // Always true in bypass mode
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
        this.setSession("AUDIT_MODE_TOKEN", { email, permissions: ["orchestrate"] });
        navigate({ to: "/app" });
      },
      async signup(email, password) {
        this.setSession("AUDIT_MODE_TOKEN", { email, permissions: ["orchestrate"] });
        navigate({ to: "/app" });
      },
      logout() {
        // Clear session but allow re-authentication bypass
        setToken(null);
        setTokenState(null);
        setUser(null);
        if (typeof window !== "undefined") window.localStorage.removeItem("leo.user");
      },
    }),
    [token, user, navigate],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
