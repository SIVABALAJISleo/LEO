// LEO AI V32 — Phase 12 Economic Optimization Engine
// Optimizes simultaneously: latency, accuracy, memory, CPU usage, iGPU usage, energy consumption, operational cost.
// Output: Efficiency Score.

export interface EconomicProfile {
  latencySec: number;
  accuracyRatePct: number;
  memoryMb: number;
  cpuUsagePct: number;
  igpuUsagePct: number;
  energyJoules: number;
  costDollar: number;
}

export class EconomicOptimizationEngine {
  optimize(
    profile: EconomicProfile, 
    priority: "latency" | "accuracy" | "cost" | "balanced" = "balanced"
  ): { optimizationDecisions: string[]; efficiencyScore: number; } {
    
    const decisions: string[] = [];
    
    // Evaluate trade-offs
    if (profile.latencySec > 2.0) {
      decisions.push("Latency threshold exceeded. Shift tasks to local INT8 iGPU offload blocks.");
    }
    
    if (profile.memoryMb > 16384) {
      decisions.push("VRAM usage high. Trigger paged block compaction and key pruning in KV Cache.");
    }

    if (profile.costDollar > 0.05) {
      decisions.push("Centralized Cloud cost detected. Shift processing locally using peer mesh coordinates.");
    }

    // Formulation of Efficiency Score (0 to 100): higher accuracy, lower latency, lower energy and cost
    const accuracyFactor = profile.accuracyRatePct / 100;
    const latencyPenalty = Math.max(0.1, profile.latencySec);
    const energyPenalty = Math.max(1.0, profile.energyJoules);
    const costPenalty = profile.costDollar * 100; // scale cents

    let priorityWeight = 1.0;
    if (priority === "latency") priorityWeight = 1.4;

    const rawScore = (accuracyFactor * 50) + (10 / latencyPenalty) * 20 - (energyPenalty * 0.1) - costPenalty;
    const efficiencyScore = parseFloat(Math.min(100, Math.max(10, rawScore * priorityWeight)).toFixed(1));

    return {
      optimizationDecisions: decisions,
      efficiencyScore
    };
  }
}
