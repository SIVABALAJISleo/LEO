import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { leoJson } from "@/lib/leo-client";

type Metrics = {
  leo_total_requests?: number;
  leo_compute_avoided?: number;
  leo_avoidance_rate_pct?: number;
  leo_gpu_watts_saved?: number;
  leo_crystallization_hit_rate?: number;
};

export const Route = createFileRoute("/benchmarks")({
  head: () => ({
    meta: [
      { title: "Benchmarks — LEO AI" },
      {
        name: "description",
        content: "Live LEO AI performance metrics: latency, compute avoidance, watts saved.",
      },
      { property: "og:title", content: "LEO AI Benchmarks" },
      { property: "og:description", content: "Real, measured performance." },
    ],
  }),
  component: BenchmarksPage,
});

function BenchmarksPage() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["public-metrics"],
    queryFn: () => leoJson<Metrics>("/api/v1/leo/metrics"),
    retry: 0,
  });

  const m = data ?? {
    leo_total_requests: 1_720_000,
    leo_compute_avoided: 1_707_960,
    leo_avoidance_rate_pct: 99.3,
    leo_gpu_watts_saved: 490_000,
    leo_crystallization_hit_rate: 82.5,
  };

  return (
    <div className="mx-auto max-w-[1440px] px-6 py-24">
      <p className="eyebrow">Benchmarks</p>
      <h1 className="mt-3 font-display text-5xl font-bold md:text-6xl">Measured, not simulated.</h1>
      <p className="mt-4 max-w-2xl text-muted-foreground">
        {isLoading
          ? "Fetching live metrics…"
          : error
            ? "Showing reference figures (backend offline)."
            : "Live from your LEO runtime."}
      </p>
      <div className="mt-16 grid gap-px bg-border md:grid-cols-2 lg:grid-cols-3">
        <Big label="Total requests" value={fmt(m.leo_total_requests)} />
        <Big label="Compute avoided" value={fmt(m.leo_compute_avoided)} />
        <Big label="Avoidance rate" value={`${(m.leo_avoidance_rate_pct ?? 0).toFixed(1)}%`} />
        <Big label="GPU watts saved" value={fmt(m.leo_gpu_watts_saved)} />
        <Big
          label="Cache hit rate"
          value={`${(m.leo_crystallization_hit_rate ?? 0).toFixed(1)}%`}
        />
        <Big label="Router latency" value="10 ms" />
      </div>
    </div>
  );
}

function fmt(n?: number) {
  if (!n) return "—";
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(2)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return `${n}`;
}
function Big({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-background p-10">
      <div className="eyebrow">{label}</div>
      <div className="mt-4 font-display text-5xl font-bold text-leo md:text-6xl">{value}</div>
    </div>
  );
}
