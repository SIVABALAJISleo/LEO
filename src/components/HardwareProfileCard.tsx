import { useEffect, useState } from "react";
import { NVIDIA_PRESETS, useNvidiaRef, type BenchmarkRun } from "@/lib/benchmark-history";

type HwProfile = {
  laptop: string;
  cpu: string;
  cores: number;
  threads: number;
  ram_gb: number;
  igpu: string;
  igpu_tflops_fp16: number;
  storage: string;
  tdp_w: number;
};

const DEFAULT_PROFILE: HwProfile = {
  laptop: "Lenovo IdeaPad Slim 3 15IAH8",
  cpu: "Intel Core i5-12450H (12th Gen)",
  cores: 8,
  threads: 12,
  ram_gb: 16,
  igpu: "Intel UHD Graphics (Alder Lake)",
  igpu_tflops_fp16: 0.4,
  storage: "512 GB NVMe SSD",
  tdp_w: 45,
};

const STORAGE_KEY = "leo.hw_profile";

export function HardwareProfileCard({
  liveRps,
  avoidanceRatePct,
  wattsSaved,
  selectedRun,
}: {
  liveRps?: number;
  avoidanceRatePct?: number;
  wattsSaved?: number;
  selectedRun?: BenchmarkRun | null;
}) {
  const [p, setP] = useState<HwProfile>(DEFAULT_PROFILE);
  const [editing, setEditing] = useState(false);
  const [showMath, setShowMath] = useState(true);
  const [ref, setRef, presetId, setPresetId] = useNvidiaRef();

  useEffect(() => {
    if (typeof window === "undefined") return;
    try {
      const raw = window.localStorage.getItem(STORAGE_KEY);
      if (raw) setP({ ...DEFAULT_PROFILE, ...JSON.parse(raw) });
    } catch {
      /* ignore */
    }
  }, []);

  function save(next: HwProfile) {
    setP(next);
    try {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
    } catch {
      /* ignore */
    }
  }

  // Use the selected benchmark run's throughput if provided, else fall back
  // to live polling rps. This links the ratio to a specific measurement.
  const effRpsSource = selectedRun
    ? {
        rps: selectedRun.throughputRps,
        label: `benchmark @ ${new Date(selectedRun.timestamp).toLocaleTimeString()}`,
      }
    : liveRps != null
      ? { rps: liveRps, label: "last run rps" }
      : null;

  const tflopsRatioPct = (p.igpu_tflops_fp16 / ref.fp16_tflops) * 100;
  const memRatioPct = (p.ram_gb / ref.mem_gb) * 100;
  const tdpRatioPct = (p.tdp_w / ref.tdp_w) * 100;
  const avoidance = avoidanceRatePct ?? 0;
  const effRps = effRpsSource ? effRpsSource.rps * (1 + avoidance / 100) : undefined;
  const throughputRatioPct = effRps ? (effRps / ref.ref_rps) * 100 : undefined;

  return (
    <section aria-labelledby="hw-profile-title" className="border border-border bg-background p-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="eyebrow">Hardware profile</p>
          <h2 id="hw-profile-title" className="mt-1 font-display text-2xl font-bold">
            {p.laptop}
          </h2>
          <p className="mt-1 text-xs text-muted-foreground">
            Compared against <span className="font-mono text-leo">{ref.label}</span>
          </p>
        </div>
        <div className="flex gap-2">
          <button
            type="button"
            onClick={() => setShowMath((v) => !v)}
            className="border border-border px-3 py-1.5 text-xs hover:border-leo hover:text-leo focus:outline-none focus-visible:ring-2 focus-visible:ring-leo"
          >
            {showMath ? "Hide math" : "Show math"}
          </button>
          <button
            type="button"
            onClick={() => setEditing((v) => !v)}
            className="border border-border px-3 py-1.5 text-xs hover:border-leo hover:text-leo focus:outline-none focus-visible:ring-2 focus-visible:ring-leo"
          >
            {editing ? "Done" : "Edit"}
          </button>
        </div>
      </div>

      {/* Reference figure picker */}
      <div className="mt-4 border border-border/60 bg-muted/20 p-4">
        <div className="flex items-center justify-between gap-3">
          <p className="text-[11px] uppercase tracking-wide text-muted-foreground">
            Reference NVIDIA figure
          </p>
          <select
            value={presetId}
            onChange={(e) => setPresetId(e.target.value)}
            className="border border-border bg-background px-2 py-1 font-mono text-xs focus:border-leo focus:outline-none"
            aria-label="NVIDIA reference preset"
          >
            {Object.entries(NVIDIA_PRESETS).map(([id, r]) => (
              <option key={id} value={id}>
                {r.label}
              </option>
            ))}
            <option value="custom">Custom</option>
          </select>
        </div>
        {editing && (
          <div className="mt-3 grid gap-2 text-xs sm:grid-cols-2 lg:grid-cols-3">
            <RefField
              label="Label"
              value={ref.label}
              onChange={(v) => setRef({ ...ref, label: v })}
            />
            <RefNum
              label="FP16 TFLOPS"
              value={ref.fp16_tflops}
              onChange={(v) => setRef({ ...ref, fp16_tflops: v })}
            />
            <RefNum
              label="Memory (GB)"
              value={ref.mem_gb}
              onChange={(v) => setRef({ ...ref, mem_gb: v })}
            />
            <RefNum
              label="Mem BW (GB/s)"
              value={ref.mem_bw_gbs}
              onChange={(v) => setRef({ ...ref, mem_bw_gbs: v })}
            />
            <RefNum
              label="TDP (W)"
              value={ref.tdp_w}
              onChange={(v) => setRef({ ...ref, tdp_w: v })}
            />
            <RefNum
              label="Reference RPS"
              value={ref.ref_rps}
              onChange={(v) => setRef({ ...ref, ref_rps: v })}
            />
          </div>
        )}
      </div>

      {editing && (
        <div className="mt-4 grid gap-3 border border-border/60 bg-muted/20 p-4 text-xs sm:grid-cols-2">
          <RefField label="Laptop" value={p.laptop} onChange={(v) => save({ ...p, laptop: v })} />
          <RefField label="CPU" value={p.cpu} onChange={(v) => save({ ...p, cpu: v })} />
          <RefNum label="Cores" value={p.cores} onChange={(v) => save({ ...p, cores: v })} />
          <RefNum label="Threads" value={p.threads} onChange={(v) => save({ ...p, threads: v })} />
          <RefNum label="RAM (GB)" value={p.ram_gb} onChange={(v) => save({ ...p, ram_gb: v })} />
          <RefField label="iGPU" value={p.igpu} onChange={(v) => save({ ...p, igpu: v })} />
          <RefNum
            label="iGPU FP16 TFLOPS"
            value={p.igpu_tflops_fp16}
            step={0.1}
            onChange={(v) => save({ ...p, igpu_tflops_fp16: v })}
          />
          <RefField
            label="Storage"
            value={p.storage}
            onChange={(v) => save({ ...p, storage: v })}
          />
          <RefNum label="TDP (W)" value={p.tdp_w} onChange={(v) => save({ ...p, tdp_w: v })} />
        </div>
      )}

      <dl className="mt-6 grid gap-px bg-border sm:grid-cols-2 lg:grid-cols-3">
        <Spec label="CPU / cores" value={`${p.cpu} · ${p.cores}C/${p.threads}T`} />
        <Spec label="RAM" value={`${p.ram_gb} GB`} />
        <Spec label="iGPU" value={p.igpu} />
        <Spec label="Storage" value={p.storage} />
        <Spec label="TDP" value={`${p.tdp_w} W`} />
        <Spec label="iGPU FP16" value={`${p.igpu_tflops_fp16.toFixed(2)} TFLOPS`} />
      </dl>

      <div className="mt-6">
        <p className="eyebrow">Documented ratio vs reference</p>
        <div className="mt-3 grid gap-px bg-border sm:grid-cols-2 lg:grid-cols-4">
          <Ratio
            label="FP16 compute"
            pct={tflopsRatioPct}
            formula={`${p.igpu_tflops_fp16} ÷ ${ref.fp16_tflops} × 100`}
            showMath={showMath}
          />
          <Ratio
            label="Memory"
            pct={memRatioPct}
            formula={`${p.ram_gb} ÷ ${ref.mem_gb} × 100`}
            showMath={showMath}
          />
          <Ratio
            label="Power draw"
            pct={tdpRatioPct}
            formula={`${p.tdp_w} ÷ ${ref.tdp_w} × 100`}
            invert
            showMath={showMath}
          />
          <Ratio
            label="Effective RPS*"
            pct={throughputRatioPct}
            formula={
              effRpsSource
                ? `${effRpsSource.rps.toFixed(2)} × (1 + ${avoidance.toFixed(1)}/100) ÷ ${ref.ref_rps} × 100`
                : "Run a benchmark"
            }
            showMath={showMath}
          />
        </div>
        <p className="mt-3 text-[11px] text-muted-foreground">
          * Effective RPS = measured rps × (1 + avoidance rate). Source:{" "}
          <span className="font-mono">{effRpsSource?.label ?? "n/a"}</span>. Reference RPS is a
          configurable nominal baseline — edit above to match your target hardware's real serving
          rate.
        </p>
        {wattsSaved != null && (
          <p className="mt-1 text-[11px] text-muted-foreground">
            Live watts saved by avoidance:{" "}
            <span className="text-leo">{wattsSaved.toLocaleString()} W</span>
          </p>
        )}
      </div>
    </section>
  );
}

