// Persistent ring buffer of SSE lifecycle events (open, error, reconnect
// attempt with computed backoff, polling fallback, recovery). Powers the
// SSE diagnostics log panel on /benchmarks. Independent of the single
// "current status" snapshot at leo.bench.sse-diag.
import { useEffect, useState } from "react";

export type SseLogKind =
  | "connect"
  | "open"
  | "error"
  | "reconnect"
  | "polling-start"
  | "polling-recover"
  | "closed"
  | "info";

export interface SseLogEntry {
  id: number;
  at: number;
  kind: SseLogKind;
  message: string;
  attempt?: number;
  backoffMs?: number;
  transport?: "sse" | "polling";
  readyState?: number | null;
}

const KEY = "leo.sse.log_v1";
const EVENT = "leo:sse-log-changed";
const MAX = 200;

function load(): SseLogEntry[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = window.localStorage.getItem(KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed.slice(-MAX) : [];
  } catch {
    return [];
  }
}

let buffer: SseLogEntry[] = load();
let nextId = buffer.reduce((m, e) => Math.max(m, e.id), 0) + 1;

function persist() {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(KEY, JSON.stringify(buffer));
    window.dispatchEvent(new CustomEvent(EVENT));
  } catch {
    /* ignore */
  }
}

export function pushSseLog(entry: Omit<SseLogEntry, "id" | "at"> & { at?: number }) {
  buffer = [...buffer, { id: nextId++, at: entry.at ?? Date.now(), ...entry }].slice(-MAX);
  persist();
}

export function getSseLog(): SseLogEntry[] {
  return buffer.slice();
}

export function clearSseLog() {
  buffer = [];
  persist();
}

export function useSseLog(): SseLogEntry[] {
  const [list, setList] = useState<SseLogEntry[]>(() => buffer.slice());
  useEffect(() => {
    const on = () => setList(buffer.slice());
    window.addEventListener(EVENT, on);
    window.addEventListener("storage", on);
    return () => {
      window.removeEventListener(EVENT, on);
      window.removeEventListener("storage", on);
    };
  }, []);
  return list;
}
