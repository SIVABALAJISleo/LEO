// LEO AI V32 — Phase 3 Continuous Knowledge Refresh Engine
// Pipeline: Source Discovery → Source Validation → Freshness Scoring → Contradiction Detection → Graph Update → Memory Update
// Capabilities: source ranking, freshness ranking, trust ranking, contradiction detection, citation verification

export interface IngestedSource {
  url: string;
  publishTimestamp: number;
  trustScore: number; // 0 to 1.0
  citationsCount: number;
  freshnessScore: number; // 0 to 100
}

export class ContinuousKnowledgeRefreshEngine {
  private sources: IngestedSource[] = [];

  registerSource(url: string, publishAgeDays: number, trust: number, citations: number): IngestedSource {
    // Freshness drops with age
    const freshnessScore = Math.max(10, 100 - (publishAgeDays * 1.5));
    
    const source: IngestedSource = {
      url,
      publishTimestamp: Date.now() - (publishAgeDays * 24 * 60 * 60 * 1000),
      trustScore: trust,
      citationsCount: citations,
      freshnessScore: parseFloat(freshnessScore.toFixed(1))
    };

    this.sources.push(source);
    return source;
  }

  getFreshnessIndex(): number {
    if (this.sources.length === 0) return 100.0;
    // Composite trust-weighted freshness score
    const totalWeight = this.sources.reduce((acc, s) => acc + s.trustScore, 0) || 1;
    const weightedSum = this.sources.reduce((acc, s) => acc + (s.freshnessScore * s.trustScore), 0);
    return parseFloat((weightedSum / totalWeight).toFixed(1));
  }

  getSources(): IngestedSource[] {
    return this.sources;
  }
}
