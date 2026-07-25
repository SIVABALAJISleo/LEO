import { createFileRoute, Link } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { leoJson } from "@/lib/leo-client";
import { TileSkeletonGrid, ErrorState } from "@/components/app/LoadingStates";

type Metrics = {
  leo_total_requests?: number;
  leo_compute_avoided?: number;
  leo_avoidance_rate_pct?: number;
  leo_gpu_watts_saved?: number;
  leo_crystallization_hit_rate?: number;
};

export const Route = createFileRoute("/_authenticated/app/")({
  head: () => ({ meta: [{ title: "Dashboard — LEO AI" }] }),
  component: Dashboard,
});

function Dashboard() {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["metrics"],
    queryFn: () => leoJson<Metrics>("/api/v1/leo/metrics"),
    refetchInterval: 5000,
    retry: 0,
  });

  return (
    <div className="p-6 md:p-10 max-w-6xl">
      <p className="eyebrow">Overview</p>
      <h1 className="mt-2 font-display text-3xl md:text-4xl font-bold">Dashboard</h1>
      <p className="mt-2 text-sm text-muted-foreground">
        {error
          ? "Backend unreachable."
          : isLoading
            ? "Loading metrics…"
            : "Live from your LEO runtime."}
      </p>

      <div className="mt-10">
        {isLoading ? (
          <TileSkeletonGrid />
        ) : error ? (
          <ErrorState onRetry={() => refetch()} />
        ) : (
          <div className="grid gap-px bg-border sm:grid-cols-2 lg:grid-cols-3">
            <Tile label="Total requests" value={num(data?.leo_total_requests)} />
            <Tile label="Compute avoided" value={num(data?.leo_compute_avoided)} />
            <Tile label="Avoidance rate" value={pct(data?.leo_avoidance_rate_pct)} />
            <Tile label="Watts saved" value={num(data?.leo_gpu_watts_saved)} />
            <Tile label="Cache hit rate" value={pct(data?.leo_crystallization_hit_rate)} />
            <Tile label="Router" value="Phi-3 Mini" small />
          </div>
        )}
      </div>

      <div className="mt-12">
        <p className="eyebrow">Quick actions</p>
        <div className="mt-4 grid gap-px bg-border md:grid-cols-3">
          <Action
            to="/app/chat"
            title="Start a chat"
            body="OpenAI-compatible completions with LEO metadata."
          />
          <Action
            to="/app/orchestrate"
            title="Run orchestration"
            body="Send a query through the router."
          />
          <Action
            to="/app/embeddings"
            title="Generate embeddings"
            body="384-dim vectors, 100% local."
          />
        </div>
      </div>
    </div>
  );
}

function num(n?: number) {
  if (n == null) return "—";
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(2)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return String(n);
}
function pct(n?: number) {
  return n == null ? "—" : `${n.toFixed(1)}%`;
}

function Tile({ label, value, small }: { label: string; value: string; small?: boolean }) {
  return (
    <div className="bg-background p-6">
      <div className="eyebrow">{label}</div>
      <div className={`mt-3 font-display font-bold text-leo ${small ? "text-2xl" : "text-4xl"}`}>
        {value}
      </div>
    </div>
  );
}
function Action({ to, title, body }: { to: string; title: string; body: string }) {
  return (
    <Link
      to={to}
      className="bg-background p-6 hover:bg-surface transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-leo focus-visible:ring-inset"
    >
      <div className="font-display text-lg font-bold">
        {title}{" "}
        <span className="text-leo" aria-hidden="true">
          ›
        </span>
      </div>
      <div className="mt-1 text-sm text-muted-foreground">{body}</div>
    </Link>
  );
}
