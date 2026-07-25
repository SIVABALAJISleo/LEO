// Comprehensive backend health + diagnostics panel.
// - Live /health ping with latency, last-success time, and exact error.
// - Shows the effective API base URL AND its source (Settings vs env vs default).
// - "Reset to defaults" clears the localStorage override.
// - "Paste & validate" helper for a new URL, with localhost guidance.
import { useEffect, useMemo, useRef, useState } from "react";
import { toast } from "sonner";
import { checkBackendHealth, useBackendHealth, type HealthResult } from "@/lib/backend-health";
import {
  getApiBase,
  getApiBaseSource,
  getEnvApiBase,
  resetApiBase,
  setApiBase,
  type ApiBaseSource,
} from "@/lib/leo-client";
import { usePollingIntervals } from "@/lib/health-history";

const SOURCE_LABEL: Record<ApiBaseSource, string> = {
  settings: "Settings override (localStorage)",
  env: "Environment variable (VITE_LEO_API_BASE_URL)",
  default: "Built-in default",
};

function formatAgo(ts?: number): string {
  if (!ts) return "never";
  const s = Math.round((Date.now() - ts) / 1000);
  if (s < 5) return "just now";
  if (s < 60) return `${s}s ago`;
  if (s < 3600) return `${Math.round(s / 60)}m ago`;
  return `${Math.round(s / 3600)}h ago`;
}

function isLocalhostUrl(u: string): boolean {
  return /^https?:\/\/(localhost|127\.0\.0\.1)(:\d+)?/i.test(u.trim());
}

export function BackendHealthPanel() {
  const [polling] = usePollingIntervals();
  const h = useBackendHealth(polling.healthMs);

  const [base, setBase] = useState("");
  const [source, setSource] = useState<ApiBaseSource>("default");
  const [envUrl, setEnvUrl] = useState<string | undefined>();
  const [lastSuccess, setLastSuccess] = useState<{ at: number; latencyMs?: number } | null>(null);
  const [, force] = useState(0);

  // Refresh "ago" label every 15s
  useEffect(() => {
    const id = setInterval(() => force((x) => x + 1), 15000);
    return () => clearInterval(id);
  }, []);

  useEffect(() => {
    setBase(getApiBase());
    setSource(getApiBaseSource());
    setEnvUrl(getEnvApiBase());
    const onChange = () => {
      setBase(getApiBase());
      setSource(getApiBaseSource());
    };
    window.addEventListener("leo:api-base-changed", onChange);
    return () => window.removeEventListener("leo:api-base-changed", onChange);
  }, []);

  useEffect(() => {
    if (h.status === "online") {
      setLastSuccess({ at: h.checkedAt ?? Date.now(), latencyMs: h.latencyMs });
    }
  }, [h.status, h.checkedAt, h.latencyMs]);

  function onReset() {
    resetApiBase();
    toast.success(
      envUrl
        ? `Reset — now using env var: ${envUrl}`
        : "Reset — using built-in default (http://localhost:8000)",
    );
  }

  return (
    <div className="space-y-6">
      <StatusBlock health={h} lastSuccess={lastSuccess} />
      <SourceBlock base={base} source={source} envUrl={envUrl} onReset={onReset} />
      <UrlHelper onSaved={(u) => setBase(u)} />
    </div>
  );
}

