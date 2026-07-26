export interface EfficiencyResult {
  efficiencyRating: number;
  status: string;
  bypassSuccess: boolean;
  localLatencyMs: number;
  simulatedCloudLatencyMs: number;
  localCostUsd: number;
  simulatedCloudCostUsd: number;
}

/**
 * Simple, local-only efficiency comparison.
 * You pass the measured local latency in ms; we compare against a
 * configurable, simulated cloud GPU latency and cost.
 */
export function calculateEfficiency(
  localTimeMs: number,
  simulatedCloudLatencyMs = 800,
  simulatedCloudCostUsd = 0.05,
): EfficiencyResult {
  const local = Math.max(1, localTimeMs);
  const cloud = Math.max(1, simulatedCloudLatencyMs);

  const efficiencyRating = (cloud / local) * 100;

  return {
    efficiencyRating,
    status: "Goal equivalence (local vs simulated cloud) computed.",
    bypassSuccess: local <= cloud,
    localLatencyMs: local,
    simulatedCloudLatencyMs: cloud,
    localCostUsd: 0,
    simulatedCloudCostUsd,
  };
}
