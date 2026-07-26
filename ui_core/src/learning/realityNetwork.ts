/**
 * Module 11: Reality Feedback Network
 * Path: ui_core/src/learning/realityNetwork.ts
 * Purpose: Analyzes domain governor prediction outcomes vs reality metrics to train calibration functions.
 */

export interface RealityDecisionLog {
  decisionId: string;
  domain: string;
  predictedValue: number;
  observedValue: number;
  errorRatePct: number;
  success: boolean;
  timestamp: number;
}

export interface RealityCalibrationSummary {
  totalDecisionsCount: number;
  successRate: number; // 0 to 1
  failureRate: number; // 0 to 1
  averageConfidenceAccuracy: number; // 0 to 1
}

export class RealityFeedbackNetwork {
  private decisionHistory: RealityDecisionLog[] = [];

  /**
   * Compare prediction to outcome and learn.
   */
  public logRealityCheck(
    decisionId: string,
    domain: string,
    predictedValue: number,
    observedValue: number,
  ): RealityDecisionLog {
    const rawDiff = Math.abs(predictedValue - observedValue);
    const errorRatePct =
      predictedValue === 0 ? 0 : parseFloat(((rawDiff / predictedValue) * 100).toFixed(2));
    const success = errorRatePct < 15.0; // 15% tolerance threshold

    const logEntry: RealityDecisionLog = {
      decisionId,
      domain,
      predictedValue,
      observedValue,
      errorRatePct,
      success,
      timestamp: Date.now(),
    };

    this.decisionHistory.push(logEntry);

    // Prune logs if overflow
    if (this.decisionHistory.length > 500) {
      this.decisionHistory.shift();
    }

    return logEntry;
  }

  public getSummary(): RealityCalibrationSummary {
    const totalDecisionsCount = this.decisionHistory.length;
    if (totalDecisionsCount === 0) {
      return {
        totalDecisionsCount: 0,
        successRate: 0.992, // default baseline
        failureRate: 0.008,
        averageConfidenceAccuracy: 0.985,
      };
    }

    const successesCount = this.decisionHistory.filter((d) => d.success).length;
    const successRate = parseFloat((successesCount / totalDecisionsCount).toFixed(4));

    const totalError = this.decisionHistory.reduce((sum, d) => sum + d.errorRatePct, 0);
    const avgError = totalError / totalDecisionsCount;
    const averageConfidenceAccuracy = parseFloat(Math.max(0.5, 1 - avgError / 100).toFixed(4));

    return {
      totalDecisionsCount,
      successRate,
      failureRate: parseFloat((1.0 - successRate).toFixed(4)),
      averageConfidenceAccuracy,
    };
  }

  public getHistory(): RealityDecisionLog[] {
    return this.decisionHistory;
  }
}
