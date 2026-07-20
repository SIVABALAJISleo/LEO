import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { leoJson } from "@/lib/leo-client";
import { TileSkeletonGrid, ErrorState } from "@/components/app/LoadingStates";

export const Route = createFileRoute("/_authenticated/app/benchmarks")({
  head: () => ({ meta: [{ title: "Benchmarks — LEO AI" }] }),
  component: Page,
});

function Page() {
  const { data, error, isLoading, refetch, isFetching } = useQuery({
    queryKey: ["app-metrics"],
    queryFn: () => leoJson<Record<string, unknown>>("/api/v1/leo/metrics"),
    refetchInterval: 3000,
    staleTime: 2_000,
    gcTime: 10 * 60_000,
    placeholderData: (prev) => prev,
    retry: 0,
  });

  const entries = data ? Object.entries(data) : [];

  return (
    <div className="p-6 md:p-10 max-w-6xl">
      <p className="eyebrow">Observability</p>
      <h1 className="mt-2 font-display text-3xl md:text-4xl font-bold">Live Benchmarks</h1>
      <p className="mt-2 text-sm text-muted-foreground" aria-live="polite">
        {error
          ? "Backend unreachable."
          : isLoading
            ? "Loading…"
            : isFetching
              ? "Refreshing…"
              : "Refreshing every 3s."}
      </p>

      <div className="mt-8">
        {isLoading && !data ? (
          <TileSkeletonGrid count={9} />
        ) : error ? (
          <ErrorState onRetry={() => refetch()} />
        ) : (
          <div className="grid gap-px bg-border sm:grid-cols-2 lg:grid-cols-3">
            {entries.map(([k, v]) => (
              <div key={k} className="bg-background p-6">
                <div className="eyebrow truncate">{k.replace(/^leo_/, "").replace(/_/g, " ")}</div>
                <div className="mt-3 font-display text-3xl font-bold text-leo truncate">
                  {typeof v === "number" ? v.toLocaleString() : String(v)}
                </div>
              </div>
            ))}
            {entries.length === 0 && (
              <div className="bg-background p-6 text-sm text-muted-foreground">No data.</div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
