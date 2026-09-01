import React, { useState, useEffect, useRef } from "react";
import { Sliders, Activity } from "lucide-react";

export function Module3SparseFFT() {
  const [kSparsity, setKSparsity] = useState<number>(64);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const width = canvas.width;
    const height = canvas.height;
    ctx.clearRect(0, 0, width, height);

    // Draw background grid
    ctx.strokeStyle = "rgba(255, 255, 255, 0.05)";
    ctx.lineWidth = 1;
    for (let x = 0; x < width; x += 40) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
      ctx.stroke();
    }

    // Draw full spectrum noise (GPU calculates all)
    ctx.strokeStyle = "rgba(255, 50, 50, 0.25)";
    ctx.beginPath();
    for (let x = 0; x < width; x++) {
      const y = height / 2 + Math.sin(x * 0.2) * 5 + (Math.random() - 0.5) * 8;
      if (x === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();

    // Draw k dominant spectral peaks recovered by sFFT
    ctx.fillStyle = "#00f0ff";
    ctx.shadowColor = "#00f0ff";
    ctx.shadowBlur = 10;
    const step = width / (kSparsity / 4);
    for (let i = 0; i < kSparsity / 4; i++) {
      const peakX = 20 + i * step + ((i * 37) % 20);
      const peakHeight = 40 + Math.sin(i * 1.5) * 30 + ((i * 17) % 25);
      ctx.fillRect(peakX - 2, height / 2 - peakHeight, 4, peakHeight * 2);
    }
    ctx.shadowBlur = 0;
  }, [kSparsity]);

  return (
    <div className="space-y-4 font-mono text-xs">
      <div className="rounded-lg border border-border/60 bg-zinc-950 p-4 space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <label className="text-muted-foreground uppercase flex items-center gap-1.5 font-bold">
            <Sliders className="h-3.5 w-3.5 text-cyan-400" /> Recovered Dominant Frequencies (k):
          </label>
          <span className="font-bold text-cyan-400">{kSparsity} Peaks (out of 1,000,000 bins)</span>
        </div>
        <input
          type="range"
          min={16}
          max={256}
          step={16}
          value={kSparsity}
          onChange={(e) => setKSparsity(Number(e.target.value))}
          className="w-full h-2 rounded bg-zinc-800 accent-cyan-400 cursor-pointer"
        />
      </div>

      <div className="rounded-lg border border-cyan-500/30 bg-black p-3 space-y-2">
        <div className="flex justify-between text-[11px] text-muted-foreground">
          <span className="text-red-400">GPU: Computes all 1,000,000 bins O(N log N)</span>
          <span className="text-cyan-400 font-bold">
            HYPER sFFT: Recovers only {kSparsity} peaks in O(k log N)
          </span>
        </div>
        <canvas
          ref={canvasRef}
          width={600}
          height={140}
          className="w-full rounded bg-zinc-950 border border-border/40"
        />
      </div>
    </div>
  );
}
