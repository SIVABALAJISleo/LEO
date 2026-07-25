import { useEffect, useState } from "react";

const KEY = "leo.bench.history";
const MAX = 50;

export type BenchmarkRun = {
  id: string;
  timestamp: string;
  apiBase: string;
  path: string;
  totalRequests: number;
  concurrency: number;
  durationMs: number;
  errors: number;
  errorRatePct: number;
  throughputRps: number;
  p50Ms: number;
  p95Ms: number;
  p99Ms: number;
  minMs: number;
  maxMs: number;
  meanMs: number;
};

function read(): BenchmarkRun[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = window.localStorage.getItem(KEY);
    return raw ? (JSON.parse(raw) as BenchmarkRun[]) : [];
  } catch {
    return [];
  }
}

function write(runs: BenchmarkRun[]) {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(KEY, JSON.stringify(runs.slice(0, MAX)));
    window.dispatchEvent(new CustomEvent("leo:bench-history"));
  } catch {
    /* ignore */
  }
}

export function saveRun(run: BenchmarkRun) {
  write([run, ...read()]);
}

export type ImportRowIssue = {
  rowIndex: number; // 0-based row index in the source file
  status: "merged" | "duplicate" | "invalid";
  reason?: string;
  id?: string;
};

export type ImportReport = {
  added: number;
  skipped: number;
  invalid: number;
  total: number;
  issues: ImportRowIssue[];
};

function validateRow(
  raw: unknown,
  rowIndex: number,
): { ok: true; run: BenchmarkRun } | { ok: false; issue: ImportRowIssue } {
  if (!raw || typeof raw !== "object") {
    return { ok: false, issue: { rowIndex, status: "invalid", reason: "not an object" } };
  }
  const r = raw as Record<string, unknown>;
  const missing: string[] = [];
  if (typeof r.id !== "string" || !r.id) missing.push("id");
  if (typeof r.timestamp !== "string" || !r.timestamp) missing.push("timestamp");
  const numericFields = ["throughputRps", "p50Ms", "p95Ms", "p99Ms", "errorRatePct"] as const;
  for (const k of numericFields) {
    const v = r[k];
    if (typeof v !== "number" || Number.isNaN(v)) missing.push(k);
  }
  if (missing.length) {
    return {
      ok: false,
      issue: {
        rowIndex,
        status: "invalid",
        reason: `missing/invalid: ${missing.join(", ")}`,
        id: typeof r.id === "string" ? r.id : undefined,
      },
    };
  }
  return { ok: true, run: r as unknown as BenchmarkRun };
}

export function importRuns(
  incoming: unknown[],
  strategy: "merge" | "replace" = "merge",
): ImportReport {
  const issues: ImportRowIssue[] = [];
  const valid: BenchmarkRun[] = [];
  incoming.forEach((raw, i) => {
    const res = validateRow(raw, i);
    if (res.ok) valid.push(res.run);
    else issues.push(res.issue);
  });
  if (strategy === "replace") {
    write(valid);
    valid.forEach((r, i) => issues.push({ rowIndex: i, status: "merged", id: r.id }));
    return {
      added: valid.length,
      skipped: 0,
      invalid: issues.filter((x) => x.status === "invalid").length,
      total: valid.length,
      issues,
    };
  }
  const current = read();
  const seen = new Set(current.map((r) => r.id));
  let added = 0;
  let skipped = 0;
  for (let i = 0; i < valid.length; i++) {
    const r = valid[i];
    if (seen.has(r.id)) {
      skipped += 1;
      issues.push({ rowIndex: i, status: "duplicate", id: r.id, reason: "id already in history" });
    } else {
      seen.add(r.id);
      current.push(r);
      added += 1;
      issues.push({ rowIndex: i, status: "merged", id: r.id });
    }
  }
  current.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
  write(current);
  return {
    added,
    skipped,
    invalid: issues.filter((x) => x.status === "invalid").length,
    total: current.length,
    issues,
  };
}

