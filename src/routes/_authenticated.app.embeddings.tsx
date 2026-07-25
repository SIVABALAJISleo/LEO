import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { leoJson } from "@/lib/leo-client";
import { toast } from "sonner";

export const Route = createFileRoute("/_authenticated/app/embeddings")({
  head: () => ({ meta: [{ title: "Embeddings — LEO AI" }] }),
  component: Page,
});

function Page() {
  const [text, setText] = useState("");
  const [vec, setVec] = useState<number[] | null>(null);
  const [loading, setLoading] = useState(false);

  async function run() {
    if (!text.trim()) return;
    setLoading(true);
    try {
      const r = await leoJson<{ data?: Array<{ embedding?: number[] }>; embedding?: number[] }>(
        "/v1/embeddings",
        { method: "POST", body: JSON.stringify({ input: text, model: "leo-embed" }) },
      );
      const v = r?.data?.[0]?.embedding ?? r?.embedding ?? null;
      setVec(v);
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="p-10 max-w-5xl">
      <p className="eyebrow">Runtime</p>
      <h1 className="mt-2 font-display text-4xl font-bold">Embeddings</h1>
      <p className="mt-2 text-sm text-muted-foreground">384-dim local vectors. 2–5ms.</p>

      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        rows={4}
        placeholder="Enter text to embed…"
        className="mt-8 w-full bg-input p-4 text-sm outline-none focus:ring-1 focus:ring-leo"
      />
      <button
        onClick={run}
        disabled={loading}
        className="mt-3 bg-leo px-5 py-3 text-sm font-semibold text-leo-foreground disabled:opacity-50"
      >
        {loading ? "Embedding…" : "Generate ›"}
      </button>

      {vec && (
        <div className="mt-8 border border-border">
          <div className="border-b border-border bg-surface px-4 py-2 eyebrow flex justify-between">
            <span>Vector</span>
            <span>{vec.length} dims</span>
          </div>
          <pre className="max-h-80 overflow-auto p-4 font-mono text-[11px]">
            [
            {vec
              .slice(0, 32)
              .map((n) => n.toFixed(4))
              .join(", ")}
            {vec.length > 32 ? ", …" : ""}]
          </pre>
        </div>
      )}
    </div>
  );
}
