// LEO AI V34 — Freshness Monitor
// Capabilities: Track information age, calculate decay weights, and output the Knowledge Freshness Score.

export interface FreshnessMetrics {
  timestamp: number;
  averageAgeDays: number;
  deprecatedFactsCount: number;
  activeStaleConceptsCount: number;
  knowledgeFreshnessScore: number; // 0 to 100
}

export class FreshnessMonitor {
  calculateFreshness(
    factsAgeArray: number[], // array of timestamp ages in milliseconds
    staleCount: number,
    deprecatedCount: number
  ): FreshnessMetrics {
    const totalFacts = factsAgeArray.length;
    let averageAgeDays = 0;

    if (totalFacts > 0) {
      const totalAgeMs = factsAgeArray.reduce((sum, val) => sum + (Date.now() - val), 0);
      const avgAgeMs = totalAgeMs / totalFacts;
      averageAgeDays = avgAgeMs / (1000 * 60 * 60 * 24);
    }

    // Knowledge Freshness Score decays as average age increases and stale concepts gather
    // Target: average age under 15 days, 0 stale elements = 100 score
    const ageFactor = Math.max(0, 100 - (averageAgeDays * 2.5)); // loss of 2.5 points per day
    const stalePenalty = staleCount * 4.5;
    const deprecatedPenalty = deprecatedCount * 8.0;

    const scoreRaw = ageFactor - stalePenalty - deprecatedPenalty;
    const knowledgeFreshnessScore = parseFloat(Math.min(100.0, Math.max(0.0, scoreRaw)).toFixed(1));

    return {
      timestamp: Date.now(),
      averageAgeDays: parseFloat(averageAgeDays.toFixed(2)),
      deprecatedFactsCount: deprecatedCount,
      activeStaleConceptsCount: staleCount,
      knowledgeFreshnessScore
    };
  }
}
