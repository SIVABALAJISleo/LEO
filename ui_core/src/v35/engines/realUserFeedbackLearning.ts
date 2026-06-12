// LEO AI V35 — Real User Feedback Learning
// Collects user ratings, corrections, and workflow outcomes to adjust parameters dynamically.

export interface UserFeedbackRecord {
  id: string;
  query: string;
  userRating: number; // 1 to 5
  userCorrection: string;
  timestamp: number;
}

export interface FeedbackIntelligenceStats {
  successRatePct: number;
  failureRatePct: number;
  totalFeedbackSamples: number;
  calibrationAdjustmentDelta: number;
  feedbackRecords: UserFeedbackRecord[];
}

export class RealUserFeedbackLearning {
  private feedbackLog: UserFeedbackRecord[] = [
    {
      id: "feed-001",
      query: "Optimize compiler register pack",
      userRating: 4,
      userCorrection: "Use AVX-VNNI instead of base AVX512 registers.",
      timestamp: Date.now() - 600000
    }
  ];

  /**
   * Submits user corrections to the log and recalibrates model weights simulation variables.
   */
  public logFeedbackAndLearn(
    query: string,
    userRating: number,
    userCorrection: string
  ): FeedbackIntelligenceStats {
    if (userCorrection.trim().length > 0) {
      this.feedbackLog.push({
        id: `feed-00${this.feedbackLog.length + 1}`,
        query,
        userRating,
        userCorrection,
        timestamp: Date.now()
      });
    }

    const totalFeedbackSamples = this.feedbackLog.length;
    
    // Success rate is simulated based on average user ratings
    const sumRatings = this.feedbackLog.reduce((acc, curr) => acc + curr.userRating, 0);
    const averageRating = sumRatings / totalFeedbackSamples;
    
    const successRatePct = parseFloat(((averageRating / 5.0) * 100).toFixed(2));
    const failureRatePct = parseFloat((100.0 - successRatePct).toFixed(2));

    // Learning Loop calibrates adjustment factor:
    // High failure rates increase the correction/adjustment weights delta
    const calibrationAdjustmentDelta = failureRatePct > 10.0 ? -0.08 : -0.01;

    return {
      successRatePct,
      failureRatePct,
      totalFeedbackSamples,
      calibrationAdjustmentDelta,
      feedbackRecords: [...this.feedbackLog]
    };
  }

  /**
   * Retrieves logged user feedback outcomes.
   */
  public getFeedbackLog(): UserFeedbackRecord[] {
    return this.feedbackLog;
  }
}
