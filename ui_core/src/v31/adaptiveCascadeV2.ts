// LEO AI V31 — Phase 11 Adaptive Model Cascade V2
// Models: Tiny (1B) → Small (7B) → Medium (13B) → Large (70B)
// Routing: Confidence-Based. Evaluates using the smallest model capable of solving the task.

export type ModelTier = "Tiny_1B" | "Small_7B" | "Medium_13B" | "Large_70B";

export interface CascadeStepV2 {
  tier: ModelTier;
  confidenceScore: number;
  thresholdScore: number;
  routed: boolean;
  resolved: boolean;
  flopsConsumedGiga: number;
  latencySec: number;
}

export interface CascadeResultV2 {
  query: string;
  steps: CascadeStepV2[];
  finalModelTier: ModelTier;
  totalFlopsGiga: number;
  totalLatencySec: number;
  resolvedAnswer: string;
}

export class AdaptiveCascadeV2 {
  private threshold = 0.80; // Confidence threshold to stop cascading

  evaluate(query: string): CascadeResultV2 {
    const steps: CascadeStepV2[] = [];
    const queryLower = query.toLowerCase();

    // Determine target complexity features
    const hasMath = queryLower.includes("solve") || queryLower.includes("equation") || queryLower.includes("calculate");
    const hasReasoning = queryLower.includes("why") || queryLower.includes("prove") || queryLower.includes("logic");
    const isUltraLong = query.length > 80;

    let solved = false;
    let totalFlops = 0;
    let totalLatency = 0;
    let finalModelTier: ModelTier = "Tiny_1B";

    // Tier 1: Tiny (1B)
    {
      // Tiny struggles with math and reasoning
      let conf = 0.90;
      if (hasMath) conf -= 0.35;
      if (hasReasoning) conf -= 0.30;
      if (isUltraLong) conf -= 0.15;
      conf = parseFloat(Math.max(0.1, conf).toFixed(2));
      
      const flops = 1.2;
      const latency = 0.05;
      totalFlops += flops;
      totalLatency += latency;
      
      const resolved = conf >= this.threshold;
      steps.push({
        tier: "Tiny_1B",
        confidenceScore: conf,
        thresholdScore: this.threshold,
        routed: true,
        resolved,
        flopsConsumedGiga: flops,
        latencySec: latency
      });
      
      if (resolved) {
        solved = true;
        finalModelTier = "Tiny_1B";
      }
    }

    // Tier 2: Small (7B)
    if (!solved) {
      let conf = 0.88;
      if (hasMath) conf -= 0.20;
      if (hasReasoning) conf -= 0.15;
      conf = parseFloat(Math.max(0.1, conf).toFixed(2));

      const flops = 8.4;
      const latency = 0.12;
      totalFlops += flops;
      totalLatency += latency;

      const resolved = conf >= this.threshold;
      steps.push({
        tier: "Small_7B",
        confidenceScore: conf,
        thresholdScore: this.threshold,
        routed: true,
        resolved,
        flopsConsumedGiga: flops,
        latencySec: latency
      });

      if (resolved) {
        solved = true;
        finalModelTier = "Small_7B";
      }
    } else {
      steps.push({ tier: "Small_7B", confidenceScore: 0, thresholdScore: this.threshold, routed: false, resolved: false, flopsConsumedGiga: 0, latencySec: 0 });
    }

    // Tier 3: Medium (13B)
    if (!solved) {
      let conf = 0.94;
      if (hasMath) conf -= 0.10;
      conf = parseFloat(Math.max(0.1, conf).toFixed(2));

      const flops = 15.6;
      const latency = 0.26;
      totalFlops += flops;
      totalLatency += latency;

      const resolved = conf >= this.threshold;
      steps.push({
        tier: "Medium_13B",
        confidenceScore: conf,
        thresholdScore: this.threshold,
        routed: true,
        resolved,
        flopsConsumedGiga: flops,
        latencySec: latency
      });

      if (resolved) {
        solved = true;
        finalModelTier = "Medium_13B";
      }
    } else {
      steps.push({ tier: "Medium_13B", confidenceScore: 0, thresholdScore: this.threshold, routed: false, resolved: false, flopsConsumedGiga: 0, latencySec: 0 });
    }

    // Tier 4: Large (70B)
    if (!solved) {
      const conf = 0.98;
      const flops = 84.0;
      const latency = 0.85;
      totalFlops += flops;
      totalLatency += latency;

      steps.push({
        tier: "Large_70B",
        confidenceScore: conf,
        thresholdScore: this.threshold,
        routed: true,
        resolved: true,
        flopsConsumedGiga: flops,
        latencySec: latency
      });
      finalModelTier = "Large_70B";
    } else {
      steps.push({ tier: "Large_70B", confidenceScore: 0, thresholdScore: this.threshold, routed: false, resolved: false, flopsConsumedGiga: 0, latencySec: 0 });
    }

    const resolvedAnswer = `[Cascade Responding Model: ${finalModelTier}] Processed with confidence matching constraints.`;

    return {
      query,
      steps,
      finalModelTier,
      totalFlopsGiga: parseFloat(totalFlops.toFixed(1)),
      totalLatencySec: parseFloat(totalLatency.toFixed(3)),
      resolvedAnswer
    };
  }
}
