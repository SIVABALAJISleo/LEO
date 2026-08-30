import React, { useState } from "react";
import { Sliders, Layers, CheckCircle2 } from "lucide-react";

export function Module9BVHConstruction() {
  const [dynamicRatio, setDynamicRatio] = useState<number>(15);
  const [isStaticScene, setIsStaticScene] = useState<boolean>(false);

  const totalTriangles = 500000;
  const dynamicTriangles = isStaticScene ? 0 : Math.round(totalTriangles * (dynamicRatio / 100));
  const fullRebuildMs = 45.0;
  const lbvhRefitMs = isStaticScene ? 0.0 : Math.round((dynamicTriangles / totalTriangles) * 6.5 * 10) / 10;
  const speedup = Math.round((fullRebuildMs / Math.max(0.1, lbvhRefitMs)) * 10) / 10;

  return (
    <div className="space-y-4 font-mono text-xs">
      <div className="rounded-lg border border-border/60 bg-zinc-950 p-4 space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <label className="text-muted-foreground uppercase flex items-center gap-1.5 font-bold">
            <Sliders className="h-3.5 w-3.5 text-cyan-400" /> Moving Geometry Ratio:
          </label>
          <span className="font-bold text-cyan-400">
            {isStaticScene ? "0% (Fully Cached)" : `${dynamicRatio}% (${(dynamicTriangles / 1000).toFixed(0)}k Triangles)`}
          </span>
        </div>
        <input
          type="range"
          min={5}
          max={100}
          step={5}
          disabled={isStaticScene}
          value={dynamicRatio}
          onChange={(e) => setDynamicRatio(Number(e.target.value))}
          className="w-full h-2 rounded bg-zinc-800 accent-cyan-400 cursor-pointer disabled:opacity-30"
        />
        <div className="flex items-center gap-2 pt-1">
          <label className="flex items-center gap-2 cursor-pointer text-zinc-300">
            <input
              type="checkbox"
              checked={isStaticScene}
              onChange={(e) => setIsStaticScene(e.target.checked)}
              className="rounded bg-zinc-800 accent-cyan-400 h-4 w-4"
            />
            <span>Static Scene (Cache BVH Tree Permanently in Host RAM)</span>
          </label>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div className="rounded border border-red-500/30 bg-red-950/20 p-3.5 space-y-2">
          <span className="font-bold text-red-400">GPU SAH Tree Rebuild (Scratch)</span>
          <div className="text-sm font-bold text-red-300">45.0 ms / frame</div>
          <span className="text-[11px] text-muted-foreground">O(T log T) Full sorting on 500,000 triangles</span>
        </div>

        <div className="rounded border border-cyan-500/30 bg-cyan-950/20 p-3.5 space-y-2">
          <span className="font-bold text-cyan-400">HYPER Morton Curve LBVH Refit</span>
          <div className="text-sm font-bold text-cyan-300">
            {lbvhRefitMs} ms / frame ({speedup}x faster)
          </div>
          <span className="text-[11px] text-cyan-200">
            O(T) Bottom-up AABB Refitting only on moved nodes
          </span>
        </div>
      </div>
    </div>
  );
}
