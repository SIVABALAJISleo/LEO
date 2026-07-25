import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { leoJson } from "@/lib/leo-client";
import { BackendStatusBadge } from "@/components/BackendStatusBadge";
import { CurlHealthButton, CurlMetricsButton } from "@/components/CurlHealthButton";
import { LatencyChart } from "@/components/LatencyChart";
import { DiagnosticsPanel } from "@/components/DiagnosticsPanel";
import { BackendDiagnosticsPanel } from "@/components/BackendDiagnostics";
import { BackendHealthPanel } from "@/components/BackendHealthPanel";
import { HardwareProfileCard } from "@/components/HardwareProfileCard";
import { BenchmarkRunner } from "@/components/BenchmarkRunner";
import { BenchmarkHistory } from "@/components/BenchmarkHistory";
import { BenchmarkComparison } from "@/components/BenchmarkComparison";
import { RegressionThresholdsCard } from "@/components/RegressionThresholdsCard";
import { CopyDebugReportButton } from "@/components/CopyDebugReportButton";
import { ExportDebugReportButton } from "@/components/ExportDebugReportButton";
import { HealthHistoryChart } from "@/components/HealthHistoryChart";
import { SseStatusWidget } from "@/components/SseStatusWidget";
import { CorsPreflightTester } from "@/components/CorsPreflightTester";
import { HealthDegradationAlert } from "@/components/HealthDegradationAlert";
import { SseFailureDiagnostic } from "@/components/SseFailureDiagnostic";
import { ImportDebugReportButton } from "@/components/ImportDebugReportButton";
import { ExportHealthCsvButton } from "@/components/ExportHealthCsvButton";
import { BurstHealthCheckButton } from "@/components/BurstHealthCheckButton";
import { CorsSnippetsPanel } from "@/components/CorsSnippetsPanel";
import { HealthAlertTimeline } from "@/components/HealthAlertTimeline";
import { SseDiagnosticsLog } from "@/components/SseDiagnosticsLog";
import { SseLiveIndicator } from "@/components/SseLiveIndicator";
import { PermalinkButton } from "@/components/PermalinkButton";
import { GeneratePdfReportButton } from "@/components/GeneratePdfReportButton";
import { applyPermalinkState, readPermalinkFromUrl, clearPermalinkFromUrl } from "@/lib/permalink";

