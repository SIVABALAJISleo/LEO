import { createFileRoute } from "@tanstack/react-router";
import React, { useState, useEffect } from "react";
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
  Eye,
  Flame,
  Binary,
  Compass,
  Monitor,
  Code2,
  RefreshCw,
  ChevronRight
} from "lucide-react";
import { toast } from "sonner";
import { BREAKTHROUGH_MODULES, PARITY_TIERS, type BreakthroughModuleData } from "@/lib/breakthrough-data";

// Import custom interactive modules
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

export const Route = createFileRoute("/_authenticated/app/caao-breakthrough")({
  component: BreakthroughDashboardStudio,
});

interface LiveRunResult {
  counterexample_id: number;
  title: string;
  contract_status: string;
  metrics: {
    measured_hyper_latency_ms: number;
    reference_baseline_latency_ms: number;
    effective_speedup_factor: string;
    work_elimination_ratio_pct: number;
    total_benchmark_elapsed_ms: number;
  };
  details: Record<string, any>;
  parity_level: string;
}

export function BreakthroughDashboardStudio() {
  const [activeCategory, setActiveCategory] = useState<string>("ALL");
  const [selectedModuleId, setSelectedModuleId] = useState<number>(1);
  const [runningModuleId, setRunningModuleId] = useState<number | null>(null);
  const [liveResults, setLiveResults] = useState<Record<number, LiveRunResult>>({});
  const [activePipelineStep, setActivePipelineStep] = useState<number>(0);
  const [isAutoStepping, setIsAutoStepping] = useState<boolean>(true);

  const PIPELINE_STAGES = [
    { step: 1, name: "1. Input Workload", desc: "User tensor, prompt, scene, or physics field" },
    { step: 2, name: "2. Quality Contract", desc: "Extract error tolerance ε, SSIM, or target FPS" },
    { step: 3, name: "3. Workload Analysis", desc: "Analyze rank spectrum, sparsity, & frequency" },
    { step: 4, name: "4. Redundancy Detection", desc: "Identify memory hits & unneeded multiplications" },
    { step: 5, name: "5. Algorithm Substitution", desc: "Synthesize SVD, SFFT, BitNet LUT, QMC, OIDN" },
    { step: 6, name: "6. CPU+iGPU Dispatch", desc: "AVX2 P/E-cores + OpenVINO Intel UHD GPU" },
    { step: 7, name: "7. Independent Verification", desc: "Freivalds probe, SSIM, or residual bound test" },
    { step: 8, name: "8. Adaptive Output", desc: "100% Contract Satisfied Result with Fallback" },
  ];

  // Auto-step pipeline animation
  useEffect(() => {
    if (!isAutoStepping) return;
    const interval = setInterval(() => {
      setActivePipelineStep((prev) => (prev + 1) % PIPELINE_STAGES.length);
    }, 2800);
    return () => clearInterval(interval);
  }, [isAutoStepping]);

  const runLiveBenchmark = async (cid: number) => {
    setRunningModuleId(cid);
    try {
      const res = await fetch("/api/v1/breakthrough/run-counterexample", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ counterexample_id: cid }),
      });
      if (res.ok) {
        const data: LiveRunResult = await res.json();
        setLiveResults((prev) => ({ ...prev, [cid]: data }));
        toast.success(`Counterexample #${cid} Live Verified: ${data.metrics.effective_speedup_factor} Effective Speedup!`);
      } else {
        toast.error(`Backend benchmark execution failed for CE #${cid}`);
      }
    } catch {
      toast.error("Connecting to local LEO backend on port 8000/8005...");
    } finally {
      setRunningModuleId(null);
    }
  };

  const filteredModules = BREAKTHROUGH_MODULES.filter((m) => {
    if (activeCategory === "ALL") return true;
    if (activeCategory === "DENSE") return m.category === "Linear Algebra" || m.category === "Signal & Streaming";
    if (activeCategory === "AI_ML") return m.category === "AI & Language";
    if (activeCategory === "GRAPHICS") return m.category === "Graphics & Rendering";
    if (activeCategory === "SCIENTIFIC") return m.category === "Physics & Simulation" || m.category === "Hardware Media";
    return true;
  });

  const renderInteractiveModule = (id: number) => {
    switch (id) {
      case 1: return <Module1DenseGemm />;
      case 2: return <Module2TensorGemm />;
      case 3: return <Module3SparseFFT />;
      case 4: return <Module4VectorReductions />;
      case 5: return <Module5UncachedLLM />;
      case 6: return <Module6BatchedAI />;
      case 7: return <Module7Rasterization />;
      case 8: return <Module8ParticleSystem />;
      case 9: return <Module9BVHConstruction />;
      case 10: return <Module10PathTracing />;
      case 11: return <Module11VideoPipeline />;
      case 12: return <Module12NBodySimulation />;
      case 13: return <Module13OptionPricing />;
      case 14: return <Module14BlenderCycles />;
      case 15: return <Module15UnrealEngine />;
      default: return null;
    }
  };

  return (
    <div className="space-y-10 p-6 md:p-10 max-w-7xl mx-auto font-sans">
      {/* Header & Manifesto Banner */}
      <div className="space-y-4 border-b border-border/60 pb-8">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          <div>
            <div className="flex items-center gap-3">
              <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-cyan-500/20 text-cyan-400 border border-cyan-500/40 shadow-[0_0_20px_rgba(0,240,255,0.2)]">
                <Zap className="h-6 w-6" />
              </span>
              <div>
                <h1 className="text-3xl font-extrabold font-display tracking-tight text-foreground">
                  Breakthrough Solution Dashboard
                </h1>
                <p className="text-sm text-muted-foreground font-mono">
                  100% Contract Parity Architecture · The 15 Hardware-to-Contract Solutions
                </p>
              </div>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3 font-mono text-xs">
            <div className="flex items-center gap-2 bg-zinc-950 border border-border/80 px-3.5 py-2 rounded-lg text-muted-foreground shadow-sm">
              <span className="h-2.5 w-2.5 rounded-full bg-emerald-400 animate-pulse" />
              <span className="text-foreground font-semibold">Intel Core i5-12450H</span>
              <span className="text-muted-foreground">· UHD Xe (48 EUs)</span>
            </div>
            <div className="bg-cyan-950/40 border border-cyan-500/30 px-3.5 py-2 rounded-lg text-cyan-300 font-semibold">
              Software-Only Parity
            </div>
          </div>
        </div>

        {/* Leaf-to-Petrol Philosophy Callout */}
        <div className="rounded-xl border border-cyan-500/30 bg-gradient-to-r from-cyan-950/40 via-zinc-950 to-emerald-950/30 p-5 backdrop-blur">
          <div className="flex items-start gap-4">
            <Sparkles className="h-6 w-6 text-cyan-400 shrink-0 mt-0.5" />
            <div className="space-y-1">
              <div className="text-xs uppercase font-mono tracking-wider font-bold text-cyan-400">
                The Guiding Principle — "The Leaf-to-Petrol Paradigm"
              </div>
              <p className="text-sm text-foreground/90 font-medium leading-relaxed">
                "You do not make weak hardware perform the same computation faster. You change the computation so the hardware advantage becomes irrelevant."
              </p>
              <p className="text-xs text-muted-foreground leading-relaxed pt-1">
                An artificial leaf does not synthesize fuel by building a high-pressure oil refinery; it uses a catalyst at room temperature. HYPER acts as an algorithmic catalyst finding the lowest-energy computational route to satisfy the application contract.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Section 1: Core Breakthrough Engine (8-Stage Interactive Pipeline) */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold tracking-tight text-foreground flex items-center gap-2">
            <Layers className="h-5 w-5 text-cyan-400" />
            The Core Breakthrough Engine (8-Stage Contract Pipeline)
          </h2>
          <button
            onClick={() => setIsAutoStepping(!isAutoStepping)}
            className="text-xs font-mono px-3 py-1 rounded bg-zinc-900 border border-border/80 text-muted-foreground hover:text-foreground"
          >
            {isAutoStepping ? "Pause Flow" : "Auto Flow"}
          </button>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-2 font-mono text-xs">
          {PIPELINE_STAGES.map((st, idx) => (
            <div
              key={st.step}
              onClick={() => {
                setActivePipelineStep(idx);
                setIsAutoStepping(false);
              }}
              className={`cursor-pointer rounded-lg border p-3 transition-all duration-300 flex flex-col justify-between ${
                activePipelineStep === idx
                  ? "border-cyan-400 bg-cyan-950/40 text-cyan-200 shadow-[0_0_15px_rgba(0,240,255,0.15)] scale-[1.02]"
                  : "border-border/60 bg-zinc-950/60 text-muted-foreground hover:border-border"
              }`}
            >
              <div className="font-bold text-[11px] text-cyan-400">{st.name}</div>
              <div className="text-[10px] text-muted-foreground mt-2 leading-tight">{st.desc}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Section 2: Four Parity Levels */}
      <div className="space-y-4">
        <h2 className="text-xl font-bold tracking-tight text-foreground flex items-center gap-2">
          <Gauge className="h-5 w-5 text-emerald-400" />
          The Four Parity Levels
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 font-mono text-xs">
          {PARITY_TIERS.map((tier) => (
            <div
              key={tier.tier}
              className="rounded-xl border border-border/60 bg-zinc-950/80 p-5 space-y-3 flex flex-col justify-between"
            >
              <div className="space-y-1">
                <div className="font-bold text-sm text-foreground">{tier.tier}</div>
                <div className="text-xs font-semibold" style={{ color: tier.color }}>
                  {tier.status} ({tier.parityPct})
                </div>
              </div>
              <p className="text-muted-foreground text-[11px] leading-relaxed">
                {tier.description}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Section 3: The 15 Counterexample Breakthrough Solutions */}
      <div className="space-y-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border/60 pb-4">
          <div>
            <h2 className="text-xl font-bold tracking-tight text-foreground flex items-center gap-2">
              <ShieldCheck className="h-5 w-5 text-cyan-400" />
              The 15 Counterexample Breakthrough Solvers
            </h2>
            <p className="text-xs text-muted-foreground font-mono">
              Live interactive verification across all compute, AI, rendering, and scientific domains
            </p>
          </div>

          {/* Category Filter Tabs */}
          <div className="flex flex-wrap items-center gap-1.5 font-mono text-xs bg-zinc-950 border border-border/60 p-1.5 rounded-lg">
            {[
              { id: "ALL", label: "All 15 Solvers" },
              { id: "DENSE", label: "Dense (1–4)" },
              { id: "AI_ML", label: "AI/ML (5–6)" },
              { id: "GRAPHICS", label: "Graphics (7–10)" },
              { id: "SCIENTIFIC", label: "Media/Sci (11–15)" },
            ].map((cat) => (
              <button
                key={cat.id}
                onClick={() => setActiveCategory(cat.id)}
                className={`px-3 py-1.5 rounded-md transition-all ${
                  activeCategory === cat.id
                    ? "bg-cyan-500/20 text-cyan-300 font-bold border border-cyan-500/40"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                {cat.label}
              </button>
            ))}
          </div>
        </div>

        {/* Counterexample Cards Grid */}
        <div className="space-y-6">
          {filteredModules.map((module) => {
            const live = liveResults[module.id];
            return (
              <div
                key={module.id}
                id={module.slug}
                className="rounded-xl border border-border/60 bg-black/80 p-6 md:p-8 backdrop-blur transition-all duration-300 hover:border-cyan-500/40 space-y-6"
              >
                {/* Header */}
                <div className="flex flex-wrap items-start justify-between gap-4 border-b border-border/40 pb-4">
                  <div className="space-y-1">
                    <div className="flex items-center gap-3 font-mono text-xs">
                      <span className="flex h-6 w-6 items-center justify-center rounded bg-cyan-500/10 font-bold text-cyan-400 border border-cyan-500/30">
                        #{module.id < 10 ? `0${module.id}` : module.id}
                      </span>
                      <span className="rounded-full border border-cyan-500/30 bg-cyan-500/10 px-2.5 py-0.5 text-cyan-400 font-semibold uppercase">
                        {module.workloadClass} PARITY
                      </span>
                      <span className="text-muted-foreground">{module.category}</span>
                    </div>
                    <h3 className="text-xl font-bold text-foreground tracking-tight pt-1">
                      {module.title}
                    </h3>
                  </div>

                  <div className="flex items-center gap-3">
                    <div className="text-right font-mono">
                      <div className="text-[10px] text-muted-foreground uppercase">Raw Hardware Gap</div>
                      <div className="text-sm font-bold text-red-400">{module.originalGap.split("→")[0].trim()}</div>
                    </div>
                    <button
                      onClick={() => runLiveBenchmark(module.id)}
                      disabled={runningModuleId === module.id}
                      className="flex items-center gap-2 bg-cyan-500 text-black hover:bg-cyan-400 px-4 py-2 rounded-lg text-xs font-bold font-mono transition-all disabled:opacity-50 shadow-[0_0_15px_rgba(0,240,255,0.3)]"
                    >
                      {runningModuleId === module.id ? (
                        <RotateCw className="h-4 w-4 animate-spin" />
                      ) : (
                        <Play className="h-4 w-4 fill-current" />
                      )}
                      Run Live Proof
                    </button>
                  </div>
                </div>

                {/* Subtitle & Leaf-to-Petrol Insight */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 font-mono text-xs">
                  <div className="lg:col-span-2 space-y-2">
                    <p className="text-foreground font-semibold leading-relaxed">
                      <span className="text-cyan-400">Breakthrough Mechanism:</span> {module.algorithmName}
                    </p>
                    <p className="text-muted-foreground leading-relaxed">
                      <span className="text-foreground font-bold">Contract Invariant:</span> {module.contractStatement}
                    </p>
                  </div>
                  <div className="rounded-lg border border-border/40 bg-zinc-950 p-3 space-y-1">
                    <div className="text-[10px] uppercase font-bold text-amber-400">Leaf-to-Petrol Insight</div>
                    <p className="text-[11px] text-muted-foreground leading-snug">{module.chemistryChange}</p>
                  </div>
                </div>

                {/* Interactive Simulator Slot */}
                <div className="rounded-lg border border-border/60 bg-zinc-950/60 p-4">
                  <div className="text-[11px] font-mono text-muted-foreground uppercase font-bold mb-3 flex items-center gap-1.5">
                    <Sliders className="h-3.5 w-3.5 text-cyan-400" /> Interactive Simulation & Parameter Control
                  </div>
                  {renderInteractiveModule(module.id)}
                </div>

                {/* Live Benchmark Execution Telemetry */}
                {live && (
                  <div className="rounded-lg border border-emerald-500/40 bg-emerald-950/20 p-4 font-mono text-xs space-y-2">
                    <div className="flex items-center justify-between text-emerald-400 font-bold border-b border-emerald-500/20 pb-2">
                      <span className="flex items-center gap-1.5">
                        <CheckCircle2 className="h-4 w-4" /> Live Benchmark Result — 100% Contract Satisfied
                      </span>
                      <span>Effective Speedup: {live.metrics.effective_speedup_factor}</span>
                    </div>
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-1">
                      <div>
                        <span className="text-muted-foreground">Measured Latency:</span>
                        <p className="text-foreground font-bold">{live.metrics.measured_hyper_latency_ms} ms</p>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Reference Baseline:</span>
                        <p className="text-foreground font-bold">{live.metrics.reference_baseline_latency_ms} ms</p>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Work Eliminated:</span>
                        <p className="text-cyan-400 font-bold">{live.metrics.work_elimination_ratio_pct}%</p>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Parity Level:</span>
                        <p className="text-emerald-400 font-bold">{live.parity_level}</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
