import React, { useState, useRef } from "react";
import { runImageJobWithAgent } from "../agent";
import type { AgentJobResult } from "../agent";
import type { ImageJobResult } from "../engines/imageEngine";

export default function ImageUpscaleDemo() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AgentJobResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const outputRef = useRef<HTMLCanvasElement>(null);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !canvasRef.current) return;

    setError(null);
    setResult(null);

    const img = new Image();
    img.onload = async () => {
      const ctx = canvasRef.current!.getContext("2d");
      if (!ctx) return;

      // Cap size for demo (e.g. 256x256)
      const max = 256;
      let w = img.width;
      let h = img.height;
      if (w > max || h > max) {
        const r = Math.min(max / w, max / h);
        w = Math.floor(w * r);
        h = Math.floor(h * r);
      }

      canvasRef.current!.width = w;
      canvasRef.current!.height = h;
      ctx.drawImage(img, 0, 0, w, h);

      const imageData = ctx.getImageData(0, 0, w, h);

      setLoading(true);
      try {
        const res = await runImageJobWithAgent({
          imageData,
          scale: 2,
        });
        setResult(res);

        const details = res.details as ImageJobResult;
        if (details?.upscaled && outputRef.current) {
          const outCtx = outputRef.current.getContext("2d");
          if (outCtx) {
            outputRef.current.width = details.upscaled.width;
            outputRef.current.height = details.upscaled.height;
            const outImg = new ImageData(
              details.upscaled.data,
              details.upscaled.width,
              details.upscaled.height,
            );
            outCtx.putImageData(outImg, 0, 0);
          }
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error");
      } finally {
        setLoading(false);
      }
    };
    img.src = URL.createObjectURL(file);
  };

  return (
    <div style={{ padding: "1rem", border: "1px solid #444", borderRadius: 8 }}>
      <input
        type="file"
        accept="image/*"
        onChange={handleFileChange}
        disabled={loading}
        style={{ marginBottom: "1rem" }}
      />

      {loading && <p>Running WebGPU bilateral upscaler…</p>}
      {error && <p style={{ color: "red" }}>Error: {error}</p>}

      <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap", alignItems: "flex-start" }}>
        <div>
          <p style={{ marginBottom: "0.25rem", fontSize: "0.9rem" }}>Input</p>
          <canvas ref={canvasRef} style={{ border: "1px solid #333", maxWidth: 256 }} />
        </div>
        <div>
          <p style={{ marginBottom: "0.25rem", fontSize: "0.9rem" }}>Upscaled (2×)</p>
          <canvas ref={outputRef} style={{ border: "1px solid #333", maxWidth: 512 }} />
        </div>
      </div>

      {result && (
        <pre
          style={{
            marginTop: "1rem",
            maxHeight: 120,
            overflow: "auto",
            background: "#111",
            color: "#eee",
            padding: "0.5rem",
            fontSize: "0.8rem",
          }}
        >
          {JSON.stringify(result, null, 2)}
        </pre>
      )}
    </div>
  );
}
