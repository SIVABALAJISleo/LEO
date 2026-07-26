/**
 * Phase 5: Reality Feedback Engine V3
 * Path: ui_core/src/learning/realityFeedbackEngineV3.ts
 * Purpose: V3 Reality check feedback tracking predictions against observed metrics.
 */

import { FeedbackLog, CalibrationReport } from "./realityFeedback";

export class RealityFeedbackEngineV3 {
  private logHistory: FeedbackLog[] = [];
  private currentWeights: Record<string, number> = {
    predictionAccuracy: 0.96,
    outcomeSuccess: 0.95,
    confidenceCalibration: 0.94,
    iGPUEfficiency: 0.98,
  };

  /**
   * Logs a reality prediction outcome and recalibrates hyperparameter weights.
   */
  public logRealityEvent(
    predictionId: string,
    metricType: string,
    predictedVal: number,
    observedVal: number,
  ): FeedbackLog {
    const errorPct =
      predictedVal === 0
        ? 0
        : parseFloat(((Math.abs(predictedVal - observedVal) / predictedVal) * 100).toFixed(2));
    const entry: FeedbackLog = {
      predictionId,
      metricType,
      predictedValue: predictedVal,
      observedValue: observedVal,
      errorPct,
      timestamp: Date.now(),
    };

    this.logHistory.push(entry);

    // Tune dynamic weight values based on error
    if (this.currentWeights[metricType] !== undefined) {
      const current = this.currentWeights[metricType];
      const learningRate = 0.05;
      const errorFactor = errorPct / 100;
      const nextWeight = current * (1 - learningRate) + (1 - errorFactor) * learningRate;
      this.currentWeights[metricType] = parseFloat(
        Math.max(0.5, Math.min(0.99, nextWeight)).toFixed(4),
      );
    }

    return entry;
  }

  public getHistory(): FeedbackLog[] {
    return this.logHistory;
  }

  public getWeights(): Record<string, number> {
    return this.currentWeights;
  }

  public getCalibration(): CalibrationReport {
    if (this.logHistory.length === 0) {
      return { successRate: 0.96, predictionAccuracy: 0.95, confidenceCalibration: 0.94 };
    }

    const totalError = this.logHistory.reduce((sum, h) => sum + h.errorPct, 0);
    const avgError = totalError / this.logHistory.length;
    const predictionAccuracy = parseFloat((1 - avgError / 100).toFixed(4));

    const highSuccessCount = this.logHistory.filter((h) => h.errorPct < 10).length;
    const successRate = parseFloat((highSuccessCount / this.logHistory.length).toFixed(4));

    return {
      successRate,
      predictionAccuracy,
      confidenceCalibration: parseFloat(
        (1 - Math.abs(successRate - predictionAccuracy)).toFixed(4),
      ),
    };
  }
}
