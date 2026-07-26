import { createFileRoute } from "@tanstack/react-router";
import { useState, useEffect } from "react";
import {
  getApiBase,
  setApiBase,
  getDebugMode,
  setDebugMode,
  type DebugMode,
} from "@/lib/leo-client";
import {
  isSyncEnabled,
  setSyncEnabled,
  getSyncPath,
  setSyncPath,
  pullAndMerge,
} from "@/lib/chat-history";
import {
  getTelemetryMode,
  setTelemetryMode,
  type TelemetryMode,
  getRetentionDays,
  setRetentionDays,
  type RetentionDays,
  clearTelemetryQueue,
} from "@/lib/telemetry-prefs";
import { pruneQueue } from "@/lib/web-vitals";
import { toast } from "sonner";
import { BackendSwitcher } from "@/components/BackendSwitcher";
import { BackendHealthPanel } from "@/components/BackendHealthPanel";
import { HealthDegradationSettings } from "@/components/HealthDegradationSettings";
import { SseReconnectSettings } from "@/components/SseReconnectSettings";

type SettingsSearch = { apiBase?: string };

export const Route = createFileRoute("/_authenticated/app/settings")({
  head: () => ({ meta: [{ title: "Settings — LEO AI" }] }),
  validateSearch: (search: Record<string, unknown>): SettingsSearch => ({
    apiBase: typeof search.apiBase === "string" ? search.apiBase : undefined,
  }),
  component: Page,
});

