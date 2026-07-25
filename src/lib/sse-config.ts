// Persisted SSE reconnect behavior (max attempts + backoff bounds).
// Read by BenchmarkRunner's live-metrics stream and configurable from Settings.
import { useEffect, useState } from "react";

export interface SseConfig {
  maxAttempts: number;
  initialBackoffMs: number;
  maxBackoffMs: number;
}

export const DEFAULT_SSE_CONFIG: SseConfig = {
  maxAttempts: 5,
  initialBackoffMs: 500,
  maxBackoffMs: 15000,
};

const KEY = "leo.sse.reconnect_v1";
const EVENT = "leo:sse-config-changed";

function clamp(n: number, lo: number, hi: number) {
  return Math.max(lo, Math.min(hi, n));
}

function sanitize(raw: Partial<SseConfig>): SseConfig {
  const cfg: SseConfig = { ...DEFAULT_SSE_CONFIG, ...raw };
  cfg.maxAttempts = clamp(Math.round(cfg.maxAttempts), 0, 50);
  cfg.initialBackoffMs = clamp(Math.round(cfg.initialBackoffMs), 100, 60_000);
  cfg.maxBackoffMs = clamp(Math.round(cfg.maxBackoffMs), cfg.initialBackoffMs, 300_000);
  return cfg;
}

export function getSseConfig(): SseConfig {
  if (typeof window === "undefined") return { ...DEFAULT_SSE_CONFIG };
  try {
    const raw = window.localStorage.getItem(KEY);
    if (!raw) return { ...DEFAULT_SSE_CONFIG };
    return sanitize(JSON.parse(raw));
  } catch {
    return { ...DEFAULT_SSE_CONFIG };
  }
}

export function setSseConfig(cfg: Partial<SseConfig>) {
  if (typeof window === "undefined") return;
  const next = sanitize({ ...getSseConfig(), ...cfg });
  window.localStorage.setItem(KEY, JSON.stringify(next));
  window.dispatchEvent(new CustomEvent(EVENT, { detail: next }));
}

export function useSseConfig(): [SseConfig, (cfg: Partial<SseConfig>) => void] {
  const [cfg, setCfg] = useState<SseConfig>(() => getSseConfig());
  useEffect(() => {
    const handler = () => setCfg(getSseConfig());
    window.addEventListener(EVENT, handler as EventListener);
    window.addEventListener("storage", handler);
    return () => {
      window.removeEventListener(EVENT, handler as EventListener);
      window.removeEventListener("storage", handler);
    };
  }, []);
  return [cfg, setSseConfig];
}
