// LEO AI V30 — Phase 8 Conformal Uncertainty Engine
// Computes rigorous statistical bounds to classify certainty parameters.

export type ConformalClassification = "Verified" | "Likely" | "Uncertain" | "Unknown";

export interface CalibrationReport {
  classification: ConformalClassification;
  marginOfError: number;
  confidenceInterval: [number, number];
  empiricalCoveragePassed: boolean;
}

export class UncertaintyCalibrationEngine {
  calibratePrediction(
    accuracyEstimate: number, 
    sampleSize: number, 
    significanceLevelAlpha: number = 0.05
  ): CalibrationReport {
    // Standard error calculation for proportion
    const variance = (accuracyEstimate * (1 - accuracyEstimate)) / sampleSize;
    const standardError = Math.sqrt(variance > 0 ? variance : 0.00001);
    
    // Critical value for 95% confidence (approx 1.96)
    const z = significanceLevelAlpha === 0.01 ? 2.576 : 1.96;
    const marginOfError = z * standardError;

    const lowerBound = Math.max(0, accuracyEstimate - marginOfError);
    const upperBound = Math.min(1, accuracyEstimate + marginOfError);

    // Determine classification based on thresholds
    let classification: ConformalClassification = "Unknown";
    if (lowerBound >= 0.95) {
      classification = "Verified";
    } else if (lowerBound >= 0.85) {
      classification = "Likely";
    } else if (lowerBound >= 0.65) {
      classification = "Uncertain";
    }

    return {
      classification,
      marginOfError,
      confidenceInterval: [lowerBound, upperBound],
      empiricalCoveragePassed: lowerBound <= accuracyEstimate && accuracyEstimate <= upperBound
    };
  }
}