function Page() {
  const search = Route.useSearch();
  const [base, setBase] = useState("");
  const [debug, setDebug] = useState<DebugMode>("off");
  const [syncOn, setSyncOn] = useState(false);
  const [syncPath, setSyncPathState] = useState("");
  const [telemetry, setTelemetry] = useState<TelemetryMode>("full");
  const [retention, setRetention] = useState<RetentionDays>(30);

  useEffect(() => {
    setBase(search.apiBase ?? getApiBase());
    setDebug(getDebugMode());
    setSyncOn(isSyncEnabled());
    setSyncPathState(getSyncPath());
    setTelemetry(getTelemetryMode());
    setRetention(getRetentionDays());
    if (search.apiBase) {
      toast.message("Prefilled API base — review and save to apply");
    }
  }, [search.apiBase]);

  function saveBase() {
    setApiBase(base.trim() || "http://localhost:8000");
    toast.success("API base updated");
  }

  function saveDebug(mode: DebugMode) {
    setDebug(mode);
    setDebugMode(mode);
    toast.success(
      mode === "off"
        ? "Debug logging disabled"
        : `Debug logging: ${mode} — open the browser console`,
    );
  }

  async function toggleSync(on: boolean) {
    setSyncOn(on);
    setSyncEnabled(on);
    if (on) {
      toast.message("Syncing chat history with LEO backend…");
      try {
        const merged = await pullAndMerge();
        toast.success(`Chat sync enabled — ${merged.length} conversation(s) merged.`);
      } catch {
        toast.error("Sync enabled, but initial pull failed. Check backend URL.");
      }
    } else {
      toast.success("Chat sync disabled. History stays on this device only.");
    }
  }

  function saveSyncPath() {
    setSyncPath(syncPath.trim());
    toast.success("Chat sync path saved.");
  }

  function saveTelemetry(mode: TelemetryMode) {
    setTelemetry(mode);
    setTelemetryMode(mode);
    if (mode === "off") toast.success("Telemetry disabled. Nothing will be sent.");
    else if (mode === "errors-only") toast.success("Telemetry limited to runtime errors only.");
    else toast.success("Full telemetry enabled.");
  }

  function saveRetention(days: RetentionDays) {
    setRetention(days);
    setRetentionDays(days);
    const remaining = pruneQueue();
    if (days === 0) toast.success("Retention set to forever. Nothing will be auto-pruned.");
    else
      toast.success(
        `Retention set to ${days} days. ${remaining.length} event(s) remain buffered (errors always kept).`,
      );
  }

  function clearNow() {
    clearTelemetryQueue();
    toast.success("Buffered telemetry cleared. Future errors will still be reported.");
  }

  return (
    <div className="p-10 max-w-2xl">
      <p className="eyebrow">Configuration</p>
      <h1 className="mt-2 font-display text-4xl font-bold">Settings</h1>

      {/* Live connectivity + diagnostics */}
      <section className="mt-8">
        <p className="eyebrow">Connectivity</p>
        <div className="mt-4">
          <BackendHealthPanel />
        </div>
      </section>

      {/* API base */}
      <section className="mt-8">
        <label className="block">
          <span className="eyebrow">API base URL</span>
          <input
            value={base}
            onChange={(e) => setBase(e.target.value)}
            placeholder="http://localhost:8000"
            aria-label="LEO backend API base URL"
            className="mt-2 w-full bg-input px-3 py-3 font-mono text-sm outline-none focus:ring-1 focus:ring-leo"
          />
        </label>
        <p className="mt-2 text-xs text-muted-foreground">
          Point the console at any LEO deployment. Stored locally.
        </p>
        <button
          onClick={saveBase}
          className="mt-4 bg-leo px-5 py-3 text-sm font-semibold text-leo-foreground focus:outline-none focus-visible:ring-2 focus-visible:ring-white"
        >
          Save ›
        </button>
      </section>

      {/* One-click backend switcher */}
      <section className="mt-12 border-t border-border pt-8">
        <BackendSwitcher />
      </section>

      {/* Chat history sync */}
      <section className="mt-12 border-t border-border pt-8">
        <p className="eyebrow">Chat history</p>
        <h2 className="mt-2 font-display text-2xl font-bold">Sync across devices</h2>
        <p className="mt-2 text-sm text-muted-foreground">
          When enabled, conversation logs are pushed to and pulled from your LEO backend so they
          appear on every browser you sign into. When disabled, history stays on this device only.
        </p>
        <label className="mt-4 flex items-center gap-3 cursor-pointer">
          <input
            type="checkbox"
            checked={syncOn}
            onChange={(e) => toggleSync(e.target.checked)}
            className="h-4 w-4 accent-leo focus:outline-none focus-visible:ring-2 focus-visible:ring-leo"
            aria-label="Enable server-side chat history sync"
          />
          <span className="text-sm">
            <span className="font-semibold">Enable server sync</span>
            <span className="ml-2 text-muted-foreground">
              (POST/GET/DELETE against your backend)
            </span>
          </span>
        </label>
        <label className="mt-4 block">
          <span className="eyebrow">Sync endpoint path</span>
          <input
            value={syncPath}
            onChange={(e) => setSyncPathState(e.target.value)}
            placeholder="/api/v1/chat/sessions"
            aria-label="Chat sync endpoint path"
            disabled={!syncOn}
            className="mt-2 w-full bg-input px-3 py-3 font-mono text-sm outline-none focus:ring-1 focus:ring-leo disabled:opacity-50"
          />
        </label>
        <button
          onClick={saveSyncPath}
          disabled={!syncOn}
          className="mt-3 border border-border px-4 py-2 text-xs font-semibold hover:border-leo hover:text-leo disabled:opacity-40 focus:outline-none focus-visible:ring-2 focus-visible:ring-leo"
        >
          Save path
        </button>
        <p className="mt-3 text-xs text-muted-foreground">
          Backend contract: <code className="text-foreground">GET</code> returns{" "}
          <code className="text-foreground">{"{ sessions: ChatSession[] }"}</code>;{" "}
          <code className="text-foreground">POST</code> body{" "}
          <code className="text-foreground">{"{ session }"}</code> upserts;{" "}
          <code className="text-foreground">DELETE /:id</code> removes.
        </p>
      </section>

      {/* Telemetry opt-out */}
      <section className="mt-12 border-t border-border pt-8">
        <p className="eyebrow">Privacy</p>
        <h2 className="mt-2 font-display text-2xl font-bold">Telemetry</h2>
        <p className="mt-2 text-sm text-muted-foreground">
          LEO collects anonymous performance metrics (Web Vitals) and runtime error reports to catch
          regressions. Choose how much to share. Turning telemetry off also stops all offline
          buffering.
        </p>
        <fieldset className="mt-4 space-y-2" aria-label="Telemetry mode">
          {[
            {
              v: "full" as TelemetryMode,
              label: "Full",
              desc: "Web Vitals + runtime errors + unhandled rejections",
            },
            {
              v: "errors-only" as TelemetryMode,
              label: "Errors only",
              desc: "Skip performance metrics. Keep runtime errors so crashes stay reportable.",
            },
            {
              v: "off" as TelemetryMode,
              label: "Off",
              desc: "Nothing is sent. Nothing is buffered.",
            },
          ].map(({ v, label, desc }) => (
            <label
              key={v}
              className={`flex cursor-pointer items-start gap-3 border p-3 text-sm ${
                telemetry === v ? "border-leo bg-leo/5" : "border-border hover:border-leo"
              }`}
            >
              <input
                type="radio"
                name="telemetry"
                value={v}
                checked={telemetry === v}
                onChange={() => saveTelemetry(v)}
                className="mt-0.5 h-4 w-4 accent-leo"
              />
              <span>
                <span className="font-semibold">{label}</span>
                <span className="ml-1 text-muted-foreground">— {desc}</span>
              </span>
            </label>
          ))}
        </fieldset>

        <div className="mt-6 border-t border-border/60 pt-6">
          <p className="eyebrow">Data retention</p>
          <p className="mt-2 text-sm text-muted-foreground">
            How long buffered performance events stay on this device before being pruned. Runtime
            errors and unhandled rejections are always preserved regardless of this setting so
            crashes remain reportable.
          </p>
          <fieldset className="mt-4 flex flex-wrap gap-2" aria-label="Telemetry retention window">
            {[
              { v: 7 as RetentionDays, label: "7 days" },
              { v: 30 as RetentionDays, label: "30 days" },
              { v: 90 as RetentionDays, label: "90 days" },
              { v: 0 as RetentionDays, label: "Forever" },
            ].map(({ v, label }) => (
              <label
                key={v}
                className={`cursor-pointer border px-4 py-2 text-sm font-semibold ${
                  retention === v
                    ? "border-leo bg-leo/10 text-leo"
                    : "border-border hover:border-leo"
                }`}
              >
                <input
                  type="radio"
                  name="retention"
                  value={v}
                  checked={retention === v}
                  onChange={() => saveRetention(v)}
                  className="sr-only"
                />
                {label}
              </label>
            ))}
          </fieldset>
          <button
            type="button"
            onClick={clearNow}
            className="mt-4 border border-border px-4 py-2 text-xs font-semibold hover:border-destructive hover:text-destructive focus:outline-none focus-visible:ring-2 focus-visible:ring-leo"
            data-testid="telemetry-clear-now"
          >
            Clear buffered telemetry now
          </button>
        </div>
      </section>

      {/* Health degradation thresholds */}
      <section className="mt-12 border-t border-border pt-8">
        <p className="eyebrow">Monitoring</p>
        <h2 className="mt-2 font-display text-2xl font-bold">Health degradation alert</h2>
        <p className="mt-2 text-sm text-muted-foreground">
          Tune when the /benchmarks banner and toast raise a degradation warning.
        </p>
        <div className="mt-4">
          <HealthDegradationSettings />
        </div>
        <div className="mt-4">
          <SseReconnectSettings />
        </div>
      </section>

      {/* Debug logging */}
      <section className="mt-12 border-t border-border pt-8">
        <p className="eyebrow">Debug</p>
        <h2 className="mt-2 font-display text-2xl font-bold">Request logging</h2>
        <p className="mt-2 text-sm text-muted-foreground">
          Log every backend request in the browser console. Secrets (Authorization header,
          passwords, tokens) are automatically redacted.
        </p>
        <fieldset className="mt-4 flex flex-wrap gap-2" aria-label="Debug logging mode">
          {(["off", "basic", "verbose"] as DebugMode[]).map((m) => (
            <label
              key={m}
              className={`cursor-pointer border px-4 py-2 text-sm font-semibold ${
                debug === m ? "border-leo bg-leo/10 text-leo" : "border-border hover:border-leo"
              }`}
            >
              <input
                type="radio"
                name="debug"
                value={m}
                checked={debug === m}
                onChange={() => saveDebug(m)}
                className="sr-only"
              />
              {m === "off" ? "Off" : m === "basic" ? "Basic (headers)" : "Verbose (+ bodies)"}
            </label>
          ))}
        </fieldset>
      </section>
    </div>
  );
}
