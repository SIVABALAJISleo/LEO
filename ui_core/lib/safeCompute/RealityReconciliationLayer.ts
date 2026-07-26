// REALITY RECONCILIATION LAYER
// Handles prediction ≠ truth scenarios with transparent corrections
// All corrections are logged with explicit reasons

export type CorrectionStrategy =
  | "ELASTIC_CORRECTION" // Fast snap for minor deltas (<10%)
  | "TEMPORAL_SMOOTHING" // Gradual transition for medium deltas (10-30%)
  | "SAFE_ROLLBACK" // Full rollback for large deltas (>30%)
  | "EXECUTION_HALT"; // Immediate stop for safety-critical failures

export interface PredictionResult {
  taskId: string;
  predictedValue: unknown;
  confidence: number;
  method: string;
  timestamp: Date;
}

export interface TruthResult {
  taskId: string;
  actualValue: unknown;
  source: "computation" | "authority" | "measurement";
  timestamp: Date;
}

export interface ReconciliationRecord {
  taskId: string;
  prediction: PredictionResult;
  truth: TruthResult;
  delta: number;
  deltaPercent: number;
  strategy: CorrectionStrategy;
  correctionApplied: boolean;
  reason: string;
  visibleToUser: boolean;
  timestamp: Date;
}

export interface ReconciliationStats {
  totalReconciliations: number;
  elasticCorrections: number;
  temporalSmoothings: number;
  safeRollbacks: number;
  executionHalts: number;
  averageDelta: number;
  maxDelta: number;
  successRate: number;
}

class RealityReconciliationLayerCore {
  private static instance: RealityReconciliationLayerCore;
  private records: ReconciliationRecord[] = [];
  private pendingPredictions: Map<string, PredictionResult> = new Map();

  private constructor() {}

  static getInstance(): RealityReconciliationLayerCore {
    if (!RealityReconciliationLayerCore.instance) {
      RealityReconciliationLayerCore.instance = new RealityReconciliationLayerCore();
    }
    return RealityReconciliationLayerCore.instance;
  }

  /**
   * Register a prediction for later reconciliation
   */
  registerPrediction(prediction: PredictionResult): void {
    this.pendingPredictions.set(prediction.taskId, prediction);
  }

  /**
   * RECONCILE prediction with truth
   * Chooses exactly ONE correction strategy
   * All corrections are visible and logged
   */
  reconcile(
    taskId: string,
    truth: TruthResult,
    options: {
      isSafetyCritical?: boolean;
      tolerancePercent?: number;
      forceStrategy?: CorrectionStrategy;
    } = {},
  ): ReconciliationRecord | null {
    const prediction = this.pendingPredictions.get(taskId);

    if (!prediction) {
      console.warn(`No pending prediction for task ${taskId}`);
      return null;
    }

    // Calculate delta
    const delta = this.calculateDelta(prediction.predictedValue, truth.actualValue);
    const deltaPercent = delta * 100;

    // Determine correction strategy
    const { strategy, reason, correctionApplied } = this.determineStrategy(
      delta,
      options.isSafetyCritical ?? false,
      options.tolerancePercent ?? 10,
      options.forceStrategy,
    );

    const record: ReconciliationRecord = {
      taskId,
      prediction,
      truth,
      delta,
      deltaPercent,
      strategy,
      correctionApplied,
      reason,
      visibleToUser: true, // Always visible - no hidden corrections
      timestamp: new Date(),
    };

    // Log the reconciliation
    this.records.push(record);
    this.pendingPredictions.delete(taskId);

    return record;
  }

  /**
   * Calculate delta between prediction and truth
   */
  private calculateDelta(predicted: unknown, actual: unknown): number {
    // Numeric comparison
    if (typeof predicted === "number" && typeof actual === "number") {
      if (actual === 0) return predicted === 0 ? 0 : 1;
      return Math.abs(predicted - actual) / Math.abs(actual);
    }

    // String comparison (Levenshtein-like)
    if (typeof predicted === "string" && typeof actual === "string") {
      const maxLen = Math.max(predicted.length, actual.length);
      if (maxLen === 0) return 0;

      let matches = 0;
      const minLen = Math.min(predicted.length, actual.length);
      for (let i = 0; i < minLen; i++) {
        if (predicted[i] === actual[i]) matches++;
      }
      return 1 - matches / maxLen;
    }

    // Boolean comparison
    if (typeof predicted === "boolean" && typeof actual === "boolean") {
      return predicted === actual ? 0 : 1;
    }

    // Object comparison (shallow)
    if (typeof predicted === "object" && typeof actual === "object") {
      try {
        const predStr = JSON.stringify(predicted);
        const actStr = JSON.stringify(actual);
        return predStr === actStr ? 0 : 0.5; // Binary match for objects
      } catch {
        return 0.5;
      }
    }

    // Default: assume 50% delta for incompatible types
    return 0.5;
  }

