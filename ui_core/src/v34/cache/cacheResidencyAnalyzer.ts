// LEO AI V34 — Cache Residency Analyzer
// Capabilities: Compute the Cache Efficiency Index based on hits rates across CPU layers.

export interface CacheResidencyTelemetry {
  timestamp: number;
  l1HitRatePct: number;
  l2HitRatePct: number;
  l3HitRatePct: number;
  ramHitRatePct: number;
  cacheEfficiencyIndex: number; // 0 to 100
}

export class CacheResidencyAnalyzer {
  calculateCacheIndex(
    l1Hits: number,
    l2Hits: number,
    l3Hits: number,
    ramHits: number,
  ): CacheResidencyTelemetry {
    const total = l1Hits + l2Hits + l3Hits + ramHits;
    if (total === 0) {
      return {
        timestamp: Date.now(),
        l1HitRatePct: 0,
        l2HitRatePct: 0,
        l3HitRatePct: 0,
        ramHitRatePct: 100,
        cacheEfficiencyIndex: 0,
      };
    }

    const l1HitRatePct = parseFloat(((l1Hits / total) * 100).toFixed(1));
    const l2HitRatePct = parseFloat(((l2Hits / total) * 100).toFixed(1));
    const l3HitRatePct = parseFloat(((l3Hits / total) * 100).toFixed(1));
    const ramHitRatePct = parseFloat(((ramHits / total) * 100).toFixed(1));

    // L1 hits count as 1.0 weight, L2 as 0.75, L3 as 0.50, RAM as 0.0
    const scoreRaw = l1HitRatePct * 1.0 + l2HitRatePct * 0.75 + l3HitRatePct * 0.5;
    const cacheEfficiencyIndex = parseFloat(Math.min(100.0, Math.max(0.0, scoreRaw)).toFixed(1));

    return {
      timestamp: Date.now(),
      l1HitRatePct,
      l2HitRatePct,
      l3HitRatePct,
      ramHitRatePct,
      cacheEfficiencyIndex,
    };
  }
}