function Spec({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-background p-4">
      <dt className="text-[11px] uppercase tracking-wide text-muted-foreground">{label}</dt>
      <dd className="mt-1 truncate font-mono text-sm">{value}</dd>
    </div>
  );
}

function Ratio({
  label,
  pct,
  formula,
  invert,
  showMath,
}: {
  label: string;
  pct?: number;
  formula: string;
  invert?: boolean;
  showMath: boolean;
}) {
  const display = pct == null ? "—" : `${pct < 0.1 ? pct.toFixed(3) : pct.toFixed(2)}%`;
  const good = pct != null && (invert ? pct < 100 : pct > 5);
  return (
    <div className="bg-background p-4">
      <div className="text-[11px] uppercase tracking-wide text-muted-foreground">{label}</div>
      <div
        className={`mt-1 font-display text-2xl font-bold ${good ? "text-leo" : "text-foreground"}`}
      >
        {display}
      </div>
      {showMath && (
        <div className="mt-2 font-mono text-[10px] leading-relaxed text-muted-foreground">
          {formula}
          {pct != null && <div className="mt-0.5 text-leo/80">= {pct.toFixed(4)}%</div>}
        </div>
      )}
    </div>
  );
}

function RefField({
  label,
  value,
  onChange,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
}) {
  return (
    <label className="flex flex-col gap-1">
      <span className="text-[11px] uppercase tracking-wide text-muted-foreground">{label}</span>
      <input
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="border border-border bg-background px-2 py-1 font-mono text-xs focus:border-leo focus:outline-none"
      />
    </label>
  );
}

function RefNum({
  label,
  value,
  step = 1,
  onChange,
}: {
  label: string;
  value: number;
  step?: number;
  onChange: (v: number) => void;
}) {
  return (
    <label className="flex flex-col gap-1">
      <span className="text-[11px] uppercase tracking-wide text-muted-foreground">{label}</span>
      <input
        type="number"
        step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value) || 0)}
        className="border border-border bg-background px-2 py-1 font-mono text-xs focus:border-leo focus:outline-none"
      />
    </label>
  );
}
