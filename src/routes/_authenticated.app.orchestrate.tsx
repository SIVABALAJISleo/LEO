import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { leoJson } from "@/lib/leo-client";
import { toast } from "sonner";

export const Route = createFileRoute("/_authenticated/app/orchestrate")({
  head: () => ({ meta: [{ title: "Orchestrate — LEO AI" }] }),
  component: Page,
});

function Page() {
  const [query, setQuery] = useState("");
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  async function run() {
    if (!query.trim()) return;
    setLoading(true);
    setResult(null);
    try {
      const res = await leoJson("/api/v1/leo/orchestrate", {
        method: "POST",
        body: JSON.stringify({ query }),
      });
      setResult(res);
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Failed");
    } finally {
      setLoading(false);
    }
  }

  const path = result?.x_leo_metadata?.resolved_by ?? result?.resolved_by;

  return (
    <div className="p-10 max-w-5xl">
      <p className="eyebrow">Runtime</p>
      <h1 className="mt-2 font-display text-4xl font-bold">Orchestrate</h1>
      <p className="mt-2 text-sm text-muted-foreground">
        Send a query through Phi-3 → GraphRAG or Mistral.
      </p>

      <div className="mt-8">
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          rows={4}
          placeholder="How do I reset my password?"
          className="w-full bg-input p-4 text-sm outline-none focus:ring-1 focus:ring-leo"
        />
        <button
          onClick={run}
          disabled={loading}
          className="mt-3 bg-leo px-5 py-3 text-sm font-semibold text-leo-foreground disabled:opacity-50"
        >
          {loading ? "Routing…" : "Run orchestration ›"}
        </button>
      </div>

      <div className="mt-12 grid gap-px bg-border md:grid-cols-3">
        <Node n="01" label="Phi-3 Router" active={!!result} />
        <Node n="02" label="GraphRAG" active={path === "GraphRAG"} />
        <Node n="03" label="Mistral 7B" active={path === "Mistral"} />
      </div>

      {result && (
        <div className="mt-8 border border-border">
          <div className="border-b border-border bg-surface px-4 py-2 eyebrow">Response</div>
          <pre className="overflow-auto p-4 font-mono text-xs">
            {JSON.stringify(result, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}

function Node({ n, label, active }: { n: string; label: string; active: boolean }) {
  return (
    <div className={`bg-background p-6 border-t-2 ${active ? "border-leo" : "border-transparent"}`}>
      <div className="font-mono text-xs text-muted-foreground">{n}</div>
      <div className={`mt-3 font-display text-lg font-bold ${active ? "text-leo" : ""}`}>
        {label}
      </div>
    </div>
  );
}
