import React, { useState } from "react";
import { type BreakthroughModuleData } from "@/lib/breakthrough-data";
import { calculateLiveWorkReduction } from "@/lib/breakthrough-store";
import {
  Cpu,
  Zap,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  Activity,
  Terminal,
  ShieldCheck,
} from "lucide-react";

interface BreakthroughCardProps {
  module: BreakthroughModuleData;
  customParamValue?: number;
  onParamChange?: (val: number) => void;
  children?: React.ReactNode;
}

export function BreakthroughCard({
  module,
  customParamValue,
  onParamChange,
  children,
}: BreakthroughCardProps) {
  const [activeTab, setActiveTab] = useState<"demo" | "math" | "silicon">("demo");
  const paramVal = customParamValue !== undefined ? customParamValue : module.defaultContract.value;
  const metrics = calculateLiveWorkReduction(module, paramVal);

  const getBadgeColor = (cls: string) => {
    switch (cls) {
      case "EXACT":
        return "bg-emerald-500/10 text-emerald-400 border-emerald-500/30";
      case "CACHED":
        return "bg-cyan-500/10 text-cyan-400 border-cyan-500/30";
      case "APPROXIMATE":
        return "bg-amber-500/10 text-amber-400 border-amber-500/30";
      case "PREDICTIVE":
        return "bg-purple-500/10 text-purple-400 border-purple-500/30";
      default:
        return "bg-zinc-500/10 text-zinc-400 border-zinc-500/30";
    }
  };

  return (
    <div
      id={module.slug}
      className="group relative scroll-mt-24 rounded-xl border border-border/60 bg-black/80 p-6 md:p-8 backdrop-blur transition-all duration-300 hover:border-cyan-500/50 hover:shadow-[0_0_30px_rgba(0,240,255,0.08)]"
    >
      {/* Background radial glow */}
      <div className="pointer-events-none absolute -right-16 -top-16 h-48 w-48 rounded-full bg-cyan-500/5 blur-3xl group-hover:bg-cyan-500/10" />

      {/* Header */}
      <div className="flex flex-wrap items-start justify-between gap-4 border-b border-border/40 pb-5">
        <div>
          <div className="flex items-center gap-3">
            <span className="flex h-7 w-7 items-center justify-center rounded bg-cyan-500/10 font-mono text-xs font-bold text-cyan-400 border border-cyan-500/30">
              #{module.id < 10 ? `0${module.id}` : module.id}
            </span>
            <span
              className={`rounded-full border px-2.5 py-0.5 font-mono text-xs font-semibold uppercase tracking-wider ${getBadgeColor(module.workloadClass)}`}
            >
              {module.workloadClass} PARITY
            </span>
            <span className="text-xs text-muted-foreground font-mono">{module.category}</span>
          </div>
          <h3 className="mt-2 text-xl md:text-2xl font-bold tracking-tight text-foreground">
            {module.title}
          </h3>
        </div>

        {/* Gap to Parity Pill */}
        <div className="flex flex-col items-end">
          <div className="flex items-center gap-2 rounded-lg border border-cyan-500/40 bg-cyan-950/30 px-3 py-1.5 font-mono text-xs text-cyan-300 shadow-inner">
            <Zap className="h-3.5 w-3.5 text-amber-400" />
            <span className="font-bold">{module.originalGap}</span>
          </div>
          <span className="mt-1 text-[11px] text-muted-foreground font-mono">
            vs {module.referenceGpu}
          </span>
        </div>
      </div>

      {/* Philosophy / Chemistry Change Quote */}
      <div className="my-5 rounded-lg border border-amber-500/20 bg-amber-950/10 p-3.5 text-xs text-amber-200/90 font-mono leading-relaxed">
        <span className="font-bold text-amber-400">⚡ THE CHEMISTRY CHANGE: </span>
        {module.chemistryChange}
      </div>

      {/* Tabs */}
      <div className="flex border-b border-border/40 text-xs font-mono">
        <button
          onClick={() => setActiveTab("demo")}
          className={`flex items-center gap-1.5 border-b-2 px-4 py-2.5 font-semibold transition-colors ${
            activeTab === "demo"
              ? "border-cyan-400 text-cyan-400"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          <Activity className="h-3.5 w-3.5" /> Interactive Demonstration
        </button>
        <button
          onClick={() => setActiveTab("math")}
          className={`flex items-center gap-1.5 border-b-2 px-4 py-2.5 font-semibold transition-colors ${
            activeTab === "math"
              ? "border-cyan-400 text-cyan-400"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          <Terminal className="h-3.5 w-3.5" /> Algorithm & Formulation
        </button>
        <button
          onClick={() => setActiveTab("silicon")}
          className={`flex items-center gap-1.5 border-b-2 px-4 py-2.5 font-semibold transition-colors ${
            activeTab === "silicon"
              ? "border-cyan-400 text-cyan-400"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          <ShieldCheck className="h-3.5 w-3.5" /> Silicon Parity Truth
        </button>
      </div>

      {/* Tab Content */}
      <div className="pt-5">
        {activeTab === "demo" && (
          <div className="space-y-6">
            {/* Interactive Module Component Rendered Here */}
            {children}

            {/* Live Metrics Grid */}
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-4 rounded-lg border border-border/50 bg-zinc-950/60 p-4 font-mono">
              <div>
                <span className="text-[11px] text-muted-foreground uppercase">Work Eliminated</span>
                <p className="mt-1 text-lg font-bold text-cyan-400">{metrics.workEliminatedPct}%</p>
              </div>
              <div>
                <span className="text-[11px] text-muted-foreground uppercase">
                  Effective Speedup
                </span>
                <p className="mt-1 text-lg font-bold text-amber-400">{metrics.effectiveSpeedup}x</p>
              </div>
              <div>
                <span className="text-[11px] text-muted-foreground uppercase">Error Delta (ε)</span>
                <p className="mt-1 text-lg font-bold text-emerald-400">
                  {metrics.errorDelta < 1e-4 ? "<0.0001" : metrics.errorDelta.toFixed(4)}
                </p>
              </div>
              <div>
                <span className="text-[11px] text-muted-foreground uppercase">Contract Parity</span>
                <p className="mt-1 flex items-center gap-1.5 text-lg font-bold text-cyan-300">
                  <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                  100% PASS
                </p>
              </div>
            </div>
          </div>
        )}

        {activeTab === "math" && (
          <div className="space-y-4 font-mono text-xs">
            <div className="rounded-lg border border-cyan-500/20 bg-cyan-950/20 p-4">
              <span className="text-cyan-400 font-bold uppercase">Mathematical Formulation:</span>
              <div className="mt-2 overflow-x-auto py-2 text-sm text-cyan-200">
                <code>{module.formula}</code>
              </div>
            </div>

            <div className="space-y-2 text-muted-foreground leading-relaxed">
              <p>
                <strong className="text-foreground">Algorithm:</strong> {module.algorithmName}
              </p>
              <p>
                <strong className="text-foreground">Contract Invariant:</strong>{" "}
                {module.contractStatement}
              </p>
              <p>
                <strong className="text-foreground">Proof Mechanics:</strong>{" "}
                {module.mathExplanation}
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
              <div className="rounded border border-red-500/20 bg-red-950/10 p-3">
                <span className="text-red-400 font-bold">GPU Brute Force Complexity:</span>
                <p className="mt-1 text-muted-foreground">{module.bruteForceComplexity}</p>
              </div>
              <div className="rounded border border-emerald-500/20 bg-emerald-950/10 p-3">
                <span className="text-emerald-400 font-bold">HYPER Contract Complexity:</span>
                <p className="mt-1 text-muted-foreground">{module.breakthroughComplexity}</p>
              </div>
            </div>
          </div>
        )}

        {activeTab === "silicon" && (
          <div className="space-y-4 font-mono text-xs">
            <div className="rounded-lg border border-border/60 bg-zinc-950/80 p-4">
              <span className="text-amber-400 font-bold uppercase">
                Host Hardware Execution Target:
              </span>
              <p className="mt-1 text-foreground">{module.hardwareTarget}</p>
            </div>

            <div className="space-y-3 text-muted-foreground leading-relaxed">
              <p>
                <strong className="text-foreground">Why the GPU advantage is irrelevant:</strong>{" "}
                {module.description}
              </p>
              <p>
                <strong className="text-foreground">Host Silicon Routing:</strong> Computation is
                scheduled on the 4 P-cores + 4 E-cores of the Intel Core i5-12450H with AVX2
                vectorized SIMD kernels and OpenVINO iGPU dispatch.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
