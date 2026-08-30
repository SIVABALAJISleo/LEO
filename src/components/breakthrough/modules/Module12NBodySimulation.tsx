import React, { useState } from "react";
import { Sliders, Activity } from "lucide-react";

export function Module12NBodySimulation() {
  const [numBodies, setNumBodies] = useState<number>(4096);

  const directPairs = (numBodies * (numBodies - 1)) / 2;
  const fmmInteractions = Math.round(numBodies * Math.log2(numBodies) * 6);
  const workSavedPct = Math.round((1 - fmmInteractions / directPairs) * 1000) / 10;
  const speedup = Math.round((directPairs / fmmInteractions) * 10) / 10;

  return (
    <div className="space-y-4 font-mono text-xs">
      <div className="rounded-lg border border-border/60 bg-zinc-950 p-4 space-y-2">
        <div className="flex justify-between">
          <label className="text-muted-foreground uppercase font-bold">Simulated Gravitational Bodies (N):</label>
          <span className="font-bold text-cyan-400">{numBodies.toLocaleString()} Bodies</span>
        </div>
        <input
          type="range"
          min={512}
          max={16384}
          step={512}
          value={numBodies}
          onChange={(e) => setNumBodies(Number(e.target.value))}
          className="w-full h-2 rounded bg-zinc-800 accent-cyan-400 cursor-pointer"
        />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div className="rounded border border-red-500/30 bg-red-950/20 p-3.5 space-y-2">
          <span className="font-bold text-red-400">GPU All-Pairs Brute Force O(N²)</span>
          <div className="text-sm font-bold text-red-300">
            {(directPairs / 1e6).toFixed(2)} Million Interactions
          </div>
          <span className="text-[11px] text-muted-foreground">Every body interacts with every single other body</span>
        </div>

        <div className="rounded border border-cyan-500/30 bg-cyan-950/20 p-3.5 space-y-2">
          <span className="font-bold text-cyan-400">HYPER Fast Multipole Method O(N)</span>
          <div className="text-sm font-bold text-cyan-300">
            {(fmmInteractions / 1000).toFixed(0)}k Cluster Expansions ({speedup}x speedup)
          </div>
          <span className="text-[11px] text-cyan-200">
            {workSavedPct}% interactions eliminated via spherical harmonics
          </span>
        </div>
      </div>
    </div>
  );
}
