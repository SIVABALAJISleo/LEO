// LEO AI V36 — Reality Alignment Engine
// Monitors calibration accuracy by comparing predicted confidence with outcome realities.

export interface PredictionAudit {
  predictionId: string;
  predictedOutcome: string;
  observedOutcome: string;
  assertedConfidence: number;
}

export interface CalibrationTelemetry {
  realityAlignmentScore: number; // 0 to 100
  predictionReliabilityScore: number; // 0 to 100
  confidenceCalibrationScore: number; // 0 to 100
  weakAssumptionsDetected: string[];
}

export class RealityAlignmentEngine {
  private auditLog: PredictionAudit[] = [
    { predictionId: "aud-01", predictedOutcome: "L3 Cache handles 95% hits", observedOutcome: "L3 Cache handles 91% hits", assertedConfidence: 0.95 },
    { predictionId: "aud-02", predictedOutcome: "iGPU throughput is 75 tok/sec", observedOutcome: "iGPU throughput is 75 tok/sec", assertedConfidence: 0.98 }
  ];

  /**
   * Tracks target predictions and audits outcomes to detect reality drifts.
   */
  public auditReality(
    predictionId: string,
    predicted: string,
    actual: string,
    confidence: number
  ): CalibrationTelemetry {
    this.auditLog.push({
      predictionId,
      predictedOutcome: predicted,
      observedOutcome: actual,
      assertedConfidence: confidence
    });

    const total = this.auditLog.length;
    const matchesCount = this.auditLog.filter(a => a.predictedOutcome === a.observedOutcome).length;
    
    const reliability = (matchesCount / total) * 100;
    
    // Compute average calibration discrepancy
    let totalCalibErr = 0;
    this.auditLog.forEach(a => {
      const outcomeVal = a.predictedOutcome === a.observedOutcome ? 1.0 : 0.0;
      totalCalibErr += Math.abs(a.assertedConfidence - outcomeVal);
    });
    
    const calibrationScore = (1.0 - (totalCalibErr / total)) * 100;
    const realityAlignment = (reliability + calibrationScore) / 2;

    const weakAssumptionsDetected: string[] = [];
    if (calibrationScore < 85) {
      weakAssumptionsDetected.push("Constant L3 page locking assumptions");
    }

    return {
      realityAlignmentScore: parseFloat(realityAlignment.toFixed(1)),
      predictionReliabilityScore: parseFloat(reliability.toFixed(1)),
      confidenceCalibrationScore: parseFloat(calibrationScore.toFixed(1)),
      weakAssumptionsDetected
    };
  }

  public getAuditLog(): PredictionAudit[] {
    return this.auditLog;
  }
}
