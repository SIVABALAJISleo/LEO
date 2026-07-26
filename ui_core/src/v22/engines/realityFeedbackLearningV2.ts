// V22 — Phase 8: Reality Feedback Learning V2
// Prediction vs Reality delta → correction signal → calibration weight update

export interface FeedbackEventV22 {
  eventId: string;
  metricKey: string;
  predicted: number;
  actual: number;
  delta: number; // actual - predicted
  correctionApplied: number;
  newWeight: number;
  timestamp: number;
}

export interface CalibrationState {
  weights: Record<string, number>;
  totalEvents: number;
  averageDelta: number;
  improvementVelocity: number; // rate of weight improvement per cycle
  calibrationScore: number; // 0–1
}

const LEARNING_RATE = 0.08;

export class RealityFeedbackLearningV2 {
  private events: FeedbackEventV22[] = [];
  private weights: Record<string, number> = {
    reasoningAccuracy: 0.9,
    hallucinationRate: 0.06,
    memoryConsistency: 0.91,
    agentQuality: 0.88,
    knowledgeFreshness: 0.87,
    enterpriseTrust: 0.89,
    retrievalSpeed: 0.85,
    intentAccuracy: 0.88,
  };
  private nextId = 1;
  private previousAvgDelta = 0;

  logFeedback(metricKey: string, predicted: number, actual: number): FeedbackEventV22 {
    if (!(metricKey in this.weights)) {
      this.weights[metricKey] = 0.8; // default weight for new metrics
    }

    const delta = actual - predicted;
    // Correction: nudge weight toward actual using learning rate
    const correction = LEARNING_RATE * delta;
    this.weights[metricKey] = Math.min(
      0.999,
      Math.max(0.001, this.weights[metricKey] + correction),
    );

    const event: FeedbackEventV22 = {
      eventId: `RFL-${String(this.nextId++).padStart(4, "0")}`,
      metricKey,
      predicted,
      actual,
      delta,
      correctionApplied: correction,
      newWeight: this.weights[metricKey],
      timestamp: Date.now(),
    };
    this.events.push(event);
    if (this.events.length > 100) this.events.shift(); // rolling window
    return event;
  }

  getCalibrationState(): CalibrationState {
    const avgDelta =
      this.events.length > 0
        ? this.events.reduce((s, e) => s + Math.abs(e.delta), 0) / this.events.length
        : 0;

    const improvementVelocity = this.previousAvgDelta - avgDelta; // positive = improving
    this.previousAvgDelta = avgDelta;

    // Calibration score: 1 - normalized average delta
    const calibrationScore = Math.max(0, 1 - avgDelta);

    return {
      weights: { ...this.weights },
      totalEvents: this.events.length,
      averageDelta: avgDelta,
      improvementVelocity,
      calibrationScore,
    };
  }

  getHistory(): FeedbackEventV22[] {
    return [...this.events].reverse().slice(0, 20);
  }

  // Auto-generate feedback events to simulate continuous learning
  simulateLearningCycle(): FeedbackEventV22[] {
    const metrics = Object.keys(this.weights);
    return metrics.map((key) => {
      const predicted = this.weights[key];
      // Reality is slightly better than prediction (system is improving)
      const actual = Math.min(0.999, predicted + (Math.random() * 0.06 - 0.01));
      return this.logFeedback(key, predicted, actual);
    });
  }
}
