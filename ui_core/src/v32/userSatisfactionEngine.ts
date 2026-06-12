// LEO AI V32 — Phase 2 User Satisfaction Intelligence Engine
// Measure: response usefulness, completion rate, resolution rate, retry rate, abandonment rate
// Formula: Resolution Success + Workflow Completion + Low Retry Rate + Positive Feedback.

export interface UserSatisfactionTelemetry {
  usefulnessScore: number; // 0 to 10
  completionRatePct: number;
  resolutionRatePct: number;
  retryRatePct: number;
  abandonmentRatePct: number;
}

export class UserSatisfactionEngine {
  calculateUtility(tele: UserSatisfactionTelemetry): { satisfactionIndex: number; realWorldUtilityScore: number; } {
    
    const resolutionSuccessFactor = tele.resolutionRatePct / 100;
    const workflowCompletionFactor = tele.completionRatePct / 100;
    const lowRetryFactor = 1.0 - (tele.retryRatePct / 100);
    const positiveFeedbackFactor = tele.usefulnessScore / 10;

    // Index is composite of these factors
    const satisfactionIndex = parseFloat(
      ((resolutionSuccessFactor * 0.3 + workflowCompletionFactor * 0.3 + lowRetryFactor * 0.2 + positiveFeedbackFactor * 0.2) * 100).toFixed(1)
    );

    // Real-world utility scales satisfaction against low abandonment
    const lowAbandonmentFactor = 1.0 - (tele.abandonmentRatePct / 100);
    const realWorldUtilityScore = parseFloat(
      ((satisfactionIndex / 100) * lowAbandonmentFactor * 10.0).toFixed(2)
    );

    return {
      satisfactionIndex,
      realWorldUtilityScore
    };
  }
}
