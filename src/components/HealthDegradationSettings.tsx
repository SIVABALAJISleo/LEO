// Settings panel for the health-degradation alert. Controls consecutive
// failure count, per-sample latency warning, and avg-latency warning.
// Values persist through useThresholds() -> localStorage.
import { useThresholds, DEFAULT_THRESHOLDS } from "@/lib/health-history";
import { toast } from "sonner";

export function HealthDegradationSettings() {
  const [t, setT] = useThresholds();

  function reset() {
    setT(DEFAULT_THRESHOLDS);
    toast.success("Thresholds reset to defaults");
  }

  return (
    <div className="border border-border p-4">
      <p className="eyebrow">Health degradation thresholds</p>
      <p className="mt-1 text-xs text-muted-foreground">
        Trigger the degradation alert when any of these limits are exceeded. Persisted per browser.
      </p>

      <div className="mt-4 grid gap-3 text-xs sm:grid-cols-2">
        <NumField
          label="Consecutive failures"
          value={t.consecutiveFailLimit}
          min={1}
          max={30}
          onChange={(v) => setT({ ...t, consecutiveFailLimit: v })}
        />
        <NumField
          label="Single-sample latency warn (ms)"
          value={t.latencyWarnMs}
          min={50}
          max={30000}
          step={50}
          onChange={(v) => setT({ ...t, latencyWarnMs: v })}
        />
        <NumField
          label="Avg latency warn (ms)"
          value={t.avgLatencyWarnMs}
          min={50}
          max={30000}
          step={50}
          onChange={(v) => setT({ ...t, avgLatencyWarnMs: v })}
        />
        <NumField
          label="Failure rate % (over window)"
          value={t.failureRatePct}
          min={1}
          max={100}
          onChange={(v) => setT({ ...t, failureRatePct: v })}
        />
        <NumField
          label="Window size (samples)"
          value={t.windowSize}
          min={2}
          max={60}
          onChange={(v) => setT({ ...t, windowSize: v })}
        />
        <NumField
          label="Timeout (ms)"
          value={t.timeoutMs}
          min={500}
          max={60000}
          step={500}
          onChange={(v) => setT({ ...t, timeoutMs: v })}
        />
      </div>

      <button
        type="button"
        onClick={reset}
        className="mt-4 border border-border px-3 py-1.5 text-xs font-semibold hover:border-leo hover:text-leo focus:outline-none focus-visible:ring-2 focus-visible:ring-leo"
      >
        Reset to defaults
      </button>
    </div>
  );
}

function NumField({
  label,
  value,
  onChange,
  min,
  max,
  step = 1,
}: {
  label: string;
  value: number;
  onChange: (v: number) => void;
  min: number;
  max: number;
  step?: number;
}) {
  return (
    <label className="flex flex-col gap-1">
      <span className="text-muted-foreground">{label}</span>
      <input
        type="number"
        value={value}
        min={min}
        max={max}
        step={step}
        onChange={(e) => {
          const n = Number(e.target.value);
          if (Number.isFinite(n)) onChange(Math.max(min, Math.min(max, n)));
        }}
        className="border border-border bg-background px-2 py-1 font-mono focus:border-leo focus:outline-none"
      />
    </label>
  );
}