  /**
   * Determine correction strategy based on delta and criticality
   */
  private determineStrategy(
    delta: number,
    isSafetyCritical: boolean,
    tolerancePercent: number,
    forceStrategy?: CorrectionStrategy,
  ): { strategy: CorrectionStrategy; reason: string; correctionApplied: boolean } {
    // Honor forced strategy if provided
    if (forceStrategy) {
      return {
        strategy: forceStrategy,
        reason: `Strategy forced: ${forceStrategy}`,
        correctionApplied: forceStrategy !== "EXECUTION_HALT",
      };
    }

    const deltaPercent = delta * 100;
    const tolerance = tolerancePercent / 100;

    // Safety-critical with any significant delta: halt
    if (isSafetyCritical && delta > tolerance) {
      return {
        strategy: "EXECUTION_HALT",
        reason: `Safety-critical task with ${deltaPercent.toFixed(1)}% delta exceeds ${tolerancePercent}% tolerance. Execution halted for human review.`,
        correctionApplied: false,
      };
    }

    // Large delta (>30%): safe rollback
    if (delta > 0.3) {
      return {
        strategy: "SAFE_ROLLBACK",
        reason: `Large prediction error (${deltaPercent.toFixed(1)}%). Rolling back to last known good state.`,
        correctionApplied: true,
      };
    }

    // Medium delta (10-30%): temporal smoothing
    if (delta > 0.1) {
      return {
        strategy: "TEMPORAL_SMOOTHING",
        reason: `Medium prediction error (${deltaPercent.toFixed(1)}%). Applying gradual correction over time.`,
        correctionApplied: true,
      };
    }

    // Small delta (<10%): elastic correction
    return {
      strategy: "ELASTIC_CORRECTION",
      reason: `Minor prediction error (${deltaPercent.toFixed(1)}%). Applying instant elastic snap.`,
      correctionApplied: true,
    };
  }

  /**
   * Get reconciliation records for a task
   */
  getRecords(taskId?: string): ReconciliationRecord[] {
    if (taskId) {
      return this.records.filter((r) => r.taskId === taskId);
    }
    return [...this.records];
  }

  /**
   * Get statistics
   */
  getStats(): ReconciliationStats {
    if (this.records.length === 0) {
      return {
        totalReconciliations: 0,
        elasticCorrections: 0,
        temporalSmoothings: 0,
        safeRollbacks: 0,
        executionHalts: 0,
        averageDelta: 0,
        maxDelta: 0,
        successRate: 1,
      };
    }

    const stats: ReconciliationStats = {
      totalReconciliations: this.records.length,
      elasticCorrections: 0,
      temporalSmoothings: 0,
      safeRollbacks: 0,
      executionHalts: 0,
      averageDelta: 0,
      maxDelta: 0,
      successRate: 0,
    };

    let totalDelta = 0;
    let successCount = 0;

    this.records.forEach((record) => {
      switch (record.strategy) {
        case "ELASTIC_CORRECTION":
          stats.elasticCorrections++;
          break;
        case "TEMPORAL_SMOOTHING":
          stats.temporalSmoothings++;
          break;
        case "SAFE_ROLLBACK":
          stats.safeRollbacks++;
          break;
        case "EXECUTION_HALT":
          stats.executionHalts++;
          break;
      }

      totalDelta += record.delta;
      stats.maxDelta = Math.max(stats.maxDelta, record.delta);

      if (record.correctionApplied) {
        successCount++;
      }
    });

    stats.averageDelta = totalDelta / this.records.length;
    stats.successRate = successCount / this.records.length;

    return stats;
  }

  /**
   * Get recent corrections for UI display
   */
  getRecentCorrections(limit: number = 10): ReconciliationRecord[] {
    return this.records.slice(-limit).reverse();
  }

  /**
   * Clear old records (for memory management)
   */
  pruneOldRecords(maxAgeMs: number = 3600000): number {
    const cutoff = Date.now() - maxAgeMs;
    const initialLength = this.records.length;

    this.records = this.records.filter((r) => r.timestamp.getTime() > cutoff);

    return initialLength - this.records.length;
  }
}

export const realityReconciliationLayer = RealityReconciliationLayerCore.getInstance();
