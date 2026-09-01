import React, { useState, useEffect, useRef } from "react";
import { Sliders, Sparkles } from "lucide-react";

export function Module7Rasterization() {
  const [splitPos, setSplitPos] = useState<number>(50);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const width = canvas.width;
    const height = canvas.height;
    ctx.clearRect(0, 0, width, height);

    const splitX = (splitPos / 100) * width;

    // Draw left side: 1/4 Coarse Res Subsampled Pixelated Grid
    ctx.save();
    ctx.beginPath();
    ctx.rect(0, 0, splitX, height);
    ctx.clip();

    const blockSize = 16;
    for (let x = 0; x < splitX; x += blockSize) {
      for (let y = 0; y < height; y += blockSize) {
        const dist = Math.sqrt((x - width / 2) ** 2 + (y - height / 2) ** 2);
        const shade = Math.floor(Math.max(10, 240 - dist * 0.9));
        ctx.fillStyle = `rgb(${Math.floor(shade * 0.2)}, ${Math.floor(shade * 0.8)}, ${shade})`;
        ctx.fillRect(x, y, blockSize - 1, blockSize - 1);
      }
    }
    ctx.restore();

    // Draw right side: Bilateral Neural Reconstructed High-Res 1080p Image
    ctx.save();
    ctx.beginPath();
    ctx.rect(splitX, 0, width - splitX, height);
    ctx.clip();

    const gradient = ctx.createRadialGradient(
      width / 2,
      height / 2,
      10,
      width / 2,
      height / 2,
      140,
    );
    gradient.addColorStop(0, "#00f0ff");
    gradient.addColorStop(0.5, "#005588");
    gradient.addColorStop(1, "#050b14");

    ctx.fillStyle = gradient;
    ctx.fillRect(splitX, 0, width - splitX, height);
    ctx.restore();

    // Draw dividing line
    ctx.strokeStyle = "#ffffff";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(splitX, 0);
    ctx.lineTo(splitX, height);
    ctx.stroke();
  }, [splitPos]);

  return (
    <div className="space-y-4 font-mono text-xs">
      <div className="rounded-lg border border-border/60 bg-zinc-950 p-4 space-y-2">
        <div className="flex justify-between">
          <label className="text-muted-foreground uppercase font-bold">
            Split Screen Comparison Slider:
          </label>
          <span className="font-bold text-cyan-400">
            Left: 540p Subsampled | Right: Neural Reconstructed (SSIM 0.96)
          </span>
        </div>
        <input
          type="range"
          min={10}
          max={90}
          value={splitPos}
          onChange={(e) => setSplitPos(Number(e.target.value))}
          className="w-full h-2 rounded bg-zinc-800 accent-cyan-400 cursor-pointer"
        />
      </div>

      <div className="rounded-lg border border-cyan-500/30 bg-black p-3 space-y-2">
        <div className="flex justify-between text-[11px] text-muted-foreground">
          <span className="text-amber-400 font-bold">540p 25% Pixel Budget (18ms)</span>
          <span className="text-cyan-400 font-bold">Bilateral Reconstructed 1080p (60+ FPS)</span>
        </div>
        <canvas
          ref={canvasRef}
          width={600}
          height={160}
          className="w-full rounded bg-zinc-950 border border-border/40"
        />
      </div>
    </div>
  );
}
