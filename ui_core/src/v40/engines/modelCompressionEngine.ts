export interface CompressionDirectives {
  quantizationBitrate: number;
  loraRank: number;
  pruningRatio: number;
  expectedMemoryMb: number;
  precisionMode: "FP16" | "INT8" | "INT4" | "Ternary_1.58b";
}

export interface BitNetConfig {
  bitnetModeActive: boolean;
  precision: "1.58-bit" | "2-bit" | "4-bit fallback";
  activationsBitrate: 8 | 16;
}

export interface BitNetTelemetry {
  compressionRatio: number;
  inferenceSpeedup: number;
}

export class ModelCompressionEngine {
  public config: BitNetConfig = {
    bitnetModeActive: true,
    precision: "1.58-bit",
    activationsBitrate: 8,
  };

  public telemetry: BitNetTelemetry = {
    compressionRatio: 0,
    inferenceSpeedup: 0,
  };

  public toggleBitNetMode(active: boolean) {
    this.config.bitnetModeActive = active;
  }

  public setPrecision(precision: BitNetConfig["precision"]) {
    this.config.precision = precision;
    // Activations match BitNet paper (8-bit)
    if (precision === "1.58-bit") {
      this.config.activationsBitrate = 8;
    }
  }

  public async evaluateCompression(ramLimitGb: number): Promise<CompressionDirectives> {
    const res = await fetch("http://localhost:8000/api/v1/v40/engines/compression", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ramLimitGb, bitnetConfig: this.config }),
    });
    return res.json();
  }

  public async fetchBitNetTelemetry(): Promise<BitNetTelemetry> {
    try {
      const res = await fetch("http://localhost:8000/api/v1/inference/bitnet/telemetry");
      const data = await res.json();
      this.telemetry.compressionRatio = data.compression_ratio;
      this.telemetry.inferenceSpeedup = data.inference_speedup;
      return this.telemetry;
    } catch (e) {
      console.error("Failed to fetch BitNet telemetry", e);
      return this.telemetry;
    }
  }
}
