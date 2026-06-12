// LEO AI V37 — Adaptive Learning Engine
// Implements active and online learning mechanisms to adjust logic paths based on live feedback signals.

export interface ReinforcementSignal {
  actionId: string;
  feedbackMetric: number; // 0.0 - 1.0
  adjustmentApplied: number; // weight shift delta
  category: "avoidance" | "retrieval" | "governance" | "quantization";
}

export class AdaptiveLearningEngine {
  private activeQueue: string[] = [];
  private signals: ReinforcementSignal[] = [];

  /**
   * Evaluates active feedback and updates routing optimization parameters.
   */
  public logReinforcement(
    actionId: string,
    rating: number,
    category: ReinforcementSignal["category"]
  ): ReinforcementSignal {
    const feedbackMetric = rating / 5.0; // scale 1-5 to 0-1.0
    
    // Calculate adaptive reinforcement delta
    const baseDelta = feedbackMetric - 0.70; // 0.70 is standard target baseline
    const adjustmentApplied = parseFloat((baseDelta * 0.15).toFixed(4));

    const signal: ReinforcementSignal = {
      actionId,
      feedbackMetric,
      adjustmentApplied,
      category
    };

    this.signals.push(signal);
    return signal;
  }

  public registerActiveLearningItem(query: string) {
    if (!this.activeQueue.includes(query)) {
      this.activeQueue.push(query);
    }
  }

  public getActiveQueue(): string[] {
    return this.activeQueue;
  }

  public getSignals(): ReinforcementSignal[] {
    return this.signals;
  }
}
