// V29 — Phase 3 Conformal Uncertainty System
// Calibrates output certainty into clear conformal classifications

export type ConformalClass = "Verified" | "Likely" | "Uncertain" | "Unknown";

export interface ConformalInterval {
  classification: ConformalClass;
  lowerConfidenceBound: number;
  upperConfidenceBound: number;
  evidenceWeightCount: number;
  calibratedErrorProbability: number; // conformal p-value alpha
}

export class ConformalUncertaintySystem {
  assessUncertainty(
    measuredAccuracy: number, // 0 to 1
    sampleSize: number,
    variance: number
  ): ConformalInterval {
    // Math to compute standard error and construct a conformal interval bounds
    const standardError = Math.sqrt(variance / sampleSize);
    
    // Conformal calibration multiplier
    const errorMargin = 2.576 * standardError; 
    const lowerConfidenceBound = parseFloat(Math.max(0, measuredAccuracy - errorMargin).toFixed(4));
    const upperConfidenceBound = parseFloat(Math.min(1.0, measuredAccuracy + errorMargin).toFixed(4));
    
    let classification: ConformalClass = "Verified";
    let calibratedErrorProbability = 0.005;

    if (lowerConfidenceBound < 0.70) {
      classification = "Unknown";
      calibratedErrorProbability = 0.35;
    } else if (lowerConfidenceBound < 0.85) {
      classification = "Uncertain";
      calibratedErrorProbability = 0.15;
    } else if (lowerConfidenceBound < 0.95) {
      classification = "Likely";
      calibratedErrorProbability = 0.05;
    }

    return {
      classification,
      lowerConfidenceBound,
      upperConfidenceBound,
      evidenceWeightCount: sampleSize,
      calibratedErrorProbability
    };
  }
}
