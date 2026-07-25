import { useEffect, useRef, useState } from "react";
import { getApiBase, getToken } from "@/lib/leo-client";
import { toast } from "sonner";

// Shape is intentionally loose — the backend may add fields freely.
export interface BackendDiagnostics {
  environment?: Record<string, unknown>;
  models?: Record<string, unknown>;
  config?: Record<string, unknown>;
  last_error?: {
    type?: string;
    message?: string;
    traceback?: string;
    at?: string;
    route?: string;
  } | null;
  [k: string]: unknown;
}

type SnapshotSource = "manual" | "auto" | "initial";

interface HistoryEntry {
  id: number;
  at: string;
  ok: boolean;
  httpStatus: number | null;
  latencyMs: number | null;
  data: BackendDiagnostics | null;
  error?: string;
  source: SnapshotSource;
  refreshMs?: number;
}

function formatHuman(iso: string): string {
  try {
    const d = new Date(iso);
    const diff = Date.now() - d.getTime();
    const s = Math.round(diff / 1000);
    const rel =
      s < 5
        ? "just now"
        : s < 60
          ? `${s}s ago`
          : s < 3600
            ? `${Math.round(s / 60)}m ago`
            : s < 86400
              ? `${Math.round(s / 3600)}h ago`
              : `${Math.round(s / 86400)}d ago`;
    return `${d.toLocaleString()} · ${rel}`;
  } catch {
    return iso;
  }
}

const HISTORY_KEY = "leo.diagnostics_history_v1";
const MAX_HISTORY = 10;
const REFRESH_OPTIONS = [0, 2000, 5000, 10000, 30000];

function loadHistory(): HistoryEntry[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = window.localStorage.getItem(HISTORY_KEY);
    if (!raw) return [];
    const p = JSON.parse(raw);
    return Array.isArray(p) ? p.slice(-MAX_HISTORY) : [];
  } catch {
    return [];
  }
}
function saveHistory(h: HistoryEntry[]) {
  try {
    window.localStorage.setItem(HISTORY_KEY, JSON.stringify(h.slice(-MAX_HISTORY)));
  } catch {
    /* quota */
  }
}

async function probeDiagnostics(source: SnapshotSource, refreshMs?: number): Promise<HistoryEntry> {
  const url = `${getApiBase()}/api/v1/leo/diagnostics`;
  const started = performance.now();
  const token = getToken();
  const headers: Record<string, string> = { Accept: "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  try {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 8000);
    const res = await fetch(url, { headers, signal: controller.signal });
    clearTimeout(timer);
    const latency = Math.round(performance.now() - started);
    let data: BackendDiagnostics | null = null;
    let err: string | undefined;
    try {
      data = (await res.json()) as BackendDiagnostics;
    } catch {
      err = "Invalid JSON response";
    }
    return {
      id: Date.now(),
      at: new Date().toISOString(),
      ok: res.ok && !err,
      httpStatus: res.status,
      latencyMs: latency,
      data,
      error: !res.ok ? `HTTP ${res.status}` : err,
      source,
      refreshMs,
    };
  } catch (e) {
    return {
      id: Date.now(),
      at: new Date().toISOString(),
      ok: false,
      httpStatus: null,
      latencyMs: Math.round(performance.now() - started),
      data: null,
      error: e instanceof Error ? e.message : "Network error",
      source,
      refreshMs,
    };
  }
}

