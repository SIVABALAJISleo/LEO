import { createFileRoute, Link } from "@tanstack/react-router";
import heroImg from "@/assets/leo-hero.jpg";
import { Cpu, Database, Gauge, GitBranch, Layers, Lock, Network, Zap } from "lucide-react";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "LEO AI — Local-first AI runtime for commodity hardware" },
      {
        name: "description",
        content:
          "Maximize AI on Intel CPU + iGPU. 99.3% compute avoided, 490kW saved. Local, private, offline.",
      },
      { property: "og:title", content: "LEO AI — Local-first AI runtime" },
      { property: "og:description", content: "Fast, private AI on ordinary hardware." },
    ],
  }),
  component: Home,
});

function Home() {
  return (
    <div>
      {/* Hero */}
      <section className="relative overflow-hidden border-b border-border">
        <div
          className="absolute inset-0 opacity-70"
          style={{
            backgroundImage: `linear-gradient(180deg, oklch(0 0 0 / 0.4) 0%, oklch(0 0 0 / 0.95) 100%), url(${heroImg})`,
            backgroundSize: "cover",
            backgroundPosition: "center",
          }}
        />
        <div className="relative mx-auto max-w-[1440px] px-6 pt-24 pb-32 md:pt-32 md:pb-44">
          <p className="eyebrow">Introducing LEO AI</p>
          <h1 className="mt-4 max-w-4xl font-display text-5xl font-bold leading-[1.02] md:text-7xl lg:text-[104px]">
            Full-power AI on <span className="text-leo">ordinary hardware.</span>
          </h1>
          <p className="mt-6 max-w-2xl text-lg text-muted-foreground md:text-xl">
            LEO AI is a local-first inference runtime that runs research-grade models on Intel CPU +
            iGPU — with semantic caching, adaptive routing, and OpenVINO acceleration. No cloud. No
            premium GPUs.
          </p>
          <div className="mt-10 flex flex-wrap gap-3">
            <Link
              to="/breakthrough"
              className="inline-flex items-center gap-2 bg-cyan-400 px-6 py-4 text-sm font-bold text-black hover:bg-cyan-300 shadow-[0_0_25px_rgba(0,240,255,0.4)]"
            >
              100% Breakthrough Engine <span>⚡</span>
            </Link>
            <Link
              to="/platform"
              className="inline-flex items-center gap-2 border border-border px-6 py-4 text-sm font-semibold hover:border-leo"
            >
              Explore the platform <span>›</span>
            </Link>
          </div>
        </div>
      </section>

      {/* Stat strip */}
      <section className="border-b border-border bg-surface">
        <div className="mx-auto grid max-w-[1440px] grid-cols-2 gap-px bg-border md:grid-cols-4">
          <Stat value="99.3%" label="Compute avoided" />
          <Stat value="490 kW" label="GPU watts saved" />
          <Stat value="1.72M" label="Requests served" />
          <Stat value="2.3 ms" label="GraphRAG latency" />
        </div>
      </section>

      {/* Pillars */}
      <section className="border-b border-border">
        <div className="mx-auto max-w-[1440px] px-6 py-24">
          <p className="eyebrow">The runtime</p>
          <h2 className="mt-3 max-w-3xl font-display text-4xl font-bold md:text-6xl">
            Three ideas that make LEO fast.
          </h2>
          <div className="mt-14 grid gap-px bg-border md:grid-cols-3">
            <Pillar
              icon={<Lock />}
              title="Local-first"
              body="Models run on your machine. Your data never leaves the device. Full offline inference with mmap'd GGUF weights."
            />
            <Pillar
              icon={<Cpu />}
              title="CPU + iGPU heterogeneous"
              body="Intel OpenVINO scheduling spreads work across CPU cores and integrated graphics. Real gains on commodity chips."
            />
            <Pillar
              icon={<Network />}
              title="Semantic routing"
              body="A Phi-3 router picks GraphRAG or Mistral 7B per query. 99.3% of requests bypass heavy compute."
            />
          </div>
        </div>
      </section>

      {/* Capabilities grid */}
      <section className="border-b border-border bg-surface">
        <div className="mx-auto max-w-[1440px] px-6 py-24">
          <div className="flex items-end justify-between gap-6 flex-wrap">
            <div>
              <p className="eyebrow">Capabilities</p>
              <h2 className="mt-3 font-display text-4xl font-bold md:text-5xl">
                Everything in one runtime.
              </h2>
            </div>
            <Link to="/features" className="text-sm font-semibold text-leo hover:brightness-110">
              All features ›
            </Link>
          </div>
          <div className="mt-12 grid gap-px bg-border sm:grid-cols-2 lg:grid-cols-4">
            {[
              { i: <Zap />, t: "Local LLM inference", d: "GGUF mmap, speculative decoding." },
              { i: <GitBranch />, t: "Multi-model routing", d: "Phi-3 router, Mistral fallback." },
              { i: <Database />, t: "Semantic memory", d: "6 memory types, ChromaDB + FAISS." },
              { i: <Layers />, t: "Knowledge graph", d: "50K+ entities, 2-hop in 6ms." },
              { i: <Gauge />, t: "Real benchmarks", d: "Measured, not simulated." },
              { i: <Cpu />, t: "OpenVINO", d: "Intel CPU + iGPU acceleration." },
              { i: <Lock />, t: "RBAC + JWT", d: "Rate limits, permissions, audit." },
              { i: <Network />, t: "OpenAI-compatible", d: "/v1/chat/completions drop-in." },
            ].map((c) => (
              <div
                key={c.t}
                className="group bg-background p-6 transition-colors hover:bg-surface-2"
              >
                <div className="text-leo">{c.i}</div>
                <div className="mt-4 font-display text-lg font-semibold">{c.t}</div>
                <div className="mt-1 text-sm text-muted-foreground">{c.d}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Big CTA */}
      <section className="border-b border-border">
        <div className="mx-auto max-w-[1440px] px-6 py-24 md:py-32">
          <p className="eyebrow">Start building</p>
          <h2 className="mt-3 max-w-3xl font-display text-5xl font-bold md:text-7xl">
            Ship AI that runs anywhere.
          </h2>
          <p className="mt-6 max-w-xl text-muted-foreground">
            OpenAI-compatible endpoints. JWT auth. Ready in minutes.
          </p>
          <div className="mt-10 flex flex-wrap gap-3">
            <Link
              to="/signup"
              className="bg-leo px-6 py-4 text-sm font-semibold text-leo-foreground hover:brightness-110"
            >
              Create an account ›
            </Link>
            <Link
              to="/docs"
              className="border border-border px-6 py-4 text-sm font-semibold hover:border-leo"
            >
              Read the docs ›
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}

function Stat({ value, label }: { value: string; label: string }) {
  return (
    <div className="bg-background px-6 py-10">
      <div className="font-display text-4xl font-bold text-leo md:text-5xl">{value}</div>
      <div className="mt-2 text-xs uppercase tracking-widest text-muted-foreground">{label}</div>
    </div>
  );
}

function Pillar({ icon, title, body }: { icon: React.ReactNode; title: string; body: string }) {
  return (
    <div className="bg-background p-8 transition-colors hover:bg-surface">
      <div className="text-leo">{icon}</div>
      <h3 className="mt-6 font-display text-2xl font-bold">{title}</h3>
      <p className="mt-3 text-sm leading-relaxed text-muted-foreground">{body}</p>
    </div>
  );
}
