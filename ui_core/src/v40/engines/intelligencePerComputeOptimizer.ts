export interface OptimizationMetrics {
  reasoningPerFlopPercent: number;
  knowledgePerGbMb: number;
  accuracyPerWattMultiplier: number;
  utilityPerDollarScore: number;
  scientificAccuracyRate: number;
  overallScore: number;
}
export class IntelligencePerComputeOptimizer {
  public async aggregateOptimizerMetrics(
    ramLimitGb: number,
    powerMode: string,
    quantizationBits: number,
  ): Promise<OptimizationMetrics> {
    const res = await fetch("http://localhost:8000/api/v1/v40/engines/optimizer", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ramLimitGb, powerMode, quantizationBits }),
    });
    return res.json();
  }
}
