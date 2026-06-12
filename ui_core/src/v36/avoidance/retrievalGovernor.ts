// LEO AI V36 — Retrieval Governor
// Bypasses heavy neural generation if external database facts contain high confidence matches.

export class RetrievalGovernor {
  public shouldBypassModel(
    retrievalScore: number,
    confidenceThreshold: number = 0.90
  ): boolean {
    return retrievalScore >= confidenceThreshold;
  }
}
