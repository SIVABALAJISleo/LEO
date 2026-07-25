import { createFileRoute } from "@tanstack/react-router";

const features = [
  ["Local LLM inference", "OpenVINO + GGUF mmap. Runs Mistral 7B and smaller on Intel CPU + iGPU."],
  ["Multi-model routing", "Phi-3 Mini router selects the cheapest correct path for every query."],
  ["Semantic memory", "Episodic, semantic, working, reflection, failure, procedural memory types."],
  ["Knowledge graph", "50K+ entities, 120K+ relationships. 2-hop queries in ~6ms."],
  ["Real benchmarks", "Measured latency, watts, throughput. Never simulated."],
  ["CPU + iGPU heterogeneous", "Work spreads across CPU cores and integrated graphics EUs."],
  ["Document understanding", "PDF, DOCX, code files ingested into semantic memory + KG."],
  ["Code assistance", "Native code understanding path with FSM-guided generation."],
  ["Modular plugins", "Plugin architecture for custom retrievers, tools, and post-processors."],
  ["OpenAI-compatible", "/v1/chat/completions and /v1/embeddings drop-in endpoints."],
  ["RBAC + JWT auth", "Role-based access, per-endpoint rate limits, audit trail."],
  ["Observability", "Prometheus-style metrics, per-request LEO metadata for cost tracking."],
];

export const Route = createFileRoute("/features")({
  head: () => ({
    meta: [
      { title: "Features — LEO AI" },
      { name: "description", content: "Every capability in the LEO AI runtime." },
      { property: "og:title", content: "LEO AI Features" },
      {
        property: "og:description",
        content:
          "Local inference, semantic memory, knowledge graph, OpenAI-compatible API, and more.",
      },
    ],
  }),
  component: FeaturesPage,
});

function FeaturesPage() {
  return (
    <div className="mx-auto max-w-[1440px] px-6 py-24">
      <p className="eyebrow">Features</p>
      <h1 className="mt-3 font-display text-5xl font-bold md:text-6xl">
        Built for real workloads.
      </h1>
      <div className="mt-16 grid gap-px bg-border md:grid-cols-2 lg:grid-cols-3">
        {features.map(([t, d]) => (
          <div key={t} className="bg-background p-8 hover:bg-surface transition-colors">
            <h3 className="font-display text-lg font-bold">{t}</h3>
            <p className="mt-2 text-sm text-muted-foreground leading-relaxed">{d}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
