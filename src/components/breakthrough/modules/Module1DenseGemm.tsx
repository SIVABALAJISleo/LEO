import React, { useState } from "react";
import { Sliders, Cpu, Zap } from "lucide-react";

export function Module1DenseGemm() {
  const [rankRatio, setRankRatio] = useState<number>(0.08);
  const [useBitNetTernary, setUseBitNetTernary] = useState<boolean>(true);

  const N = 4096;
  const k = Math.max(8, Math.round(N * rankRatio));
  const bruteFlops = 2 * N ** 3; // 2 * 4096^3 = 137.4 GFLOPs
  const svdFlops = 2 * N ** 2 * k;
  const workSavedPct = Math.round((1 - svdFlops / bruteFlops) * 1000) / 10;
  const speedup = Math.round((bruteFlops / svdFlops) * 10) / 10;
  const errorBound = Math.round(rankRatio * 0.003 * 10000) / 10000;

  return (
    <div className="space-y-4 font-mono text-xs">
      <div className="rounded-lg border border-border/60 bg-zinc-950 p-4 space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <label className="text-muted-foreground uppercase flex items-center gap-1.5 font-bold">
            <Sliders className="h-3.5 w-3.5 text-cyan-400" /> Truncated Rank Ratio (k/N = {k}/{N}):
          </label>
          <span className="font-bold text-cyan-400">
            {(rankRatio * 100).toFixed(1)}% ({k} Eigenvectors)
          </span>
        </div>
        <input
          type="range"
          min={0.01}
          max={0.3}
          step={0.01}
          value={rankRatio}
          onChange={(e) => setRankRatio(Number(e.target.value))}
          className="w-full h-2 rounded bg-zinc-800 accent-cyan-400 cursor-pointer"
        />
        <div className="flex items-center gap-3 pt-1">
          <label className="flex items-center gap-2 cursor-pointer text-zinc-300">
            <input
              type="checkbox"
              checked={useBitNetTernary}
              onChange={(e) => setUseBitNetTernary(e.target.checked)}
              className="rounded bg-zinc-800 accent-cyan-400 h-4 w-4"
            />
            <span>Enable BitNet b1.58 Ternary Addition Kernels (Multiplication-Free)</span>
          </label>
        </div>
      </div>

      {/* Visual Bar Chart Comparison */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div className="rounded border border-red-500/30 bg-red-950/20 p-3.5 space-y-2">
          <div className="flex justify-between font-bold text-red-400">
            <span>GPU Full-Rank Brute Force</span>
            <span>137.4 GFLOPs</span>
          </div>
          <div className="w-full bg-zinc-800 h-3 rounded overflow-hidden">
            <div className="bg-red-500 h-full w-full" />
          </div>
          <span className="text-[11px] text-muted-foreground">
            O(N³) = 2×4096³ dense FP32 operations
          </span>
        </div>

        <div className="rounded border border-cyan-500/30 bg-cyan-950/20 p-3.5 space-y-2">
          <div className="flex justify-between font-bold text-cyan-400">
            <span>HYPER Randomized SVD + BitNet</span>
            <span>
              {(svdFlops / 1e9).toFixed(2)} {useBitNetTernary ? "G-Adds" : "GFLOPs"}
            </span>
          </div>
          <div className="w-full bg-zinc-800 h-3 rounded overflow-hidden">
            <div
              className="bg-cyan-400 h-full transition-all duration-300"
              style={{ width: `${Math.max(4, 100 - workSavedPct)}%` }}
            />
          </div>
          <span className="text-[11px] text-cyan-300">
            {workSavedPct}% Work Eliminated ({speedup}x speedup | ε = {errorBound})
          </span>
        </div>
      </div>
    </div>
  );
}
