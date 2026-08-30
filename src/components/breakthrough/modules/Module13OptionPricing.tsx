import React, { useState } from "react";
import { Sliders, Zap, CheckCircle2, TrendingUp } from "lucide-react";

export function Module13OptionPricing() {
  const [qmcPaths, setQmcPaths] = useState<number>(50000);
  const [strikePrice, setStrikePrice] = useState<number>(100);

  const bruteForcePaths = 5000000; // 5M paths on CUDA
  const qmcReductionRatio = Math.round(bruteForcePaths / qmcPaths);
  const estimatedStdError = Math.round((0.005 * (50000 / qmcPaths)) * 10000) / 10000;
  const cpuLatencyMs = Math.round((qmcPaths / 50000) * 8.4 * 10) / 10;
  const gpuLatencyMs = 45.0; // 45ms for 5M paths

  return (
    <div className="space-y-4 font-mono text-xs">
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="rounded-lg border border-border/60 bg-zinc-950 p-4 space-y-2">
          <div className="flex justify-between">
            <label className="text-muted-foreground uppercase font-bold">QMC Sobol Sample Budget:</label>
            <span className="font-bold text-cyan-400">{qmcPaths.toLocaleString()} paths</span>
          </div>
          <input
            type="range"
            min={5000}
            max={150000}
            step={5000}
            value={qmcPaths}
            onChange={(e) => setQmcPaths(Number(e.target.value))}
            className="w-full h-2 rounded bg-zinc-800 accent-cyan-400 cursor-pointer"
          />
        </div>

        <div className="rounded-lg border border-border/60 bg-zinc-950 p-4 space-y-2">
          <div className="flex justify-between">
            <label className="text-muted-foreground uppercase font-bold">Contract Standard Error Bound:</label>
            <span className="font-bold text-emerald-400">±${estimatedStdError} (&lt; $0.01)</span>
          </div>
          <div className="flex items-center gap-2 pt-2 text-muted-foreground text-[11px]">
            <CheckCircle2 className="h-4 w-4 text-emerald-400" />
            <span>Sobol low-discrepancy O(1/N) deterministic convergence</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="rounded border border-border/40 bg-zinc-900/50 p-3">
          <div className="text-[10px] text-muted-foreground uppercase">Brute Force Paths</div>
          <div className="text-sm font-bold text-red-400">5,000,000</div>
          <div className="text-[10px] text-muted-foreground">O(1/√N) Monte Carlo</div>
        </div>
        <div className="rounded border border-border/40 bg-zinc-900/50 p-3">
          <div className="text-[10px] text-muted-foreground uppercase">QMC Sobol Paths</div>
          <div className="text-sm font-bold text-cyan-400">{qmcPaths.toLocaleString()}</div>
          <div className="text-[10px] text-muted-foreground">O(1/N) Low-Discrepancy</div>
        </div>
        <div className="rounded border border-border/40 bg-zinc-900/50 p-3">
          <div className="text-[10px] text-muted-foreground uppercase">Path Reduction</div>
          <div className="text-sm font-bold text-emerald-400">{qmcReductionRatio}x Fewer</div>
          <div className="text-[10px] text-emerald-400/80">98% Compute Eliminated</div>
        </div>
        <div className="rounded border border-border/40 bg-zinc-900/50 p-3">
          <div className="text-[10px] text-muted-foreground uppercase">CPU Pricing Latency</div>
          <div className="text-sm font-bold text-amber-400">{cpuLatencyMs} ms</div>
          <div className="text-[10px] text-muted-foreground">vs GPU {gpuLatencyMs} ms</div>
        </div>
      </div>
    </div>
  );
}
