// Settings controls for SSE reconnect behavior. Persists via useSseConfig.
import { useSseConfig, DEFAULT_SSE_CONFIG } from "@/lib/sse-config";
import { toast } from "sonner";

export function SseReconnectSettings() {
  const [cfg, setCfg] = useSseConfig();

  return (
    <div className="border border-border p-4">
      <p className="eyebrow">SSE reconnect behavior</p>
      <p className="mt-1 text-xs text-muted-foreground">
        Controls the live-metrics stream retry loop on /benchmarks.
      </p>
      <div className="mt-4 grid gap-3 text-xs sm:grid-cols-3">
        <Field
          label="Max attempts"
          hint="After this many retries the stream falls back to polling."
          min={0}
          max={50}
          step={1}
          value={cfg.maxAttempts}
          onChange={(v) => setCfg({ maxAttempts: v })}
        />
        <Field
          label="Initial backoff (ms)"
          hint="Delay before the first retry; doubles each attempt."
          min={100}
          max={60000}
          step={100}
          value={cfg.initialBackoffMs}
          onChange={(v) => setCfg({ initialBackoffMs: v })}
        />
        <Field
          label="Max backoff (ms)"
          hint="Upper cap on exponential backoff between retries."
          min={cfg.initialBackoffMs}
          max={300000}
          step={500}
          value={cfg.maxBackoffMs}
          onChange={(v) => setCfg({ maxBackoffMs: v })}
        />
      </div>
      <div className="mt-4 flex flex-wrap gap-2">
        <button
          type="button"
          onClick={() => {
            setCfg({ ...DEFAULT_SSE_CONFIG });
            toast.success("SSE reconnect reset to defaults");
          }}
          className="border border-border px-3 py-1.5 text-xs font-semibold hover:border-leo hover:text-leo focus:outline-none focus-visible:ring-2 focus-visible:ring-leo"
        >
          Reset to defaults
        </button>
      </div>
    </div>
  );
}

function Field({
  label,
  hint,
  min,
  max,
  step,
  value,
  onChange,
}: {
  label: string;
  hint: string;
  min: number;
  max: number;
  step: number;
  value: number;
  onChange: (v: number) => void;
}) {
  return (
    <label className="flex flex-col gap-1">
      <span className="text-muted-foreground">{label}</span>
      <input
        type="number"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => {
          const v = Number(e.target.value);
          if (Number.isFinite(v)) onChange(v);
        }}
        className="border border-border bg-background px-2 py-1 font-mono focus:border-leo focus:outline-none"
      />
      <span className="text-[10px] text-muted-foreground">{hint}</span>
    </label>
  );
}
