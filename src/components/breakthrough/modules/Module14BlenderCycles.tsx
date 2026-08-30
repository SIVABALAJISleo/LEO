import React, { useState } from "react";
import { Sliders, Sparkles, CheckCircle2 } from "lucide-react";

export function Module14BlenderCycles() {
  const [spp, setSpp] = useState<number>(16);

  const baselineSpp = 512;
  const cpuEmbreeTimeSec = Math.round(((spp / baselineSpp) * 580 + 3.2) * 10) / 10;
  const gpuCyclesTimeSec = 28.0; // RTX 3060 at 512 SPP

  return (
    <div className="space-y-4 font-mono text-xs">
      <div className="rounded-lg border border-border/60 bg-zinc-950 p-4 space-y-2">
        <div className="flex justify-between">
          <label className="text-muted-foreground uppercase font-bold">Cycles Adaptive SPP + Intel OIDN:</label>
          <span className="font-bold text-cyan-400">{spp} SPP (Intel Embree CPU Kernels)</span>
        </div>
        <input
          type="range"
          min={4}
          max={64}
          step={4}
          value={spp}
          onChange={(e) => setSpp(Number(e.target.value))}
          className="w-full h-2 rounded bg-zinc-800 accent-cyan-400 cursor-pointer"
        />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div className="rounded border border-red-500/30 bg-red-950/20 p-3.5 space-y-2">
          <span className="font-bold text-red-400">GPU Cycles 512 SPP Brute Force</span>
          <div className="text-sm font-bold text-red-300">{gpuCyclesTimeSec} seconds</div>
          <span className="text-[11px] text-muted-foreground">512 raw samples without intelligent denoising</span>
        </div>

        <div className="rounded border border-cyan-500/30 bg-cyan-950/20 p-3.5 space-y-2">
          <span className="font-bold text-cyan-400">HYPER 16-SPP Embree + OIDN Denoise</span>
          <div className="text-sm font-bold text-cyan-300">{cpuEmbreeTimeSec} seconds</div>
          <span className="text-[11px] text-cyan-200">
            32x sample reduction with native Intel Embree ray traversal
          </span>
        </div>
      </div>
    </div>
  );
}
