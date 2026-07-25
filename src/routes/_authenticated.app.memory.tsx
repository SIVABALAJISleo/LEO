import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { leoJson } from "@/lib/leo-client";
import { toast } from "sonner";
import { ListSkeleton, ErrorState, EmptyState } from "@/components/app/LoadingStates";

const TYPES = ["episodic", "semantic", "working", "reflection", "failure", "procedural"] as const;

export const Route = createFileRoute("/_authenticated/app/memory")({
  head: () => ({ meta: [{ title: "Memory — LEO AI" }] }),
  component: Page,
});

function Page() {
  const [type, setType] = useState<(typeof TYPES)[number]>("semantic");
  const [content, setContent] = useState("");
  const [busy, setBusy] = useState(false);
  const { data, refetch, isLoading, error } = useQuery({
    queryKey: ["memory", type],
    queryFn: () => leoJson<unknown>(`/api/v1/memory?type=${type}`),
    staleTime: 30_000,
    gcTime: 10 * 60_000,
    placeholderData: (prev) => prev,
    retry: 0,
  });

  async function add() {
    if (!content.trim() || busy) return;
    setBusy(true);
    try {
      await leoJson("/api/v1/memory", { method: "POST", body: JSON.stringify({ type, content }) });
      setContent("");
      toast.success("Memory stored");
      refetch();
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Failed to store memory");
    } finally {
      setBusy(false);
    }
  }

  const rows: unknown[] = Array.isArray(data)
    ? data
    : ((data as { items?: unknown[]; results?: unknown[] } | null)?.items ??
      (data as { results?: unknown[] } | null)?.results ??
      []);

  return (
    <div className="p-6 md:p-10 max-w-5xl">
      <p className="eyebrow">Runtime</p>
      <h1 className="mt-2 font-display text-3xl md:text-4xl font-bold">Semantic Memory</h1>

      <div className="mt-6 flex flex-wrap gap-1" role="tablist" aria-label="Memory type">
        {TYPES.map((t) => (
          <button
            key={t}
            role="tab"
            aria-selected={t === type}
            onClick={() => setType(t)}
            className={`px-3 py-1.5 text-xs font-mono uppercase tracking-wide border focus:outline-none focus-visible:ring-2 focus-visible:ring-leo ${
              t === type
                ? "border-leo text-leo"
                : "border-border text-muted-foreground hover:border-foreground"
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          add();
        }}
        className="mt-6 flex flex-col sm:flex-row gap-2"
      >
        <label className="sr-only" htmlFor="mem-content">
          New {type} memory
        </label>
        <input
          id="mem-content"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder={`Store new ${type} memory…`}
          className="flex-1 bg-input px-3 py-2 text-sm outline-none focus:ring-1 focus:ring-leo"
        />
        <button
          type="submit"
          disabled={busy || !content.trim()}
          className="bg-leo px-4 py-2 text-sm font-semibold text-leo-foreground disabled:opacity-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-leo"
        >
          {busy ? "Storing…" : "Store ›"}
        </button>
      </form>

      <div className="mt-8 border border-border">
        <div className="border-b border-border bg-surface px-4 py-2 eyebrow flex justify-between">
          <span>{type} memories</span>
          <span aria-label={`${rows.length} entries`}>{rows.length}</span>
        </div>
        {isLoading && !data ? (
          <ListSkeleton />
        ) : error ? (
          <div className="p-4">
            <ErrorState onRetry={() => refetch()} />
          </div>
        ) : rows.length === 0 ? (
          <EmptyState title="No entries yet" body={`Store your first ${type} memory above.`} />
        ) : (
          <ul>
            {rows.map((r, i) => (
              <li key={i} className="border-b border-border last:border-0 p-4 text-sm">
                <div>
                  {typeof r === "string"
                    ? r
                    : ((r as { content?: string })?.content ?? JSON.stringify(r))}
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
