// CORS preflight tester: sends an OPTIONS request to <apiBase><path> with
// user-selectable method + headers and reports what's missing in the
// Access-Control-Allow-* response headers.
import { useMemo, useState } from "react";
import { toast } from "sonner";
import { getApiBase } from "@/lib/leo-client";

type CheckKind = "ok" | "warn" | "fail";
interface HeaderCheck {
  header: string;
  received: string | null;
  kind: CheckKind;
  note: string;
}

interface PreflightResult {
  url: string;
  origin: string;
  method: string;
  ok: boolean;
  httpStatus?: number;
  latencyMs?: number;
  checks: HeaderCheck[];
  rawHeaders: [string, string][];
  error?: string;
}

const PATH_PRESETS = [
  "/health",
  "/api/v1/leo/metrics",
  "/api/v1/leo/diagnostics",
  "/api/v1/leo/chat",
];
const METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE"];

async function runPreflight(
  base: string,
  path: string,
  method: string,
  reqHeaders: string[],
): Promise<PreflightResult> {
  const cleanPath = path.startsWith("/") ? path : `/${path}`;
  const url = `${base.replace(/\/+$/, "")}${cleanPath}`;
  const origin = typeof window !== "undefined" ? window.location.origin : "*";
  const started = performance.now();
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 5000);
  try {
    const res = await fetch(url, {
      method: "OPTIONS",
      signal: controller.signal,
      headers: {
        Origin: origin,
        "Access-Control-Request-Method": method,
        "Access-Control-Request-Headers": reqHeaders.join(", "),
      },
    });
    const latencyMs = Math.round(performance.now() - started);
    const rawHeaders: [string, string][] = [];
    res.headers.forEach((v, k) => rawHeaders.push([k, v]));

    const allowOrigin = res.headers.get("access-control-allow-origin");
    const allowMethods = res.headers.get("access-control-allow-methods");
    const allowHeaders = res.headers.get("access-control-allow-headers");
    const checks: HeaderCheck[] = [];

    if (!allowOrigin) {
      checks.push({
        header: "Access-Control-Allow-Origin",
        received: null,
        kind: "fail",
        note: `Missing. Must be "${origin}" or "*".`,
      });
    } else if (allowOrigin === "*" || allowOrigin === origin) {
      checks.push({
        header: "Access-Control-Allow-Origin",
        received: allowOrigin,
        kind: allowOrigin === "*" ? "warn" : "ok",
        note:
          allowOrigin === "*"
            ? "Wildcard works but blocks credentialed requests."
            : "Origin allowed.",
      });
    } else {
      checks.push({
        header: "Access-Control-Allow-Origin",
        received: allowOrigin,
        kind: "fail",
        note: `Does not match request origin "${origin}".`,
      });
    }

    const methodsList = (allowMethods ?? "")
      .toLowerCase()
      .split(/[,\s]+/)
      .filter(Boolean);
    if (!allowMethods) {
      checks.push({
        header: "Access-Control-Allow-Methods",
        received: null,
        kind: "fail",
        note: `Missing. Must include ${method}.`,
      });
    } else if (!methodsList.includes(method.toLowerCase()) && !methodsList.includes("*")) {
      checks.push({
        header: "Access-Control-Allow-Methods",
        received: allowMethods,
        kind: "fail",
        note: `${method} not listed.`,
      });
    } else {
      checks.push({
        header: "Access-Control-Allow-Methods",
        received: allowMethods,
        kind: "ok",
        note: `${method} allowed.`,
      });
    }

    const headersList = (allowHeaders ?? "")
      .toLowerCase()
      .split(/[,\s]+/)
      .filter(Boolean);
    const missing = reqHeaders.filter(
      (h: string) => !headersList.includes(h.toLowerCase()) && !headersList.includes("*"),
    );
    if (!allowHeaders) {
      checks.push({
        header: "Access-Control-Allow-Headers",
        received: null,
        kind: reqHeaders.length ? "fail" : "warn",
        note: reqHeaders.length
          ? `Missing. Add ${reqHeaders.join(", ")}.`
          : "Not sent — fine if the client doesn't send extra headers.",
      });
    } else if (missing.length) {
      checks.push({
        header: "Access-Control-Allow-Headers",
        received: allowHeaders,
        kind: "fail",
        note: `Missing: ${missing.join(", ")}`,
      });
    } else {
      checks.push({
        header: "Access-Control-Allow-Headers",
        received: allowHeaders,
        kind: "ok",
        note: "All requested headers allowed.",
      });
    }

    clearTimeout(timer);
    const ok = res.ok && checks.every((c) => c.kind !== "fail");
    return { url, origin, method, ok, httpStatus: res.status, latencyMs, checks, rawHeaders };
  } catch (err) {
    clearTimeout(timer);
    return {
      url,
      origin,
      method,
      ok: false,
      checks: [],
      rawHeaders: [],
      error:
        err instanceof Error
          ? err.name === "AbortError"
            ? "Preflight timed out after 5s"
            : `${err.name}: ${err.message}`
          : String(err),
    };
  }
}

