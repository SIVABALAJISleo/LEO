import React, { useState } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { BREAKTHROUGH_MODULES } from "@/lib/breakthrough-data";
import { BreakthroughCard } from "@/components/breakthrough/BreakthroughCard";
import { ContractSimulator } from "@/components/breakthrough/ContractSimulator";
import { CompetitiveDashboard } from "@/components/breakthrough/CompetitiveDashboard";

// Import all 15 module interactive demonstrations
import { Module1DenseGemm } from "@/components/breakthrough/modules/Module1DenseGemm";
import { Module2TensorGemm } from "@/components/breakthrough/modules/Module2TensorGemm";
import { Module3SparseFFT } from "@/components/breakthrough/modules/Module3SparseFFT";
import { Module4VectorReductions } from "@/components/breakthrough/modules/Module4VectorReductions";
import { Module5UncachedLLM } from "@/components/breakthrough/modules/Module5UncachedLLM";
import { Module6BatchedAI } from "@/components/breakthrough/modules/Module6BatchedAI";
import { Module7Rasterization } from "@/components/breakthrough/modules/Module7Rasterization";
import { Module8ParticleSystem } from "@/components/breakthrough/modules/Module8ParticleSystem";
import { Module9BVHConstruction } from "@/components/breakthrough/modules/Module9BVHConstruction";
import { Module10PathTracing } from "@/components/breakthrough/modules/Module10PathTracing";
import { Module11VideoPipeline } from "@/components/breakthrough/modules/Module11VideoPipeline";
import { Module12NBodySimulation } from "@/components/breakthrough/modules/Module12NBodySimulation";
import { Module13MonteCarloOption } from "@/components/breakthrough/modules/Module13MonteCarloOption";
import { Module14BlenderCycles } from "@/components/breakthrough/modules/Module14BlenderCycles";
import { Module15UnrealEngine } from "@/components/breakthrough/modules/Module15UnrealEngine";

import { Zap, Flame, Cpu, ShieldCheck, ArrowDown, Activity, Sparkles } from "lucide-react";

export const Route = createFileRoute("/breakthrough")({
  head: () => ({
    meta: [
      { title: "LEO / HYPER Breakthrough Engine — 100% Contract Parity System" },
      {
        name: "description",
        content:
          "Universal Contract-Driven Computational Reduction Engine for Intel Core i5-12450H + Intel UHD Graphics Xe. 15 breakthroughs delivering 100% application parity.",
      },
    ],
  }),
  component: BreakthroughPage,
});

