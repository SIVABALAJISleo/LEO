// LEO AI V32 — Phase 11 Reality Outcome Learning Engine
// Pipeline: Prediction → Real Outcome → Difference → Root Cause → Adjustment
// Purpose: Track calibration errors, confidence errors, and outcome deviations to calculate the Reality Alignment Score.

export interface RealityDeviation {
  metricId: string;
  predictedValue: number;
  actualValue: number;
  difference: number;
  rootCause: string;
  adjustmentApplied: string;
}

export class RealityOutcomeLearningEngine {
  private deviationsList: RealityDeviation[] = [];

  assessDeviation(metricId: string, predicted: number, actual: number): RealityDeviation {
    const difference = parseFloat((actual - predicted).toFixed(3));

    let rootCause = "Minor statistical jitter.";
    let adjustment = "No adjustment needed.";

    if (Math.abs(difference) > 10.0) {
      rootCause = "Obsolete mapping nodes in semantic caching graphs.";
      adjustment = "Trigger continuous knowledge refresh update sweep.";
    }

    const dev: RealityDeviation = {
      metricId,
      predictedValue: predicted,
      actualValue: actual,
      difference,
      rootCause,
      adjustmentApplied: adjustment,
    };

    this.deviationsList.push(dev);
    return dev;
  }

  getRealityAlignmentScore(): number {
    const total = this.deviationsList.length;
    if (total === 0) return 98.5; // default benchmark value

    const averageError =
      this.deviationsList.reduce((acc, d) => acc + Math.abs(d.difference), 0) / total;
    // Score declines with average error deviation
    return parseFloat(Math.max(10, 100 - averageError * 2.2).toFixed(1));
  }

  getDeviations(): RealityDeviation[] {
    return this.deviationsList;
  }
}
