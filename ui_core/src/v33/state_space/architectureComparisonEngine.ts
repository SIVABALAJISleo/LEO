// LEO AI V33 — Architecture Comparison Engine
// Capabilities: Compute the Architecture Efficiency Index for a set of options.

import { StateSpaceResearchEngine, ArchitectureMetrics } from "./stateSpaceResearchEngine";

export interface EfficiencyIndexReport {
  timestamp: number;
  contextLength: number;
  preferredArchitecture: string;
  architectureEfficiencyIndex: number; // Overall performance score relative to cost (0 - 100)
  detailedScores: {
    name: string;
    efficiencyIndex: number;
    memoryEfficiency: number;
    latencyScore: number;
    reasoningScore: number;
  }[];
}

export class ArchitectureComparisonEngine {
  private researchEngine = new StateSpaceResearchEngine();

  calculateEfficiencyIndex(contextLength: number, maxMemoryAllowedMB: number): EfficiencyIndexReport {
    const architectures = this.researchEngine.evaluateArchitectures(contextLength);

    const detailedScores = architectures.map(arch => {
      // Memory efficiency: how much margin we have under constraints
      const memoryRatio = arch.memoryUsageMB / maxMemoryAllowedMB;
      const memoryEfficiency = memoryRatio > 1.0 
        ? Math.max(0.1, 1 / (memoryRatio * memoryRatio)) // heavily penalize exceeding memory
        : 1.0 - (memoryRatio * 0.3); // higher margin = better

      // Latency score: lower latency is better
      const latencyScore = Math.max(0.1, 100 / (arch.latencyMsPerToken + 1.0));

      // Reasoning score: scale reasoning quality and context retention
      const reasoningScore = arch.reasoningQuality * arch.contextRetentionRate;

      // Overall efficiency index: balanced product of memory margin, speed, and reasoning
      // Normalized roughly to 0-100 scale
      const indexRaw = (memoryEfficiency * 0.4 + latencyScore * 0.3 + reasoningScore * 0.3) * 100;
      const efficiencyIndex = parseFloat(Math.min(100, Math.max(0, indexRaw)).toFixed(1));

      return {
        name: arch.name,
        efficiencyIndex,
        memoryEfficiency: parseFloat(memoryEfficiency.toFixed(2)),
        latencyScore: parseFloat(latencyScore.toFixed(2)),
        reasoningScore: parseFloat(reasoningScore.toFixed(2))
      };
    });

    // Sort descending by efficiency index
    const sorted = [...detailedScores].sort((a, b) => b.efficiencyIndex - a.efficiencyIndex);
    const top = sorted[0];

    return {
      timestamp: Date.now(),
      contextLength,
      preferredArchitecture: top ? top.name : "Unknown",
      architectureEfficiencyIndex: top ? top.efficiencyIndex : 0,
      detailedScores: sorted
    };
  }
}
