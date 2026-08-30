import React, { useState } from "react";
import { Sliders, Sparkles, CheckCircle2 } from "lucide-react";

export function Module10PathTracing() {
  const [spp, setSpp] = useState<number>(4);
  const [enableOidn, setEnableOidn] = useState<boolean>(true);

  const baselineGpuSpp = 100;
  const workSavedPct = Math.round((1 - spp / baselineGpuSpp) * 100);
  const psnr = enableOidn ? Math.round((32 + Math.log2(spp) * 2.8) * 10) / 10 : Math.round((18 + Math.log2(spp) * 2.5) * 10) / 10;
  const ssim = enableOidn ? Math.min(0.98, Math.round((0.88 + Math.log2(spp) * 0.03) * 100) / 100) : 0.65;

  return (
    <div className="space-y-4 font-mono text-xs">
      <div className="rounded-lg border border-border/60 bg-zinc-950 p-4 space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <label className="text-muted-foreground uppercase flex items-center gap-1.5 font-bold">
            <Sliders className="h-3.5 w-3.5 text-cyan-400" /> Samples Per Pixel (SPP):
          </label>
          <span className="font-bold text-cyan-400">{spp} SPP (Sobol Low-Discrepancy)</span>
        </div>
        <input
          type="range"
          min={1}
          max={32}
          step={1}
          value={spp}
          onChange={(e) => setSpp(Number(e.target.value))}
          className="w-full h-2 rounded bg-zinc-800 accent-cyan-400 cursor-pointer"
        />
        <div className="flex items-center gap-2 pt-1">
          <label className="flex items-center gap-2 cursor-pointer text-zinc-300">
            <input
              type="checkbox"
              checked={enableOidn}
              onChange={(e) => setEnableOidn(e.target.checked)}
              className="rounded bg-zinc-800 accent-cyan-400 h-4 w-4"
            />
            <span>Enable Intel Open Image Denoise (OIDN CPU Neural Denoising Filter)</span>
          </label>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <div className="rounded border border-cyan-500/30 bg-cyan-950/20 p-3.5">
          <span className="text-muted-foreground uppercase text-[10px]">Work Eliminated</span>
          <div className="text-lg font-bold text-cyan-400 mt-1">{workSavedPct}% Rays Saved</div>
          <span className="text-[10px] text-cyan-300">{spp} SPP vs GPU 100 SPP</span>
        </div>

        <div className="rounded border border-amber-500/30 bg-amber-950/20 p-3.5">
          <span className="text-muted-foreground uppercase text-[10px]">Peak SNR Quality</span>
          <div className="text-lg font-bold text-amber-400 mt-1">{psnr} dB</div>
          <span className="text-[10px] text-amber-300">Broadcast Quality Standard: &gt;35 dB</span>
        </div>

        <div className="rounded border border-emerald-500/30 bg-emerald-950/20 p-3.5">
          <span className="text-muted-foreground uppercase text-[10px]">Structural Similarity</span>
          <div className="text-lg font-bold text-emerald-400 mt-1">SSIM {ssim}</div>
          <span className="text-[10px] text-emerald-300">Perceptually Indistinguishable</span>
        </div>
      </div>
    </div>
  );
}
