// Persisted configuration for the burst health-check button. Lets users
// choose count, inter-request interval, and endpoint path so they can
// reproduce failure modes precisely without redeploying.
import { useEffect, useState } from "react";

export interface BurstConfig {
  count: number;
  intervalMs: number;
  path: string;
}

export const DEFAULT_BURST_CONFIG: BurstConfig = {
  count: 5,
  intervalMs: 400,
  path: "/health",
};

const KEY = "leo.burst.config_v1";
const LAST_KEY = "leo.burst.last_run_v1";
const EVENT = "leo:burst-config-changed";
const LAST_EVENT = "leo:burst-last-run-changed";

function clamp(n: number, lo: number, hi: number) {
  return Math.max(lo, Math.min(hi, Math.round(n)));
}

function sanitize(raw: Partial<BurstConfig>): BurstConfig {
  const c = { ...DEFAULT_BURST_CONFIG, ...raw };
  c.count = clamp(c.count, 1, 100);
  c.intervalMs = clamp(c.intervalMs, 0, 60_000);
  c.path = typeof c.path === "string" && c.path.trim() ? c.path.trim() : DEFAULT_BURST_CONFIG.path;
  if (!c.path.startsWith("/")) c.path = "/" + c.path;
  return c;
}

export function getBurstConfig(): BurstConfig {
  if (typeof window === "undefined") return { ...DEFAULT_BURST_CONFIG };
  try {
    const raw = window.localStorage.getItem(KEY);
    if (!raw) return { ...DEFAULT_BURST_CONFIG };
    return sanitize(JSON.parse(raw));
  } catch {
    return { ...DEFAULT_BURST_CONFIG };
  }
}

export function setBurstConfig(cfg: Partial<BurstConfig>) {
  if (typeof window === "undefined") return;
  const next = sanitize({ ...getBurstConfig(), ...cfg });
  window.localStorage.setItem(KEY, JSON.stringify(next));
  window.dispatchEvent(new CustomEvent(EVENT, { detail: next }));
}

export function useBurstConfig(): [BurstConfig, (cfg: Partial<BurstConfig>) => void] {
  const [cfg, setCfg] = useState<BurstConfig>(() => getBurstConfig());
  useEffect(() => {
    const on = () => setCfg(getBurstConfig());
    window.addEventListener(EVENT, on as EventListener);
    window.addEventListener("storage", on);
    return () => {
      window.removeEventListener(EVENT, on as EventListener);
      window.removeEventListener("storage", on);
    };
  }, []);
  return [cfg, setBurstConfig];
}

export function getLastRunBurstConfig(): BurstConfig | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = window.localStorage.getItem(LAST_KEY);
    if (!raw) return null;
    return sanitize(JSON.parse(raw));
  } catch {
    return null;
  }
}

export function recordLastRunBurstConfig(cfg: BurstConfig) {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(LAST_KEY, JSON.stringify(sanitize(cfg)));
    window.dispatchEvent(new CustomEvent(LAST_EVENT, { detail: cfg }));
  } catch {
    /* ignore */
  }
}

export function useLastRunBurstConfig(): BurstConfig | null {
  const [cfg, setCfg] = useState<BurstConfig | null>(() => getLastRunBurstConfig());
  useEffect(() => {
    const on = () => setCfg(getLastRunBurstConfig());
    window.addEventListener(LAST_EVENT, on as EventListener);
    window.addEventListener("storage", on);
    return () => {
      window.removeEventListener(LAST_EVENT, on as EventListener);
      window.removeEventListener("storage", on);
    };
  }, []);
  return cfg;
}
