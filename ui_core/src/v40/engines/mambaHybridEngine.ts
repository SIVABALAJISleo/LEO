export interface MambaTelemetry {
  contextLengthTokens: number;
  memoryUsageMb: number;
  attentionFlops: number;
  mambaFlops: number;
  speedupVsTransformer: number;
  tokensPerSec: number;
  effectiveFlops: number;
}

export type SpeculativeMode = "PEARL" | "EAGLE-3" | "OFF";

export interface MambaConfig {
  hybridRatio: number; // 0 (Full Transformer) to 1 (Full Mamba)
  contextLength: number;
  speculativeMode: SpeculativeMode;
}

export class MambaHybridEngine {
  public config: MambaConfig = {
    hybridRatio: 0.5,
    contextLength: 4096,
    speculativeMode: "PEARL",
  };

  public setHybridRatio(ratio: number) {
    this.config.hybridRatio = Math.max(0, Math.min(1, ratio));
  }

  public setContextLength(length: number) {
    this.config.contextLength = length;
  }

  public setSpeculativeMode(mode: SpeculativeMode) {
    this.config.speculativeMode = mode;
  }

  public async projectScalingMetrics(): Promise<MambaTelemetry> {
    try {
      const res = await fetch("http://localhost:8000/api/v1/v40/engines/mamba", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          contextLength: this.config.contextLength,
          hybridRatio: this.config.hybridRatio,
          speculativeMode: this.config.speculativeMode,
        }),
      });
      return await res.json();
    } catch (e) {
      console.error("Failed to project Mamba scaling metrics", e);
      // Return simulated fallback for demo if backend is not available
      return this.simulateLinearScalingDemo();
    }
  }

  /**
   * Linear scaling demo: shows O(n) vs O(n^2) computational difference
   */
  private simulateLinearScalingDemo(): MambaTelemetry {
    const N = this.config.contextLength;

    // O(n^2) Attention FLOPs approximation
    const attentionFlops = N * N * 2;

    // O(n) Mamba FLOPs approximation (linear with hidden size constants)
    const mambaFlops = N * 16 * 2;

    // Combine based on hybrid ratio
    const effectiveFlops =
      attentionFlops * (1 - this.config.hybridRatio) + mambaFlops * this.config.hybridRatio;

    let tokensPerSec = 12.0; // Base CPU speed

    // Speculative decoding speedup multiplier
    if (this.config.speculativeMode === "PEARL") tokensPerSec *= 3.5;
    else if (this.config.speculativeMode === "EAGLE-3") tokensPerSec *= 2.8;

    return {
      contextLengthTokens: N,
      memoryUsageMb: (N * 2) / 1024, // simplified 2KB per token
      attentionFlops,
      mambaFlops,
      speedupVsTransformer: attentionFlops / effectiveFlops,
      tokensPerSec,
      effectiveFlops,
    };
  }
}