// ---------- Pre-parse schema validation ----------
// Runs BEFORE importRuns() so users see exactly which columns/fields are
// missing or mismatched, without every row being flagged individually.

export type SchemaField = {
  name: string;
  type: "string" | "number";
  required: boolean;
};

export const SCHEMA_FIELDS: SchemaField[] = [
  { name: "id", type: "string", required: true },
  { name: "timestamp", type: "string", required: true },
  { name: "apiBase", type: "string", required: false },
  { name: "path", type: "string", required: false },
  { name: "totalRequests", type: "number", required: false },
  { name: "concurrency", type: "number", required: false },
  { name: "durationMs", type: "number", required: false },
  { name: "errors", type: "number", required: false },
  { name: "errorRatePct", type: "number", required: true },
  { name: "throughputRps", type: "number", required: true },
  { name: "p50Ms", type: "number", required: true },
  { name: "p95Ms", type: "number", required: true },
  { name: "p99Ms", type: "number", required: true },
  { name: "minMs", type: "number", required: false },
  { name: "maxMs", type: "number", required: false },
  { name: "meanMs", type: "number", required: false },
];

export type SchemaIssue = {
  field: string;
  severity: "error" | "warning";
  message: string;
};

export type SchemaReport = {
  ok: boolean;
  format: "json" | "csv" | "unknown";
  detectedFields: string[];
  issues: SchemaIssue[];
  rowCount: number;
};

export function validateSchema(text: string, name: string): SchemaReport {
  const trimmed = text.trim();
  const looksCsv =
    name.toLowerCase().endsWith(".csv") || (!trimmed.startsWith("[") && !trimmed.startsWith("{"));
  const issues: SchemaIssue[] = [];
  let detected: string[] = [];
  let rowCount = 0;
  const format: SchemaReport["format"] = looksCsv ? "csv" : "json";

  try {
    if (looksCsv) {
      const lines = trimmed.split(/\r?\n/).filter((l) => l.length > 0);
      if (lines.length < 2) {
        issues.push({
          field: "*",
          severity: "error",
          message: "CSV needs a header row and at least one data row.",
        });
        return { ok: false, format, detectedFields: [], issues, rowCount: 0 };
      }
      detected = splitCsvLine(lines[0]);
      rowCount = lines.length - 1;
    } else {
      const data = JSON.parse(trimmed);
      const arr = Array.isArray(data)
        ? data
        : Array.isArray((data as { runs?: unknown }).runs)
          ? (data as { runs: unknown[] }).runs
          : [data];
      rowCount = arr.length;
      const first = arr.find((x) => x && typeof x === "object") as
        Record<string, unknown> | undefined;
      detected = first ? Object.keys(first) : [];
      if (!first) {
        issues.push({
          field: "*",
          severity: "error",
          message: "No object rows found in JSON payload.",
        });
      }
    }
  } catch (e) {
    issues.push({
      field: "*",
      severity: "error",
      message: `Parse failed: ${(e as Error).message}`,
    });
    return { ok: false, format, detectedFields: [], issues, rowCount: 0 };
  }

  const detectedSet = new Set(detected);
  for (const f of SCHEMA_FIELDS) {
    if (!detectedSet.has(f.name)) {
      if (f.required) {
        issues.push({
          field: f.name,
          severity: "error",
          message: `Missing required ${f.type} column/field "${f.name}".`,
        });
      } else {
        issues.push({
          field: f.name,
          severity: "warning",
          message: `Optional field "${f.name}" not present — will default.`,
        });
      }
    }
  }
  const known = new Set(SCHEMA_FIELDS.map((f) => f.name));
  for (const d of detected) {
    if (!known.has(d)) {
      issues.push({
        field: d,
        severity: "warning",
        message: `Unknown field "${d}" will be ignored.`,
      });
    }
  }

  const ok = !issues.some((i) => i.severity === "error");
  return { ok, format, detectedFields: detected, issues, rowCount };
}

