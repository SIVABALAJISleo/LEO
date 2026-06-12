// LEO AI V36 — Reality Feedback Engine
// Logs model predictions and matches them against observed reality outcomes.

export interface PredictionRecord {
  id: string;
  prediction: string;
  confidence: number;
  timestamp: number;
  actualOutcome?: string;
  errorMeasured?: number;
}

export class RealityFeedbackEngine {
  private log: PredictionRecord[] = [];

  public logPrediction(id: string, prediction: string, confidence: number): void {
    this.log.push({
      id,
      prediction,
      confidence,
      timestamp: Date.now()
    });
  }

  public getLoggedPredictions(): PredictionRecord[] {
    return this.log;
  }
}
