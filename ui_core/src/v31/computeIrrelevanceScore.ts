// LEO AI V31 — Phase 16 Compute Irrelevance Score
// Track: Queries Avoided, Memory Hits, GraphRAG Hits, Inference Saved, Energy Saved.
// Generate: Compute Irrelevance Index (0-100 score).

export interface ScoreBreakdown {
  queriesAvoidedPct: number;
  memoryHitsPct: number;
  graphRagHitsPct: number;
  inferenceSavedPct: number;
  energySavedPct: number;
}

export class ComputeIrrelevanceScore {
  private queriesAvoided = 0;
  private memoryHits = 0;
  private graphRagHits = 0;
  private totalQueries = 0;
  private energySavedJoules = 0;

  recordEvaluation(avoided: boolean, source: "memory" | "graphrag" | "inference", energySaved: number): void {
    this.totalQueries++;
    if (avoided) {
      this.queriesAvoided++;
      if (source === "memory") this.memoryHits++;
      if (source === "graphrag") this.graphRagHits++;
    }
    this.energySavedJoules += energySaved;
  }

  getMetrics(): ScoreBreakdown & { index: number; energySavedKWh: number; } {
    const total = this.totalQueries || 1;
    const queriesAvoidedPct = parseFloat(((this.queriesAvoided / total) * 100).toFixed(1));
    const memoryHitsPct = parseFloat(((this.memoryHits / total) * 100).toFixed(1));
    const graphRagHitsPct = parseFloat(((this.graphRagHits / total) * 100).toFixed(1));
    const inferenceSavedPct = queriesAvoidedPct;
    
    // Scale energy savings relative to a benchmark
    const maxPossibleEnergySaved = total * 85.0; // 85 Joules is neural fallback draw
    const energySavedPct = parseFloat(((this.energySavedJoules / maxPossibleEnergySaved) * 100).toFixed(1));

    // Index is a composite weight of avoidance rate, cache hits, and energy efficiency
    const index = Math.min(100, parseFloat(
      (queriesAvoidedPct * 0.4 + memoryHitsPct * 0.2 + graphRagHitsPct * 0.2 + energySavedPct * 0.2).toFixed(1)
    ));

    return {
      queriesAvoidedPct,
      memoryHitsPct,
      graphRagHitsPct,
      inferenceSavedPct,
      energySavedPct,
      index,
      energySavedKWh: parseFloat((this.energySavedJoules / 3600000).toFixed(4)) // 1 Wh = 3600 Joules
    };
  }

  reset(): void {
    this.queriesAvoided = 0;
    this.memoryHits = 0;
    this.graphRagHits = 0;
    this.totalQueries = 0;
    this.energySavedJoules = 0;
  }
}
