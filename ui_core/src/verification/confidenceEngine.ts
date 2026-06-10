/**
 * Phase 13: Confidence Calibration Engine
 * Path: ui_core/src/verification/confidenceEngine.ts
 * Purpose: Analyzes reasoning structures, verification checks, and evidence weights to assign calibrated confidence metrics to answers.
 */

export interface CalibrationTelemetry {
  evidenceWeight: number;      // 0 to 1
  reasoningConsistency: number; // 0 to 1
  verificationSuccessCount: number;
  verificationTotalCount: number;
}

export interface CalibrationResponse {
  answer: string;
  calibratedConfidence: number; // 0 to 1
  evidenceLevel: "strong" | "adequate" | "weak";
  verificationStatus: "fully_verified" | "partially_verified" | "unverified";
  telemetry: CalibrationTelemetry;
}

export class ConfidenceEngine {
  /**
   * Calculates confidence based on evidence, checks, and logic consistency.
   */
  public calibrateOutput(
    answer: string,
    evidenceWeight: number,
    reasoningConsistency: number,
    verifySuccess: number,
    verifyTotal: number
  ): CalibrationResponse {
    // Determine Verification status
    let verificationStatus: "fully_verified" | "partially_verified" | "unverified" = "unverified";
    const verificationRatio = verifyTotal === 0 ? 0 : verifySuccess / verifyTotal;

    if (verificationRatio === 1.0 && verifyTotal > 0) {
      verificationStatus = "fully_verified";
    } else if (verificationRatio >= 0.5 && verifyTotal > 0) {
      verificationStatus = "partially_verified";
    }

    // Determine Evidence level
    let evidenceLevel: "strong" | "adequate" | "weak" = "weak";
    if (evidenceWeight >= 0.85) {
      evidenceLevel = "strong";
    } else if (evidenceWeight >= 0.5) {
      evidenceLevel = "adequate";
    }

    // Calibrate confidence
    // High confidence requires: strong evidence (evidenceWeight >= 0.85), successful verification (verificationRatio >= 0.9), consistent reasoning (reasoningConsistency >= 0.9)
    let calibratedConfidence = (evidenceWeight * 0.4) + (reasoningConsistency * 0.3) + (verificationRatio * 0.3);

    // Apply strict penalty constraints for unverified paths
    if (verificationStatus === "unverified") {
      calibratedConfidence = Math.min(0.35, calibratedConfidence * 0.5);
    } else if (verificationStatus === "partially_verified") {
      calibratedConfidence = Math.min(0.75, calibratedConfidence * 0.8);
    }

    // Round
    calibratedConfidence = parseFloat(calibratedConfidence.toFixed(4));

    return {
      answer,
      calibratedConfidence,
      evidenceLevel,
      verificationStatus,
      telemetry: {
        evidenceWeight,
        reasoningConsistency,
        verificationSuccessCount: verifySuccess,
        verificationTotalCount: verifyTotal
      }
    };
  }
}

export class ConfidenceEngineV16 {
  /**
   * V16 Upgraded Confidence Calibration.
   * Weak evidence strictly results in a low confidence score, capped at 0.30.
   */
  public calibrateOutputV16(
    answer: string,
    evidenceWeight: number,
    reasoningConsistency: number,
    verifySuccess: number,
    verifyTotal: number
  ): CalibrationResponse {
    let verificationStatus: "fully_verified" | "partially_verified" | "unverified" = "unverified";
    const verificationRatio = verifyTotal === 0 ? 0 : verifySuccess / verifyTotal;

    if (verificationRatio === 1.0 && verifyTotal > 0) {
      verificationStatus = "fully_verified";
    } else if (verificationRatio >= 0.5 && verifyTotal > 0) {
      verificationStatus = "partially_verified";
    }

    // V16 Evidence Level Rules (Strong >= 0.90, Adequate >= 0.60, else Weak)
    let evidenceLevel: "strong" | "adequate" | "weak" = "weak";
    if (evidenceWeight >= 0.90) {
      evidenceLevel = "strong";
    } else if (evidenceWeight >= 0.60) {
      evidenceLevel = "adequate";
    }

    let calibratedConfidence = (evidenceWeight * 0.5) + (reasoningConsistency * 0.25) + (verificationRatio * 0.25);

    // Apply strict V16 constraints
    if (evidenceLevel === "weak") {
      calibratedConfidence = Math.min(0.30, calibratedConfidence * 0.4);
    } else if (verificationStatus === "unverified") {
      calibratedConfidence = Math.min(0.35, calibratedConfidence * 0.5);
    } else if (verificationStatus === "partially_verified") {
      calibratedConfidence = Math.min(0.70, calibratedConfidence * 0.75);
    }

    calibratedConfidence = parseFloat(calibratedConfidence.toFixed(4));

    return {
      answer,
      calibratedConfidence,
      evidenceLevel,
      verificationStatus,
      telemetry: {
        evidenceWeight,
        reasoningConsistency,
        verificationSuccessCount: verifySuccess,
        verificationTotalCount: verifyTotal
      }
    };
  }
}

