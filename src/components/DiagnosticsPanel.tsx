import { toast } from "sonner";
import {
  clearHealthHistory,
  computeReliability,
  exportHealthCsv,
  exportHealthJson,
  getDiagnosticsSnapshot,
  useHealthHistory,
  useThresholds,
} from "@/lib/health-history";

const STATUS_COLOR: Record<string, string> = {
  online: "text-leo",
  error: "text-orange-400",
  unreachable: "text-red-400",
  checking: "text-muted-foreground",
};

function download(filename: string, content: string, mime: string) {
  const blob = new Blob([content], { type: mime });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
  toast.success(`Exported ${filename}`);
}

export function DiagnosticsPanel() {
  const history = useHealthHistory();
  const rows = history.slice(-20).reverse();
  const [t, setT] = useThresholds();
  const report = computeReliability(history, t);
  const latest = history[history.length - 1];
  const schemaIssues = latest?.schemaIssues ?? [];

  const alertClass =
    report.level === "critical"
      ? "border-red-500 bg-red-500/10 text-red-300"
      : report.level === "warn"
        ? "border-orange-400 bg-orange-400/10 text-orange-200"
        : "border-border bg-background/60 text-muted-foreground";

  return (
    <section className="border border-border bg-background/60">
      <header className="flex flex-wrap items-center justify-between gap-2 border-b border-border px-4 py-3">
        <div>
          <div className="eyebrow">Diagnostics</div>
          <div className="text-xs text-muted-foreground">
            Last {rows.length} backend health checks · persisted locally
          </div>
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={() =>
              download(`leo-health-${Date.now()}.json`, exportHealthJson(20), "application/json")
            }
            className="border border-border px-2 py-1 text-[11px] hover:border-leo hover:text-leo"
          >
            Export JSON
          </button>
          <button
            type="button"
            onClick={() =>
              download(`leo-health-${Date.now()}.csv`, exportHealthCsv(20), "text/csv")
            }
            className="border border-border px-2 py-1 text-[11px] hover:border-leo hover:text-leo"
          >
            Export CSV
          </button>
          <button
            type="button"
            onClick={async () => {
              const json = JSON.stringify(getDiagnosticsSnapshot(20), null, 2);
              try {
                await navigator.clipboard.writeText(json);
                toast.success("Diagnostics snapshot copied to clipboard");
              } catch {
                toast.error("Clipboard blocked — export JSON instead");
              }
            }}
            className="border border-border px-2 py-1 text-[11px] hover:border-leo hover:text-leo"
          >
            Copy snapshot
          </button>
          <button
            type="button"
            onClick={() => {
              if (confirm("Clear all persisted health samples?")) clearHealthHistory();
            }}
            className="border border-border px-2 py-1 text-[11px] text-muted-foreground hover:border-red-500 hover:text-red-400"
          >
            Clear
          </button>
        </div>
      </header>

      <div
        className={`border-b border-border px-4 py-3 text-xs ${alertClass}`}
        role={report.level === "critical" ? "alert" : "status"}
        aria-live="polite"
      >
        <div className="flex flex-wrap items-baseline justify-between gap-2">
          <strong className="uppercase tracking-wide">Reliability: {report.level}</strong>
          <span className="font-mono">
            failure {report.failureRatePct}% · slow {report.slowSamples}/{report.windowSize}
          </span>
        </div>
        {report.reasons.length > 0 && (
          <ul className="mt-1 list-inside list-disc">
            {report.reasons.map((r) => (
              <li key={r}>{r}</li>
            ))}
          </ul>
        )}
      </div>

      {schemaIssues.length > 0 && (
        <div
          className="border-b border-border bg-orange-400/10 px-4 py-3 text-xs text-orange-200"
          role="alert"
        >
          <strong>/health schema warnings</strong>
          <ul className="mt-1 list-inside list-disc">
            {schemaIssues.map((s) => (
              <li key={s.field}>
                <span className="font-mono">{s.field}</span>: {s.message}
              </li>
            ))}
          </ul>
        </div>
      )}

      <details className="border-b border-border px-4 py-3 text-xs">
        <summary className="cursor-pointer text-muted-foreground">Thresholds</summary>
        <div className="mt-3 grid grid-cols-2 gap-3">
          <NumField
            label="Latency warn (ms)"
            value={t.latencyWarnMs}
            onChange={(v) => setT({ ...t, latencyWarnMs: v })}
          />
          <NumField
            label="Timeout (ms)"
            value={t.timeoutMs}
            onChange={(v) => setT({ ...t, timeoutMs: v })}
          />
          <NumField
            label="Failure rate (%)"
            value={t.failureRatePct}
            onChange={(v) => setT({ ...t, failureRatePct: v })}
          />
          <NumField
            label="Window size"
            value={t.windowSize}
            onChange={(v) => setT({ ...t, windowSize: v })}
          />
        </div>
      </details>

      <div className="max-h-[360px] overflow-auto">
        <table className="w-full border-collapse text-xs">
          <thead className="sticky top-0 bg-background/95 text-left text-muted-foreground">
            <tr>
              <th className="px-4 py-2 font-medium">Time</th>
              <th className="px-4 py-2 font-medium">Status</th>
              <th className="px-4 py-2 font-medium">HTTP</th>
              <th className="px-4 py-2 font-medium">Latency</th>
              <th className="px-4 py-2 font-medium">Payload / message</th>
            </tr>
          </thead>
          <tbody>
            {rows.length === 0 && (
              <tr>
                <td colSpan={5} className="px-4 py-6 text-center text-muted-foreground">
                  No health checks recorded yet.
                </td>
              </tr>
            )}
            {rows.map((r) => (
              <tr key={r.id} className="border-t border-border/60 align-top">
                <td className="whitespace-nowrap px-4 py-2 font-mono">
                  {r.checkedAt ? new Date(r.checkedAt).toLocaleTimeString() : "—"}
                </td>
                <td className={`px-4 py-2 font-medium ${STATUS_COLOR[r.status] ?? ""}`}>
                  {r.status}
                </td>
                <td className="px-4 py-2 font-mono">{r.httpStatus ?? "—"}</td>
                <td className="px-4 py-2 font-mono">
                  {r.latencyMs != null ? `${r.latencyMs}ms` : "—"}
                </td>
                <td className="px-4 py-2 font-mono text-muted-foreground">
                  <div className="max-w-[520px] truncate" title={r.bodyExcerpt ?? r.message ?? ""}>
                    {r.bodyExcerpt ?? r.message ?? "—"}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function NumField({
  label,
  value,
  onChange,
}: {
  label: string;
  value: number;
  onChange: (v: number) => void;
}) {
  return (
    <label className="flex flex-col gap-1">
      <span className="text-[11px] text-muted-foreground">{label}</span>
      <input
        type="number"
        min={0}
        value={value}
        onChange={(e) => onChange(Number(e.target.value) || 0)}
        className="border border-border bg-background px-2 py-1 font-mono text-xs focus:border-leo focus:outline-none"
      />
    </label>
  );
}
