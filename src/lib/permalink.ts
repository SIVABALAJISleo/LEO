// Encode/decode a shareable permalink for the /benchmarks debugging state:
// thresholds, health history, last CORS preflight, SSE reconnect settings,
// and the SSE diagnostics log. Uses base64url for URL safety.
import {
  getHealthHistory,
  getThresholds,
  setThresholds,
  importHealthEntries,
  DEFAULT_THRESHOLDS,
  type HealthThresholds,
} from "./health-history";
import { getSseConfig, setSseConfig, DEFAULT_SSE_CONFIG } from "./sse-config";
import { getSseLog, type SseLogEntry } from "./sse-log";

const CORS_RESULT_KEY = "leo.cors.last_result";
const SSE_LOG_KEY = "leo.sse.log_v1";

export interface PermalinkState {
  v: 1;
  generatedAt: string;
  thresholds: HealthThresholds;
  history: ReturnType<typeof getHealthHistory>;
  sseConfig: ReturnType<typeof getSseConfig>;
  sseLog: SseLogEntry[];
  corsResult: unknown;
}

function toB64Url(s: string): string {
  const b64 = typeof btoa !== "undefined" ? btoa(unescape(encodeURIComponent(s))) : "";
  return b64.replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}
function fromB64Url(s: string): string {
  const b64 = s.replace(/-/g, "+").replace(/_/g, "/") + "===".slice((s.length + 3) % 4);
  return typeof atob !== "undefined" ? decodeURIComponent(escape(atob(b64))) : "";
}

function readJson<T>(key: string): T | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = window.localStorage.getItem(key);
    return raw ? (JSON.parse(raw) as T) : null;
  } catch {
    return null;
  }
}

export function buildPermalinkState(): PermalinkState {
  return {
    v: 1,
    generatedAt: new Date().toISOString(),
    thresholds: getThresholds(),
    history: getHealthHistory(),
    sseConfig: getSseConfig(),
    sseLog: getSseLog(),
    corsResult: readJson(CORS_RESULT_KEY),
  };
}

export function encodePermalinkState(state: PermalinkState): string {
  return toB64Url(JSON.stringify(state));
}

export function decodePermalinkState(payload: string): PermalinkState | null {
  try {
    const obj = JSON.parse(fromB64Url(payload));
    if (!obj || obj.v !== 1) return null;
    return obj as PermalinkState;
  } catch {
    return null;
  }
}

export function buildPermalinkUrl(state: PermalinkState = buildPermalinkState()): string {
  if (typeof window === "undefined") return "";
  const u = new URL(window.location.href);
  u.searchParams.delete("state");
  u.searchParams.set("state", encodePermalinkState(state));
  return u.toString();
}

export interface RestoreSummary {
  thresholds: boolean;
  history: number;
  sseConfig: boolean;
  sseLog: number;
  corsResult: boolean;
}

/** Apply a decoded permalink to local storage. Replaces existing state. */
export function applyPermalinkState(state: PermalinkState): RestoreSummary {
  const summary: RestoreSummary = {
    thresholds: false,
    history: 0,
    sseConfig: false,
    sseLog: 0,
    corsResult: false,
  };

  if (state.thresholds && typeof state.thresholds === "object") {
    setThresholds({ ...DEFAULT_THRESHOLDS, ...state.thresholds });
    summary.thresholds = true;
  }
  if (Array.isArray(state.history)) {
    const rep = importHealthEntries(state.history, "replace");
    summary.history = rep.imported;
  }
  if (state.sseConfig && typeof state.sseConfig === "object") {
    setSseConfig({ ...DEFAULT_SSE_CONFIG, ...state.sseConfig });
    summary.sseConfig = true;
  }
  if (Array.isArray(state.sseLog) && typeof window !== "undefined") {
    try {
      window.localStorage.setItem(SSE_LOG_KEY, JSON.stringify(state.sseLog.slice(-200)));
      window.dispatchEvent(new CustomEvent("leo:sse-log-changed"));
      summary.sseLog = state.sseLog.length;
    } catch {
      /* ignore */
    }
  }
  if (state.corsResult && typeof window !== "undefined") {
    try {
      window.localStorage.setItem(CORS_RESULT_KEY, JSON.stringify(state.corsResult));
      summary.corsResult = true;
    } catch {
      /* ignore */
    }
  }
  return summary;
}

export function readPermalinkFromUrl(): PermalinkState | null {
  if (typeof window === "undefined") return null;
  const u = new URL(window.location.href);
  const p = u.searchParams.get("state");
  return p ? decodePermalinkState(p) : null;
}

export function clearPermalinkFromUrl() {
  if (typeof window === "undefined") return;
  const u = new URL(window.location.href);
  u.searchParams.delete("state");
  window.history.replaceState({}, "", u.toString());
}
