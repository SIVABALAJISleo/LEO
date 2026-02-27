/**
 * GPU SAVINGS TRACKER
 * 
 * Tracks and exposes GPU efficiency metrics showing:
 * - % GPU compute avoided
 * - % jobs downgraded safely
 * - % reuse achieved
 * - % delegation prevented
 * 
 * This measures REAL IMPACT - not FLOPS.
 */

export interface GpuSavingsScore {
  // Core metrics
  computeAvoidedPercent: number;    // % of jobs where GPU was skipped entirely
  safeDowngradePercent: number;     // % of jobs that used reduced precision/res
  reusePercent: number;             // % of results served from cache/similarity
  delegationPreventedPercent: number; // % of jobs handled locally vs sent out
  
  // Efficiency breakdown
  totalJobsProcessed: number;
  jobsAvoidedGpu: number;
  jobsDowngraded: number;
  jobsFromCache: number;
  jobsCollapsed: number;
  jobsDelegated: number;
  jobsDeferred: number;
  
  // Impact metrics
  estimatedGpuHoursSaved: number;
  estimatedCostSaved: number;       // In USD (rough estimate)
  effectiveThroughputMultiplier: number; // How much more work done vs raw GPU
  
  // Quality assurance
  averageQualityScore: number;
  qualityViolations: number;        // Jobs that fell below quality floor
  
  // Timestamps
  trackerStartedAt: Date;
  lastUpdatedAt: Date;
}

export interface JobSavingsRecord {
  jobId: string;
  savedGpu: boolean;
  savingsType: 'avoided' | 'downgraded' | 'cached' | 'collapsed' | 'delegated' | 'deferred' | 'none';
  gpuHoursSaved: number;
  qualityScore: number;
  timestamp: Date;
}

class GpuSavingsTrackerEngine {
  private static instance: GpuSavingsTrackerEngine;
  private records: JobSavingsRecord[] = [];
  private startedAt: Date = new Date();
  
  // Running totals for efficiency
  private totals = {
    processed: 0,
    avoided: 0,
    downgraded: 0,
    cached: 0,
    collapsed: 0,
    delegated: 0,
    deferred: 0,
    gpuHoursSaved: 0,
    qualitySum: 0,
    qualityViolations: 0,
  };

  private constructor() {}

  static getInstance(): GpuSavingsTrackerEngine {
    if (!GpuSavingsTrackerEngine.instance) {
      GpuSavingsTrackerEngine.instance = new GpuSavingsTrackerEngine();
    }
    return GpuSavingsTrackerEngine.instance;
  }

  /**
   * Sync metrics with the real backend impact endpoint
   */
  async syncWithBackend(): Promise<void> {
    try {
      const response = await fetch('/api/status/impact');
      if (!response.ok) throw new Error('Failed to fetch impact metrics');
      const data = await response.json();
      
      // Update totals based on real backend data
      this.totals.avoided = data.compute_avoided_count;
      this.totals.cached = data.cache_hits;
      this.totals.processed = data.compute_avoided_count + data.cache_hits;
      
      console.log('GPU Savings synced with backend:', data);
    } catch (error) {
      console.error('Failed to sync GPU savings:', error);
    }
  }

  /**
   * Record a job's GPU savings
   */
  recordJobSavings(
    jobId: string,
    savingsType: JobSavingsRecord['savingsType'],
    gpuHoursSaved: number,
    qualityScore: number,
    qualityFloor: number = 0.8
  ): void {
    const record: JobSavingsRecord = {
      jobId,
      savedGpu: savingsType !== 'none' && savingsType !== 'delegated',
      savingsType,
      gpuHoursSaved,
      qualityScore,
      timestamp: new Date(),
    };

    this.records.push(record);
    
    // Update running totals
    this.totals.processed++;
    this.totals.gpuHoursSaved += gpuHoursSaved;
    this.totals.qualitySum += qualityScore;
    
    if (qualityScore < qualityFloor) {
      this.totals.qualityViolations++;
    }

    switch (savingsType) {
      case 'avoided':
        this.totals.avoided++;
        break;
      case 'downgraded':
        this.totals.downgraded++;
        break;
      case 'cached':
        this.totals.cached++;
        break;
      case 'collapsed':
        this.totals.collapsed++;
        break;
      case 'delegated':
        this.totals.delegated++;
        break;
      case 'deferred':
        this.totals.deferred++;
        break;
    }

    // Keep only last 10000 records for memory
    if (this.records.length > 10000) {
      this.records = this.records.slice(-10000);
    }
  }