function StatusBlock({
  health,
  lastSuccess,
}: {
  health: HealthResult & { refresh: () => void };
  lastSuccess: { at: number; latencyMs?: number } | null;
}) {
  const dot =
    health.status === "online"
      ? "bg-leo"
      : health.status === "checking"
        ? "bg-yellow-400 animate-pulse"
        : health.status === "unreachable"
          ? "bg-red-500"
          : "bg-orange-400";

  const label =
    health.status === "online"
      ? "Online"
      : health.status === "checking"
        ? "Checking…"
        : health.status === "unreachable"
          ? "Unreachable"
          : "Error";

  return (
    <div className="border border-border bg-background/60 p-4">
      <div className="flex flex-wrap items-center gap-3">
        <span className={`inline-block h-2.5 w-2.5 rounded-full ${dot}`} aria-hidden />
        <span className="font-semibold" role="status" aria-live="polite">
          Backend {label}
        </span>
        {health.latencyMs != null && health.status === "online" && (
          <span className="text-xs text-muted-foreground">· {health.latencyMs}ms</span>
        )}
        <button
          type="button"
          onClick={health.refresh}
          className="ml-auto border border-border px-3 py-1 text-xs font-semibold hover:border-leo hover:text-leo focus:outline-none focus-visible:ring-2 focus-visible:ring-leo"
        >
          Re-check now
        </button>
      </div>

      <dl className="mt-4 grid gap-x-6 gap-y-2 text-xs sm:grid-cols-[max-content_1fr]">
        <dt className="text-muted-foreground">Request URL</dt>
        <dd className="font-mono break-all">{health.url}</dd>

        <dt className="text-muted-foreground">Last success</dt>
        <dd>
          {lastSuccess
            ? `${formatAgo(lastSuccess.at)} (${lastSuccess.latencyMs ?? "?"}ms)`
            : "no successful check yet"}
        </dd>

        <dt className="text-muted-foreground">Last check</dt>
        <dd>{health.checkedAt ? formatAgo(health.checkedAt) : "—"}</dd>

        {health.httpStatus != null && (
          <>
            <dt className="text-muted-foreground">HTTP status</dt>
            <dd>{health.httpStatus}</dd>
          </>
        )}
      </dl>

      {health.status !== "online" && health.status !== "checking" && (
        <div className="mt-4 border-l-2 border-red-500 bg-red-500/5 p-3">
          <p className="text-xs font-semibold text-red-400">
            {health.failureKind ? `${health.failureKind.toUpperCase()} — ` : ""}
            {health.message ?? "Unknown error"}
          </p>
          {health.errorName && (
            <p className="mt-1 font-mono text-[11px] text-muted-foreground">{health.errorName}</p>
          )}
          {health.hints && health.hints.length > 0 && (
            <ul className="mt-3 space-y-1 text-xs text-muted-foreground">
              {health.hints.map((hint, i) => (
                <li key={i} className="flex gap-2">
                  <span className="text-leo" aria-hidden>
                    →
                  </span>
                  <code className="whitespace-pre-wrap break-words font-mono text-[11px]">
                    {hint}
                  </code>
                </li>
              ))}
            </ul>
          )}
          {health.bodyExcerpt && (
            <details className="mt-3 text-xs">
              <summary className="cursor-pointer text-muted-foreground">Response body</summary>
              <pre className="mt-2 overflow-x-auto bg-input p-2 font-mono text-[11px]">
                {health.bodyExcerpt}
              </pre>
            </details>
          )}
        </div>
      )}
    </div>
  );
}

function SourceBlock({
  base,
  source,
  envUrl,
  onReset,
}: {
  base: string;
  source: ApiBaseSource;
  envUrl?: string;
  onReset: () => void;
}) {
  return (
    <div className="border border-border p-4">
      <p className="eyebrow">Effective API base URL</p>
      <code className="mt-2 block break-all font-mono text-sm">{base || "—"}</code>
      <p className="mt-2 text-xs text-muted-foreground">
        Source: <span className="font-semibold text-foreground">{SOURCE_LABEL[source]}</span>
      </p>
      {source === "settings" && envUrl && envUrl !== base && (
        <p className="mt-1 text-xs text-orange-400">
          ⚠ A Settings override is active. It shadows your env var{" "}
          <code className="font-mono">{envUrl}</code>.
        </p>
      )}
      <button
        type="button"
        onClick={onReset}
        disabled={source !== "settings"}
        className="mt-3 border border-border px-4 py-2 text-xs font-semibold hover:border-leo hover:text-leo disabled:opacity-40 disabled:hover:border-border disabled:hover:text-foreground focus:outline-none focus-visible:ring-2 focus-visible:ring-leo"
      >
        Reset to defaults
      </button>
      {source !== "settings" && (
        <p className="mt-2 text-[11px] text-muted-foreground">
          Nothing to reset — no Settings override is active.
        </p>
      )}
    </div>
  );
}

