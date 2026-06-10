/**
 * PHASE 6: Reality Feedback Engine
 * Purpose: Logs predicted values against observed outcomes, calculating error percentage
 * to optimize configuration parameters.
 */

export interface FeedbackEntry {
  predictionId: string;
  metric: string;
  predicted: number;
  observed: number;
  errorPct: number;
  adjustment: number;
  timestamp: number;
}

export class RealityFeedbackEngine {
  private history: FeedbackEntry[] = [];
  private weights: Record<string, number> = {
    intentAccuracyWeight: 0.95,
    reasoningConfidence: 0.90,
    verificationRigour: 0.96,
  };

  public logFeedback(predictionId: string, metric: string, predicted: number, observed: number): FeedbackEntry {
    const error = Math.abs(predicted - observed);
    const errorPct = predicted > 0 ? (error / predicted) * 100 : 0;
    
    // Learning adjustments
    const learningRate = 0.04;
    const signal = (predicted - observed) / Math.max(predicted, 1);
    const adjustment = signal * learningRate;

    if (metric in this.weights) {
      this.weights[metric] = Math.max(0.1, Math.min(1.0, this.weights[metric] + adjustment));
    }

    const entry: FeedbackEntry = {
      predictionId,
      metric,
      predicted,
      observed,
      errorPct,
      adjustment,
      timestamp: Date.now(),
    };

    this.history.push(entry);
    if (this.history.length > 50) {
      this.history.shift();
    }

    return entry;
  }

  public getWeights(): Record<string, number> {
    return this.weights;
  }

  public getHistory(): FeedbackEntry[] {
    return this.history;
  }
}
