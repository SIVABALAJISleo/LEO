import type { BenchmarkRun } from "./benchmark-history";

// Base64url helpers that work in browser + edge without Buffer.
function toB64Url(s: string): string {
  const b64 = typeof btoa !== "undefined" ? btoa(unescape(encodeURIComponent(s))) : "";
  return b64.replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}
function fromB64Url(s: string): string {
  const b64 = s.replace(/-/g, "+").replace(/_/g, "/") + "===".slice((s.length + 3) % 4);
  return typeof atob !== "undefined" ? decodeURIComponent(escape(atob(b64))) : "";
}

export function encodeRunShare(run: BenchmarkRun): string {
  return toB64Url(JSON.stringify(run));
}

export function encodeComparisonShare(base: BenchmarkRun, target: BenchmarkRun): string {
  return toB64Url(JSON.stringify({ b: base, t: target }));
}

export function decodeRunShare(payload: string): BenchmarkRun | null {
  try {
    return JSON.parse(fromB64Url(payload)) as BenchmarkRun;
  } catch {
    return null;
  }
}
export function decodeComparisonShare(
  payload: string,
): { base: BenchmarkRun; target: BenchmarkRun } | null {
  try {
    const p = JSON.parse(fromB64Url(payload)) as { b: BenchmarkRun; t: BenchmarkRun };
    return { base: p.b, target: p.t };
  } catch {
    return null;
  }
}

export function buildShareUrl(kind: "run" | "compare", payload: string): string {
  if (typeof window === "undefined") return "";
  const u = new URL(window.location.href);
  u.searchParams.delete("run");
  u.searchParams.delete("compare");
  u.searchParams.set(kind, payload);
  return u.toString();
}

export function readShareParams(): {
  run: BenchmarkRun | null;
  compare: { base: BenchmarkRun; target: BenchmarkRun } | null;
} {
  if (typeof window === "undefined") return { run: null, compare: null };
  const u = new URL(window.location.href);
  const runP = u.searchParams.get("run");
  const cmpP = u.searchParams.get("compare");
  return {
    run: runP ? decodeRunShare(runP) : null,
    compare: cmpP ? decodeComparisonShare(cmpP) : null,
  };
}
