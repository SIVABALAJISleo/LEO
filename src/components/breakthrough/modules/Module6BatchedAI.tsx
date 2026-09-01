import React, { useState } from "react";
import { Sliders, Cpu, ArrowRight } from "lucide-react";

export function Module6BatchedAI() {
  const [batchSize, setBatchSize] = useState<number>(16);

  const gpuQueueDelayMs = (batchSize - 1) * 12.5; // queuing delay to fill batch
  const gpuComputeTimeMs = 35.0;
  const gpuTotalLatencyMs = gpuQueueDelayMs + gpuComputeTimeMs;

  const hyperBatch1LatencyMs = 18.0; // dedicated single-user latency

  return (
    <div className="space-y-4 font-mono text-xs">
      <div className="rounded-lg border border-border/60 bg-zinc-950 p-4 space-y-2">
        <div className="flex justify-between">
          <label className="text-muted-foreground uppercase font-bold">
            Multi-Tenant Server Batch Size (B):
          </label>
          <span className="font-bold text-amber-400">
            Batch-{batchSize} ({gpuQueueDelayMs.toFixed(0)}ms Queuing Latency)
          </span>
        </div>
        <input
          type="range"
          min={1}
          max={32}
          step={1}
          value={batchSize}
          onChange={(e) => setBatchSize(Number(e.target.value))}
          className="w-full h-2 rounded bg-zinc-800 accent-amber-400 cursor-pointer"
        />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div className="rounded border border-red-500/30 bg-red-950/20 p-3.5 space-y-2">
          <span className="font-bold text-red-400">Cloud GPU Server (Batch-{batchSize})</span>
          <div className="text-sm font-bold text-red-300">
            {gpuTotalLatencyMs.toFixed(0)} ms TTFT
          </div>
          <span className="text-[11px] text-muted-foreground">
            Queuing Delay: {gpuQueueDelayMs.toFixed(0)}ms | High Multi-User Throughput, Poor
            Single-User Latency
          </span>
        </div>

        <div className="rounded border border-cyan-500/30 bg-cyan-950/20 p-3.5 space-y-2">
          <span className="font-bold text-cyan-400">LEO Local Interactive (Batch-1)</span>
          <div className="text-sm font-bold text-cyan-300">{hyperBatch1LatencyMs} ms TTFT</div>
          <span className="text-[11px] text-cyan-200">
            0ms Queuing Delay | Instant Local P-Core Response
          </span>
        </div>
      </div>
    </div>
  );
}
