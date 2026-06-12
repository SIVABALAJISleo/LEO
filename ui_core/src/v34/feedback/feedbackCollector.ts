// LEO AI V34 — Feedback Collector
// Capabilities: Log user ratings, collect edited responses, and compile interaction profiles.

export interface UserRating {
  ratingId: string;
  query: string;
  ratingValue: number; // 1 to 5
  userEdits?: string;
  timestamp: number;
}

export class FeedbackCollector {
  private ratingsLog: UserRating[] = [];

  logFeedback(query: string, ratingValue: number, userEdits?: string): UserRating {
    const rating: UserRating = {
      ratingId: `rating-v34-${Math.random().toString(36).substring(7)}`,
      query,
      ratingValue,
      userEdits,
      timestamp: Date.now()
    };
    this.ratingsLog.push(rating);
    return rating;
  }

  getRecentRatings(): UserRating[] {
    return this.ratingsLog;
  }
}
