import React, { useState } from "react";
import { Sliders, Cpu, Zap } from "lucide-react";

export function Module2TensorGemm() {
  const [sparsity, setSparsity] = useState<number>(65);

  const totalParams = 1000000;
  const zeroWeights = Math.round(totalParams * (sparsity / 100));
  const posWeights = Math.round((totalParams - zeroWeights) / 2);
  const negWeights = totalParams - zeroWeights - posWeights;

  return (
    <div className="space-y-4 font-mono text-xs">
      <div className="rounded-lg border border-border/60 bg-zinc-950 p-4 space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <label className="text-muted-foreground uppercase flex items-center gap-1.5 font-bold">
            <Sliders className="h-3.5 w-3.5 text-amber-400" /> Ternary Zero-Weight Sparsity:
          </label>
          <span className="font-bold text-amber-400">{sparsity}% (Zero Multiplies)</span>
        </div>
        <input
          type="range"
          min={20}
          max={90}
          step={5}
          value={sparsity}
          onChange={(e) => setSparsity(Number(e.target.value))}
          className="w-full h-2 rounded bg-zinc-800 accent-amber-400 cursor-pointer"
        />
      </div>

      {/* Ternary Weight Distribution Visualization */}
      <div className="rounded-lg border border-cyan-500/30 bg-black/60 p-4 space-y-3">
        <span className="text-muted-foreground uppercase font-bold text-[11px]">
          1.58-Bit Ternary Weight Allocation ({"{-1, 0, +1}"}):
        </span>
        <div className="flex h-5 w-full rounded overflow-hidden text-[10px] font-bold text-black">
          <div
            className="bg-emerald-400 flex items-center justify-center transition-all"
            style={{ width: `${(posWeights / totalParams) * 100}%` }}
          >
            +1 ({(posWeights / 1000).toFixed(0)}k)
          </div>
          <div
            className="bg-zinc-700 text-zinc-300 flex items-center justify-center transition-all"
            style={{ width: `${(zeroWeights / totalParams) * 100}%` }}
          >
            0 (BYPASSED)
          </div>
          <div
            className="bg-red-400 flex items-center justify-center transition-all"
            style={{ width: `${(negWeights / totalParams) * 100}%` }}
          >
            -1 ({(negWeights / 1000).toFixed(0)}k)
          </div>
        </div>
        <div className="flex justify-between text-[11px] text-muted-foreground">
          <span className="text-emerald-400">
            Positive Additions: {(posWeights / 1000).toFixed(0)}k
          </span>
          <span className="text-zinc-400">
            Zero Multiplications: {(zeroWeights / 1000).toFixed(0)}k
          </span>
          <span className="text-red-400">
            Negative Subtractions: {(negWeights / 1000).toFixed(0)}k
          </span>
        </div>
      </div>
    </div>
  );
}
