// One-click switcher between backend URL presets (local / tunnel / deployed).
import { getApiBase, setApiBase } from "./leo-client";

export type PresetKind = "local" | "tunnel" | "deployed" | "custom";

export interface BackendPreset {
  kind: PresetKind;
  label: string;
  url: string;
  hint: string;
}

const KEY = "leo.api_base_presets";
const ACTIVE_KEY = "leo.api_base_preset_active";

export const DEFAULT_PRESETS: BackendPreset[] = [
  {
    kind: "local",
    label: "Local",
    url: "http://localhost:8005",
    hint: "Python backend running on your machine (dev only).",
  },
  {
    kind: "tunnel",
    label: "Tunnel",
    url: "",
    hint: "Public ngrok / Cloudflare Tunnel URL exposing your laptop backend.",
  },
  {
    kind: "deployed",
    label: "Deployed",
    url: "",
    hint: "Production LEO backend (e.g. https://api.yourdomain.com).",
  },
];

export function getPresets(): BackendPreset[] {
  if (typeof window === "undefined") return DEFAULT_PRESETS;
  try {
    const raw = window.localStorage.getItem(KEY);
    if (!raw) return DEFAULT_PRESETS;
    const parsed = JSON.parse(raw) as BackendPreset[];
    return DEFAULT_PRESETS.map((d) => parsed.find((p) => p.kind === d.kind) ?? d);
  } catch {
    return DEFAULT_PRESETS;
  }
}

export function savePresets(list: BackendPreset[]) {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(KEY, JSON.stringify(list));
}

export function getActivePresetKind(): PresetKind {
  if (typeof window === "undefined") return "local";
  return (window.localStorage.getItem(ACTIVE_KEY) as PresetKind) || detectKind(getApiBase());
}

export function activatePreset(kind: PresetKind) {
  const preset = getPresets().find((p) => p.kind === kind);
  if (!preset || !preset.url) throw new Error(`No URL configured for ${kind}`);
  setApiBase(preset.url);
  if (typeof window !== "undefined") {
    window.localStorage.setItem(ACTIVE_KEY, kind);
    window.dispatchEvent(new CustomEvent("leo:api-base-changed", { detail: preset.url }));
  }
}

export function updatePresetUrl(kind: PresetKind, url: string) {
  const list = getPresets().map((p) => (p.kind === kind ? { ...p, url } : p));
  savePresets(list);
}

function detectKind(url: string): PresetKind {
  if (/localhost|127\.0\.0\.1/.test(url)) return "local";
  if (/\.ngrok|\.trycloudflare\.com|\.loca\.lt/.test(url)) return "tunnel";
  if (/^https?:\/\//.test(url)) return "deployed";
  return "custom";
}