  /**
   * Get the current GPU savings score
   */
  getSavingsScore(): GpuSavingsScore {
    const total = this.totals.processed || 1; // Avoid division by zero
    const localJobs = this.totals.processed - this.totals.delegated;

    return {
      // Core percentages
      computeAvoidedPercent: Math.round((this.totals.avoided / total) * 100),
      safeDowngradePercent: Math.round((this.totals.downgraded / total) * 100),
      reusePercent: Math.round(((this.totals.cached + this.totals.collapsed) / total) * 100),
      delegationPreventedPercent: Math.round((localJobs / total) * 100),

      // Job counts
      totalJobsProcessed: this.totals.processed,
      jobsAvoidedGpu: this.totals.avoided,
      jobsDowngraded: this.totals.downgraded,
      jobsFromCache: this.totals.cached,
      jobsCollapsed: this.totals.collapsed,
      jobsDelegated: this.totals.delegated,
      jobsDeferred: this.totals.deferred,

      // Impact
      estimatedGpuHoursSaved: Math.round(this.totals.gpuHoursSaved * 100) / 100,
      estimatedCostSaved: Math.round(this.totals.gpuHoursSaved * 2.5 * 100) / 100, // ~$2.50/GPU-hour estimate
      effectiveThroughputMultiplier: this.calculateThroughputMultiplier(),

      // Quality
      averageQualityScore: Math.round((this.totals.qualitySum / total) * 100) / 100,
      qualityViolations: this.totals.qualityViolations,

      // Timestamps
      trackerStartedAt: this.startedAt,
      lastUpdatedAt: new Date(),
    };
  }

  /**
   * Get efficiency summary as human-readable text
   */
  getEfficiencySummary(): string {
    const score = this.getSavingsScore();
    
    if (score.totalJobsProcessed === 0) {
      return 'No jobs processed yet. Efficiency metrics will appear after workload execution.';
    }

    const lines = [
      `GPU Efficiency Score: ${score.computeAvoidedPercent + score.reusePercent}%`,
      `├─ Compute Avoided: ${score.computeAvoidedPercent}%`,
      `├─ Cache/Reuse: ${score.reusePercent}%`,
      `├─ Safe Downgrades: ${score.safeDowngradePercent}%`,
      `├─ Local Processing: ${score.delegationPreventedPercent}%`,
      `├─ GPU Hours Saved: ${score.estimatedGpuHoursSaved}h (~$${score.estimatedCostSaved})`,
      `└─ Quality Score: ${score.averageQualityScore} (${score.qualityViolations} violations)`,
    ];

    return lines.join('\n');
  }

  /**
   * Get breakdown by savings type
   */
  getSavingsBreakdown(): Array<{ type: string; count: number; percent: number }> {
    const total = this.totals.processed || 1;
    
    return [
      { type: 'GPU Avoided', count: this.totals.avoided, percent: Math.round((this.totals.avoided / total) * 100) },
      { type: 'Downgraded', count: this.totals.downgraded, percent: Math.round((this.totals.downgraded / total) * 100) },
      { type: 'Cache Hit', count: this.totals.cached, percent: Math.round((this.totals.cached / total) * 100) },
      { type: 'Collapsed', count: this.totals.collapsed, percent: Math.round((this.totals.collapsed / total) * 100) },
      { type: 'Delegated', count: this.totals.delegated, percent: Math.round((this.totals.delegated / total) * 100) },
      { type: 'Deferred', count: this.totals.deferred, percent: Math.round((this.totals.deferred / total) * 100) },
    ];
  }

  /**
   * Check if system is achieving target efficiency
   */
  isEfficiencyTargetMet(targetPercent: number = 50): boolean {
    const score = this.getSavingsScore();
    return (score.computeAvoidedPercent + score.reusePercent) >= targetPercent;
  }

  /**
   * Reset all tracking data
   */
  reset(): void {
    this.records = [];
    this.startedAt = new Date();
    this.totals = {
      processed: 0,
      avoided: 0,
      downgraded: 0,
      cached: 0,
      collapsed: 0,
      delegated: 0,
      deferred: 0,
      gpuHoursSaved: 0,
      qualitySum: 0,
      qualityViolations: 0,
    };
  }

  private calculateThroughputMultiplier(): number {
    // How much more work can be done with efficiency gains
    // If 50% of work is avoided/cached, effective multiplier is 2x
    const total = this.totals.processed || 1;
    const saved = this.totals.avoided + this.totals.cached + this.totals.collapsed;
    const multiplier = total / (total - saved + 1);
    return Math.round(multiplier * 10) / 10;
  }
}

export const gpuSavingsTracker = GpuSavingsTrackerEngine.getInstance();
