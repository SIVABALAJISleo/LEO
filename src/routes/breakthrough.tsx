import React, { useState } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { BREAKTHROUGH_MODULES, PARITY_TIERS } from "@/lib/breakthrough-data";
import { BreakthroughCard } from "@/components/breakthrough/BreakthroughCard";
import { ContractSimulator } from "@/components/breakthrough/ContractSimulator";
import { CompetitiveDashboard } from "@/components/breakthrough/CompetitiveDashboard";
import { NvidiaGpuMatrix } from "@/components/breakthrough/NvidiaGpuMatrix";
import { MasterReductionPipeline } from "@/components/breakthrough/MasterReductionPipeline";
import { DomainWorkbenches } from "@/components/breakthrough/DomainWorkbenches";
import { FalsificationReport } from "@/components/breakthrough/FalsificationReport";

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
import { Module13OptionPricing } from "@/components/breakthrough/modules/Module13OptionPricing";
import { Module14BlenderCycles } from "@/components/breakthrough/modules/Module14BlenderCycles";
import { Module15UnrealEngine } from "@/components/breakthrough/modules/Module15UnrealEngine";

import { Zap, Flame, Cpu, ShieldCheck, ArrowDown, Activity, Sparkles, Server, Layers, BarChart3, Atom } from "lucide-react";

import { CGACEStudio } from "@/components/breakthrough/CGACEStudio";

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
  const [activeTab, setActiveTab] = useState<"cgace" | "pipeline" | "solvers" | "nvidia_matrix" | "workbenches" | "falsification">("cgace");

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
    13: <Module13OptionPricing />,
    14: <Module14BlenderCycles />,
    15: <Module15UnrealEngine />,
  };

  return (
    <div className="min-h-screen bg-black text-foreground font-sans selection:bg-cyan-500/30 selection:text-cyan-200">
      {/* Background Ambience */}
      <div className="pointer-events-none fixed inset-0 z-0 overflow-hidden opacity-20">
        <div className="absolute -left-48 -top-48 h-96 w-96 rounded-full bg-cyan-500/20 blur-[128px]" />
        <div className="absolute -right-48 top-1/3 h-96 w-96 rounded-full bg-purple-500/20 blur-[128px]" />
        <div className="absolute bottom-0 left-1/3 h-96 w-96 rounded-full bg-emerald-500/20 blur-[128px]" />
      </div>

      <div className="relative z-10 mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8 space-y-12">
        {/* Master Header */}
        <div className="space-y-6 text-center">
          <div className="inline-flex items-center gap-2 rounded-full border border-cyan-500/30 bg-cyan-500/10 px-4 py-1.5 font-mono text-xs font-semibold text-cyan-400 backdrop-blur">
            <Sparkles className="h-3.5 w-3.5 text-amber-400" />
            <span>THE 100% CONTRACT PARITY SYSTEM</span>
            <span className="text-muted-foreground">·</span>
            <span className="text-emerald-400">C-GACE ARCHITECTURE</span>
          </div>

          <h1 className="text-4xl font-extrabold tracking-tight sm:text-5xl md:text-6xl text-foreground">
            HYPER Breakthrough Engine
          </h1>
          <p className="mx-auto max-w-3xl text-sm sm:text-base text-muted-foreground font-mono leading-relaxed">
            The GPU wins by doing more operations in parallel. HYPER wins by needing fundamentally fewer operations for the same result. That is the "chemistry change" — making the GPU's speed irrelevant by eliminating the work it excels at.
          </p>

          {/* Master Navigation Bar */}
          <div className="flex flex-wrap items-center justify-center gap-2 font-mono text-xs pt-4">
            {[
              { id: "cgace", label: "C-GACE Adaptive Studio", icon: Sparkles },
              { id: "pipeline", label: "Master Pipeline Simulator", icon: Layers },
              { id: "solvers", label: "15 In-Browser Solvers", icon: Zap },
              { id: "nvidia_matrix", label: "NVIDIA Historical Matrix (1995–2025)", icon: Server },
              { id: "workbenches", label: "Domain Workbenches", icon: Atom },
              { id: "falsification", label: "Scientific Audit & Falsification", icon: ShieldCheck },
            ].map((t) => {
              const Icon = t.icon;
              return (
                <button
                  key={t.id}
                  onClick={() => setActiveTab(t.id as any)}
                  className={`flex items-center gap-2 px-4 py-2.5 rounded-xl font-bold transition-all ${
                    activeTab === t.id
                      ? "bg-cyan-500 text-black shadow-[0_0_20px_rgba(0,240,255,0.4)] scale-105"
                      : "bg-zinc-950/80 border border-border/80 text-muted-foreground hover:text-foreground hover:border-border"
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  <span>{t.label}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Tab View 0: C-GACE Studio */}
        {activeTab === "cgace" && (
          <CGACEStudio />
        )}

        {/* Tab View 1: Master Pipeline Simulator */}
        {activeTab === "pipeline" && (
          <div className="space-y-8">
            <MasterReductionPipeline />
            <ContractSimulator />
          </div>
        )}

        {/* Tab View 2: 15 Live Solvers */}
        {activeTab === "solvers" && (
          <div className="space-y-8">
            <CompetitiveDashboard />
            <div className="space-y-6">
              <h2 className="text-2xl font-bold text-foreground font-sans">
                All 15 Interactive Mathematical Solvers
              </h2>
              <div className="grid grid-cols-1 gap-6">
                {BREAKTHROUGH_MODULES.map((module) => (
                  <BreakthroughCard key={module.id} module={module}>
                    {moduleDemoMap[module.id]}
                  </BreakthroughCard>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Tab View 3: NVIDIA Historical Matrix (1995–2025) */}
        {activeTab === "nvidia_matrix" && (
          <NvidiaGpuMatrix />
        )}

        {/* Tab View 4: Domain Workbenches */}
        {activeTab === "workbenches" && (
          <DomainWorkbenches />
        )}

        {/* Tab View 5: Scientific Audit & Falsification */}
        {activeTab === "falsification" && (
          <FalsificationReport />
        )}
      </div>
    </div>
  );
}
