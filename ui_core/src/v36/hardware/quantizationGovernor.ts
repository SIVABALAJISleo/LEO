// LEO AI V36 — Quantization Governor
// Directs GGUF and llama.cpp weight scales dynamically based on RAM pressure.

export class QuantizationGovernor {
  public determineBitrate(ramUsagePct: number): number {
    if (ramUsagePct > 90.0) return 2; // Q2_K
    if (ramUsagePct > 75.0) return 4; // Q4_K_M
    if (ramUsagePct > 50.0) return 8; // Q8_0
    return 16; // FP16 fallback
  }
}
