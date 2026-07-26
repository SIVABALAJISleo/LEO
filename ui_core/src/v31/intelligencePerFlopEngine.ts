// LEO AI V31 — Phase 17 Intelligence Per FLOP Engine
// Metrics: Reasoning Quality (1-10 scale) ÷ FLOPS Consumed (GFLOPS)
// Goal: Maximize useful intelligence per FLOP.

export interface FlopEfficiencyReport {
  flopsGiga: number;
  reasoningQualityScore: number; // 0 to 10 scale
  efficiencyCoefficient: number; // Quality / GigaFlop
  classification: "SubOptimal" | "Standard" | "HighlyEfficient" | "OptimalAvoidance";
}

export class IntelligencePerFlopEngine {
  calculateEfficiency(flopsGiga: number, reasoningQualityScore: number): FlopEfficiencyReport {
    // If FLOPS is zero (because we hit a local cache), efficiency coefficient is maximum
    const effectiveFlops = flopsGiga || 0.001;
    const coeff = parseFloat((reasoningQualityScore / effectiveFlops).toFixed(3));

    let classification: "SubOptimal" | "Standard" | "HighlyEfficient" | "OptimalAvoidance" =
      "Standard";
    if (flopsGiga === 0) {
      classification = "OptimalAvoidance";
    } else if (coeff > 5.0) {
      classification = "HighlyEfficient";
    } else if (coeff < 0.2) {
      classification = "SubOptimal";
    }

    return {
      flopsGiga,
      reasoningQualityScore,
      efficiencyCoefficient: coeff,
      classification,
    };
  }
}
