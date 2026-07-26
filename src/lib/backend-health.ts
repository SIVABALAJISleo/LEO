// Runtime backend connectivity check.
// Pings the LEO backend /health endpoint, validates response schema,
// records latency, and captures a payload excerpt for Diagnostics.
import { useEffect, useRef, useState } from "react";
import { getApiBase } from "./leo-client";
import { pushHealthEntry } from "./health-history";

export type HealthStatus = "checking" | "online" | "unreachable" | "error";

export interface SchemaIssue {
  field: string;
  message: string;
}

/* eslint-disable prettier/prettier */
export type FailureKind =
  | "cors"
  | "network"
  | "timeout"
  | "mixed-content"
  | "dns"
  | "http"
  | "schema";
/* eslint-enable prettier/prettier */

export interface HealthResult {
  status: HealthStatus;
  url: string;
  latencyMs?: number;
  httpStatus?: number;
  message?: string;
  checkedAt?: number;
  bodyExcerpt?: string;
  schemaIssues?: SchemaIssue[];
  failureKind?: FailureKind;
  /** Actionable, human-readable hints (e.g. required CORS headers). */
  hints?: string[];
  /** Raw error name/type from the fetch failure, if any. */
  errorName?: string;
}

const HEALTH_PATH = "/health";
const TIMEOUT_MS = 5000;

export function buildHealthUrl(base = getApiBase()): string {
  return `${base.replace(/\/+$/, "")}${HEALTH_PATH}`;
}

// Expected shape from a FastAPI /health implementation:
//   { status: "ok" | "healthy", version?: string, uptime_s?: number }
export function validateHealthPayload(raw: unknown): SchemaIssue[] {
  const issues: SchemaIssue[] = [];
  if (typeof raw !== "object" || raw === null) {
    return [{ field: "(root)", message: "Response is not a JSON object" }];
  }
  const obj = raw as Record<string, unknown>;
  if (!("status" in obj)) {
    issues.push({ field: "status", message: "Missing required field" });
  } else if (typeof obj.status !== "string") {
    issues.push({ field: "status", message: `Expected string, got ${typeof obj.status}` });
  } else if (!["ok", "healthy", "up"].includes(obj.status.toLowerCase())) {
    issues.push({ field: "status", message: `Unexpected value "${obj.status}"` });
  }
  if ("version" in obj && typeof obj.version !== "string") {
    issues.push({ field: "version", message: `Expected string, got ${typeof obj.version}` });
  }
  if ("uptime_s" in obj && typeof obj.uptime_s !== "number") {
    issues.push({ field: "uptime_s", message: `Expected number, got ${typeof obj.uptime_s}` });
  }
  return issues;
}

export async function checkBackendHealth(base = getApiBase()): Promise<HealthResult> {
  const url = buildHealthUrl(base);
  const started = performance.now();
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);
  try {
    const res = await fetch(url, {
      method: "GET",
      signal: controller.signal,
      headers: { Accept: "application/json" },
    });
    const latencyMs = Math.round(performance.now() - started);
    const text = await res.text().catch(() => "");
    const bodyExcerpt = text.length > 240 ? `${text.slice(0, 240)}…` : text;

    let schemaIssues: SchemaIssue[] | undefined;
    if (res.ok) {
      try {
        schemaIssues = validateHealthPayload(JSON.parse(text));
      } catch {
        schemaIssues = [{ field: "(root)", message: "Response is not valid JSON" }];
      }
    }

    if (res.ok) {
      return {
        status: "online",
        url,
        latencyMs,
        httpStatus: res.status,
        checkedAt: Date.now(),
        bodyExcerpt,
        schemaIssues,
      };
    }
    return {
      status: "error",
      url,
      latencyMs,
      httpStatus: res.status,
      message: `HTTP ${res.status}`,
      checkedAt: Date.now(),
      bodyExcerpt,
      failureKind: "http",
      hints:
        res.status === 404
          ? [`The backend returned 404. Confirm it exposes GET /health at ${url}.`]
          : res.status >= 500
            ? ["The backend crashed handling /health. Check server logs for the traceback."]
            : res.status === 401 || res.status === 403
              ? ["/health should be public. Remove auth middleware for this route."]
              : undefined,
    };
  } catch (err: unknown) {
    const latencyMs = Math.round(performance.now() - started);
    return { ...classifyFetchError(err, url), latencyMs, checkedAt: Date.now() };
  } finally {
    clearTimeout(timer);
  }
}