export function BackendDiagnosticsPanel() {
  const [history, setHistory] = useState<HistoryEntry[]>(() => loadHistory());
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [compareId, setCompareId] = useState<number | null>(null);
  const [isFetching, setIsFetching] = useState(false);
  const [refreshMs, setRefreshMs] = useState(0);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const latest = history[history.length - 1] ?? null;
  const selected = history.find((h) => h.id === selectedId) ?? latest;
  const compare = history.find((h) => h.id === compareId) ?? null;

  const prevErrRef = useRef<string | null>(null);

  async function run(source: SnapshotSource = "manual") {
    setIsFetching(true);
    const entry = await probeDiagnostics(source, refreshMs || undefined);
    setHistory((prev) => {
      const next = [...prev, entry].slice(-MAX_HISTORY);
      saveHistory(next);
      return next;
    });
    // last_error change detection (only when auto-refresh is active)
    if (refreshMs > 0 && entry.ok) {
      const errSig = entry.data?.last_error
        ? `${entry.data.last_error.type ?? ""}|${entry.data.last_error.message ?? ""}|${entry.data.last_error.at ?? ""}`
        : "";
      const prev = prevErrRef.current;
      if (prev !== null && prev !== errSig) {
        if (errSig === "") toast.success("last_error cleared");
        else
          toast.error(
            `New backend error: ${entry.data?.last_error?.message ?? entry.data?.last_error?.type ?? "unknown"}`,
          );
      }
      prevErrRef.current = errSig;
    }
    setIsFetching(false);
  }

  useEffect(() => {
    if (history.length === 0) void run("initial");
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (timerRef.current) clearInterval(timerRef.current);
    if (refreshMs > 0) {
      timerRef.current = setInterval(() => void run("auto"), refreshMs);
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [refreshMs]);

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(JSON.stringify(selected?.data ?? {}, null, 2));
      toast.success("Diagnostics copied");
    } catch {
      toast.error("Clipboard blocked");
    }
  };

  const download = () => {
    if (!selected?.data) {
      toast.error("No diagnostics payload to download");
      return;
    }
    const blob = new Blob([JSON.stringify(selected.data, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `leo-diagnostics-${selected.at.replace(/[:.]/g, "-")}.json`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  };

  const downloadCsv = () => {
    if (history.length === 0) {
      toast.error("No history to export");
      return;
    }
    const esc = (v: unknown) => {
      const s = v == null ? "" : String(v);
      return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
    };
    const header = [
      "timestamp",
      "ok",
      "http_status",
      "latency_ms",
      "environment",
      "models",
      "config",
      "last_error_type",
      "last_error_message",
      "last_error_route",
      "last_error_at",
      "error",
    ];
    const metaLines = [
      `# exported_at=${new Date().toISOString()}`,
      `# api_base=${getApiBase()}`,
      `# endpoint=/api/v1/leo/diagnostics`,
      `# count=${history.length}`,
    ];
    const rows = history.map((h) =>
      [
        h.at,
        h.ok,
        h.httpStatus ?? "",
        h.latencyMs ?? "",
        h.data?.environment ? JSON.stringify(h.data.environment) : "",
        h.data?.models ? JSON.stringify(h.data.models) : "",
        h.data?.config ? JSON.stringify(h.data.config) : "",
        h.data?.last_error?.type ?? "",
        h.data?.last_error?.message ?? "",
        h.data?.last_error?.route ?? "",
        h.data?.last_error?.at ?? "",
        h.error ?? "",
      ]
        .map(esc)
        .join(","),
    );
    const csv = [...metaLines, header.join(","), ...rows].join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `leo-diagnostics-history-${new Date().toISOString().replace(/[:.]/g, "-")}.csv`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  };

  const clearHistory = () => {
    setHistory([]);
    saveHistory([]);
    setSelectedId(null);
    setCompareId(null);
    prevErrRef.current = null;
    toast.success("Diagnostics history cleared");
  };

  const copyLatestJson = async () => {
    if (!latest?.data) {
      toast.error("No latest payload to copy");
      return;
    }
    try {
      await navigator.clipboard.writeText(JSON.stringify(latest.data, null, 2));
      toast.success("Latest diagnostics JSON copied");
    } catch {
      toast.error("Clipboard blocked");
    }
  };

  const buildDiffReport = () => {
    if (!compare || !selected) return null;
    const keys = ["environment", "models", "config", "last_error"] as const;
    const sections = keys.map((k) => {
      const a = JSON.stringify(compare.data?.[k] ?? null, null, 2);
      const b = JSON.stringify(selected.data?.[k] ?? null, null, 2);
      const lines = diffLines(a, b);
      const changed = a !== b;
      return { key: k, changed, lines };
    });
    return {
      meta: {
        exported_at: new Date().toISOString(),
        api_base: getApiBase(),
        endpoint: "/api/v1/leo/diagnostics",
        baseline: { at: compare.at, source: compare.source, httpStatus: compare.httpStatus },
        current: { at: selected.at, source: selected.source, httpStatus: selected.httpStatus },
      },
      sections,
    };
  };

  const exportDiffJson = () => {
    const report = buildDiffReport();
    if (!report) {
      toast.error("Set a compare baseline first (double-click a snapshot)");
      return;
    }
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `leo-diagnostics-diff-${new Date().toISOString().replace(/[:.]/g, "-")}.json`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  };

  const exportDiffMarkdown = () => {
    const report = buildDiffReport();
    if (!report) {
      toast.error("Set a compare baseline first (double-click a snapshot)");
      return;
    }
    const { meta, sections } = report;
    const md: string[] = [];
    md.push(`# LEO Diagnostics Diff Report`);
    md.push("");
    md.push(`- Exported: \`${meta.exported_at}\``);
    md.push(`- API base: \`${meta.api_base}\``);
    md.push(`- Endpoint: \`${meta.endpoint}\``);
    md.push(
      `- Baseline: \`${meta.baseline.at}\` (source: ${meta.baseline.source}, HTTP ${meta.baseline.httpStatus ?? "n/a"})`,
    );
    md.push(
      `- Current:  \`${meta.current.at}\` (source: ${meta.current.source}, HTTP ${meta.current.httpStatus ?? "n/a"})`,
    );
    md.push("");
    for (const s of sections) {
      md.push(`## ${s.key} — ${s.changed ? "changed" : "unchanged"}`);
      md.push("");
      if (!s.changed) {
        md.push("_no changes_");
        md.push("");
        continue;
      }
      md.push("```diff");
      for (const ln of s.lines) {
        const prefix = ln.kind === "add" ? "+" : ln.kind === "del" ? "-" : " ";
        md.push(`${prefix} ${ln.text}`);
      }
      md.push("```");
      md.push("");
    }
    const blob = new Blob([md.join("\n")], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `leo-diagnostics-diff-${new Date().toISOString().replace(/[:.]/g, "-")}.md`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  };

  const url = `${getApiBase()}/api/v1/leo/diagnostics`;
  const connOk = latest?.ok === true;
  const connWarn = latest && !latest.ok;

  return (
    <section className="border border-border bg-background/60">
      <header className="flex flex-wrap items-center justify-between gap-2 border-b border-border px-4 py-3">
        <div className="min-w-0">
          <div className="eyebrow">Backend /diagnostics</div>
          <div className="text-xs text-muted-foreground font-mono truncate max-w-[420px]">
            {url}
          </div>
          <div className="mt-1 flex items-center gap-2 text-[11px]">
            <span
              aria-live="polite"
              className={`inline-flex items-center gap-1 px-2 py-0.5 border ${
                connOk
                  ? "border-green-500/40 bg-green-500/10 text-green-300"
                  : connWarn
                    ? "border-red-500/40 bg-red-500/10 text-red-300"
                    : "border-border text-muted-foreground"
              }`}
            >
              {connOk ? "● reachable" : connWarn ? "● unreachable" : "● unknown"}
              {latest?.httpStatus != null && (
                <span className="font-mono">HTTP {latest.httpStatus}</span>
              )}
              {latest?.latencyMs != null && <span className="font-mono">{latest.latencyMs}ms</span>}
            </span>
          </div>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <label className="inline-flex items-center gap-1 text-[11px] text-muted-foreground">
            Auto
            <select
              value={refreshMs}
              onChange={(e) => setRefreshMs(Number(e.target.value))}
              className="border border-border bg-background px-1 py-0.5 font-mono text-[11px] focus:border-leo focus:outline-none"
              aria-label="Auto-refresh interval"
            >
              {REFRESH_OPTIONS.map((o) => (
                <option key={o} value={o}>
                  {o === 0 ? "off" : `${o / 1000}s`}
                </option>
              ))}
            </select>
          </label>
          <button
            type="button"
            onClick={() => void run("manual")}
            disabled={isFetching}
            className="border border-border px-2 py-1 text-[11px] hover:border-leo hover:text-leo disabled:opacity-50"
          >
            {isFetching ? "Fetching…" : "Refresh"}
          </button>
          <button
            type="button"
            onClick={copyLatestJson}
            disabled={!latest?.data}
            className="border border-border px-2 py-1 text-[11px] hover:border-leo hover:text-leo disabled:opacity-50"
            title="Copy latest /diagnostics JSON payload (including last_error)"
          >
            Copy JSON
          </button>
          <button
            type="button"
            onClick={copy}
            disabled={!selected?.data}
            className="border border-border px-2 py-1 text-[11px] hover:border-leo hover:text-leo disabled:opacity-50"
          >
            Copy
          </button>
          <button
            type="button"
            onClick={download}
            disabled={!selected?.data}
            className="border border-border px-2 py-1 text-[11px] hover:border-leo hover:text-leo disabled:opacity-50"
          >
            Download JSON
          </button>
          <button
            type="button"
            onClick={downloadCsv}
            disabled={history.length === 0}
            className="border border-border px-2 py-1 text-[11px] hover:border-leo hover:text-leo disabled:opacity-50"
          >
            Download CSV
          </button>
          <button
            type="button"
            onClick={exportDiffJson}
            disabled={!compare || !selected}
            className="border border-border px-2 py-1 text-[11px] hover:border-leo hover:text-leo disabled:opacity-50"
            title="Export the current baseline↔current diff as JSON"
          >
            Export diff JSON
          </button>
          <button
            type="button"
            onClick={exportDiffMarkdown}
            disabled={!compare || !selected}
            className="border border-border px-2 py-1 text-[11px] hover:border-leo hover:text-leo disabled:opacity-50"
            title="Export the current baseline↔current diff as Markdown"
          >
            Export diff MD
          </button>
          <button
            type="button"
            onClick={clearHistory}
            disabled={history.length === 0}
            className="border border-border px-2 py-1 text-[11px] hover:border-red-500/60 hover:text-red-300 disabled:opacity-50"
          >
            Clear
          </button>
        </div>
      </header>

      {connWarn && (
        <div
          className="border-b border-red-500/40 bg-red-500/10 px-4 py-2 text-[11px] text-red-200"
          role="alert"
        >
          <strong>Unreachable:</strong> {latest?.error ?? "unknown error"} — check that your backend
          is running and that <code className="font-mono">/api/v1/leo/diagnostics</code> exists.
        </div>
      )}

      <div className="grid gap-0 border-b border-border md:grid-cols-[220px_1fr]">
        {/* History list */}
        <div className="border-b border-border md:border-b-0 md:border-r md:border-border">
          <div className="px-3 py-2 text-[11px] uppercase tracking-wide text-muted-foreground">
            History ({history.length}/{MAX_HISTORY})
          </div>
          <ul className="max-h-[300px] overflow-auto">
            {history.length === 0 && (
              <li className="px-3 py-2 text-[11px] text-muted-foreground">No snapshots yet.</li>
            )}
            {history
              .slice()
              .reverse()
              .map((h) => {
                const isSel = (selectedId ?? latest?.id) === h.id;
                const isCmp = compareId === h.id;
                return (
                  <li key={h.id}>
                    <button
                      type="button"
                      onClick={() => setSelectedId(h.id)}
                      onDoubleClick={() => setCompareId(h.id === compareId ? null : h.id)}
                      className={`flex w-full items-center justify-between gap-2 border-l-2 px-3 py-1.5 text-left text-[11px] font-mono hover:bg-muted/30 ${
                        isSel
                          ? "border-leo bg-muted/20"
                          : isCmp
                            ? "border-orange-400"
                            : "border-transparent"
                      }`}
                      title="Click to view · Double-click to set as compare baseline"
                    >
                      <span className="flex min-w-0 flex-col">
                        <span className="truncate">{new Date(h.at).toLocaleTimeString()}</span>
                        <span className="text-[10px] opacity-60 normal-case">
                          {h.source}
                          {h.source === "auto" && h.refreshMs ? ` · ${h.refreshMs / 1000}s` : ""}
                        </span>
                      </span>
                      <span className={h.ok ? "text-green-400" : "text-red-400"}>
                        {h.httpStatus ?? "ERR"}
                      </span>
                    </button>
                  </li>
                );
              })}
          </ul>
          {history.length >= 2 && (
            <div className="border-t border-border px-3 py-2 text-[10px] text-muted-foreground">
              Double-click a row to set compare baseline
              {compare && (
                <button
                  type="button"
                  onClick={() => setCompareId(null)}
                  className="ml-2 underline hover:text-leo"
                >
                  clear
                </button>
              )}
            </div>
          )}
        </div>

        {/* Detail */}
        <div className="px-4 py-3 text-xs" aria-live="polite">
          {!selected ? (
            <p className="text-muted-foreground">No diagnostics yet — click Refresh.</p>
          ) : (
            <>
              <div className="mb-2 flex flex-wrap items-center gap-3 text-[11px] text-muted-foreground">
                <span>
                  Snapshot: <span className="font-mono">{formatHuman(selected.at)}</span>
                  <span className="ml-1 opacity-70">
                    · source: <span className="font-mono">{selected.source}</span>
                    {selected.source === "auto" && selected.refreshMs ? (
                      <>
                        {" "}
                        · every <span className="font-mono">{selected.refreshMs / 1000}s</span>
                      </>
                    ) : null}
                  </span>
                </span>
                {compare && (
                  <span>
                    vs baseline: <span className="font-mono">{formatHuman(compare.at)}</span>
                    <span className="ml-1 opacity-70">
                      · source: <span className="font-mono">{compare.source}</span>
                    </span>
                  </span>
                )}
              </div>

              {selected.data?.last_error && (
                <div
                  className="mb-3 border border-orange-400/40 bg-orange-400/10 p-3 text-orange-100"
                  role="alert"
                >
                  <div className="flex items-baseline justify-between gap-2">
                    <strong className="uppercase tracking-wide">Last error</strong>
                    {selected.data.last_error.at && (
                      <span className="font-mono text-[11px]">{selected.data.last_error.at}</span>
                    )}
                  </div>
                  <div className="mt-1 font-mono">
                    {selected.data.last_error.type ? `${selected.data.last_error.type}: ` : ""}
                    {selected.data.last_error.message ?? "(no message)"}
                  </div>
                  {selected.data.last_error.route && (
                    <div className="mt-1 font-mono text-[11px] opacity-80">
                      route: {selected.data.last_error.route}
                    </div>
                  )}
                  {selected.data.last_error.traceback && (
                    <details className="mt-2">
                      <summary className="cursor-pointer text-[11px] opacity-80">Traceback</summary>
                      <pre className="mt-2 max-h-64 overflow-auto whitespace-pre-wrap font-mono text-[11px]">
                        {selected.data.last_error.traceback}
                      </pre>
                    </details>
                  )}
                </div>
              )}

              {compare ? (
                <DiffView baseline={compare.data} current={selected.data} />
              ) : selected.data ? (
                <pre className="max-h-[360px] overflow-auto whitespace-pre-wrap font-mono text-[11px] text-muted-foreground">
                  {JSON.stringify(
                    {
                      environment: selected.data.environment,
                      models: selected.data.models,
                      config: selected.data.config,
                    },
                    null,
                    2,
                  )}
                </pre>
              ) : (
                <p className="text-red-300">No payload — {selected.error}</p>
              )}
            </>
          )}
        </div>
      </div>
    </section>
  );
}

function DiffView({
  baseline,
  current,
}: {
  baseline: BackendDiagnostics | null;
  current: BackendDiagnostics | null;
}) {
  const keys = ["environment", "models", "config", "last_error"] as const;
  return (
    <div className="space-y-3">
      {keys.map((k) => {
        const a = JSON.stringify(baseline?.[k] ?? null, null, 2);
        const b = JSON.stringify(current?.[k] ?? null, null, 2);
        const same = a === b;
        return (
          <div key={k} className="border border-border">
            <div
              className={`flex items-center justify-between border-b border-border px-2 py-1 text-[11px] uppercase tracking-wide ${
                same ? "text-muted-foreground" : "text-orange-300"
              }`}
            >
              <span>{k}</span>
              <span>{same ? "unchanged" : "changed"}</span>
            </div>
            {!same && (
              <div className="bg-background font-mono text-[11px] max-h-72 overflow-auto">
                {diffLines(a, b).map((ln, i) => (
                  <div
                    key={i}
                    className={
                      ln.kind === "add"
                        ? "bg-green-500/10 text-green-300 px-2"
                        : ln.kind === "del"
                          ? "bg-red-500/10 text-red-300 px-2"
                          : "text-muted-foreground px-2"
                    }
                  >
                    <span className="select-none opacity-60 mr-2">
                      {ln.kind === "add" ? "+" : ln.kind === "del" ? "-" : " "}
                    </span>
                    {ln.text || "\u00a0"}
                  </div>
                ))}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

type DiffLine = { kind: "eq" | "add" | "del"; text: string };

// Simple LCS-based line diff — good enough for small JSON blocks.
function diffLines(aText: string, bText: string): DiffLine[] {
  const a = aText.split("\n");
  const b = bText.split("\n");
  const n = a.length,
    m = b.length;
  const dp: number[][] = Array.from({ length: n + 1 }, () => new Array(m + 1).fill(0));
  for (let i = n - 1; i >= 0; i--) {
    for (let j = m - 1; j >= 0; j--) {
      dp[i][j] = a[i] === b[j] ? dp[i + 1][j + 1] + 1 : Math.max(dp[i + 1][j], dp[i][j + 1]);
    }
  }
  const out: DiffLine[] = [];
  let i = 0,
    j = 0;
  while (i < n && j < m) {
    if (a[i] === b[j]) {
      out.push({ kind: "eq", text: a[i] });
      i++;
      j++;
    } else if (dp[i + 1][j] >= dp[i][j + 1]) {
      out.push({ kind: "del", text: a[i] });
      i++;
    } else {
      out.push({ kind: "add", text: b[j] });
      j++;
    }
  }
  while (i < n) out.push({ kind: "del", text: a[i++] });
  while (j < m) out.push({ kind: "add", text: b[j++] });
  return out;
}
