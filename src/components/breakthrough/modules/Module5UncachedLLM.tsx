import React, { useState } from "react";
import { Sliders, Zap, CheckCircle2 } from "lucide-react";

export function Module5UncachedLLM() {
  const [hitRate, setHitRate] = useState<number>(75);
  const [pldSpeedup, setPldSpeedup] = useState<number>(2.5);

  const gpuLatencyMs = 15.0; // 15ms per token on RTX 3060
  const cacheLatencyMs = 0.05; // 0.05ms FAISS lookup
  const uncachedCpuLatencyMs = 8.0 / pldSpeedup; // 3.2ms with PLD
  const effectiveLatencyMs =
    Math.round(
      ((hitRate / 100) * cacheLatencyMs + (1 - hitRate / 100) * uncachedCpuLatencyMs) * 100,
    ) / 100;
  const speedupOverGpu = Math.round((gpuLatencyMs / Math.max(0.01, effectiveLatencyMs)) * 10) / 10;

  return (
    <div className="space-y-4 font-mono text-xs">
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="rounded-lg border border-border/60 bg-zinc-950 p-4 space-y-2">
          <div className="flex justify-between">
            <label className="text-muted-foreground uppercase font-bold">
              Semantic Cache Hit Rate:
            </label>
            <span className="font-bold text-cyan-400">{hitRate}%</span>
          </div>
          <input
            type="range"
            min={10}
            max={95}
            step={5}
            value={hitRate}
            onChange={(e) => setHitRate(Number(e.target.value))}
            className="w-full h-2 rounded bg-zinc-800 accent-cyan-400 cursor-pointer"
          />
        </div>

        <div className="rounded-lg border border-border/60 bg-zinc-950 p-4 space-y-2">
          <div className="flex justify-between">
            <label className="text-muted-foreground uppercase font-bold">
              PLD Speculative Speedup:
            </label>
            <span className="font-bold text-amber-400">{pldSpeedup}x Draft Acceleration</span>
          </div>
          <input
            type="range"
            min={1.2}
            max={4.0}
            step={0.2}
            value={pldSpeedup}
            onChange={(e) => setPldSpeedup(Number(e.target.value))}
            className="w-full h-2 rounded bg-zinc-800 accent-amber-400 cursor-pointer"
          />
        </div>
      </div>

      <div className="rounded-lg border border-cyan-500/40 bg-cyan-950/20 p-4 flex flex-wrap items-center justify-between gap-4">
        <div>
          <span className="text-cyan-400 font-bold uppercase">Effective End-to-End Latency:</span>
          <p className="text-2xl font-black text-foreground mt-1">
            {effectiveLatencyMs} ms{" "}
            <span className="text-sm font-normal text-muted-foreground">
              vs GPU's {gpuLatencyMs} ms
            </span>
          </p>
        </div>
        <div className="flex items-center gap-2 rounded-lg bg-cyan-400/10 border border-cyan-400/30 px-3.5 py-2 text-cyan-300 font-bold">
          <Zap className="h-4 w-4 text-amber-400" />
          {speedupOverGpu}x Faster than Discrete GPU
        </div>
      </div>
    </div>
  );
}