export function parseImportedFile(text: string, name: string): unknown[] {
  const trimmed = text.trim();
  const looksCsv =
    name.toLowerCase().endsWith(".csv") || (!trimmed.startsWith("[") && !trimmed.startsWith("{"));
  if (looksCsv) return parseCsv(trimmed);
  const data = JSON.parse(trimmed);
  if (Array.isArray(data)) return data;
  // Accept the wrapped template shape { $schema, runs: [...] }.
  if (data && typeof data === "object" && Array.isArray((data as { runs?: unknown }).runs)) {
    return (data as { runs: unknown[] }).runs;
  }
  return [data];
}

function parseCsv(text: string): unknown[] {
  const lines = text.split(/\r?\n/).filter((l) => l.length > 0);
  if (lines.length < 2) return [];
  const header = splitCsvLine(lines[0]);
  const numericKeys = new Set<string>([
    "totalRequests",
    "concurrency",
    "durationMs",
    "errors",
    "errorRatePct",
    "throughputRps",
    "p50Ms",
    "p95Ms",
    "p99Ms",
    "minMs",
    "maxMs",
    "meanMs",
  ]);
  return lines.slice(1).map((line) => {
    const cells = splitCsvLine(line);
    const obj: Record<string, unknown> = {};
    header.forEach((h, i) => {
      const v = cells[i] ?? "";
      obj[h] = numericKeys.has(h) ? Number(v) : v;
    });
    return obj;
  });
}

function splitCsvLine(line: string): string[] {
  const out: string[] = [];
  let cur = "";
  let inQ = false;
  for (let i = 0; i < line.length; i++) {
    const c = line[i];
    if (inQ) {
      if (c === '"' && line[i + 1] === '"') {
        cur += '"';
        i++;
      } else if (c === '"') inQ = false;
      else cur += c;
    } else {
      if (c === ",") {
        out.push(cur);
        cur = "";
      } else if (c === '"') inQ = true;
      else cur += c;
    }
  }
  out.push(cur);
  return out;
}

export function clearHistory() {
  write([]);
}

const CSV_COLS: (keyof BenchmarkRun)[] = [
  "id",
  "timestamp",
  "apiBase",
  "path",
  "totalRequests",
  "concurrency",
  "durationMs",
  "errors",
  "errorRatePct",
  "throughputRps",
  "p50Ms",
  "p95Ms",
  "p99Ms",
  "minMs",
  "maxMs",
  "meanMs",
];

export function runsToCsv(runs: BenchmarkRun[]): string {
  const esc = (v: unknown) => {
    const s = v == null ? "" : String(v);
    return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
  };
  const header = CSV_COLS.join(",");
  const rows = runs.map((r) => CSV_COLS.map((k) => esc(r[k])).join(","));
  return [header, ...rows].join("\n");
}

export function downloadRuns(runs: BenchmarkRun[], format: "json" | "csv") {
  if (typeof window === "undefined" || runs.length === 0) return;
  const isCsv = format === "csv";
  const body = isCsv ? runsToCsv(runs) : JSON.stringify(runs, null, 2);
  const blob = new Blob([body], {
    type: isCsv ? "text/csv;charset=utf-8" : "application/json",
  });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `leo-bench-history-${Date.now()}.${format}`;
  a.click();
  URL.revokeObjectURL(url);
}

// ---------- Import templates ----------
// Downloadable schema examples users can populate manually and re-import
// without hitting row-level validation errors.

export const TEMPLATE_ROW: BenchmarkRun = {
  id: "example-run-0001",
  timestamp: "2026-01-01T00:00:00.000Z",
  apiBase: "http://localhost:8005",
  path: "/api/v1/leo/metrics",
  totalRequests: 200,
  concurrency: 8,
  durationMs: 4200,
  errors: 0,
  errorRatePct: 0,
  throughputRps: 47.6,
  p50Ms: 18.2,
  p95Ms: 42.1,
  p99Ms: 61.3,
  minMs: 11.4,
  maxMs: 88.7,
  meanMs: 22.9,
};

