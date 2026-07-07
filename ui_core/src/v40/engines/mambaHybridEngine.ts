export interface MambaTelemetry { contextLengthTokens: number; memoryUsageMb: number; attentionFlops: number; mambaFlops: number; speedupVsTransformer: number; }
export class MambaHybridEngine {
  public async projectScalingMetrics(contextLength: number): Promise<MambaTelemetry> {
    const res = await fetch("http://localhost:8000/api/v1/v40/engines/mamba", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ contextLength })
    });
    return res.json();
  }
}