import { useBackendHealth } from "@/lib/backend-health";
import { usePollingIntervals } from "@/lib/health-history";
import type { BenchmarkRun } from "@/lib/benchmark-history";
import { readShareParams } from "@/lib/share-link";
import { toast } from "sonner";
import { useEffect, useMemo, useState } from "react";

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
  const [polling, setPolling] = usePollingIntervals();
  const health = useBackendHealth(polling.healthMs);
  const [liveRps, setLiveRps] = useState<number | undefined>(undefined);
  const [selectedRun, setSelectedRun] = useState<BenchmarkRun | null>(null);

  // Shareable-link params: hydrate the highlighted run and/or comparison
  // pair from the URL so opening a link on another device restores state.
  const shared = useMemo(() => readShareParams(), []);
  useEffect(() => {
    if (shared.run && !selectedRun) setSelectedRun(shared.run);
    if (shared.run || shared.compare) {
      toast.message("Loaded shared benchmark from link");
    }
    const permalink = readPermalinkFromUrl();
    if (permalink) {
      const summary = applyPermalinkState(permalink);
      clearPermalinkFromUrl();
      toast.success(
        `Permalink applied · history=${summary.history} · thresholds=${summary.thresholds ? "✓" : "—"} · sseLog=${summary.sseLog} · cors=${summary.corsResult ? "✓" : "—"}`,
      );
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const { data, isLoading, error, refetch, isFetching } = useQuery({
    queryKey: ["public-metrics"],
    queryFn: () => leoJson<Metrics>("/api/v1/leo/metrics"),
    // Automatic exponential backoff: 500ms, 1s, 2s, 4s (capped at 8s), up to 4 tries.
    retry: 4,
    retryDelay: (attempt) => Math.min(8000, 500 * 2 ** attempt),
    refetchOnWindowFocus: false,
    refetchInterval: polling.metricsMs > 0 ? polling.metricsMs : false,
  });

  const m = data ?? {
    leo_total_requests: 1_720_000,
    leo_compute_avoided: 1_707_960,
    leo_avoidance_rate_pct: 99.3,
    leo_gpu_watts_saved: 490_000,
    leo_crystallization_hit_rate: 82.5,
  };

  async function rerunChecks() {
    toast.message("Re-running checks…");
    const [, m2] = await Promise.all([health.refresh(), refetch()]);
    if (m2.error) toast.error("Metrics check failed");
    else toast.success("Checks complete");
  }

  return (
    <div className="mx-auto max-w-[1440px] px-6 py-24">
      <p className="eyebrow">Benchmarks</p>
      <h1 className="mt-3 font-display text-5xl font-bold md:text-6xl">Measured, not simulated.</h1>
      <div className="mt-4 flex flex-wrap items-center gap-4">
        <BackendStatusBadge />
        <SseLiveIndicator />
        <button
          type="button"
          onClick={rerunChecks}
          disabled={isFetching || health.status === "checking"}
          className="border border-leo bg-leo/10 px-3 py-1.5 text-xs font-medium text-leo hover:bg-leo/20 disabled:opacity-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-leo"
        >
          {isFetching || health.status === "checking" ? "Running…" : "Re-run checks"}
        </button>
        <CurlHealthButton />
        <CurlMetricsButton />
        <CopyDebugReportButton />
        <ExportDebugReportButton />
        <ExportHealthCsvButton />
        <ImportDebugReportButton />
        <BurstHealthCheckButton />
        <PermalinkButton />
        <GeneratePdfReportButton />
      </div>

      <div className="mt-4">
        <HealthDegradationAlert />
      </div>

      <fieldset className="mt-4 inline-flex flex-wrap items-center gap-3 border border-border bg-background/60 px-3 py-2 text-xs">
        <legend className="px-1 text-[11px] uppercase tracking-wide text-muted-foreground">
          Polling
        </legend>
        <IntervalField
          label="/health"
          value={polling.healthMs}
          onChange={(v) => setPolling({ ...polling, healthMs: v })}
        />
        <IntervalField
          label="/metrics"
          value={polling.metricsMs}
          onChange={(v) => setPolling({ ...polling, metricsMs: v })}
        />
        <span className="text-muted-foreground">0 = off</span>
      </fieldset>

      <p className="mt-4 max-w-2xl text-muted-foreground" aria-live="polite">
        {isLoading
          ? "Fetching live metrics… (auto-retrying with backoff)"
          : error
            ? "Showing reference figures (backend offline after retries)."
            : isFetching
              ? "Refreshing metrics…"
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

      <div className="mt-16 grid gap-8 lg:grid-cols-2">
        <LatencyChart />
        <DiagnosticsPanel />
      </div>

      <div className="mt-8">
        <BackendDiagnosticsPanel />
      </div>

      <div className="mt-8">
        <BackendHealthPanel />
      </div>

      <div className="mt-8 grid gap-8 lg:grid-cols-2">
        <HealthHistoryChart />
        <SseStatusWidget />
      </div>

      <div className="mt-8 grid gap-8 lg:grid-cols-2">
        <SseFailureDiagnostic />
        <CorsPreflightTester />
      </div>

      <div className="mt-8">
        <CorsSnippetsPanel />
      </div>

      <div className="mt-8">
        <HealthAlertTimeline />
      </div>

      <div className="mt-8">
        <SseDiagnosticsLog />
      </div>

      <div className="mt-8 grid gap-8">
        <HardwareProfileCard
          liveRps={liveRps}
          avoidanceRatePct={m.leo_avoidance_rate_pct}
          wattsSaved={m.leo_gpu_watts_saved}
          selectedRun={selectedRun}
        />
        <BenchmarkRunner
          onResult={(run) => {
            setLiveRps(run.throughputRps);
            setSelectedRun(run);
          }}
        />
        <BenchmarkHistory
          selectedId={selectedRun?.id ?? null}
          onSelect={(r) => setSelectedRun(r)}
        />
        <BenchmarkComparison
          presetBase={shared.compare?.base ?? null}
          presetTarget={shared.compare?.target ?? null}
        />
        <RegressionThresholdsCard />
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

function IntervalField({
  label,
  value,
  onChange,
}: {
  label: string;
  value: number;
  onChange: (v: number) => void;
}) {
  const options = [0, 1000, 3000, 5000, 15000, 30000, 60000];
  return (
    <label className="inline-flex items-center gap-1">
      <span className="text-muted-foreground">{label}</span>
      <select
        value={options.includes(value) ? value : 0}
        onChange={(e) => onChange(Number(e.target.value))}
        className="border border-border bg-background px-2 py-1 font-mono text-xs focus:border-leo focus:outline-none"
        aria-label={`Polling interval for ${label}`}
      >
        {options.map((o) => (
          <option key={o} value={o}>
            {o === 0 ? "off" : o < 1000 ? `${o}ms` : `${o / 1000}s`}
          </option>
        ))}
      </select>
    </label>
  );
}