function UrlHelper({ onSaved }: { onSaved: (url: string) => void }) {
  const [url, setUrl] = useState("");
  const [validating, setValidating] = useState(false);
  const [result, setResult] = useState<HealthResult | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const isLocal = useMemo(() => (url.trim() ? isLocalhostUrl(url) : false), [url]);
  const pageOnHttps = typeof window !== "undefined" && window.location.protocol === "https:";

  async function validate() {
    if (!url.trim()) {
      toast.error("Paste a URL first.");
      return;
    }
    abortRef.current?.abort();
    abortRef.current = new AbortController();
    setValidating(true);
    setResult(null);
    try {
      const r = await checkBackendHealth(url.trim());
      setResult(r);
      if (r.status === "online") toast.success(`Reachable (${r.latencyMs}ms)`);
      else toast.error(r.message ?? "Unreachable");
    } finally {
      setValidating(false);
    }
  }

  function save() {
    if (!url.trim()) return;
    setApiBase(url.trim());
    onSaved(url.trim());
    toast.success("API base saved.");
  }

  return (
    <div className="border border-border p-4">
      <p className="eyebrow">Paste &amp; validate a backend URL</p>
      <p className="mt-2 text-xs text-muted-foreground">
        Try a URL before committing to it. Health-check runs against{" "}
        <code className="font-mono">{"<url>/health"}</code>.
      </p>
      <div className="mt-3 flex flex-col gap-2 sm:flex-row">
        <input
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://xxxx.trycloudflare.com"
          aria-label="Backend URL to validate"
          className="flex-1 bg-input px-3 py-2 font-mono text-sm outline-none focus:ring-1 focus:ring-leo"
        />
        <button
          type="button"
          onClick={validate}
          disabled={validating || !url.trim()}
          className="border border-border px-4 py-2 text-xs font-semibold hover:border-leo hover:text-leo disabled:opacity-40 focus:outline-none focus-visible:ring-2 focus-visible:ring-leo"
        >
          {validating ? "Checking…" : "Validate"}
        </button>
        <button
          type="button"
          onClick={save}
          disabled={!url.trim() || result?.status !== "online"}
          className="bg-leo px-4 py-2 text-xs font-semibold text-leo-foreground disabled:opacity-40 focus:outline-none focus-visible:ring-2 focus-visible:ring-white"
        >
          Save as API base
        </button>
      </div>

      {isLocal && pageOnHttps && (
        <div className="mt-3 border-l-2 border-orange-400 bg-orange-400/5 p-3 text-xs">
          <p className="font-semibold text-orange-400">You pasted a localhost URL.</p>
          <p className="mt-1 text-muted-foreground">
            This browser tab isn't running on your laptop, so <code>localhost</code> can't resolve.
            Expose the backend with a tunnel and use its public https URL:
          </p>
          <pre className="mt-2 overflow-x-auto bg-input p-2 font-mono text-[11px]">
            {`cloudflared tunnel --url http://localhost:8005
# or
ngrok http 8005`}
          </pre>
        </div>
      )}

      {result && (
        <div className="mt-3 text-xs">
          <p>
            Result:{" "}
            <span
              className={
                result.status === "online" ? "font-semibold text-leo" : "font-semibold text-red-400"
              }
            >
              {result.status}
            </span>
            {result.httpStatus ? ` · HTTP ${result.httpStatus}` : ""}
            {result.latencyMs != null ? ` · ${result.latencyMs}ms` : ""}
          </p>
          {result.status !== "online" && result.message && (
            <p className="mt-1 text-red-400">{result.message}</p>
          )}
          {result.hints && result.hints.length > 0 && (
            <ul className="mt-2 space-y-1 text-muted-foreground">
              {result.hints.map((h, i) => (
                <li key={i} className="flex gap-2">
                  <span className="text-leo" aria-hidden>
                    →
                  </span>
                  <code className="whitespace-pre-wrap break-words font-mono text-[11px]">{h}</code>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