export function downloadTemplate(format: "json" | "csv") {
  if (typeof window === "undefined") return;
  const body =
    format === "csv"
      ? runsToCsv([TEMPLATE_ROW])
      : JSON.stringify(
          {
            $schema: "leo-bench-history v1",
            note: "Every row needs `id` (string) and `throughputRps` (number). Timestamps are ISO-8601. All *Ms/*Rps/*Pct fields are numeric.",
            runs: [TEMPLATE_ROW],
          },
          null,
          2,
        );
  const blob = new Blob([body], {
    type: format === "csv" ? "text/csv;charset=utf-8" : "application/json",
  });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `leo-bench-template.${format}`;
  a.click();
  URL.revokeObjectURL(url);
}

export function useBenchmarkHistory(): BenchmarkRun[] {
  const [runs, setRuns] = useState<BenchmarkRun[]>([]);
  useEffect(() => {
    setRuns(read());
    const on = () => setRuns(read());
    window.addEventListener("leo:bench-history", on);
    window.addEventListener("storage", on);
    return () => {
      window.removeEventListener("leo:bench-history", on);
      window.removeEventListener("storage", on);
    };
  }, []);
  return runs;
}

// -------- Configurable NVIDIA reference figures --------

export type NvidiaRef = {
  label: string;
  fp16_tflops: number;
  mem_gb: number;
  mem_bw_gbs: number;
  tdp_w: number;
  ref_rps: number;
};

export const NVIDIA_PRESETS: Record<string, NvidiaRef> = {
  "h100-sxm": {
    label: "NVIDIA H100 SXM",
    fp16_tflops: 989,
    mem_gb: 80,
    mem_bw_gbs: 3350,
    tdp_w: 700,
    ref_rps: 1000,
  },
  "a100-80": {
    label: "NVIDIA A100 80GB",
    fp16_tflops: 312,
    mem_gb: 80,
    mem_bw_gbs: 2039,
    tdp_w: 400,
    ref_rps: 600,
  },
  l4: {
    label: "NVIDIA L4",
    fp16_tflops: 121,
    mem_gb: 24,
    mem_bw_gbs: 300,
    tdp_w: 72,
    ref_rps: 250,
  },
  "rtx-4090": {
    label: "NVIDIA RTX 4090",
    fp16_tflops: 330,
    mem_gb: 24,
    mem_bw_gbs: 1008,
    tdp_w: 450,
    ref_rps: 500,
  },
  t4: {
    label: "NVIDIA T4",
    fp16_tflops: 65,
    mem_gb: 16,
    mem_bw_gbs: 320,
    tdp_w: 70,
    ref_rps: 150,
  },
};

const REF_KEY = "leo.nvidia_ref";

export function useNvidiaRef(): [NvidiaRef, (r: NvidiaRef) => void, string, (id: string) => void] {
  const [preset, setPreset] = useState<string>("h100-sxm");
  const [ref, setRef] = useState<NvidiaRef>(NVIDIA_PRESETS["h100-sxm"]);
  useEffect(() => {
    if (typeof window === "undefined") return;
    try {
      const raw = window.localStorage.getItem(REF_KEY);
      if (raw) {
        const parsed = JSON.parse(raw) as { preset: string; ref: NvidiaRef };
        setPreset(parsed.preset);
        setRef(parsed.ref);
      }
    } catch {
      /* ignore */
    }
  }, []);
  function save(next: NvidiaRef, nextPreset = preset) {
    setRef(next);
    setPreset(nextPreset);
    try {
      window.localStorage.setItem(REF_KEY, JSON.stringify({ preset: nextPreset, ref: next }));
    } catch {
      /* ignore */
    }
  }
  return [
    ref,
    (r) => save(r, "custom"),
    preset,
    (id) => {
      if (id === "custom") save(ref, "custom");
      else save(NVIDIA_PRESETS[id] ?? ref, id);
    },
  ];
}
