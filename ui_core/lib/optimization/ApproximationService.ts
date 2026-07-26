import { BloomFilter, HyperLogLog } from "./Approximation";

/**
 * ApproximationService (Pillar 5)
 * Centralizes probabilistic data structures for O(1) space/time checks.
 * Replaces brute-force logic with efficient estimation.
 */
export class ApproximationService {
  private static instance: ApproximationService;
  private bloomFilter: BloomFilter;
  private hyperLogLog: HyperLogLog;
  private queryCounter: HyperLogLog;

  private constructor() {
    // Expected items: 10,000, False Positive Rate: 1%
    this.bloomFilter = new BloomFilter(10000, 0.01);
    this.hyperLogLog = new HyperLogLog(10); // 2% error rate
    this.queryCounter = new HyperLogLog(10);
  }

  static getInstance(): ApproximationService {
    if (!ApproximationService.instance) {
      ApproximationService.instance = new ApproximationService();
    }
    return ApproximationService.instance;
  }

  /**
   * Records a query for unique count estimation.
   */
  recordQuery(query: string): void {
    this.queryCounter.add(query);
  }

  /**
   * Estimated count of unique queries seen.
   */
  getUniqueQueryCount(): number {
    return this.queryCounter.count();
  }

  /**
   * Marks a query as "known slow" or "uncacheable".
   */
  markUncacheable(query: string): void {
    this.bloomFilter.add(query);
  }

  /**
   * Quickly checks if a query is likely uncacheable.
   * Prevents unnecessary expensive cache lookups.
   */
  isLikelyUncacheable(query: string): boolean {
    return this.bloomFilter.has(query);
  }

  /**
   * Provides a bounded estimation for heavy simulations.
   * @param exactValue The raw value to approximate.
   * @param tolerance Fractional tolerance (e.g., 0.05 for 5%).
   */
  estimate(exactValue: number, tolerance: number = 0.05): number {
    const variance = exactValue * tolerance;
    return exactValue + (Math.random() * 2 - 1) * variance;
  }
}
