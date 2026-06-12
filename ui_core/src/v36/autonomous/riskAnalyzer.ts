// LEO AI V36 — Risk Analyzer
// Analyzes multi-future crash risk outputs and filters worst-case vectors.

import { TrajectoryPath } from "./futureSimulationEngine";

export class RiskAnalyzer {
  public auditRisks(paths: TrajectoryPath[]): { averageRisk: number; failedPathsCount: number } {
    if (paths.length === 0) return { averageRisk: 0, failedPathsCount: 0 };
    
    let sumRisk = 0;
    let failedPathsCount = 0;

    paths.forEach(p => {
      sumRisk += p.crashRiskScore;
      if (p.crashRiskScore > 0.85) {
        failedPathsCount++;
      }
    });

    return {
      averageRisk: parseFloat((sumRisk / paths.length).toFixed(4)),
      failedPathsCount
    };
  }
}
