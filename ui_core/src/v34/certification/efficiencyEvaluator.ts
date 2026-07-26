// LEO AI V34 — Efficiency Evaluator
// Capabilities: Compute intelligence-per-watt values, optimize resource cost, and map dollar efficiencies.

export interface EfficiencyMetricsReport {
  intelligencePerWatt: number;
  intelligencePerDollar: number;
  hardwareSavingsFactor: number;
}

export class EfficiencyEvaluator {
  evaluateEfficiency(
    compositeIndex: number,
    powerDrawWatts: number,
    gpuHoursAvoided: number,
  ): EfficiencyMetricsReport {
    const power = Math.max(1.0, powerDrawWatts);

    // Intelligence per watt = composite index / power draw
    const intelligencePerWatt = parseFloat((compositeIndex / power).toFixed(3));

    // Intelligence per dollar = composite index * (gpu hours saved / standard cost per hour)
    // standard gpu hour cost = $1.50
    const moneySaved = gpuHoursAvoided * 1.5;
    const intelligencePerDollar = parseFloat(
      (compositeIndex / Math.max(1.0, 100 - moneySaved)).toFixed(3),
    );

    return {
      intelligencePerWatt,
      intelligencePerDollar,
      hardwareSavingsFactor: parseFloat((1.0 + gpuHoursAvoided * 0.15).toFixed(2)),
    };
  }
}
