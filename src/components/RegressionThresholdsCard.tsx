import { useRegressionThresholds, DEFAULT_THRESHOLDS } from "@/lib/regression-thresholds";

export function RegressionThresholdsCard() {
  const [t, setT] = useRegressionThresholds();

  return (
    <section aria-labelledby="thresholds-title" className="border border-border bg-background p-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="eyebrow">Alerts</p>
          <h2 id="thresholds-title" className="mt-1 font-display text-2xl font-bold">
            Regression thresholds
          </h2>
          <p className="mt-1 text-xs text-muted-foreground">
            When a comparison exceeds these tolerances vs. the baseline, the UI surfaces an inline
            banner and a toast.
          </p>
        </div>
        <label className="inline-flex items-center gap-2 text-xs">
          <input
            type="checkbox"
            checked={t.enabled}
            onChange={(e) => setT({ ...t, enabled: e.target.checked })}
            className="h-4 w-4 accent-[#76B900]"
          />
          <span className="uppercase tracking-wide">{t.enabled ? "Enabled" : "Disabled"}</span>
        </label>
      </div>

      <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        <Field
          label="p50 increase %"
          value={t.p50PctIncrease}
          onChange={(v) => setT({ ...t, p50PctIncrease: v })}
        />
        <Field
          label="p95 increase %"
          value={t.p95PctIncrease}
          onChange={(v) => setT({ ...t, p95PctIncrease: v })}
        />
        <Field
          label="p99 increase %"
          value={t.p99PctIncrease}
          onChange={(v) => setT({ ...t, p99PctIncrease: v })}
        />
        <Field
          label="throughput drop %"
          value={t.throughputPctDrop}
          onChange={(v) => setT({ ...t, throughputPctDrop: v })}
        />
        <Field
          label="error rate abs %"
          value={t.errorRateAbsPct}
          onChange={(v) => setT({ ...t, errorRateAbsPct: v })}
          step={0.1}
        />
      </div>

      <button
        type="button"
        onClick={() => setT(DEFAULT_THRESHOLDS)}
        className="mt-4 border border-border px-3 py-1.5 text-xs hover:border-leo hover:text-leo focus:outline-none focus-visible:ring-2 focus-visible:ring-leo"
      >
        Reset defaults
      </button>
    </section>
  );
}

function Field({
  label,
  value,
  onChange,
  step = 1,
}: {
  label: string;
  value: number;
  onChange: (v: number) => void;
  step?: number;
}) {
  return (
    <label className="flex flex-col gap-1 text-xs">
      <span className="uppercase tracking-wide text-muted-foreground">{label}</span>
      <input
        type="number"
        min={0}
        step={step}
        value={value}
        onChange={(e) => onChange(Math.max(0, Number(e.target.value) || 0))}
        className="border border-border bg-background px-2 py-1 font-mono text-xs focus:border-leo focus:outline-none"
      />
    </label>
  );
}
