import { useMemo, useRef, useState } from "react";
import {
  useBenchmarkHistory,
  clearHistory,
  downloadRuns,
  downloadTemplate,
  importRuns,
  parseImportedFile,
  validateSchema,
  type BenchmarkRun,
  type ImportReport,
  type SchemaReport,
} from "@/lib/benchmark-history";
import { buildShareUrl, encodeRunShare } from "@/lib/share-link";
import { toast } from "sonner";

type SortKey =
  | "timestamp"
  | "path"
  | "totalRequests"
  | "concurrency"
  | "throughputRps"
  | "p50Ms"
  | "p95Ms"
  | "p99Ms"
  | "errorRatePct";

const COLS: { key: SortKey; label: string; num?: boolean }[] = [
  { key: "timestamp", label: "When" },
  { key: "path", label: "Path" },
  { key: "totalRequests", label: "N", num: true },
  { key: "concurrency", label: "C", num: true },
  { key: "throughputRps", label: "rps", num: true },
  { key: "p50Ms", label: "p50", num: true },
  { key: "p95Ms", label: "p95", num: true },
  { key: "p99Ms", label: "p99", num: true },
  { key: "errorRatePct", label: "err%", num: true },
];

export function BenchmarkHistory({
  selectedId,
  onSelect,
}: {
  selectedId?: string | null;
  onSelect?: (run: BenchmarkRun | null) => void;
}) {
  const runs = useBenchmarkHistory();
  const [sortKey, setSortKey] = useState<SortKey>("timestamp");
  const [dir, setDir] = useState<"asc" | "desc">("desc");

  const sorted = useMemo(() => {
    const arr = [...runs];
    arr.sort((a, b) => {
      const av = a[sortKey] as number | string;
      const bv = b[sortKey] as number | string;
      const cmp =
        typeof av === "number" && typeof bv === "number"
          ? av - bv
          : String(av).localeCompare(String(bv));
      return dir === "asc" ? cmp : -cmp;
    });
    return arr;
  }, [runs, sortKey, dir]);

  function toggle(k: SortKey) {
    if (k === sortKey) setDir(dir === "asc" ? "desc" : "asc");
    else {
      setSortKey(k);
      setDir(k === "timestamp" ? "desc" : "desc");
    }
  }

  const fileRef = useRef<HTMLInputElement>(null);
  const [importReport, setImportReport] = useState<(ImportReport & { fileName: string }) | null>(
    null,
  );
  const [schemaReport, setSchemaReport] = useState<(SchemaReport & { fileName: string }) | null>(
    null,
  );

  async function onImportFile(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    e.target.value = "";
    if (!file) return;
    try {
      const text = await file.text();
      // Pre-parse schema validation — surfaces missing/mismatched columns
      // BEFORE we start row-by-row parsing, so the user knows exactly what
      // to fix in their file.
      const schema = validateSchema(text, file.name);
      setSchemaReport({ ...schema, fileName: file.name });
      if (!schema.ok) {
        const errs = schema.issues.filter((i) => i.severity === "error").length;
        toast.error(
          `Schema check failed — ${errs} error${errs === 1 ? "" : "s"}. See details below.`,
        );
        setImportReport(null);
        return;
      }
      const parsed = parseImportedFile(text, file.name);
      if (parsed.length === 0) {
        toast.error("No benchmark runs found in file");
        setImportReport({
          added: 0,
          skipped: 0,
          invalid: 0,
          total: 0,
          issues: [],
          fileName: file.name,
        });
        return;
      }
      const res = importRuns(parsed, "merge");
      setImportReport({ ...res, fileName: file.name });
      const parts = [`${res.added} merged`];
      if (res.skipped) parts.push(`${res.skipped} duplicate`);
      if (res.invalid) parts.push(`${res.invalid} invalid`);
      const msg = `Import: ${parts.join(" · ")}`;
      if (res.invalid > 0) toast.warning(msg);
      else toast.success(msg);
    } catch (err) {
      toast.error("Import failed: " + (err as Error).message);
      setImportReport({
        added: 0,
        skipped: 0,
        invalid: 1,
        total: 0,
        issues: [{ rowIndex: 0, status: "invalid", reason: (err as Error).message }],
        fileName: file.name,
      });
    }
  }

  return (
    <section
      aria-labelledby="bench-history-title"
      className="border border-border bg-background p-6"
    >
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="eyebrow">History</p>
          <h2 id="bench-history-title" className="mt-1 font-display text-2xl font-bold">
            Saved benchmark runs
          </h2>
          <p className="mt-1 text-xs text-muted-foreground">
            Click a row to link the Hardware profile ratio to that run.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <input
            ref={fileRef}
            type="file"
            accept=".json,.csv,application/json,text/csv"
            onChange={onImportFile}
            className="hidden"
            aria-label="Import benchmark history file"
          />
          <button
            type="button"
            onClick={() => fileRef.current?.click()}
            className="border border-leo/60 px-3 py-1.5 text-xs text-leo hover:bg-leo/10 focus:outline-none focus-visible:ring-2 focus-visible:ring-leo"
          >
            Import JSON / CSV
          </button>
          <div
            className="inline-flex items-stretch border border-border text-xs"
            role="group"
            aria-label="Download import template"
          >
            <span className="px-2 py-1.5 text-muted-foreground">Template</span>
            <button
              type="button"
              onClick={() => downloadTemplate("json")}
              className="border-l border-border px-2 py-1.5 hover:border-leo hover:text-leo focus:outline-none focus-visible:ring-2 focus-visible:ring-leo"
              title="Download an example JSON matching the import schema"
            >
              JSON
            </button>
            <button
              type="button"
              onClick={() => downloadTemplate("csv")}
              className="border-l border-border px-2 py-1.5 hover:border-leo hover:text-leo focus:outline-none focus-visible:ring-2 focus-visible:ring-leo"
              title="Download an example CSV matching the import schema"
            >
              CSV
            </button>
          </div>
          <button
            type="button"
            onClick={async () => {
              const sel = runs.find((r) => r.id === selectedId);
              if (!sel) {
                toast.error("Select a run first");
                return;
              }
              const url = buildShareUrl("run", encodeRunShare(sel));
              try {
                await navigator.clipboard.writeText(url);
                toast.success("Run share link copied");
              } catch {
                toast.error("Copy failed");
              }
            }}
            disabled={!selectedId}
            className="border border-border px-3 py-1.5 text-xs hover:border-leo hover:text-leo disabled:opacity-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-leo"
          >
            Share selected
          </button>

          <button
            type="button"
            onClick={() => downloadRuns(runs, "json")}
            disabled={runs.length === 0}
            className="border border-border px-3 py-1.5 text-xs hover:border-leo hover:text-leo disabled:opacity-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-leo"
          >
            Export JSON
          </button>
          <button
            type="button"
            onClick={() => downloadRuns(runs, "csv")}
            disabled={runs.length === 0}
            className="border border-border px-3 py-1.5 text-xs hover:border-leo hover:text-leo disabled:opacity-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-leo"
          >
            Export CSV
          </button>
          <button
            type="button"
            onClick={() => {
              clearHistory();
              onSelect?.(null);
            }}
            disabled={runs.length === 0}
            className="border border-border px-3 py-1.5 text-xs hover:border-destructive hover:text-destructive disabled:opacity-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-destructive"
          >
            Clear
          </button>
        </div>
      </div>

      {schemaReport && (
        <div
          role="status"
          aria-live="polite"
          className={`mt-4 border p-3 text-xs ${
            schemaReport.ok
              ? "border-border bg-muted/10"
              : "border-destructive/60 bg-destructive/10 text-destructive"
          }`}
        >
          <div className="flex flex-wrap items-baseline justify-between gap-2">
            <div>
              <span className="eyebrow">Schema check</span>{" "}
              <span className="font-mono text-muted-foreground">{schemaReport.fileName}</span>{" "}
              <span className="font-mono text-[10px] uppercase text-muted-foreground">
                {schemaReport.format}
              </span>
            </div>
            <div className="flex items-center gap-3 font-mono">
              <span>{schemaReport.rowCount} rows</span>
              <span>{schemaReport.detectedFields.length} fields</span>
              <span className={schemaReport.ok ? "text-leo" : "text-destructive"}>
                {schemaReport.ok ? "OK" : "FAIL"}
              </span>
              <button
                type="button"
                onClick={() => setSchemaReport(null)}
                className="text-muted-foreground hover:text-leo focus:outline-none focus-visible:ring-2 focus-visible:ring-leo"
                aria-label="Dismiss schema report"
              >
                ×
              </button>
            </div>
          </div>
          {schemaReport.issues.length > 0 && (
            <ul className="mt-2 space-y-0.5 font-mono text-[11px]">
              {schemaReport.issues.slice(0, 30).map((iss, i) => (
                <li
                  key={i}
                  className={iss.severity === "error" ? "text-destructive" : "text-yellow-600"}
                >
                  <span className="mr-1 uppercase">[{iss.severity}]</span>
                  <span className="mr-1">{iss.field}:</span>
                  <span className="text-muted-foreground">{iss.message}</span>
                </li>
              ))}
              {schemaReport.issues.length > 30 && (
                <li className="text-[10px] text-muted-foreground">
                  … {schemaReport.issues.length - 30} more issues suppressed.
                </li>
              )}
            </ul>
          )}
          {schemaReport.detectedFields.length > 0 && (
            <p className="mt-2 text-[10px] text-muted-foreground">
              Detected fields:{" "}
              <span className="font-mono">{schemaReport.detectedFields.join(", ")}</span>
            </p>
          )}
        </div>
      )}

      {importReport && (
        <div
          role="status"
          aria-live="polite"
          className="mt-4 border border-border bg-muted/10 p-3 text-xs"
        >
          <div className="flex flex-wrap items-baseline justify-between gap-2">
            <div>
              <span className="eyebrow">Import report</span>{" "}
              <span className="font-mono text-muted-foreground">{importReport.fileName}</span>
            </div>
            <div className="flex gap-3 font-mono">
              <span className="text-leo">{importReport.added} merged</span>
              <span className="text-muted-foreground">{importReport.skipped} duplicate</span>
              <span className={importReport.invalid ? "text-destructive" : "text-muted-foreground"}>
                {importReport.invalid} invalid
              </span>
              <button
                type="button"
                onClick={() => setImportReport(null)}
                className="text-muted-foreground hover:text-leo focus:outline-none focus-visible:ring-2 focus-visible:ring-leo"
                aria-label="Dismiss import report"
              >
                ×
              </button>
            </div>
          </div>
          {importReport.issues.length > 0 && (
            <details className="mt-2">
              <summary className="cursor-pointer text-[11px] uppercase tracking-wide text-muted-foreground hover:text-leo">
                Row-level details ({importReport.issues.length})
              </summary>
              <div className="mt-2 max-h-48 overflow-y-auto">
                <table className="w-full text-[11px]">
                  <thead className="text-muted-foreground">
                    <tr>
                      <th className="text-left px-2 py-1">Row</th>
                      <th className="text-left px-2 py-1">Status</th>
                      <th className="text-left px-2 py-1">ID</th>
                      <th className="text-left px-2 py-1">Reason</th>
                    </tr>
                  </thead>
                  <tbody>
                    {importReport.issues.slice(0, 200).map((iss, i) => (
                      <tr key={i} className="border-t border-border/40">
                        <td className="px-2 py-1 font-mono">{iss.rowIndex + 1}</td>
                        <td
                          className={`px-2 py-1 font-mono ${
                            iss.status === "invalid"
                              ? "text-destructive"
                              : iss.status === "duplicate"
                                ? "text-yellow-600"
                                : "text-leo"
                          }`}
                        >
                          {iss.status}
                        </td>
                        <td
                          className="px-2 py-1 font-mono truncate max-w-[180px]"
                          title={iss.id ?? ""}
                        >
                          {iss.id ?? "—"}
                        </td>
                        <td className="px-2 py-1 text-muted-foreground">{iss.reason ?? ""}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                {importReport.issues.length > 200 && (
                  <p className="mt-2 text-[10px] text-muted-foreground">
                    Showing first 200 of {importReport.issues.length} rows.
                  </p>
                )}
              </div>
            </details>
          )}
        </div>
      )}

      <div className="mt-4 overflow-x-auto">
        <table className="w-full min-w-[720px] border-collapse text-xs">
          <thead>
            <tr className="border-b border-border text-[11px] uppercase tracking-wide text-muted-foreground">
              {COLS.map((c) => (
                <th
                  key={c.key}
                  scope="col"
                  className={`px-3 py-2 ${c.num ? "text-right" : "text-left"}`}
                >
                  <button
                    type="button"
                    onClick={() => toggle(c.key)}
                    className="inline-flex items-center gap-1 hover:text-leo focus:outline-none focus-visible:ring-2 focus-visible:ring-leo"
                    aria-sort={
                      sortKey === c.key ? (dir === "asc" ? "ascending" : "descending") : "none"
                    }
                  >
                    {c.label}
                    {sortKey === c.key && <span aria-hidden>{dir === "asc" ? "↑" : "↓"}</span>}
                  </button>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {sorted.length === 0 && (
              <tr>
                <td colSpan={COLS.length} className="px-3 py-6 text-center text-muted-foreground">
                  No runs yet. Run a benchmark to populate history.
                </td>
              </tr>
            )}
            {sorted.map((r) => {
              const isSel = r.id === selectedId;
              return (
                <tr
                  key={r.id}
                  onClick={() => onSelect?.(isSel ? null : r)}
                  className={`cursor-pointer border-b border-border/60 hover:bg-muted/30 ${
                    isSel ? "bg-leo/10" : ""
                  }`}
                >
                  <td className="px-3 py-2 font-mono">{new Date(r.timestamp).toLocaleString()}</td>
                  <td className="px-3 py-2 font-mono truncate max-w-[200px]" title={r.path}>
                    {r.path}
                  </td>
                  <td className="px-3 py-2 text-right font-mono">{r.totalRequests}</td>
                  <td className="px-3 py-2 text-right font-mono">{r.concurrency}</td>
                  <td className="px-3 py-2 text-right font-mono text-leo">
                    {r.throughputRps.toFixed(1)}
                  </td>
                  <td className="px-3 py-2 text-right font-mono">{r.p50Ms.toFixed(1)}</td>
                  <td className="px-3 py-2 text-right font-mono">{r.p95Ms.toFixed(1)}</td>
                  <td className="px-3 py-2 text-right font-mono">{r.p99Ms.toFixed(1)}</td>
                  <td
                    className={`px-3 py-2 text-right font-mono ${
                      r.errorRatePct > 5 ? "text-destructive" : ""
                    }`}
                  >
                    {r.errorRatePct.toFixed(2)}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </section>
  );
}
