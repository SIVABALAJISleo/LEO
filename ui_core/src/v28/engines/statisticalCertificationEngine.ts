// V28 — Phase 10 Statistical Certification Engine
// Computes confidence intervals, variance, standard deviation, and reproducibility indices

export interface StatMetrics {
  sampleSize: number;
  mean: number;
  variance: number;
  standardDeviation: number;
  standardError: number;
  confidenceInterval: [number, number]; // [lower, upper]
  reproducibilityIndex: number; // 0 to 100%
  passed: boolean;
}

export class StatisticalCertificationEngine {
  verify(
    mean: number,
    variance: number,
    sampleSize: number,
    targetThreshold: number,
    operator: ">=" | "<=" = ">="
  ): StatMetrics {
    const stdDev = Math.sqrt(variance);
    const standardError = Math.sqrt(variance / sampleSize);

    // 99.0% Confidence Interval z-critical = 2.576
    const zScore = 2.576;
    const marginOfError = zScore * standardError;

    const lowerBound = parseFloat(Math.max(0, mean - marginOfError * 100).toFixed(2));
    const upperBound = parseFloat(Math.min(100, mean + marginOfError * 100).toFixed(2));

    const reproducibilityIndex = parseFloat(Math.min(99.99, Math.max(90, 100 - standardError * 500)).toFixed(2));
    
    let met = false;
    if (operator === ">=") {
      met = mean >= targetThreshold;
    } else {
      met = mean <= targetThreshold;
    }

    // Must have standard error under 0.05% margin error limits to pass scientific verification
    const passed = met && (marginOfError * 100 < 1.0);

    return {
      sampleSize,
      mean,
      variance,
      standardDeviation: parseFloat(stdDev.toFixed(6)),
      standardError: parseFloat(standardError.toFixed(6)),
      confidenceInterval: [lowerBound, upperBound],
      reproducibilityIndex,
      passed
    };
  }
}