/** Classify a fetch()-thrown error into a user-actionable HealthResult.
 *  The browser deliberately hides CORS/network distinctions from JS for
 *  security reasons — the error is always a generic TypeError("Failed to
 *  fetch"). We infer the likely cause from context (page origin vs URL
 *  scheme/host) and surface concrete remediation hints. */
function classifyFetchError(err: unknown, url: string): HealthResult {
  const base: HealthResult = { status: "unreachable", url };
  if (err instanceof DOMException && err.name === "AbortError") {
    return {
      ...base,
      failureKind: "timeout",
      errorName: "AbortError",
      message: `Timed out after ${TIMEOUT_MS}ms — the backend didn't respond in time.`,
      hints: [
        "Confirm the backend process is running and listening on the port in the URL.",
        "If you're behind a tunnel, verify the tunnel is still active.",
      ],
    };
  }
  const raw = err instanceof Error ? err.message : String(err);
  const name = err instanceof Error ? err.name : undefined;

  // Mixed content: HTTPS page → HTTP backend (not localhost).
  if (
    typeof window !== "undefined" &&
    window.location.protocol === "https:" &&
    url.startsWith("http://") &&
    !/^http:\/\/(localhost|127\.0\.0\.1)/i.test(url)
  ) {
    return {
      ...base,
      failureKind: "mixed-content",
      errorName: name,
      message: "Browser blocked the request: the page is HTTPS but the backend URL is HTTP.",
      hints: [
        "Serve the backend over HTTPS (deploy it, or expose it via a tunnel like Cloudflare/ngrok).",
        "Or open the frontend over HTTP for local testing.",
      ],
    };
  }

  // Localhost from a non-local origin can't resolve.
  if (
    typeof window !== "undefined" &&
    /^http:\/\/(localhost|127\.0\.0\.1)/i.test(url) &&
    !/^(localhost|127\.0\.0\.1)/i.test(window.location.hostname)
  ) {
    return {
      ...base,
      failureKind: "network",
      errorName: name,
      message: "This browser tab isn't on your laptop — it can't reach http://localhost.",
      hints: [
        "Expose your backend with a tunnel: `cloudflared tunnel --url http://localhost:8005`",
        "Then paste the public https://…trycloudflare.com URL into Settings.",
      ],
    };
  }

  // Generic TypeError("Failed to fetch") — most often CORS on a reachable host.
  if (name === "TypeError" || /failed to fetch|networkerror/i.test(raw)) {
    const origin = typeof window !== "undefined" ? window.location.origin : "<frontend-origin>";
    return {
      ...base,
      failureKind: "cors",
      errorName: name,
      message: `Fetch failed. Most likely CORS is blocking the request from ${origin}.`,
      hints: [
        `Add CORS headers on the backend so ${origin} is allowed. FastAPI:`,
        `  app.add_middleware(CORSMiddleware, allow_origins=["${origin}"], allow_methods=["*"], allow_headers=["*"])`,
        "Required response headers: Access-Control-Allow-Origin, Access-Control-Allow-Methods, Access-Control-Allow-Headers.",
        "The backend must also answer OPTIONS /health with 204 and the same headers.",
        "If it isn't CORS, the host/port may be wrong or the process isn't running.",
      ],
    };
  }

  return { ...base, failureKind: "network", errorName: name, message: raw || "Network error" };
}

export function useBackendHealth(intervalMs = 15000): HealthResult & { refresh: () => void } {
  const [result, setResult] = useState<HealthResult>({
    status: "checking",
    url: buildHealthUrl(),
  });
  const mounted = useRef(true);

  async function run() {
    if (!mounted.current) return;
    setResult((r) => ({ ...r, status: "checking", url: buildHealthUrl() }));
    const r = await checkBackendHealth();
    if (mounted.current) setResult(r);
    pushHealthEntry(r);
  }

  useEffect(() => {
    mounted.current = true;
    run();
    const id = intervalMs > 0 ? setInterval(run, intervalMs) : null;
    const onFocus = () => run();
    window.addEventListener("focus", onFocus);
    window.addEventListener("leo:api-base-changed", onFocus as EventListener);
    return () => {
      mounted.current = false;
      if (id) clearInterval(id);
      window.removeEventListener("focus", onFocus);
      window.removeEventListener("leo:api-base-changed", onFocus as EventListener);
    };
  }, [intervalMs]);

  return { ...result, refresh: run };
}
