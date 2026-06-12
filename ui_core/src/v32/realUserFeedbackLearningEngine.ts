// LEO AI V32 — Phase 1 Real User Feedback Learning Engine
// Feedback Pipeline: User Query → Response → User Action → User Satisfaction → Outcome Tracking → Improvement Signal → Memory Update → Routing Update
// Purpose: Transform user interactions into intelligence improvements.

export interface UserActionLog {
  query: string;
  action: "Accepted" | "Rejected" | "Edited" | "Ignored";
  repeatedQuestion: boolean;
  satisfactionRating: number; // 1 to 5
}

export interface UserLearningProfile {
  successScore: number;       // 0 to 100
  correctionScore: number;    // 0 to 100
  rejectionScore: number;     // 0 to 100
  clarificationScore: number; // 0 to 100
  workflowCompletionScore: number; // 0 to 100
}

export class RealUserFeedbackLearningEngine {
  private logs: UserActionLog[] = [];

  recordInteraction(
    query: string, 
    action: "Accepted" | "Rejected" | "Edited" | "Ignored",
    repeatedQuestion: boolean,
    satisfactionRating: number
  ): void {
    this.logs.push({ query, action, repeatedQuestion, satisfactionRating });
  }

  generateProfile(): { profile: UserLearningProfile; confidenceAdjustedLearningWeights: Record<string, number>; } {
    const total = this.logs.length || 1;
    
    const acceptedCount = this.logs.filter(l => l.action === "Accepted").length;
    const editedCount = this.logs.filter(l => l.action === "Edited").length;
    const rejectedCount = this.logs.filter(l => l.action === "Rejected").length;
    const repeatedCount = this.logs.filter(l => l.repeatedQuestion).length;

    const successScore = parseFloat(((acceptedCount / total) * 100).toFixed(1));
    const correctionScore = parseFloat(((editedCount / total) * 100).toFixed(1));
    const rejectionScore = parseFloat(((rejectedCount / total) * 100).toFixed(1));
    const clarificationScore = parseFloat(((repeatedCount / total) * 100).toFixed(1));
    const workflowCompletionScore = parseFloat((( (acceptedCount + editedCount) / total) * 100).toFixed(1));

    const profile: UserLearningProfile = {
      successScore,
      correctionScore,
      rejectionScore,
      clarificationScore,
      workflowCompletionScore
    };

    // Calculate weight corrections: lower success implies we need higher exploration weights, higher edit implies higher verification weights
    const confidenceAdjustedLearningWeights = {
      semanticCacheRetrievalWeight: parseFloat((0.85 + (successScore / 100) * 0.1).toFixed(3)),
      neuralEscalationWeight: parseFloat((0.15 + (rejectionScore / 100) * 0.3).toFixed(3)),
      verificationRigidityWeight: parseFloat((0.60 + (correctionScore / 100) * 0.25).toFixed(3)),
      prefixMatchConfidence: parseFloat((0.90 - (clarificationScore / 100) * 0.2).toFixed(3))
    };

    return {
      profile,
      confidenceAdjustedLearningWeights
    };
  }

  getLogsCount(): number {
    return this.logs.length;
  }
}
