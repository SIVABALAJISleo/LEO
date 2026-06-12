// LEO AI V33 — Memory Residency Analyzer
// Capabilities: Trace L1/L2/L3 RAM hits, analyze memory access bottlenecks, and output the Cache Efficiency Score.

export interface CacheAccessStats {
  timestamp: number;
  l1Hits: number;
  l2Hits: number;
  l3Hits: number;
  ramHits: number;
  pageFaults: number;
  cacheEfficiencyScore: number; // 0 to 100
}

export class MemoryResidencyAnalyzer {
  private accessLog: CacheAccessStats[] = [];

  analyzeAccessPatterns(
    l1Hits: number,
    l2Hits: number,
    l3Hits: number,
    ramHits: number,
    pageFaults: number
  ): CacheAccessStats {
    const totalAccesses = l1Hits + l2Hits + l3Hits + ramHits + pageFaults;
    
    // Cache efficiency score computes how much RAM fetches are avoided
    // L1 hits = weight 1.0, L2 hits = weight 0.8, L3 hits = weight 0.5, RAM = 0.05
    let efficiencyNumerator = (l1Hits * 1.0) + (l2Hits * 0.8) + (l3Hits * 0.5) + (ramHits * 0.05);
    
    let cacheEfficiencyScore = totalAccesses > 0 
      ? (efficiencyNumerator / totalAccesses) * 100 
      : 100;
    
    // Penalize page faults
    if (pageFaults > 0) {
      cacheEfficiencyScore -= (pageFaults / (totalAccesses || 1)) * 200;
    }

    const finalScore = parseFloat(Math.min(100, Math.max(0, cacheEfficiencyScore)).toFixed(1));

    const stats: CacheAccessStats = {
      timestamp: Date.now(),
      l1Hits,
      l2Hits,
      l3Hits,
      ramHits,
      pageFaults,
      cacheEfficiencyScore: finalScore,
    };

    this.accessLog.push(stats);
    return stats;
  }

  getRecentStats(): CacheAccessStats | null {
    return this.accessLog[this.accessLog.length - 1] || null;
  }
}