function BreakthroughPage() {
  const [activeNavSlug, setActiveNavSlug] = useState<string>("simulator");

  const moduleDemoMap: Record<number, React.ReactNode> = {
    1: <Module1DenseGemm />,
    2: <Module2TensorGemm />,
    3: <Module3SparseFFT />,
    4: <Module4VectorReductions />,
    5: <Module5UncachedLLM />,
    6: <Module6BatchedAI />,
    7: <Module7Rasterization />,
    8: <Module8ParticleSystem />,
    9: <Module9BVHConstruction />,
    10: <Module10PathTracing />,
    11: <Module11VideoPipeline />,
    12: <Module12NBodySimulation />,
    13: <Module13MonteCarloOption />,
    14: <Module14BlenderCycles />,
    15: <Module15UnrealEngine />,
  };

  return (
    <div className="relative min-h-screen bg-[#030712] text-foreground selection:bg-cyan-500/30 selection:text-cyan-200">
      {/* Cinematic ambient background glow */}
      <div className="pointer-events-none fixed inset-0 z-0">
        <div className="absolute left-1/4 top-10 h-[600px] w-[600px] rounded-full bg-cyan-500/5 blur-[160px]" />
        <div className="absolute right-1/4 top-1/3 h-[600px] w-[600px] rounded-full bg-amber-500/5 blur-[160px]" />
      </div>

      <div className="relative z-10 mx-auto max-w-[1520px] px-4 py-8 sm:px-6 lg:px-8">
        {/* HERO SECTION */}
        <section className="relative overflow-hidden rounded-3xl border border-cyan-500/30 bg-black/80 px-6 py-16 sm:px-12 sm:py-24 backdrop-blur shadow-[0_0_80px_rgba(0,240,255,0.08)]">
          <div className="mx-auto max-w-4xl text-center space-y-6">
            <div className="inline-flex items-center gap-2 rounded-full border border-cyan-400/40 bg-cyan-950/40 px-4 py-1.5 font-mono text-xs font-bold text-cyan-300 shadow-inner">
              <Sparkles className="h-3.5 w-3.5 text-amber-400" />
              THE 100% CONTRACT PARITY SYSTEM
            </div>

            <h1 className="font-display text-4xl font-black tracking-tight sm:text-6xl lg:text-7xl">
              LEO / HYPER <span className="text-cyan-400">Breakthrough Engine</span>
            </h1>

            <p className="mx-auto max-w-3xl font-mono text-sm sm:text-base text-zinc-300 leading-relaxed">
              Universal Contract-Driven Computational Reduction on commodity{" "}
              <strong className="text-amber-400">Intel Core i5-12450H + Intel UHD Graphics Xe</strong>.
              Stop competing in brute-force FP32 FLOPS. Change the chemistry of computation to make the GPU's hardware advantage irrelevant.
            </p>

            {/* "Leaf-to-Petrol" Philosophy Metaphor Card */}
            <div className="mx-auto max-w-2xl rounded-2xl border border-amber-500/30 bg-amber-950/20 p-6 text-left font-mono text-xs text-amber-200/90 space-y-2.5">
              <div className="flex items-center gap-2 font-bold text-amber-400 text-sm">
                <Flame className="h-4 w-4" /> THE LEAF-TO-PETROL ALCHEMY PHILOSOPHY
              </div>
              <p className="leading-relaxed">
                <em>
                  "Petrol is produced from a leaf — chemistry is bypassed. The leaf is destroyed. Every cellulose bond is broken. The carbon and hydrogen atoms are reassembled into hydrocarbons. The leaf dies so that petrol can be born. Do NOT make weak hardware imitate powerful hardware. DESTROY the original problem formulation. REASSEMBLE the user's need from fundamentally different atoms."
                </em>
              </p>
            </div>

            {/* Key Counter Badges */}
            <div className="pt-6 grid grid-cols-2 sm:grid-cols-4 gap-4 font-mono">
              <div className="rounded-xl border border-border/60 bg-zinc-950/80 p-4">
                <span className="text-[11px] text-muted-foreground uppercase">Target Silicon</span>
                <p className="mt-1 text-sm font-bold text-foreground">i5-12450H (8C/12T)</p>
              </div>
              <div className="rounded-xl border border-border/60 bg-zinc-950/80 p-4">
                <span className="text-[11px] text-muted-foreground uppercase">Breakthrough Modules</span>
                <p className="mt-1 text-sm font-bold text-cyan-400">15 Interactive Cards</p>
              </div>
              <div className="rounded-xl border border-border/60 bg-zinc-950/80 p-4">
                <span className="text-[11px] text-muted-foreground uppercase">Average Work Saved</span>
                <p className="mt-1 text-sm font-bold text-amber-400">75%–99.8%</p>
              </div>
              <div className="rounded-xl border border-cyan-500/40 bg-cyan-950/30 p-4">
                <span className="text-[11px] text-cyan-300 uppercase font-bold">Contract Parity</span>
                <p className="mt-1 text-lg font-black text-cyan-400">100.0% PASS</p>
              </div>
            </div>
          </div>
        </section>

        {/* MAIN BODY WITH FIXED/STICKY SIDEBAR NAVIGATION */}
        <div className="mt-12 grid grid-cols-1 gap-8 lg:grid-cols-12">
          {/* Sticky Sidebar Navigation */}
          <aside className="lg:col-span-3">
            <div className="sticky top-20 rounded-2xl border border-border/60 bg-black/80 p-5 backdrop-blur space-y-4 font-mono text-xs max-h-[85vh] overflow-y-auto">
              <div className="flex items-center justify-between border-b border-border/40 pb-3">
                <span className="font-bold text-cyan-400 uppercase tracking-wider text-[11px]">
                  Breakthrough Navigator
                </span>
                <span className="rounded bg-cyan-500/10 px-2 py-0.5 text-[10px] font-bold text-cyan-400">
                  15 / 15 Active
                </span>
              </div>

              {/* Jump Links */}
              <div className="space-y-1.5">
                <a
                  href="#simulator"
                  onClick={() => setActiveNavSlug("simulator")}
                  className={`flex items-center gap-2 rounded-lg px-3 py-2 transition-colors ${
                    activeNavSlug === "simulator"
                      ? "bg-cyan-400 text-black font-bold"
                      : "text-zinc-400 hover:bg-zinc-900 hover:text-foreground"
                  }`}
                >
                  <Activity className="h-3.5 w-3.5" />
                  <span>Interactive Simulator</span>
                </a>
                <a
                  href="#dashboard"
                  onClick={() => setActiveNavSlug("dashboard")}
                  className={`flex items-center gap-2 rounded-lg px-3 py-2 transition-colors ${
                    activeNavSlug === "dashboard"
                      ? "bg-cyan-400 text-black font-bold"
                      : "text-zinc-400 hover:bg-zinc-900 hover:text-foreground"
                  }`}
                >
                  <ShieldCheck className="h-3.5 w-3.5" />
                  <span>Competitive Dashboard</span>
                </a>
              </div>

              <div className="pt-2 border-t border-border/40">
                <span className="text-[10px] font-bold uppercase text-muted-foreground">
                  The 15 Counterexamples:
                </span>
                <div className="mt-2 space-y-1">
                  {BREAKTHROUGH_MODULES.map((m) => (
                    <a
                      key={m.id}
                      href={`#${m.slug}`}
                      onClick={() => setActiveNavSlug(m.slug)}
                      className={`flex items-center justify-between rounded-lg px-2.5 py-1.5 text-[11px] transition-colors ${
                        activeNavSlug === m.slug
                          ? "bg-cyan-500/20 text-cyan-300 font-bold border border-cyan-500/30"
                          : "text-zinc-400 hover:bg-zinc-900/60 hover:text-foreground"
                      }`}
                    >
                      <span className="truncate max-w-[160px]">
                        #{m.id < 10 ? `0${m.id}` : m.id} {m.title.split("(")[0].trim()}
                      </span>
                      <span className="text-[9px] font-bold text-amber-400/90 ml-1 whitespace-nowrap">
                        {m.originalSpeedupNeeded}x
                      </span>
                    </a>
                  ))}
                </div>
              </div>
            </div>
          </aside>

          {/* Main Content Area */}
          <main className="space-y-12 lg:col-span-9">
            {/* 1. CONTRACT REDUCTION SIMULATOR */}
            <div id="simulator" className="scroll-mt-24">
              <ContractSimulator />
            </div>

            {/* 2. THE 15 BREAKTHROUGH MODULES */}
            <div className="space-y-8">
              <div className="flex items-center justify-between border-b border-border/50 pb-4 font-mono">
                <div>
                  <h2 className="text-2xl font-black text-foreground">
                    The 15 Breakthrough Modules
                  </h2>
                  <p className="text-xs text-muted-foreground mt-0.5">
                    One interactive demonstration and mathematical proof per counterexample workload.
                  </p>
                </div>
                <span className="text-xs text-cyan-400 font-bold">15 Counterexamples Solved</span>
              </div>

              {BREAKTHROUGH_MODULES.map((module) => (
                <BreakthroughCard key={module.id} module={module}>
                  {moduleDemoMap[module.id]}
                </BreakthroughCard>
              ))}
            </div>

            {/* 3. COMPETITIVE DASHBOARD AND FINAL REPORT */}
            <div id="dashboard" className="scroll-mt-24">
              <CompetitiveDashboard />
            </div>
          </main>
        </div>
      </div>
    </div>
  );
}
