// LEO AI V30 — Phase 13 Reality Alignment Network
// Computes similarity distance between simulated world predictions and empirical outcomes.

export interface AlignmentEvent {
  eventId: string;
  simulatedPrediction: string;
  actualOutcome: string;
  predictionAccuracyScore: number;
  correctionFactor: number;
}

export class RealityAlignmentNetwork {
  private history: AlignmentEvent[] = [];
  private currentCalibrationRate: number = 0.985;

  logEvent(prediction: string, predictedConfidence: number, actualOutcomeScore: number) {
    const errorDelta = Math.abs(predictedConfidence - actualOutcomeScore);
    const event: AlignmentEvent = {
      eventId: `align-${Math.random().toString(36).substring(2, 9)}`,
      simulatedPrediction: prediction,
      actualOutcome: `Score: ${actualOutcomeScore.toFixed(3)}`,
      predictionAccuracyScore: 1 - errorDelta,
      correctionFactor: errorDelta * 0.1
    };

    this.history.push(event);
    
    // Auto-adjust current calibration rate
    this.currentCalibrationRate = parseFloat(
      Math.max(0.95, Math.min(0.995, this.currentCalibrationRate - (errorDelta * 0.05))).toFixed(4)
    );
  }

  getOverallAlignment(): number {
    if (this.history.length === 0) return this.currentCalibrationRate;
    const sum = this.history.reduce((a, b) => a + b.predictionAccuracyScore, 0);
    return sum / this.history.length;
  }

  getEvents(): AlignmentEvent[] {
    return this.history;
  }
}
