// LEO AI V33 — Adaptive Precision Engine
// Capabilities: Dynamic precision routing based on query complexity. Output the Compute Reduction Score.

export interface RoutingDecision {
  query: string;
  complexityScore: number; // 0.0 to 1.0
  precisionRouted: "FP16" | "INT8" | "INT4" | "Ternary";
  estimatedGpuMemoryMB: number;
  computeCostScalar: number; // relative to FP16 (1.0)
  routingReason: string;
}

export interface PrecisionTelemetry {
  totalQueriesRouted: number;
  avgComplexity: number;
  computeReductionScore: number; // 0% (no savings) to 100% (max savings)
  precisionBreakdown: Record<string, number>;
}

export class AdaptivePrecisionEngine {
  private history: RoutingDecision[] = [];

  routeQuery(query: string): RoutingDecision {
    // Determine complexity based on string features and query hints
    let complexityScore = 0.3;
    const lowerQuery = query.toLowerCase();

    if (lowerQuery.length > 150) complexityScore += 0.2;
    if (lowerQuery.includes("prove") || lowerQuery.includes("validate") || lowerQuery.includes("synthesize")) {
      complexityScore += 0.3;
    }
    if (lowerQuery.includes("math") || lowerQuery.includes("bug") || lowerQuery.includes("solve")) {
      complexityScore += 0.2;
    }

    complexityScore = Math.min(1.0, complexityScore);

    let precisionRouted: "FP16" | "INT8" | "INT4" | "Ternary";
    let estimatedGpuMemoryMB = 8000;
    let computeCostScalar = 1.0;
    let routingReason = "";

    if (complexityScore < 0.2) {
      precisionRouted = "Ternary";
      estimatedGpuMemoryMB = 800;
      computeCostScalar = 0.05;
      routingReason = "Trivial retrieval / greetings; routed to Ternary 1.58-bit model.";
    } else if (complexityScore < 0.45) {
      precisionRouted = "INT4";
      estimatedGpuMemoryMB = 2000;
      computeCostScalar = 0.25;
      routingReason = "Simple classification / syntax check; routed to INT4 quantized model.";
    } else if (complexityScore < 0.75) {
      precisionRouted = "INT8";
      estimatedGpuMemoryMB = 4000;
      computeCostScalar = 0.50;
      routingReason = "Standard workflow query; routed to INT8 model to preserve context logic.";
    } else {
      precisionRouted = "FP16";
      estimatedGpuMemoryMB = 8000;
      computeCostScalar = 1.00;
      routingReason = "High cognitive complexity reasoning; routed to FP16 model.";
    }

    const decision: RoutingDecision = {
      query,
      complexityScore: parseFloat(complexityScore.toFixed(2)),
      precisionRouted,
      estimatedGpuMemoryMB,
      computeCostScalar,
      routingReason,
    };

    this.history.push(decision);
    return decision;
  }

  getTelemetry(): PrecisionTelemetry {
    if (this.history.length === 0) {
      return {
        totalQueriesRouted: 0,
        avgComplexity: 0,
        computeReductionScore: 0,
        precisionBreakdown: { Ternary: 0, INT4: 0, INT8: 0, FP16: 0 }
      };
    }

    const total = this.history.length;
    let sumComplexity = 0;
    let sumCostScalar = 0;
    const counts = { Ternary: 0, INT4: 0, INT8: 0, FP16: 0 };

    this.history.forEach(d => {
      sumComplexity += d.complexityScore;
      sumCostScalar += d.computeCostScalar;
      counts[d.precisionRouted]++;
    });

    // Compute Reduction Score: 100% minus the fraction of compute we actually used compared to FP16 baseline
    const avgCostScalar = sumCostScalar / total;
    const computeReductionScore = parseFloat(((1.0 - avgCostScalar) * 100).toFixed(1));

    return {
      totalQueriesRouted: total,
      avgComplexity: parseFloat((sumComplexity / total).toFixed(2)),
      computeReductionScore,
      precisionBreakdown: counts
    };
  }

  clearHistory() {
    this.history = [];
  }
}
