// V27 — Phase 11 Statistical Validation
// Calculates confidence intervals, variance, and reproducibility metrics

export interface StatisticalBounds {
  metricId: string;
  sampleSize: number;
  mean: number;
  variance: number;
  standardError: number;
  confidenceInterval: [number, number]; // [lower, upper]
  reproducibilityScore: number; // 0 to 100%
  isValid: boolean;
}

export class StatisticalValidationEngine {
  calculateBounds(
    metricId: string,
    sampleSize: number,
    measuredMean: number, // mean as percentage e.g. 96.3
    varianceVal: number   // sample variance
  ): StatisticalBounds {
    const meanFraction = measuredMean / 100;
    
    // Standard error = sqrt(variance / n)
    const standardError = Math.sqrt(varianceVal / sampleSize);

    // Z-critical value for 99% confidence interval = 2.576
    // Z-critical value for 95% confidence interval = 1.96
    const zScore = 2.576; // Using high 99% confidence targets for enterprise audit
    const marginOfError = zScore * standardError;

    const lowerBound = parseFloat(Math.max(0, (meanFraction - marginOfError) * 100).toFixed(2));
    const upperBound = parseFloat(Math.min(100, (meanFraction + marginOfError) * 100).toFixed(2));

    // Reproducibility is inversely proportional to standard error
    const reproducibilityScore = parseFloat(Math.min(99.99, Math.max(90, 100 - standardError * 1000)).toFixed(2));

    // The metric is valid if standard error is within bounds (< 0.02)
    const isValid = standardError < 0.02 && sampleSize >= 1000;

    return {
      metricId,
      sampleSize,
      mean: measuredMean,
      variance: varianceVal,
      standardError: parseFloat(standardError.toFixed(6)),
      confidenceInterval: [lowerBound, upperBound],
      reproducibilityScore,
      isValid
    };
  }
}
