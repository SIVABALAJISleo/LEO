import { createFileRoute } from "@tanstack/react-router";

const endpoints = [
  ["POST", "/v1/chat/completions", "OpenAI-compatible chat", "450ms avg"],
  ["POST", "/v1/embeddings", "384-dim local embeddings", "2-5ms"],
  ["POST", "/api/v1/leo/orchestrate", "Router → GraphRAG or Mistral", "varies"],
  ["GET", "/api/v1/leo/metrics", "Live runtime metrics", "1ms"],
  ["POST", "/api/v1/memory", "Store or query semantic memory", "3ms"],
  ["POST", "/api/v1/kg/query", "Knowledge graph 2-hop query", "6ms"],
  ["POST", "/api/v1/security/*", "RBAC, audit, keys", "-"],
];

export const Route = createFileRoute("/docs")({
  head: () => ({
    meta: [
      { title: "Docs — LEO AI" },
      { name: "description", content: "LEO AI API reference: 45+ endpoints across 8 categories." },
      { property: "og:title", content: "LEO AI Docs" },
      { property: "og:description", content: "API reference and integration guides." },
    ],
  }),
  component: DocsPage,
});

function DocsPage() {
  return (
    <div className="mx-auto max-w-[1440px] px-6 py-24">
      <p className="eyebrow">Documentation</p>
      <h1 className="mt-3 font-display text-5xl font-bold md:text-6xl">Build with LEO.</h1>
      <p className="mt-4 max-w-2xl text-muted-foreground">
        Full reference lives in{" "}
        <code className="text-leo">LEO_AI_BACKEND_API_DOCUMENTATION.md</code>, plus an OpenAPI 3.0
        spec you can import into Postman or generate SDKs from.
      </p>

      <div className="mt-16">
        <div className="eyebrow mb-4">Key endpoints</div>
        <div className="border border-border">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border bg-surface text-left">
                <th className="p-4 font-mono text-xs">Method</th>
                <th className="p-4 font-mono text-xs">Path</th>
                <th className="p-4 font-mono text-xs">Description</th>
                <th className="p-4 font-mono text-xs text-right">Latency</th>
              </tr>
            </thead>
            <tbody>
              {endpoints.map(([m, p, d, l]) => (
                <tr
                  key={p}
                  className="border-b border-border last:border-0 hover:bg-surface transition-colors"
                >
                  <td className="p-4">
                    <span className="inline-block bg-leo px-2 py-0.5 font-mono text-xs font-bold text-leo-foreground">
                      {m}
                    </span>
                  </td>
                  <td className="p-4 font-mono">{p}</td>
                  <td className="p-4 text-muted-foreground">{d}</td>
                  <td className="p-4 text-right font-mono text-xs text-leo">{l}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="mt-16 grid gap-px bg-border md:grid-cols-3">
        <div className="bg-background p-8">
          <div className="eyebrow">Auth</div>
          <p className="mt-3 font-mono text-xs text-muted-foreground">
            Authorization: Bearer &lt;JWT&gt;
          </p>
          <p className="mt-2 text-sm text-muted-foreground">
            JWT with RBAC scopes: orchestrate, memory, kg, security, admin.
          </p>
        </div>
        <div className="bg-background p-8">
          <div className="eyebrow">Rate limits</div>
          <p className="mt-3 text-sm text-muted-foreground">
            Global 600/60s. Chat 100/min. Embeddings 1000/min. Memory/KG 500/min.
          </p>
        </div>
        <div className="bg-background p-8">
          <div className="eyebrow">SDK</div>
          <p className="mt-3 text-sm text-muted-foreground">
            Any OpenAI SDK works out of the box. Point base URL at your LEO deployment.
          </p>
        </div>
      </div>
    </div>
  );
}
