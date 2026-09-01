import React, { useState, useEffect } from "react";
import {
  Layers,
  Zap,
  Sliders,
  CheckCircle2,
  AlertTriangle,
  Play,
  RotateCw,
  Cpu,
  ArrowRight,
  ShieldCheck,
  Flame,
  Activity,
  Sparkles,
  Server,
} from "lucide-react";

interface PipelineStep {
  id: number;
  title: string;
  shortDesc: string;
  activeDescription: string;
  mathematicalAction: string;
  hyperDecision: string;
  gpuBruteForceAction: string;
}

export function MasterReductionPipeline() {
  const [activeStep, setActiveStep] = useState<number>(0);
  const [isAutoPlaying, setIsAutoPlaying] = useState<boolean>(true);
  const [selectedContractTolerance, setSelectedContractTolerance] = useState<number>(0.01);
  const [selectedWorkload, setSelectedWorkload] = useState<string>("dense_matrix");
  const [isGpuComparisonMode, setIsGpuComparisonMode] = useState<boolean>(false);

  const PIPELINE_STEPS: PipelineStep[] = [
    {
      id: 1,
      title: "1. Input Ingestion",
      shortDesc: "Workload Tensor / Prompt / Scene",
      activeDescription: "Receiving raw application input stream and computational specification.",
      mathematicalAction: "T in R^{N x M}, Prompt tokens S_1..T, or 3D Triangle mesh with N faces.",
      hyperDecision: "Profile input dimensions, condition number, and temporal history.",
      gpuBruteForceAction: "Blindly allocates 100% VRAM memory buffers on GPU.",
    },
    {
      id: 2,
      title: "2. Contract Analysis",
      shortDesc: "Extract Tolerances & Invariants",
      activeDescription:
        "Extracting downstream perceptual and numerical requirements (epsilon, SSIM, target FPS).",
      mathematicalAction:
        "Define Contract C = { ||Y - Y*|| / ||Y*|| <= eps, SSIM(I) >= 0.95, Latency <= 33ms }",
      hyperDecision: `Sets error budget eps = ${selectedContractTolerance} and downstream SLA.`,
      gpuBruteForceAction:
        "Ignores contract; mandates IEEE-754 FP32 bit-level execution regardless of user need.",
    },
    {
      id: 3,
      title: "3. Workload Classification",
      shortDesc: "Classify Mathematical Structure",
      activeDescription: "Evaluating spectral decay, low-rank eigenspectrum, and sparsity density.",
      mathematicalAction:
        "Rank estimation: r = argmin_k (sigma_{k+1} / sigma_1 < eps), Sparsity S = count(W == 0) / N^2",
      hyperDecision: "Tags workload as APPROXIMATE LOW-RANK or SPARSE FREQUENCY.",
      gpuBruteForceAction: "Assumes dense full-rank worst-case O(N^3) matrix multiplication.",
    },
    {
      id: 4,
      title: "4. Redundancy Detection",
      shortDesc: "Semantic Hits & Multiplier Elimination",
      activeDescription:
        "Scanning for repeated token prefixes, static BVH bounding boxes, or cached query clusters.",
      mathematicalAction:
        "Cosine similarity sim(q, q_cached) > 0.75, or static geometry cache hit.",
      hyperDecision: "Identifies 85% to 99% redundant floating-point operations.",
      gpuBruteForceAction: "Recomputes all operations from scratch with zero caching.",
    },
    {
      id: 5,
      title: "5. Algorithm Substitution",
      shortDesc: "Synthesize Lowest-Energy Formulation",
      activeDescription:
        "Substituting brute-force algorithms with sublinear, addition-only, or quasi-random solvers.",
      mathematicalAction:
        "Replace O(N^3) GEMM with O(Nkr) Randomized SVD + BitNet Ternary LUT additions.",
      hyperDecision: "Selects Randomized SVD + AVX2 vectorized integer accumulation.",
      gpuBruteForceAction: "Launches 16,384 CUDA cores for dense FP32 multiply-accumulate.",
    },
    {
      id: 6,
      title: "6. CPU+iGPU Heterogeneous Dispatch",
      shortDesc: "AVX2 P/E-Cores + Intel UHD Xe",
      activeDescription:
        "Dispatching kernels across 4 P-cores, 4 E-cores, and OpenVINO Intel UHD GPU.",
      mathematicalAction:
        "Partition load: 60% AVX2 vectorized CPU threads + 40% Intel UHD 48 EUs OpenVINO.",
      hyperDecision: "Zero PCIe transfer bottleneck; shared unified system memory bus (51.2 GB/s).",
      gpuBruteForceAction: "Incurs 16 GB/s host-to-device PCIe transfer latency.",
    },
    {
      id: 7,
      title: "7. Independent Verification",
      shortDesc: "Freivalds Probe & SSIM Check",
      activeDescription:
        "Verifying output against quality contract via randomized Monte Carlo checks in O(N^2).",
      mathematicalAction:
        "Freivalds test: ||A * (B * r) - C_approx * r|| < eps * ||r|| with error prob < 2^{-k}.",
      hyperDecision: "Contract verification passed (Relative L2 error < 0.001 <= epsilon).",
      gpuBruteForceAction: "Unchecked execution; consumes 450W power blindly.",
    },
    {
      id: 8,
      title: "8. Adaptive Output & Fallback",
      shortDesc: "100% Contract Satisfied Delivery",
      activeDescription:
        "Delivering final verified result with 100% application parity and 0W idle power.",
      mathematicalAction:
        "Return Y_verified. If error > eps, seamlessly fallback to exact SIMD baseline.",
      hyperDecision: "100% Contract Parity achieved with 92% work eliminated!",
      gpuBruteForceAction: "Delivers identical user result after consuming 20x more energy.",
    },
  ];

  // Auto-play animation
  useEffect(() => {
    if (!isAutoPlaying) return;
    const timer = setInterval(() => {
      setActiveStep((prev) => (prev + 1) % PIPELINE_STEPS.length);
    }, 3200);
    return () => clearInterval(timer);
  }, [isAutoPlaying, PIPELINE_STEPS.length]);

  const currentStep = PIPELINE_STEPS[activeStep];

  return (
    <div className="space-y-6 font-mono text-xs">
      {/* Header & Controls */}
      <div className="rounded-xl border border-cyan-500/30 bg-black/80 p-6 backdrop-blur space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 text-cyan-400 font-bold text-xs uppercase tracking-wider">
              <Layers className="h-4 w-4" /> The 8-Stage Contract Engine
            </div>
            <h2 className="text-xl md:text-2xl font-bold font-sans text-foreground mt-1">
              Master Computational Reduction Pipeline
            </h2>
            <p className="text-muted-foreground text-xs font-sans mt-1">
              How HYPER dynamically finds the cheapest computation that satisfies the required
              quality contract.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => setIsGpuComparisonMode(!isGpuComparisonMode)}
              className={`px-3 py-1.5 rounded-lg border text-xs font-bold transition-all ${
                isGpuComparisonMode
                  ? "bg-amber-500/20 text-amber-300 border-amber-500/40"
                  : "bg-zinc-900 border-border/80 text-muted-foreground hover:text-foreground"
              }`}
            >
              {isGpuComparisonMode
                ? "Comparing vs GPU Brute Force"
                : "Show GPU Brute Force Contrast"}
            </button>

            <button
              onClick={() => setIsAutoPlaying(!isAutoPlaying)}
              className="flex items-center gap-1.5 bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 px-3 py-1.5 rounded-lg font-bold hover:bg-cyan-500/30 transition-colors"
            >
              {isAutoPlaying ? (
                <RotateCw className="h-3.5 w-3.5 animate-spin" />
              ) : (
                <Play className="h-3.5 w-3.5" />
              )}
              {isAutoPlaying ? "Auto Flowing" : "Resume Flow"}
            </button>
          </div>
        </div>

        {/* Dynamic Inputs */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-3 border-t border-border/40">
          <div className="space-y-1.5">
            <label className="text-muted-foreground uppercase font-bold text-[10px]">
              Select Input Workload:
            </label>
            <select
              value={selectedWorkload}
              onChange={(e) => setSelectedWorkload(e.target.value)}
              className="w-full bg-zinc-950 border border-border/80 rounded-lg px-3 py-2 text-xs text-foreground focus:outline-none focus:border-cyan-500/50"
            >
              <option value="dense_matrix">Dense Transformer GEMM (256x256)</option>
              <option value="spectral_fft">2D Spectral Audio/Signal FFT (1024-point)</option>
              <option value="nbody_physics">
                N-Body Astrodynamics Particle Cluster (512 particles)
              </option>
              <option value="path_tracing">Monte Carlo Path Tracing (4 SPP vs 512 SPP)</option>
            </select>
          </div>

          <div className="space-y-1.5">
            <div className="flex justify-between text-[10px]">
              <label className="text-muted-foreground uppercase font-bold">
                Contract Quality Tolerance (ε):
              </label>
              <span className="font-bold text-cyan-400">
                ε = {selectedContractTolerance} ({(selectedContractTolerance * 100).toFixed(1)}%
                error budget)
              </span>
            </div>
            <input
              type="range"
              min={0.001}
              max={0.05}
              step={0.001}
              value={selectedContractTolerance}
              onChange={(e) => setSelectedContractTolerance(Number(e.target.value))}
              className="w-full h-2 rounded bg-zinc-800 accent-cyan-400 cursor-pointer"
            />
          </div>
        </div>
      </div>

      {/* 8-Stage Progress Bar */}
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-2">
        {PIPELINE_STEPS.map((step, idx) => (
          <button
            key={step.id}
            onClick={() => {
              setActiveStep(idx);
              setIsAutoPlaying(false);
            }}
            className={`text-left rounded-lg border p-3 transition-all duration-300 flex flex-col justify-between ${
              activeStep === idx
                ? "border-cyan-400 bg-cyan-950/50 text-cyan-200 shadow-[0_0_15px_rgba(0,240,255,0.2)] scale-[1.02]"
                : "border-border/60 bg-zinc-950/70 text-muted-foreground hover:border-border/90"
            }`}
          >
            <div className="font-bold text-[11px] text-cyan-400">{step.title}</div>
            <div className="text-[10px] text-muted-foreground mt-2 leading-snug line-clamp-2">
              {step.shortDesc}
            </div>
          </button>
        ))}
      </div>

      {/* Active Step Deep-Dive Card */}
      <div className="rounded-xl border border-cyan-500/40 bg-black/90 p-6 md:p-8 backdrop-blur space-y-6">
        <div className="flex flex-wrap items-center justify-between gap-4 border-b border-border/40 pb-4">
          <div>
            <span className="text-xs uppercase font-bold text-cyan-400">
              Active Stage {currentStep.id} of 8:
            </span>
            <h3 className="text-xl md:text-2xl font-bold text-foreground font-sans mt-0.5">
              {currentStep.title} — {currentStep.shortDesc}
            </h3>
          </div>

          <div className="flex items-center gap-2 bg-emerald-500/10 border border-emerald-500/30 px-3 py-1.5 rounded-lg text-emerald-400 font-bold">
            <CheckCircle2 className="h-4 w-4" />
            <span>CONTRACT INVARIANT VERIFIED</span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <div className="rounded-lg border border-border/60 bg-zinc-950 p-4 space-y-2">
              <span className="text-muted-foreground font-bold uppercase text-[10px]">
                Mathematical Transformation:
              </span>
              <p className="text-cyan-300 font-mono text-xs">{currentStep.mathematicalAction}</p>
            </div>

            <div className="rounded-lg border border-cyan-500/30 bg-cyan-950/20 p-4 space-y-2">
              <span className="text-cyan-400 font-bold uppercase text-[10px]">
                HYPER Algorithmic Catalyst:
              </span>
              <p className="text-foreground text-xs leading-relaxed">{currentStep.hyperDecision}</p>
            </div>
          </div>

          <div className="space-y-4">
            <div className="rounded-lg border border-border/60 bg-zinc-950 p-4 space-y-2">
              <span className="text-muted-foreground font-bold uppercase text-[10px]">
                Stage Description:
              </span>
              <p className="text-foreground text-xs leading-relaxed">
                {currentStep.activeDescription}
              </p>
            </div>

            {isGpuComparisonMode && (
              <div className="rounded-lg border border-red-500/30 bg-red-950/20 p-4 space-y-2">
                <span className="text-red-400 font-bold uppercase text-[10px]">
                  NVIDIA GPU Brute-Force Path:
                </span>
                <p className="text-red-200/90 text-xs leading-relaxed">
                  {currentStep.gpuBruteForceAction}
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