function buildCurl(
  url: string,
  origin: string,
  method: string,
  headers: string[],
  verbose = false,
): string {
  const q = (s: string) => `'${s.replace(/'/g, `'\\''`)}'`;
  const flags = verbose ? "-i -sS" : "-sS -o /dev/null -D -";
  const lines = [
    `curl ${flags} -X OPTIONS ${q(url)} \\`,
    `  -H ${q(`Origin: ${origin}`)} \\`,
    `  -H ${q(`Access-Control-Request-Method: ${method}`)}`,
  ];
  if (headers.length) {
    lines[lines.length - 1] += " \\";
    lines.push(`  -H ${q(`Access-Control-Request-Headers: ${headers.join(", ")}`)}`);
  }
  return lines.join("\n");
}

const CORS_RESULT_KEY = "leo.cors.last_result";

export function CorsPreflightTester() {
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<PreflightResult | null>(() => {
    if (typeof window === "undefined") return null;
    try {
      const raw = window.localStorage.getItem(CORS_RESULT_KEY);
      return raw ? (JSON.parse(raw) as PreflightResult) : null;
    } catch {
      return null;
    }
  });
  const [showCurl, setShowCurl] = useState(false);
  const [path, setPath] = useState<string>("/health");
  const [method, setMethod] = useState<string>("GET");
  const [headersInput, setHeadersInput] = useState<string>("content-type, authorization");

  const base = getApiBase();
  const origin = typeof window !== "undefined" ? window.location.origin : "*";

  const reqHeaders = useMemo(
    () =>
      headersInput
        .split(",")
        .map((s) => s.trim().toLowerCase())
        .filter(Boolean),
    [headersInput],
  );

  const cleanPath = path.startsWith("/") ? path : `/${path}`;
  const fullUrl = `${base.replace(/\/+$/, "")}${cleanPath}`;
  const curl = buildCurl(fullUrl, origin, method, reqHeaders);
  const curlVerbose = buildCurl(fullUrl, origin, method, reqHeaders, true);

  // Summarize what's missing from the last result for prominent highlighting.
  const missingSummary = useMemo(() => {
    if (!result || !result.checks.length) return null;
    const failing = result.checks.filter((c) => c.kind === "fail");
    if (!failing.length) return null;
    return failing.map((c) => c.header.replace(/^Access-Control-Allow-/, "Allow-"));
  }, [result]);

  async function run() {
    setRunning(true);
    try {
      const r = await runPreflight(base, path, method, reqHeaders);
      setResult(r);
      try {
        window.localStorage.setItem(CORS_RESULT_KEY, JSON.stringify(r));
      } catch {
        /* ignore quota */
      }
      if (r.ok) toast.success("CORS preflight passed");
      else toast.error(r.error ?? "CORS preflight failed");
    } finally {
      setRunning(false);
    }
  }

  async function copy(text: string, label: string) {
    try {
      await navigator.clipboard.writeText(text);
      toast.success(`${label} copied`);
    } catch {
      toast.error("Clipboard blocked — select and copy manually");
    }
  }

  return (
    <div className="border border-border p-4">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <div>
          <p className="eyebrow">CORS preflight tester</p>
          <p className="mt-1 text-xs text-muted-foreground">
            Pick any path + method to send an OPTIONS preflight against{" "}
            <code className="font-mono">{base}</code>.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={() => setShowCurl((s) => !s)}
            className="border border-border px-3 py-1.5 text-xs font-semibold hover:bg-input focus:outline-none focus-visible:ring-2 focus-visible:ring-white"
            aria-expanded={showCurl}
          >
            {showCurl ? "Hide curl" : "Show curl"}
          </button>
          <button
            type="button"
            onClick={run}
            disabled={running}
            className="bg-leo px-3 py-1.5 text-xs font-semibold text-leo-foreground disabled:opacity-40 focus:outline-none focus-visible:ring-2 focus-visible:ring-white"
          >
            {running ? "Testing…" : "Test CORS preflight"}
          </button>
        </div>
      </div>

      <div className="mt-4 grid gap-3 text-xs sm:grid-cols-[1fr_auto]">
        <label className="flex flex-col gap-1">
          <span className="text-muted-foreground">Path</span>
          <input
            list="cors-path-presets"
            value={path}
            onChange={(e) => setPath(e.target.value)}
            className="border border-border bg-background px-2 py-1 font-mono focus:border-leo focus:outline-none"
            placeholder="/api/v1/leo/chat"
            aria-label="Request path"
          />
          <datalist id="cors-path-presets">
            {PATH_PRESETS.map((p) => (
              <option key={p} value={p} />
            ))}
          </datalist>
        </label>
        <label className="flex flex-col gap-1">
          <span className="text-muted-foreground">Method</span>
          <select
            value={method}
            onChange={(e) => setMethod(e.target.value)}
            className="border border-border bg-background px-2 py-1 font-mono focus:border-leo focus:outline-none"
            aria-label="Request method"
          >
            {METHODS.map((m) => (
              <option key={m} value={m}>
                {m}
              </option>
            ))}
          </select>
        </label>
        <label className="flex flex-col gap-1 sm:col-span-2">
          <span className="text-muted-foreground">Request headers (comma-separated)</span>
          <input
            value={headersInput}
            onChange={(e) => setHeadersInput(e.target.value)}
            className="border border-border bg-background px-2 py-1 font-mono focus:border-leo focus:outline-none"
            placeholder="content-type, authorization"
            aria-label="Access-Control-Request-Headers list"
          />
        </label>
      </div>

      {showCurl && (
        <div className="mt-4 space-y-3 text-xs">
          <div>
            <div className="flex items-center justify-between gap-2">
              <p className="eyebrow">Headers only</p>
              <button
                type="button"
                onClick={() => copy(curl, "curl command")}
                className="border border-border px-2 py-0.5 text-[11px] font-semibold hover:bg-input focus:outline-none focus-visible:ring-2 focus-visible:ring-white"
              >
                Copy
              </button>
            </div>
            <pre className="mt-1 overflow-x-auto bg-input p-2 font-mono text-[11px] whitespace-pre">
              {curl}
            </pre>
          </div>
          <div>
            <div className="flex items-center justify-between gap-2">
              <p className="eyebrow">Verbose (with body)</p>
              <button
                type="button"
                onClick={() => copy(curlVerbose, "verbose curl command")}
                className="border border-border px-2 py-0.5 text-[11px] font-semibold hover:bg-input focus:outline-none focus-visible:ring-2 focus-visible:ring-white"
              >
                Copy
              </button>
            </div>
            <pre className="mt-1 overflow-x-auto bg-input p-2 font-mono text-[11px] whitespace-pre">
              {curlVerbose}
            </pre>
          </div>
        </div>
      )}

      {result && (
        <div className="mt-4 space-y-3 text-xs">
          <p>
            <span className={result.ok ? "font-semibold text-leo" : "font-semibold text-red-400"}>
              {result.ok ? "PASS" : "FAIL"}
            </span>
            {" · "}
            <code className="font-mono">{result.method}</code> {result.url}
            {result.httpStatus != null && ` · HTTP ${result.httpStatus}`}
            {result.latencyMs != null && ` · ${result.latencyMs}ms`}
          </p>

          {missingSummary && (
            <div role="alert" className="border-l-2 border-red-500 bg-red-500/5 p-3">
              <p className="font-semibold text-red-400">
                Missing / mismatched: {missingSummary.join(" · ")}
              </p>
              <p className="mt-1 text-muted-foreground">
                Add these to your backend CORS config so the browser accepts the preflight.
              </p>
            </div>
          )}

          {result.error && (
            <div className="border-l-2 border-red-500 bg-red-500/5 p-3">
              <p className="font-semibold text-red-400">{result.error}</p>
              <p className="mt-1 text-muted-foreground">
                Common causes: server not running, OPTIONS handler missing, or no CORS headers.
              </p>
            </div>
          )}

          {result.checks.length > 0 && (
            <ul className="space-y-2">
              {result.checks.map((c) => (
                <li key={c.header} className="border border-border p-2">
                  <div className="flex items-center gap-2">
                    <span
                      className={
                        c.kind === "ok"
                          ? "text-leo"
                          : c.kind === "warn"
                            ? "text-orange-400"
                            : "text-red-400"
                      }
                      aria-hidden
                    >
                      {c.kind === "ok" ? "✓" : c.kind === "warn" ? "!" : "✗"}
                    </span>
                    <code className="font-mono text-[11px]">{c.header}</code>
                  </div>
                  <p className="mt-1 pl-6 text-muted-foreground">{c.note}</p>
                  {c.received != null && (
                    <p className="mt-1 pl-6 font-mono text-[11px] break-all">
                      received: {c.received}
                    </p>
                  )}
                </li>
              ))}
            </ul>
          )}

          {result.rawHeaders.length > 0 && (
            <details>
              <summary className="cursor-pointer text-muted-foreground">
                All response headers
              </summary>
              <pre className="mt-2 overflow-x-auto bg-input p-2 font-mono text-[11px]">
                {result.rawHeaders.map(([k, v]) => `${k}: ${v}`).join("\n")}
              </pre>
            </details>
          )}
        </div>
      )}
    </div>
  );
}
