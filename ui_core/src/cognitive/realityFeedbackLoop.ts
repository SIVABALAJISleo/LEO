/**
 * PHASE 4: Reality Feedback Loop
 * Compares prediction vectors against actual outcomes, measuring error rates
 * to update model parameters and confidence weights.
 */

export interface FeedbackRecord {
  timestamp: number;
  predictionId: string;
  metric: string;
  predictedValue: number;
  observedValue: number;
  errorPercentage: number;
  weightAdjustment: number;
}

export class RealityFeedbackLoop {
  private feedbackHistory: FeedbackRecord[] = [];
  private currentModelWeights: Record<string, number> = {
    crystallizationWeight: 0.95,
    localInferenceConfidence: 0.90,
    activeResearchRate: 0.85,
    gpuAccelerationPriority: 0.88,
  };

  /**
   * Records an observation and computes feedback adjustments.
   */
  public logReality(predictionId: string, metric: string, predictedValue: number, observedValue: number): FeedbackRecord {
    const error = Math.abs(predictedValue - observedValue);
    const errorPercentage = predictedValue > 0 ? (error / predictedValue) * 100 : 0;
    
    // Gradient weight adjustment
    // If observed latency is much higher, reduce confidence in that path
    const learningRate = 0.05;
    const errorSignal = (predictedValue - observedValue) / Math.max(predictedValue, 1);
    const weightAdjustment = errorSignal * learningRate;

    // Apply weight adjustments to system config
    if (metric in this.currentModelWeights) {
      this.currentModelWeights[metric] = Math.max(0.1, Math.min(1.0, this.currentModelWeights[metric] + weightAdjustment));
    }

    const record: FeedbackRecord = {
      timestamp: Date.now(),
      predictionId,
      metric,
      predictedValue,
      observedValue,
      errorPercentage,
      weightAdjustment,
    };

    this.feedbackHistory.push(record);
    if (this.feedbackHistory.length > 100) {
      this.feedbackHistory.shift(); // Keep bounded sliding window
    }

    return record;
  }

  public getModelWeights(): Record<string, number> {
    return this.currentModelWeights;
  }

  public getHistory(): FeedbackRecord[] {
    return this.feedbackHistory;
  }

  public getAverageError(): number {
    if (this.feedbackHistory.length === 0) return 0;
    const sum = this.feedbackHistory.reduce((acc, r) => acc + r.errorPercentage, 0);
    return sum / this.feedbackHistory.length;
  }
}
