import { useEffect, useState } from "react";
import { toast } from "sonner";
import {
  activatePreset,
  getActivePresetKind,
  getPresets,
  updatePresetUrl,
  type BackendPreset,
  type PresetKind,
} from "@/lib/backend-presets";
import { checkBackendHealth } from "@/lib/backend-health";

export function BackendSwitcher() {
  const [presets, setPresets] = useState<BackendPreset[]>([]);
  const [active, setActive] = useState<PresetKind>("local");

  useEffect(() => {
    setPresets(getPresets());
    setActive(getActivePresetKind());
  }, []);

  async function switchTo(kind: PresetKind) {
    const p = presets.find((x) => x.kind === kind);
    if (!p?.url) {
      toast.error(`No URL saved for "${kind}". Paste one below first.`);
      return;
    }
    try {
      activatePreset(kind);
      setActive(kind);
      toast.message(`Switched to ${kind} — pinging ${p.url}…`);
      const h = await checkBackendHealth(p.url);
      if (h.status === "online") {
        toast.success(`${kind} backend online (${h.latencyMs}ms)`);
      } else {
        toast.error(`${kind} backend ${h.status}: ${h.message ?? h.httpStatus ?? ""}`);
      }
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Failed to switch");
    }
  }

  function updateUrl(kind: PresetKind, url: string) {
    updatePresetUrl(kind, url);
    setPresets(getPresets());
  }

  return (
    <div>
      <p className="eyebrow">Backend switcher</p>
      <h2 className="mt-2 font-display text-2xl font-bold">One-click environment</h2>
      <p className="mt-2 text-sm text-muted-foreground">
        Swap between your local laptop backend, a public tunnel (ngrok / Cloudflare), or a deployed
        production URL. Health is verified after each switch.
      </p>

      <div className="mt-4 grid gap-3 sm:grid-cols-3" role="radiogroup" aria-label="Backend preset">
        {presets.map((p) => (
          <button
            key={p.kind}
            type="button"
            role="radio"
            aria-checked={active === p.kind}
            onClick={() => switchTo(p.kind)}
            className={`border p-4 text-left focus:outline-none focus-visible:ring-2 focus-visible:ring-leo ${
              active === p.kind ? "border-leo bg-leo/10" : "border-border hover:border-leo"
            }`}
          >
            <div className="flex items-center justify-between">
              <span className="font-display text-lg font-bold">{p.label}</span>
              {active === p.kind && (
                <span className="text-[10px] font-bold uppercase tracking-wider text-leo">
                  Active
                </span>
              )}
            </div>
            <p className="mt-1 text-xs text-muted-foreground">{p.hint}</p>
            <code className="mt-2 block truncate font-mono text-[11px] text-foreground/80">
              {p.url || "— not set —"}
            </code>
          </button>
        ))}
      </div>

      <div className="mt-6 space-y-3">
        {presets.map((p) => (
          <label key={p.kind} className="block">
            <span className="eyebrow">{p.label} URL</span>
            <input
              value={p.url}
              onChange={(e) => updateUrl(p.kind, e.target.value)}
              placeholder={
                p.kind === "local"
                  ? "http://localhost:8005"
                  : p.kind === "tunnel"
                    ? "https://xxxx.ngrok-free.app"
                    : "https://api.yourdomain.com"
              }
              className="mt-1 w-full bg-input px-3 py-2 font-mono text-sm outline-none focus:ring-1 focus:ring-leo"
              aria-label={`${p.label} backend URL`}
            />
          </label>
        ))}
      </div>

      <details className="mt-6 border border-border p-4 text-sm">
        <summary className="cursor-pointer font-semibold">
          Tunnel setup (expose your laptop backend to the preview)
        </summary>
        <div className="mt-3 space-y-3 text-muted-foreground">
          <div>
            <p className="font-semibold text-foreground">
              Option A — Cloudflare Tunnel (free, no signup)
            </p>
            <pre className="mt-1 overflow-x-auto bg-input p-3 font-mono text-xs">{`# 1. Install
brew install cloudflared        # macOS
winget install --id Cloudflare.cloudflared   # Windows

# 2. Start your Python backend on 8005, then:
cloudflared tunnel --url http://localhost:8005

# 3. Copy the https://<random>.trycloudflare.com URL
#    into the "Tunnel" field above and click Tunnel.`}</pre>
          </div>
          <div>
            <p className="font-semibold text-foreground">Option B — ngrok</p>
            <pre className="mt-1 overflow-x-auto bg-input p-3 font-mono text-xs">{`# 1. Install & auth
brew install ngrok/ngrok/ngrok
ngrok config add-authtoken <YOUR_TOKEN>

# 2. Start tunnel
ngrok http 8005

# 3. Paste the https://xxxx.ngrok-free.app URL
#    into the "Tunnel" field above.`}</pre>
          </div>
          <p className="text-xs">
            Make sure your Python backend enables CORS for the frontend origin (Lovable preview or
            your deployed domain).
          </p>
        </div>
      </details>
    </div>
  );
}
