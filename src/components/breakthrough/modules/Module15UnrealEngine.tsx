import React, { useState } from "react";
import { Sliders, Layers, CheckCircle2 } from "lucide-react";

export function Module15UnrealEngine() {
  const [distanceScale, setDistanceScale] = useState<number>(1.2);

  const rawTriangles = 10000000; // 10 Million
  const lodTriangles = Math.round(rawTriangles / (distanceScale * 4));
  const workSavedPct = Math.round((1 - lodTriangles / rawTriangles) * 100);
  const viewportFps = Math.round(28 + (1 / distanceScale) * 12);

  return (
    <div className="space-y-4 font-mono text-xs">
      <div className="rounded-lg border border-border/60 bg-zinc-950 p-4 space-y-2">
        <div className="flex justify-between">
          <label className="text-muted-foreground uppercase font-bold">Software Nanite Distance LOD Scale:</label>
          <span className="font-bold text-amber-400">{distanceScale.toFixed(1)}x Aggressiveness ({workSavedPct}% Geometry Culled)</span>
        </div>
        <input
          type="range"
          min={0.5}
          max={3.0}
          step={0.1}
          value={distanceScale}
          onChange={(e) => setDistanceScale(Number(e.target.value))}
          className="w-full h-2 rounded bg-zinc-800 accent-amber-400 cursor-pointer"
        />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div className="rounded border border-red-500/30 bg-red-950/20 p-3.5 space-y-2">
          <span className="font-bold text-red-400">GPU Hardware Mesh Shaders (10M Triangles)</span>
          <div className="text-sm font-bold text-red-300">10,000,000 Polygons Rasterized</div>
          <span className="text-[11px] text-muted-foreground">Hardware RT Lumen global illumination</span>
        </div>

        <div className="rounded border border-cyan-500/30 bg-cyan-950/20 p-3.5 space-y-2">
          <span className="font-bold text-cyan-400">HYPER Software Continuous LOD + Probes</span>
          <div className="text-sm font-bold text-cyan-300">
            {(lodTriangles / 1e6).toFixed(2)}M Triangles ({viewportFps} FPS Viewport)
          </div>
          <span className="text-[11px] text-cyan-200">
            Software occlusion culling + Screen-space diffuse irradiance caching
          </span>
        </div>
      </div>
    </div>
  );
}
