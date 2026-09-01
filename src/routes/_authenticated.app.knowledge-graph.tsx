import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { leoJson } from "@/lib/leo-client";
import { toast } from "sonner";

export const Route = createFileRoute("/_authenticated/app/knowledge-graph")({
  head: () => ({ meta: [{ title: "Knowledge Graph — LEO AI" }] }),
  component: Page,
});

function Page() {
  const [q, setQ] = useState("");
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  async function run() {
    if (!q.trim()) return;
    setLoading(true);
    try {
      const r = await leoJson("/api/v1/kg/query", {
        method: "POST",
        body: JSON.stringify({ query: q, hops: 2 }),
      });
      setResult(r);
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="p-10 max-w-5xl">
      <p className="eyebrow">Runtime</p>
      <h1 className="mt-2 font-display text-4xl font-bold">Knowledge Graph</h1>
      <p className="mt-2 text-sm text-muted-foreground">2-hop traversal over 50K+ entities.</p>

      <div className="mt-8 flex gap-2">
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Entity or query…"
          className="flex-1 bg-input px-3 py-2.5 text-sm outline-none focus:ring-1 focus:ring-leo"
        />
        <button
          onClick={run}
          disabled={loading}
          className="bg-leo px-5 py-2.5 text-sm font-semibold text-leo-foreground disabled:opacity-50"
        >
          {loading ? "Traversing…" : "Query ›"}
        </button>
      </div>

      <div className="mt-6 grid gap-px bg-border md:grid-cols-3">
        <Stat label="Entities" v="50K+" />
        <Stat label="Relationships" v="120K+" />
        <Stat label="2-hop latency" v="6ms" />
      </div>

      {result && (
        <div className="mt-8 border border-border">
          <div className="border-b border-border bg-surface px-4 py-2 eyebrow">Result</div>
          <pre className="overflow-auto p-4 font-mono text-xs">
            {JSON.stringify(result, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}
function Stat({ label, v }: { label: string; v: string }) {
  return (
    <div className="bg-background p-5">
      <div className="eyebrow">{label}</div>
      <div className="mt-2 font-display text-2xl font-bold text-leo">{v}</div>
    </div>
  );
}
