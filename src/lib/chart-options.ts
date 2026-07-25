import { useEffect, useState } from "react";

// Persisted chart rendering options for the Benchmark runner + comparison
// charts. Loaded from localStorage on mount so refreshing the page keeps the
// user's preferred view (range, smoothing window, visible metric series).

export type ChartOptions = {
  rangeBuckets: number; // 30 / 60 / 120 / 0 (0 = all)
  smoothingWindow: number; // 1 / 3 / 5 / 7 (1 = off)
  showLatency: boolean;
  showThroughput: boolean;
};

const KEY = "leo.bench.chartOptions";

const DEFAULTS: ChartOptions = {
  rangeBuckets: 120,
  smoothingWindow: 1,
  showLatency: true,
  showThroughput: true,
};

function read(): ChartOptions {
  if (typeof window === "undefined") return DEFAULTS;
  try {
    const raw = window.localStorage.getItem(KEY);
    if (!raw) return DEFAULTS;
    const parsed = JSON.parse(raw) as Partial<ChartOptions>;
    return { ...DEFAULTS, ...parsed };
  } catch {
    return DEFAULTS;
  }
}

function write(opts: ChartOptions) {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(KEY, JSON.stringify(opts));
    window.dispatchEvent(new CustomEvent("leo:chart-options"));
  } catch {
    /* ignore quota */
  }
}

export function useChartOptions(): [ChartOptions, (patch: Partial<ChartOptions>) => void] {
  const [opts, setOpts] = useState<ChartOptions>(DEFAULTS);
  useEffect(() => {
    setOpts(read());
    const on = () => setOpts(read());
    window.addEventListener("leo:chart-options", on);
    window.addEventListener("storage", on);
    return () => {
      window.removeEventListener("leo:chart-options", on);
      window.removeEventListener("storage", on);
    };
  }, []);
  return [
    opts,
    (patch) => {
      const next = { ...opts, ...patch };
      setOpts(next);
      write(next);
    },
  ];
}

// Simple centered moving-average smoother. Window <=1 returns the input.
export function smoothSeries(values: number[], window: number): number[] {
  if (window <= 1 || values.length === 0) return values;
  const w = Math.min(window, values.length);
  const half = Math.floor(w / 2);
  const out: number[] = new Array(values.length);
  for (let i = 0; i < values.length; i++) {
    let sum = 0;
    let count = 0;
    for (let j = i - half; j <= i + half; j++) {
      if (j >= 0 && j < values.length) {
        sum += values[j];
        count += 1;
      }
    }
    out[i] = count ? sum / count : 0;
  }
  return out;
}
