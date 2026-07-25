import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/platform")({
  head: () => ({
    meta: [
      { title: "Platform — LEO AI" },
      {
        name: "description",
        content:
          "The LEO AI platform: Phi-3 router, GraphRAG, Mistral 7B, OpenVINO, GGUF mmap, speculative decoding.",
      },
      { property: "og:title", content: "LEO AI Platform" },
      { property: "og:description", content: "Architecture of the LEO AI runtime." },
    ],
  }),
  component: PlatformPage,
});

function PlatformPage() {
  return (
    <div className="mx-auto max-w-[1440px] px-6 py-24">
      <p className="eyebrow">Platform</p>
      <h1 className="mt-3 max-w-4xl font-display text-5xl font-bold md:text-7xl">
        Every request takes the fastest path.
      </h1>
      <p className="mt-6 max-w-2xl text-lg text-muted-foreground">
        LEO orchestrates a router, a graph, and a full LLM. Simple questions never touch a 7B model.
      </p>

      <div className="mt-20 grid gap-px bg-border md:grid-cols-3">
        <Step
          n="01"
          title="Phi-3 Mini Router"
          latency="10 ms"
          body="Classifies intent. Simple → GraphRAG. Complex → Mistral 7B."
        />
        <Step
          n="02"
          title="GraphRAG"
          latency="2.3 ms"
          body="50K+ entities, 2-hop traversal on ChromaDB + FAISS + SQLite."
        />
        <Step
          n="03"
          title="Mistral 7B"
          latency="1500 ms"
          body="Full generation for novel queries. Speculative decoding on iGPU."
        />
      </div>

      <div className="mt-20 grid gap-px bg-border md:grid-cols-2">
        <Card
          title="OpenVINO acceleration"
          body="Intel CPU + integrated GPU execution. Heterogeneous scheduling across cores and EUs."
        />
        <Card
          title="GGUF memory-mapped models"
          body="Weights stream from disk. Zero copy. Small RAM footprint."
        />
        <Card
          title="Semantic cache"
          body="Crystallized answers with 82.5% hit rate. Compute skipped for known queries."
        />
        <Card
          title="OpenAI-compatible API"
          body="/v1/chat/completions and /v1/embeddings as drop-in replacements."
        />
      </div>
    </div>
  );
}

function Step({
  n,
  title,
  latency,
  body,
}: {
  n: string;
  title: string;
  latency: string;
  body: string;
}) {
  return (
    <div className="bg-background p-8">
      <div className="flex items-baseline justify-between">
        <div className="font-mono text-xs text-muted-foreground">{n}</div>
        <div className="font-mono text-xs text-leo">{latency}</div>
      </div>
      <h3 className="mt-6 font-display text-2xl font-bold">{title}</h3>
      <p className="mt-3 text-sm text-muted-foreground leading-relaxed">{body}</p>
    </div>
  );
}
function Card({ title, body }: { title: string; body: string }) {
  return (
    <div className="bg-background p-8 hover:bg-surface transition-colors">
      <h3 className="font-display text-xl font-bold">{title}</h3>
      <p className="mt-3 text-sm text-muted-foreground leading-relaxed">{body}</p>
    </div>
  );
}
