import React, { useState } from "react";
import { Sliders, Cpu, Zap, CheckCircle2 } from "lucide-react";

export function Module11VideoPipeline() {
  const [bitrateMbps, setBitrateMbps] = useState<number>(15);

  return (
    <div className="space-y-4 font-mono text-xs">
      <div className="rounded-lg border border-border/60 bg-zinc-950 p-4 space-y-2">
        <div className="flex justify-between">
          <label className="text-muted-foreground uppercase font-bold">
            4K 60FPS Video Bitrate Target:
          </label>
          <span className="font-bold text-cyan-400">{bitrateMbps} Mbps (HEVC Main 10)</span>
        </div>
        <input
          type="range"
          min={4}
          max={50}
          step={1}
          value={bitrateMbps}
          onChange={(e) => setBitrateMbps(Number(e.target.value))}
          className="w-full h-2 rounded bg-zinc-800 accent-cyan-400 cursor-pointer"
        />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div className="rounded border border-red-500/30 bg-red-950/20 p-3.5 space-y-2">
          <span className="font-bold text-red-400">CPU Software Encode (libx265)</span>
          <div className="text-sm font-bold text-red-300">12 FPS (100% CPU Lockup)</div>
          <span className="text-[11px] text-muted-foreground">
            Software ALU cycles on P/E-cores
          </span>
        </div>

        <div className="rounded border border-cyan-500/30 bg-cyan-950/20 p-3.5 space-y-2">
          <span className="font-bold text-cyan-400">Intel QuickSync Hardware (MFX)</span>
          <div className="text-sm font-bold text-cyan-300">145 FPS (&lt;3% CPU Usage)</div>
          <span className="text-[11px] text-cyan-200">
            Dedicated on-die fixed-function ASIC silicon (Zero CPU load)
          </span>
        </div>
      </div>
    </div>
  );
}
