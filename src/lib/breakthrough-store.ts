import { useState, useEffect } from "react";
import {
  BREAKTHROUGH_MODULES,
  type BreakthroughModuleData,
  type WorkloadClassification,
} from "./breakthrough-data";

export interface SimulationResult {
  workloadId: number;
  workloadTitle: string;
  contractParamLabel: string;
  contractParamValue: number;
  workEliminatedPct: number;
  effectiveSpeedup: number;
  errorDelta: number;
  contractSatisfied: boolean;
  activePath: string[];
  executionTimeMs: number;
  gpuBruteForceTimeMs: number;
  timestamp: string;
}

const STORAGE_KEY = "leo_breakthrough_simulation_runs";
const CUSTOM_PARAMS_KEY = "leo_breakthrough_custom_params";

export function loadSavedSimulationRuns(): SimulationResult[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

export function saveSimulationRun(result: SimulationResult): void {
  if (typeof window === "undefined") return;
  try {
    const runs = loadSavedSimulationRuns();
    const updated = [result, ...runs.slice(0, 49)]; // keep latest 50
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
  } catch (e) {
    console.error("Failed to save simulation run to LocalStorage:", e);
  }
}

export function loadCustomParams(): Record<number, number> {
  if (typeof window === "undefined") return {};
  try {
    const raw = localStorage.getItem(CUSTOM_PARAMS_KEY);
    return raw ? JSON.parse(raw) : {};
  } catch {
    return {};
  }
}

export function saveCustomParam(moduleId: number, value: number): void {
  if (typeof window === "undefined") return;
  try {
    const params = loadCustomParams();
    params[moduleId] = value;
    localStorage.setItem(CUSTOM_PARAMS_KEY, JSON.stringify(params));
  } catch (e) {
    console.error("Failed to save custom param to LocalStorage:", e);
  }
}

export function calculateLiveWorkReduction(
  module: BreakthroughModuleData,
  paramValue: number,
): {
  workEliminatedPct: number;
  effectiveSpeedup: number;
  errorDelta: number;
  contractSatisfied: boolean;
  activePath: string[];
  executionTimeMs: number;
  gpuBruteForceTimeMs: number;
} {
  let workEliminatedPct = 95.0;
  let effectiveSpeedup = module.workReductionFactor;
  let errorDelta = 0.001;
  let contractSatisfied = true;
  let activePath = [
    "Input",
    "Contract Analysis",
    "Classification",
    "Algorithm Substitution",
    "CPU+iGPU Dispatch",
    "Verification",
  ];
  let executionTimeMs = 12.5;
  let gpuBruteForceTimeMs = 450.0;

  switch (module.id) {
    case 1: {
      // Dense GEMM (Rank Ratio)
      // Rank ratio in [0.01, 0.50]
      const rankRatio = Math.max(0.01, Math.min(0.5, paramValue));
      workEliminatedPct = Math.round((1.0 - 2 * rankRatio) * 100 * 10) / 10;
      effectiveSpeedup = Math.round((1.0 / (2 * rankRatio)) * 10) / 10;
      errorDelta = Math.round(rankRatio * 0.005 * 10000) / 10000;
      contractSatisfied = errorDelta <= 0.005;
      executionTimeMs = Math.round(18.0 * rankRatio * 10) / 10;
      gpuBruteForceTimeMs = 120.0;
      activePath = [
        "Input",
        "Eigenspectrum Rank Analysis",
        "Low-Rank Truncation",
        "BitNet Ternary Adders",
        "AVX2 P-Core Dispatch",
        "Residual Verification",
      ];
      break;
    }

    case 2: {
      // FP16 Tensor GEMM (Sparsity %)
      const sparsity = Math.max(10, Math.min(95, paramValue));
      workEliminatedPct = Math.round((sparsity * 0.95 + 4.5) * 10) / 10;
      effectiveSpeedup = Math.round((100 / Math.max(5, 100 - sparsity)) * 15 * 10) / 10;
      errorDelta = 0.0; // Exact ternary
      contractSatisfied = true;
      executionTimeMs = Math.round(8.5 * (1 - sparsity / 100) * 10) / 10;
      gpuBruteForceTimeMs = 180.0;
      activePath = [
        "Input",
        "Ternary {-1,0,+1} Quantization",
        "Zero-Weight Bypass",
        "AddNet Reduction Tree",
        "AVX2 Integer SIMD",
        "Exact Match Check",
      ];
      break;
    }

    case 3: {
      // Sparse FFT (k peaks)
      const k = Math.max(16, Math.min(1024, paramValue));
      workEliminatedPct = Math.round((1.0 - k / 10000.0) * 100 * 10) / 10;
      effectiveSpeedup = Math.round((10000.0 / k) * 3.5 * 10) / 10;
      errorDelta = Math.round((1.0 / k) * 1000) / 1000;
      contractSatisfied = errorDelta <= 0.05;
      executionTimeMs = Math.round(0.8 + k * 0.005 * 10) / 10;
      gpuBruteForceTimeMs = 45.0;
      activePath = [
        "Signal Stream",
        "Energy Dispersion Analysis",
        "Dirichlet Filter Isolation",
        "Sublinear k-Peak Recovery",
        "IDFT Epsilon Check",
      ];
      break;
    }

    case 4: {
      // Vector Reductions (Error Bound)
      const eps = Math.max(0.001, Math.min(0.05, paramValue));
      workEliminatedPct = 99.8;
      effectiveSpeedup = Math.round((1.0 / Math.max(0.001, eps * 2)) * 10) / 10;
      errorDelta = eps;
      contractSatisfied = eps <= 0.02;
      executionTimeMs = 0.05;
      gpuBruteForceTimeMs = 85.0;
      activePath = [
        "100GB Data Stream",
        "HyperLogLog 12KB Sketch",
        "L1 Cache Residency",
        "Count-Min Sketch Heavy Hitters",
        "Probabilistic Bound Verify",
      ];
      break;
    }

    case 5: {
      // Uncached LLM (Cache Hit Rate %)
      const hitRate = Math.max(5, Math.min(95, paramValue));
      workEliminatedPct = hitRate;
      effectiveSpeedup = Math.round(((hitRate * 200 + (100 - hitRate) * 2.5) / 100) * 10) / 10;
      errorDelta = 0.0;
      contractSatisfied = true;
      executionTimeMs =
        Math.round(((hitRate / 100) * 0.05 + (1 - hitRate / 100) * 8.0) * 100) / 100;
      gpuBruteForceTimeMs = 15.0;
      activePath = [
        "Query Embedding",
        "FAISS Vector Lattice Match",
        "0.05ms Zero-Compute Bypass",
        "Speculative PLD Context Decode",
        "Output Buffer",
      ];
      break;
    }

    case 7: {
      // 3D Rasterization (Target FPS)
      const fps = Math.max(30, Math.min(120, paramValue));
      workEliminatedPct = 75.0; // 540p vs 1080p
      effectiveSpeedup = 4.0;
      errorDelta = 0.04; // 1 - SSIM (0.96)
      contractSatisfied = fps >= 30;
      executionTimeMs = Math.round((1000.0 / fps) * 10) / 10;
      gpuBruteForceTimeMs = 45.0;
      activePath = [
        "Scene Geometry",
        "Coarse 540p Raymarching",
        "Subsampled SDF Shading",
        "Bilateral Temporal Upscaler",
        "60+ FPS Viewport",
      ];
      break;
    }

    case 10: {
      // Path Tracing (SPP)
      const spp = Math.max(1, Math.min(32, paramValue));
      workEliminatedPct = Math.round((1.0 - spp / 100.0) * 100 * 10) / 10;
      effectiveSpeedup = Math.round((100.0 / spp) * 1.5 * 10) / 10;
      errorDelta = Math.round((0.08 / Math.sqrt(spp)) * 1000) / 1000;
      contractSatisfied = spp >= 4;
      executionTimeMs = Math.round((spp * 3.5 + 12.0) * 10) / 10;
      gpuBruteForceTimeMs = 350.0;
      activePath = [
        "Camera Rays",
        "Sobol Low-Discrepancy QMC",
        "4-SPP Radiance Accumulation",
        "Intel OIDN CPU Neural Denoise",
        "PSNR 38dB Image",
      ];
      break;
    }

    case 12: {
      // N-Body Simulation (Bodies N)
      const n = Math.max(512, Math.min(32768, paramValue));
      const bruteFlops = n * n;
      const fmmFlops = n * Math.log2(n) * 8;
      workEliminatedPct = Math.round((1.0 - fmmFlops / bruteFlops) * 100 * 10) / 10;
      effectiveSpeedup = Math.round((bruteFlops / fmmFlops) * 10) / 10;
      errorDelta = 0.00004;
      contractSatisfied = true;
      executionTimeMs = Math.round(n * 0.003 * 10) / 10;
      gpuBruteForceTimeMs = Math.round(n * n * 0.00002 * 10) / 10;
      activePath = [
        "Particle Lattice",
        "Octree Hierarchical Partitioning",
        "Multipole Expansion Moments",
        "Local Harmonic Translations",
        "Symplectic Leapfrog Step",
      ];
      break;
    }

    default:
      workEliminatedPct = 85.0;
      effectiveSpeedup = module.workReductionFactor;
      errorDelta = 0.002;
      contractSatisfied = true;
      executionTimeMs = 15.0;
      gpuBruteForceTimeMs = 180.0;
      activePath = [
        "Input Contract",
        "Workload Classification",
        "Algorithmic Transformation",
        "Intel CPU/iGPU Scheduling",
        "Parity Verification",
      ];
      break;
  }

  return {
    workEliminatedPct,
    effectiveSpeedup,
    errorDelta,
    contractSatisfied,
    activePath,
    executionTimeMs,
    gpuBruteForceTimeMs,
  };
}

export function useBreakthroughStore() {
  const [runs, setRuns] = useState<SimulationResult[]>([]);
  const [customParams, setCustomParams] = useState<Record<number, number>>({});

  useEffect(() => {
    setRuns(loadSavedSimulationRuns());
    setCustomParams(loadCustomParams());
  }, []);

  const updateParam = (moduleId: number, value: number) => {
    saveCustomParam(moduleId, value);
    setCustomParams((prev) => ({ ...prev, [moduleId]: value }));
  };

  const recordRun = (result: SimulationResult) => {
    saveSimulationRun(result);
    setRuns((prev) => [result, ...prev.slice(0, 49)]);
  };

  return {
    runs,
    customParams,
    updateParam,
    recordRun,
  };
}
