import React, { useState, useEffect, useRef } from "react";
import { Sliders, Sparkles } from "lucide-react";

export function Module8ParticleSystem() {
  const [guideCount, setGuideCount] = useState<number>(10000);
  const [curlTurbulence, setCurlTurbulence] = useState<number>(1.5);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let animId: number;
    let t = 0;

    const render = () => {
      t += 0.02;
      const width = canvas.width;
      const height = canvas.height;

      ctx.fillStyle = "rgba(5, 8, 15, 0.25)";
      ctx.fillRect(0, 0, width, height);

      const renderCount = Math.min(250, guideCount / 40);
      for (let i = 0; i < renderCount; i++) {
        const seed = i * 137.5;
        const radius = 25 + Math.sin(t + i * 0.1) * 20 + ((i * 19) % 35);
        const angle = t * 0.8 + seed;

        // Curl noise offset
        const curlX = Math.sin(angle * curlTurbulence) * 25;
        const curlY = Math.cos(angle * curlTurbulence) * 25;

        const x = width / 2 + Math.cos(angle) * (radius + 20) + curlX;
        const y = height / 2 + Math.sin(angle) * (radius + 20) + curlY;

        ctx.fillStyle = i % 2 === 0 ? "#00f0ff" : "#ffb700";
        ctx.beginPath();
        ctx.arc(x, y, 1.8, 0, Math.PI * 2);
        ctx.fill();
      }

      animId = requestAnimationFrame(render);
    };

    render();
    return () => cancelAnimationFrame(animId);
  }, [guideCount, curlTurbulence]);

  return (
    <div className="space-y-4 font-mono text-xs">
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="rounded-lg border border-border/60 bg-zinc-950 p-4 space-y-2">
          <div className="flex justify-between">
            <label className="text-muted-foreground uppercase font-bold">
              Base Guide Particles:
            </label>
            <span className="font-bold text-cyan-400">{guideCount.toLocaleString()} Guides</span>
          </div>
          <input
            type="range"
            min={2000}
            max={50000}
            step={2000}
            value={guideCount}
            onChange={(e) => setGuideCount(Number(e.target.value))}
            className="w-full h-2 rounded bg-zinc-800 accent-cyan-400 cursor-pointer"
          />
        </div>

        <div className="rounded-lg border border-border/60 bg-zinc-950 p-4 space-y-2">
          <div className="flex justify-between">
            <label className="text-muted-foreground uppercase font-bold">
              Analytical Curl Turbulence:
            </label>
            <span className="font-bold text-amber-400">{curlTurbulence.toFixed(1)}x Vorticity</span>
          </div>
          <input
            type="range"
            min={0.5}
            max={3.0}
            step={0.1}
            value={curlTurbulence}
            onChange={(e) => setCurlTurbulence(Number(e.target.value))}
            className="w-full h-2 rounded bg-zinc-800 accent-amber-400 cursor-pointer"
          />
        </div>
      </div>

      <div className="rounded-lg border border-cyan-500/30 bg-black p-3 space-y-2">
        <div className="flex justify-between text-[11px] text-muted-foreground">
          <span className="text-cyan-400 font-bold">
            Real-Time Incompressible Curl Noise Vortex
          </span>
          <span className="text-amber-400">Equivalent Visual Fidelity: 1,000,000 Particles</span>
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
