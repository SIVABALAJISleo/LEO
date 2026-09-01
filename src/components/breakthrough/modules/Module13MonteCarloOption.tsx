import React, { useState } from "react";
import { Sliders, Zap } from "lucide-react";

export function Module13MonteCarloOption() {
  const [qmcPaths, setQmcPaths] = useState<number>(50000);

  const equivalentMcPaths = qmcPaths * 100; // O(1/N) vs O(1/sqrt(N))
  const stdError = Math.round((1.0 / qmcPaths) * 100000) / 100000;

  return (
    <div className="space-y-4 font-mono text-xs">
      <div className="rounded-lg border border-border/60 bg-zinc-950 p-4 space-y-2">
        <div className="flex justify-between">
          <label className="text-muted-foreground uppercase font-bold">
            Sobol Low-Discrepancy Simulated Paths:
          </label>
          <span className="font-bold text-amber-400">{qmcPaths.toLocaleString()} Paths</span>
        </div>
        <input
          type="range"
          min={5000}
          max={200000}
          step={5000}
          value={qmcPaths}
          onChange={(e) => setQmcPaths(Number(e.target.value))}
          className="w-full h-2 rounded bg-zinc-800 accent-amber-400 cursor-pointer"
        />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div className="rounded border border-red-500/30 bg-red-950/20 p-3.5 space-y-2">
          <span className="font-bold text-red-400">GPU Pseudo-Random MC (10M Paths)</span>
          <div className="text-sm font-bold text-red-300">
            {(equivalentMcPaths / 1e6).toFixed(1)} Million Paths Needed
          </div>
          <span className="text-[11px] text-muted-foreground">
            O(1/√N) slow convergence due to path clumping
          </span>
        </div>

        <div className="rounded border border-cyan-500/30 bg-cyan-950/20 p-3.5 space-y-2">
          <span className="font-bold text-cyan-400">HYPER Sobol QMC (Brownian Bridge)</span>
          <div className="text-sm font-bold text-cyan-300">
            {qmcPaths.toLocaleString()} Paths (100x fewer paths)
          </div>
          <span className="text-[11px] text-cyan-200">
            O(1/N) deterministic uniform spatial filling (StdError: {stdError})
          </span>
        </div>
      </div>
    </div>
  );
}
