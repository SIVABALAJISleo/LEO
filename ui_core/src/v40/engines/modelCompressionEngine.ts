export interface CompressionDirectives { quantizationBitrate: number; loraRank: number; pruningRatio: number; expectedMemoryMb: number; precisionMode: "FP16" | "INT8" | "INT4" | "Ternary_1.58b"; }
export class ModelCompressionEngine {
  public async evaluateCompression(ramLimitGb: number): Promise<CompressionDirectives> {
    const res = await fetch("http://localhost:8000/api/v1/v40/engines/compression", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ramLimitGb })
    });
    return res.json();
  }
}
