import React, { useState } from "react";
import { Sliders, Database, Zap } from "lucide-react";

export function Module4VectorReductions() {
  const [tolerance, setTolerance] = useState<number>(0.01);

  const rawElements = 1000000000; // 1 Billion records
  const gpuMemoryRequiredGb = (rawElements * 8) / (1024 ** 3); // 7.45 GB
  const hllRegisters = Math.round((1.04 / tolerance) ** 2);
  const hllMemoryKb = Math.round((hllRegisters * 6) / 8 / 1024 * 10) / 10;
  const memoryReductionRatio = Math.round((gpuMemoryRequiredGb * 1024 * 1024) / hllMemoryKb);

  return (
    <div className="space-y-4 font-mono text-xs">
      <div className="rounded-lg border border-border/60 bg-zinc-950 p-4 space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <label className="text-muted-foreground uppercase flex items-center gap-1.5 font-bold">
            <Sliders className="h-3.5 w-3.5 text-amber-400" /> Relative Error Bound (ε):
          </label>
          <span className="font-bold text-amber-400">±{(tolerance * 100).toFixed(2)}% Error</span>
        </div>
        <input
          type="range"
          min={0.002}
          max={0.05}
          step={0.002}
          value={tolerance}
          onChange={(e) => setTolerance(Number(e.target.value))}
          className="w-full h-2 rounded bg-zinc-800 accent-amber-400 cursor-pointer"
        />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div className="rounded border border-red-500/30 bg-red-950/20 p-3.5 space-y-2">
          <span className="font-bold text-red-400">GPU Exact Memory Sweep</span>
          <p className="text-muted-foreground text-[11px]">
            Reads all 1,000,000,000 elements from global VRAM:
          </p>
          <div className="text-sm font-bold text-red-300">
            {gpuMemoryRequiredGb.toFixed(2)} GB VRAM Footprint
          </div>
        </div>

        <div className="rounded border border-cyan-500/30 bg-cyan-950/20 p-3.5 space-y-2">
          <span className="font-bold text-cyan-400">HYPER HyperLogLog++ Sketch</span>
          <p className="text-muted-foreground text-[11px]">
            Streams into {hllRegisters.toLocaleString()} registers (L1 Cache Resident):
          </p>
          <div className="text-sm font-bold text-cyan-300">
            {hllMemoryKb} KB RAM ({memoryReductionRatio.toLocaleString()}x smaller)
          </div>
        </div>
      </div>
    </div>
  );
}
