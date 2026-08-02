// Thin fetch wrapper for the LEO AI backend.
// Base URL is configurable via VITE_LEO_API_BASE_URL or per-user via localStorage.
import { toast } from "sonner";

const DEFAULT_BASE = "http://localhost:8000";

export type ApiBaseSource = "settings" | "env" | "default";

export function getApiBase(): string {
  let base = "http://127.0.0.1:8005";
  
  // Strip trailing slash if present
  base = base.replace(/\/$/, "");
  
  // Strip trailing /api/v1 since paths like /api/v1/auth/me are hardcoded in the frontend
  if (base.endsWith("/api/v1")) {
    base = base.slice(0, -7);
  }
  
  return base;
}

export function getApiBaseSource(): ApiBaseSource {
  if (typeof window !== "undefined") {
    const stored = window.localStorage.getItem("leo.api_base");
    if (stored) return "settings";
  }
  if (import.meta.env.VITE_LEO_API_BASE_URL) return "env";
  return "default";
}

export function getEnvApiBase(): string | undefined {
  return import.meta.env.VITE_LEO_API_BASE_URL as string | undefined;
}

export function setApiBase(url: string) {
  if (typeof window !== "undefined") {
    window.localStorage.setItem("leo.api_base", url);
    window.dispatchEvent(new CustomEvent("leo:api-base-changed", { detail: url }));
  }
}

/** Clear the Settings/localStorage override so the app falls back to
 *  VITE_LEO_API_BASE_URL (or the built-in default). */
export function resetApiBase() {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem("leo.api_base");
  window.dispatchEvent(new CustomEvent("leo:api-base-changed", { detail: getApiBase() }));
}

export function getToken(): string | null {
  return null; // Migrated to HttpOnly Cookies
}

export function setToken(token: string | null) {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem("leo.jwt"); // Ensure legacy tokens are purged
}

// -------- Debug logging (configurable in Settings) --------

export type DebugMode = "off" | "basic" | "verbose";

export function getDebugMode(): DebugMode {
  if (typeof window === "undefined") return "off";
  return (window.localStorage.getItem("leo.debug") as DebugMode) || "off";
}
export function setDebugMode(mode: DebugMode) {
  if (typeof window === "undefined") return;
  window.localStorage.setItem("leo.debug", mode);
}

const SECRET_HEADERS = new Set(["authorization", "cookie", "x-api-key", "x-auth-token"]);
const SECRET_BODY_KEYS = /^(password|token|access_token|refresh_token|api_key|secret|jwt)$/i;

function redactHeaders(h: Headers): Record<string, string> {
  const out: Record<string, string> = {};
  h.forEach((v, k) => {
    out[k] = SECRET_HEADERS.has(k.toLowerCase()) ? "[REDACTED]" : v;
  });
  return out;
}
function redactBody(body: unknown): unknown {
  if (typeof body === "string") {
    try {
      return redactBody(JSON.parse(body));
    } catch {
      return body.length > 500 ? `${body.slice(0, 500)}…[${body.length} chars]` : body;
    }
  }
  if (Array.isArray(body)) return body.map(redactBody);
  if (body && typeof body === "object") {
    const out: Record<string, unknown> = {};
    for (const [k, v] of Object.entries(body as Record<string, unknown>)) {
      out[k] = SECRET_BODY_KEYS.test(k) ? "[REDACTED]" : redactBody(v);
    }
    return out;
  }
  return body;
}

// -------- Errors + global handlers --------

export class LeoError extends Error {
  constructor(
    public status: number,
    message: string,
    public body?: unknown,
  ) {
    super(message);
  }
}

let onUnauthorized: (() => void) | null = null;
export function setUnauthorizedHandler(fn: (() => void) | null) {
  onUnauthorized = fn;
}

// -------- 429 retry toast with countdown --------

function show429Toast(retryAfterSec: number, retry: () => void) {
  let remaining = Math.max(1, Math.floor(retryAfterSec));
  const id = toast.error(`Rate limit — retry in ${remaining}s`, {
    duration: (remaining + 1) * 1000,
    action: {
      label: "Retry now",
      onClick: () => retry(),
    },
  });
  const interval = setInterval(() => {
    remaining -= 1;
    if (remaining <= 0) {
      clearInterval(interval);
      toast.dismiss(id);
      retry();
      return;
    }
    toast.error(`Rate limit — retry in ${remaining}s`, {
      id,
      duration: (remaining + 1) * 1000,
      action: { label: "Retry now", onClick: () => retry() },
    });
  }, 1000);
}

// -------- Core fetch --------

export async function leoFetch(path: string, init: RequestInit = {}): Promise<Response> {
  const token = getToken();
  const headers = new Headers(init.headers);
  if (!headers.has("Content-Type") && init.body && typeof init.body === "string") {
    headers.set("Content-Type", "application/json");
  }
  if (token && !headers.has("Authorization")) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const debug = getDebugMode();
  const url = `${getApiBase()}${path}`;
  const startedAt = performance.now();
  if (debug !== "off") {
    console.groupCollapsed(`%c[LEO] → ${init.method ?? "GET"} ${path}`, "color:#76B900");
    console.log("url:", url);
    console.log("headers:", redactHeaders(headers));
    if (debug === "verbose" && init.body) console.log("body:", redactBody(init.body));
    console.groupEnd();
  }

  let res: Response;
  try {
    res = await fetch(url, { ...init, headers, credentials: "include" });
  } catch (err) {
    const msg = "Cannot reach LEO backend. Check the API base URL in Settings.";
    toast.error(msg);
    if (debug !== "off") console.error("[LEO] network error:", err);
    throw new LeoError(0, msg, err);
  }

  if (debug !== "off") {
    const ms = Math.round(performance.now() - startedAt);

    console.groupCollapsed(
      `%c[LEO] ← ${res.status} ${init.method ?? "GET"} ${path} (${ms}ms)`,
      res.ok ? "color:#76B900" : "color:#ef4444",
    );
    console.log("status:", res.status);
    if (debug === "verbose") {
      const clone = res.clone();
      clone
        .text()
        .then((t) => console.log("body:", redactBody(t)))
        .catch(() => {});
    }
    console.groupEnd();
  }

  if (res.status === 401) {
    setToken(null);
    toast.error("Your session expired. Please sign in again.");
    onUnauthorized?.();
  } else if (res.status === 429) {
    const retry = Number(res.headers.get("retry-after")) || 5;
    show429Toast(retry, () => {
      void leoFetch(path, init);
    });
  } else if (res.status >= 500) {
    toast.error(`Backend error (${res.status}). Please try again.`);
  }
  return res;
}

export async function leoJson<T = unknown>(path: string, init: RequestInit = {}): Promise<T> {
  const res = await leoFetch(path, init);
  const text = await res.text();
  const data = text ? safeParse(text) : null;
  if (!res.ok) {
    const msg =
      (data as { message?: string; error?: string; detail?: string } | null)?.message ??
      (data as { error?: string } | null)?.error ??
      (data as { detail?: string } | null)?.detail ??
      res.statusText ??
      `Request failed (${res.status})`;
    throw new LeoError(res.status, msg, data);
  }
  return data as T;
}

function safeParse(text: string) {
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}
