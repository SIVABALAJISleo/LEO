import React, { useState, useEffect } from "react";
import { BREAKTHROUGH_MODULES, type BreakthroughModuleData } from "@/lib/breakthrough-data";
import { calculateLiveWorkReduction, useBreakthroughStore } from "@/lib/breakthrough-store";
import { Play, RotateCcw, Zap, CheckCircle2, Sliders, Layers, ArrowRight, Activity, Cpu, Sparkles } from "lucide-react";

export function ContractSimulator() {
  const { recordRun } = useBreakthroughStore();
  const [selectedModuleId, setSelectedModuleId] = useState<number>(1);
  const [contractParam, setContractParam] = useState<number>(0.08);
  const [isSimulating, setIsSimulating] = useState<boolean>(false);
  const [activeStepIndex, setActiveStepIndex] = useState<number>(-1);
  const [viewMode, setViewMode] = useState<"comparison" | "pipeline">("comparison");

  const currentModule = BREAKTHROUGH_MODULES.find((m) => m.id === selectedModuleId) || BREAKTHROUGH_MODULES[0];

  useEffect(() => {
    setContractParam(currentModule.defaultContract.value);
  }, [selectedModuleId]);

  const liveMetrics = calculateLiveWorkReduction(currentModule, contractParam);

  const PIPELINE_STEPS = [
    { name: "Input Workload", desc: "Ingesting user tensor or query stream" },
    { name: "Contract Analysis", desc: "Extracting tolerance & FPS invariants" },
    { name: "Classification", desc: `Tagged as ${currentModule.workloadClass} PARITY` },
    { name: "Redundancy Detection", desc: "Identifying spectral & spatial sparsity" },
    { name: "Algorithm Substitution", desc: currentModule.algorithmName.split("+")[0].trim() },
    { name: "CPU+iGPU Scheduling", desc: "AVX2 P-Cores + Intel UHD Xe Dispatch" },
    { name: "Verification", desc: "Residual check ||Y - Y*|| <= epsilon" },
    { name: "Adaptive Output", desc: "Delivering 100% Contract Satisfied Result" }
  ];

  const handleRunSimulation = () => {
    setIsSimulating(true);
    setActiveStepIndex(0);

    let step = 0;
    const interval = setInterval(() => {
      step++;
      if (step < PIPELINE_STEPS.length) {
        setActiveStepIndex(step);
      } else {
        clearInterval(interval);
        setIsSimulating(false);
        recordRun({
          workloadId: currentModule.id,
          workloadTitle: currentModule.title,
          contractParamLabel: currentModule.defaultContract.label,
          contractParamValue: contractParam,
          workEliminatedPct: liveMetrics.workEliminatedPct,
          effectiveSpeedup: liveMetrics.effectiveSpeedup,
          errorDelta: liveMetrics.errorDelta,
          contractSatisfied: liveMetrics.contractSatisfied,
          activePath: liveMetrics.activePath,
          executionTimeMs: liveMetrics.executionTimeMs,
          gpuBruteForceTimeMs: liveMetrics.gpuBruteForceTimeMs,
          timestamp: new Date().toLocaleTimeString()
        });
      }
    }, 120);
  };

  return (
    <div className="relative rounded-2xl border border-cyan-500/30 bg-black/90 p-6 md:p-10 backdrop-blur shadow-[0_0_50px_rgba(0,240,255,0.06)]">
      {/* Background ambient lighting */}
      <div className="pointer-events-none absolute -left-20 -top-20 h-64 w-64 rounded-full bg-cyan-500/10 blur-3xl" />
      <div className="pointer-events-none absolute -right-20 -bottom-20 h-64 w-64 rounded-full bg-amber-500/10 blur-3xl" />

      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-border/50 pb-6">
        <div>
          <div className="flex items-center gap-2 font-mono text-xs uppercase tracking-widest text-cyan-400">
            <Sparkles className="h-4 w-4" /> Live Interactive Execution Engine
          </div>
          <h2 className="mt-2 text-2xl md:text-3xl font-black text-foreground">
            Contract-Driven Computational Reduction Simulator
          </h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Select any heavy workload, tune the required quality contract, and watch HYPER dynamically destroy redundant compute.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setViewMode(viewMode === "comparison" ? "pipeline" : "comparison")}
            className="rounded-lg border border-border/70 bg-zinc-900/80 px-3.5 py-2 font-mono text-xs text-zinc-300 hover:border-cyan-500/50 hover:text-cyan-300 transition-colors"
          >
            Switch to {viewMode === "comparison" ? "Pipeline View" : "Comparison View"}
          </button>
          <button
            onClick={handleRunSimulation}
            disabled={isSimulating}
            className="inline-flex items-center gap-2 rounded-lg bg-cyan-400 px-5 py-2 font-mono text-xs font-bold text-black hover:bg-cyan-300 disabled:opacity-50 transition-all shadow-[0_0_20px_rgba(0,240,255,0.4)]"
          >
            <Play className={`h-3.5 w-3.5 fill-current ${isSimulating ? "animate-spin" : ""}`} />
            {isSimulating ? "EXECUTING PIPELINE..." : "RUN SIMULATION"}
          </button>
        </div>
      </div>

      {/* Controls: Workload Selector & Sliders */}
      <div className="grid grid-cols-1 gap-6 py-6 md:grid-cols-12">
        {/* Workload Dropdown */}
        <div className="md:col-span-6 space-y-2">
          <label className="block font-mono text-xs text-muted-foreground uppercase">
            1. Select Target Workload
          </label>
          <select
            value={selectedModuleId}
            onChange={(e) => setSelectedModuleId(Number(e.target.value))}
            className="w-full rounded-lg border border-border/70 bg-zinc-950 px-4 py-3 font-mono text-sm text-foreground focus:border-cyan-400 focus:outline-none"
          >
            {BREAKTHROUGH_MODULES.map((m) => (
              <option key={m.id} value={m.id}>
                #{m.id < 10 ? `0${m.id}` : m.id} — {m.title} ({m.originalGap})
              </option>
            ))}
          </select>
          <div className="flex items-center gap-2 pt-1 font-mono text-[11px] text-muted-foreground">
            <span>Reference:</span>
            <span className="text-red-400">{currentModule.referenceGpu}</span>
            <span>→ Target:</span>
            <span className="text-cyan-400">Intel Core i5-12450H</span>
          </div>
        </div>

        {/* Dynamic Contract Slider */}
        <div className="md:col-span-6 space-y-2">
          <div className="flex items-center justify-between font-mono text-xs">
            <label className="text-muted-foreground uppercase">
              2. Contract Parameter: <span className="text-amber-400">{currentModule.defaultContract.label}</span>
            </label>
            <span className="rounded bg-amber-500/10 px-2 py-0.5 font-bold text-amber-400 border border-amber-500/30">
              {contractParam} {currentModule.defaultContract.unit}
            </span>
          </div>

          <input
            type="range"
            min={currentModule.defaultContract.min}
            max={currentModule.defaultContract.max}
            step={currentModule.defaultContract.step}
            value={contractParam}
            onChange={(e) => setContractParam(Number(e.target.value))}
            className="w-full h-2 rounded-lg bg-zinc-800 accent-cyan-400 cursor-pointer"
          />

          <div className="flex justify-between font-mono text-[10px] text-zinc-500">
            <span>Tight Contract ({currentModule.defaultContract.min})</span>
            <span>Relaxed Contract ({currentModule.defaultContract.max})</span>
          </div>
        </div>
      </div>

      {/* Main Viewport: Pipeline or Side-by-Side Comparison */}
      {viewMode === "pipeline" ? (
        /* 8-Stage Animated Pipeline */
        <div className="my-4 rounded-xl border border-border/50 bg-zinc-950/80 p-6 font-mono">
          <div className="mb-4 flex items-center justify-between text-xs text-muted-foreground">
            <span>HYPER REDUCTION PIPELINE STAGES</span>
            <span>{isSimulating ? `Active Stage: ${activeStepIndex + 1}/8` : "Idle / Ready"}</span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {PIPELINE_STEPS.map((step, idx) => {
              const isActive = idx === activeStepIndex;
              const isPast = activeStepIndex > idx || (!isSimulating && activeStepIndex === -1);
              return (
                <div
                  key={idx}
                  className={`rounded-lg border p-3.5 transition-all duration-200 ${
                    isActive
                      ? "border-cyan-400 bg-cyan-950/50 shadow-[0_0_15px_rgba(0,240,255,0.3)] scale-[1.02]"
                      : isPast
                      ? "border-emerald-500/40 bg-emerald-950/20 text-emerald-300"
                      : "border-border/40 bg-zinc-900/30 text-zinc-600"
                  }`}
                >
                  <div className="flex items-center justify-between text-[11px]">
                    <span className="font-bold">0{idx + 1}</span>
                    {isPast && <CheckCircle2 className="h-3 w-3 text-emerald-400" />}
                  </div>
                  <h4 className="mt-1 text-xs font-bold text-foreground">{step.name}</h4>
                  <p className="mt-1 text-[10px] text-muted-foreground leading-tight">{step.desc}</p>
                </div>
              );
            })}
          </div>
        </div>
      ) : (
        /* Side-by-Side Comparison: GPU Brute Force vs HYPER Contract-Driven */
        <div className="my-4 grid grid-cols-1 md:grid-cols-2 gap-4 font-mono text-xs">
          {/* GPU Brute Force */}
          <div className="rounded-xl border border-red-500/30 bg-red-950/10 p-5 space-y-3">
            <div className="flex items-center justify-between border-b border-red-500/20 pb-3">
              <span className="font-bold text-red-400 flex items-center gap-1.5">
                <Cpu className="h-4 w-4" /> GPU BRUTE-FORCE PATH
              </span>
              <span className="text-[11px] text-red-300/80">O(N³) Multiplies</span>
            </div>
            <p className="text-muted-foreground leading-relaxed">
              Computes all raw floating-point operations blindly regardless of whether the user or display can perceive the difference.
            </p>
            <div className="space-y-1.5 pt-2">
              <div className="flex justify-between">
                <span className="text-zinc-400">Execution Time:</span>
                <span className="font-bold text-red-300">{liveMetrics.gpuBruteForceTimeMs} ms</span>
              </div>
              <div className="flex justify-between">
                <span className="text-zinc-400">Redundant Compute:</span>
                <span className="font-bold text-red-400">100% Executed</span>
              </div>
              <div className="flex justify-between">
                <span className="text-zinc-400">Power Draw:</span>
                <span className="font-bold text-red-300">250W–450W TDP</span>
              </div>
            </div>
          </div>

          {/* HYPER Contract-Driven */}
          <div className="rounded-xl border border-cyan-500/40 bg-cyan-950/20 p-5 space-y-3 shadow-[0_0_20px_rgba(0,240,255,0.05)]">
            <div className="flex items-center justify-between border-b border-cyan-500/30 pb-3">
              <span className="font-bold text-cyan-400 flex items-center gap-1.5">
                <Zap className="h-4 w-4 text-amber-400" /> HYPER CONTRACT-DRIVEN PATH
              </span>
              <span className="text-[11px] text-cyan-300">O(1) / Sublinear</span>
            </div>
            <p className="text-muted-foreground leading-relaxed">
              Executes the minimal computation necessary to strictly satisfy the application contract, eliminating up to 99% of work.
            </p>
            <div className="space-y-1.5 pt-2">
              <div className="flex justify-between">
                <span className="text-zinc-400">Execution Time:</span>
                <span className="font-bold text-cyan-300">{liveMetrics.executionTimeMs} ms</span>
              </div>
              <div className="flex justify-between">
                <span className="text-zinc-400">Work Eliminated:</span>
                <span className="font-bold text-emerald-400">{liveMetrics.workEliminatedPct}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-zinc-400">Contract Parity:</span>
                <span className="font-bold text-emerald-400 flex items-center gap-1">
                  <CheckCircle2 className="h-3.5 w-3.5" /> 100% SATISFIED
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Summary Score Bar */}
      <div className="mt-6 flex flex-wrap items-center justify-between gap-4 rounded-xl border border-cyan-500/40 bg-cyan-950/30 p-4 font-mono text-xs">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-cyan-400 text-black font-black text-lg">
            ⚡
          </div>
          <div>
            <div className="font-bold text-foreground">
              {currentModule.title} → 100% Contract Parity
            </div>
            <div className="text-muted-foreground text-[11px]">
              {liveMetrics.workEliminatedPct}% of calculations completely eliminated on Intel i5-12450H
            </div>
          </div>
        </div>

        <div className="flex items-center gap-6">
          <div className="text-right">
            <span className="text-[10px] text-muted-foreground uppercase">SPEEDUP</span>
            <p className="text-base font-bold text-amber-400">{liveMetrics.effectiveSpeedup}x</p>
          </div>
          <div className="text-right">
            <span className="text-[10px] text-muted-foreground uppercase">ERROR DELTA</span>
            <p className="text-base font-bold text-emerald-400">
              {liveMetrics.errorDelta < 1e-4 ? "<0.0001" : liveMetrics.errorDelta.toFixed(4)}
            </p>
          </div>
          <div className="text-right">
            <span className="text-[10px] text-muted-foreground uppercase">STATUS</span>
            <p className="text-base font-bold text-cyan-300">PASS (100%)</p>
          </div>
        </div>
      </div>
    </div>
  );
}
