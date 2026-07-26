/**
 * Compute Tracker
 * Profile and export compute metrics for analysis.
 */

import { NoveltyState } from "../intelligence/NoveltyDetector";

export interface ComputeRecord {
  timestamp: number;
  inferenceTimeMs: number;
  noveltyState: NoveltyState;
  tokensProcessed: number;
  cacheHit: boolean;
  mode: "cached" | "lightweight" | "full";
}

export class ComputeTracker {
  private static instance: ComputeTracker;
  private records: ComputeRecord[] = [];
  private readonly MAX_RECORDS = 10000;

  private constructor() {}

  static getInstance(): ComputeTracker {
    if (!ComputeTracker.instance) {
      ComputeTracker.instance = new ComputeTracker();
    }
    return ComputeTracker.instance;
  }

  /**
   * Log compute event
   */
  log(record: Omit<ComputeRecord, "timestamp">): void {
    this.records.push({
      timestamp: Date.now(),
      ...record,
    });

    if (this.records.length > this.MAX_RECORDS) {
      this.records.shift();
    }
  }

  /**
   * Export CSV for graphing
   */
  exportCSV(): string {
    const headers = [
      "timestamp",
      "inference_time_ms",
      "novelty_state",
      "tokens_processed",
      "cache_hit",
      "mode",
    ];

    const rows = this.records.map((r) => [
      new Date(r.timestamp).toISOString(),
      r.inferenceTimeMs.toFixed(2),
      r.noveltyState,
      r.tokensProcessed,
      r.cacheHit ? "1" : "0",
      r.mode,
    ]);

    return [headers.join(","), ...rows.map((row) => row.join(","))].join("\n");
  }

  /**
   * Get summary statistics
   */
  getSummary() {
    if (this.records.length === 0) {
      return null;
    }

    const cacheHits = this.records.filter((r) => r.cacheHit).length;
    const avgInferenceTime =
      this.records.reduce((sum, r) => sum + r.inferenceTimeMs, 0) / this.records.length;
    const totalTokens = this.records.reduce((sum, r) => sum + r.tokensProcessed, 0);

    const byNovelty = {
      NEW: this.records.filter((r) => r.noveltyState === NoveltyState.NEW).length,
      SIMILAR: this.records.filter((r) => r.noveltyState === NoveltyState.SIMILAR).length,
      SAME: this.records.filter((r) => r.noveltyState === NoveltyState.SAME).length,
    };

    const avgTimeByMode = {
      cached: this.averageTime("cached"),
      lightweight: this.averageTime("lightweight"),
      full: this.averageTime("full"),
    };

    return {
      totalRecords: this.records.length,
      cacheHitRate: (cacheHits / this.records.length) * 100,
      avgInferenceTimeMs: avgInferenceTime,
      totalTokensProcessed: totalTokens,
      noveltyDistribution: byNovelty,
      avgTimeByMode,
    };
  }

  private averageTime(mode: string): number {
    const records = this.records.filter((r) => r.mode === mode);
    if (records.length === 0) return 0;
    return records.reduce((sum, r) => sum + r.inferenceTimeMs, 0) / records.length;
  }

  /**
   * Clear all records
   */
  clear(): void {
    this.records = [];
  }
}
