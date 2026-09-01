import { createFileRoute } from "@tanstack/react-router";
import React, { useState } from "react";
import {
  Zap,
  Cpu,
  Layers,
  Activity,
  ShieldCheck,
  Gauge,
  TrendingUp,
  Sliders,
  CheckCircle2,
  ArrowRight,
  Sparkles,
  Server,
  Play,
  RotateCw,
  Atom,
  BarChart3,
} from "lucide-react";
import { BREAKTHROUGH_MODULES } from "@/lib/breakthrough-data";
import { MasterReductionPipeline } from "@/components/breakthrough/MasterReductionPipeline";
import { NvidiaGpuMatrix } from "@/components/breakthrough/NvidiaGpuMatrix";
import { DomainWorkbenches } from "@/components/breakthrough/DomainWorkbenches";
import { FalsificationReport } from "@/components/breakthrough/FalsificationReport";
import { BreakthroughCard } from "@/components/breakthrough/BreakthroughCard";
import { ContractSimulator } from "@/components/breakthrough/ContractSimulator";

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

import { CGACEStudio } from "@/components/breakthrough/CGACEStudio";

export const Route = createFileRoute("/_authenticated/app/caao-breakthrough")({
  component: BreakthroughDashboardStudio,
});

export function BreakthroughDashboardStudio() {
  const [activeTab, setActiveTab] = useState<
    "cgace" | "pipeline" | "solvers" | "nvidia_matrix" | "workbenches" | "falsification"
  >("cgace");

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
    <div className="space-y-8 p-4 sm:p-6 md:p-8 max-w-7xl mx-auto font-sans">
      {/* Header & Host Specs */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-border/60 pb-6">
        <div>
          <div className="flex items-center gap-3">
            <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-cyan-500/20 text-cyan-400 border border-cyan-500/40 shadow-[0_0_20px_rgba(0,240,255,0.2)]">
              <Zap className="h-5 w-5" />
            </span>
            <div>
              <h1 className="text-2xl md:text-3xl font-extrabold font-display tracking-tight text-foreground">
                HYPER Breakthrough Engine
              </h1>
              <p className="text-xs md:text-sm text-muted-foreground font-mono">
                Contract-Gated Adaptive Computation Elimination (C-GACE) · 100% Contract Parity
              </p>
            </div>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2 font-mono text-xs">
          <div className="flex items-center gap-2 bg-zinc-950 border border-border/80 px-3 py-1.5 rounded-lg text-muted-foreground">
            <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-foreground font-semibold">Intel i5-12450H</span>
            <span className="text-muted-foreground">· UHD Xe (48 EUs)</span>
          </div>
          <div className="bg-cyan-950/40 border border-cyan-500/30 px-3 py-1.5 rounded-lg text-cyan-300 font-semibold">
            100% Contract Parity
          </div>
        </div>
      </div>

      {/* Navigation Sub-Tabs */}
      <div className="flex flex-wrap items-center gap-2 font-mono text-xs">
        {[
          { id: "cgace", label: "C-GACE Adaptive Studio", icon: Sparkles },
          { id: "pipeline", label: "Master Pipeline Simulator", icon: Layers },
          { id: "solvers", label: "15 In-Browser Solvers", icon: Zap },
          { id: "nvidia_matrix", label: "NVIDIA Matrix (1995–2025)", icon: Server },
          { id: "workbenches", label: "Domain Workbenches", icon: Atom },
          { id: "falsification", label: "Scientific Audit & Falsification", icon: ShieldCheck },
        ].map((t) => {
          const Icon = t.icon;
          return (
            <button
              key={t.id}
              onClick={() => setActiveTab(t.id as any)}
              className={`flex items-center gap-2 px-3.5 py-2 rounded-lg font-bold transition-all ${
                activeTab === t.id
                  ? "bg-cyan-500 text-black shadow-[0_0_15px_rgba(0,240,255,0.3)] scale-[1.02]"
                  : "bg-zinc-950/80 border border-border/80 text-muted-foreground hover:text-foreground"
              }`}
            >
              <Icon className="h-4 w-4" />
              <span>{t.label}</span>
            </button>
          );
        })}
      </div>

      {/* Render Active Tab */}
      {activeTab === "cgace" && <CGACEStudio />}

      {activeTab === "pipeline" && (
        <div className="space-y-8">
          <MasterReductionPipeline />
          <ContractSimulator />
        </div>
      )}

      {activeTab === "solvers" && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 gap-6">
            {BREAKTHROUGH_MODULES.map((module) => (
              <BreakthroughCard key={module.id} module={module}>
                {moduleDemoMap[module.id]}
              </BreakthroughCard>
            ))}
          </div>
        </div>
      )}

      {activeTab === "nvidia_matrix" && <NvidiaGpuMatrix />}

      {activeTab === "workbenches" && <DomainWorkbenches />}

      {activeTab === "falsification" && <FalsificationReport />}
    </div>
  );
}
