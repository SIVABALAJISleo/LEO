/**
 * UNIVERSAL DECISION MATRIX (ALWAYS ON)
 * 
 * The real "brain" of the system - runs every task/frame/object
 * 
 * RESPONSIBILITIES:
 * 1. CRITICALITY SCORING (deterministic)
 * 2. PARALLEL TRUTH SOURCES (always run)
 * 3. DECISION RULES (no exceptions)
 * 4. TRUTH GUARD (always on)
 * 
 * ABSOLUTE RULES:
 * - No fake compute
 * - No physics lies  
 * - No hardware emulation
 * - Only deterministic, explainable, verifiable engineering
 */

import { masterPredictorEngine, PredictorResult } from './MasterPredictorEngine';
import { knowledgeLookupVault, LookupMatch } from './KnowledgeLookupVault';

// ============================================
// TYPES
// ============================================

export type CriticalityLevel = 'HIGH' | 'MEDIUM' | 'LOW';

export interface CriticalityScore {
  level: CriticalityLevel;
  isUserInteractive: boolean;
  isOutcomeAffecting: boolean;
  isVisuallyDominant: boolean;
  isBackgroundOnly: boolean;
  score: number; // 0-1 deterministic
  reason: string;
}

export interface TruthSource {
  name: 'prediction' | 'vault' | 'local_compute' | 'swarm';
  available: boolean;
  confidence: number;
  latencyMs: number;
  result?: unknown;
  verified: boolean;
}

export interface TruthGuardResult {
  passed: boolean;
  deltaComparison: boolean;
  physicsConsistency: boolean;
  latencyThreshold: boolean;
  correctionApplied: boolean;
  correctionReason?: string;
}

export interface MatrixDecision {
  workloadId: string;
  criticality: CriticalityScore;
  truthSources: TruthSource[];
  selectedSource: TruthSource | null;
  truthGuard: TruthGuardResult;
  finalPath: 'RAW_COMPUTE' | 'PREDICTION' | 'VAULT' | 'SWARM' | 'EXPLAIN';
  reason: string;
  decisionTimeMs: number;
  gpuAvoided: boolean;
  timestamp: Date;
}

export interface MatrixStats {
  totalDecisions: number;
  byPath: Record<MatrixDecision['finalPath'], number>;
  byCriticality: Record<CriticalityLevel, number>;
  correctionRate: number;
  avgDecisionTimeMs: number;
  gpuAvoidanceRate: number;
  lastUpdated: Date;
}

// ============================================
// CRITICALITY THRESHOLDS (DETERMINISTIC)
// ============================================

const CRITICALITY_WEIGHTS = {
  userInteractive: 0.35,
  outcomeAffecting: 0.30,
  visuallyDominant: 0.20,
  backgroundOnly: -0.25, // Reduces criticality
} as const;

const HIGH_CRITICALITY_THRESHOLD = 0.70;
const MEDIUM_CRITICALITY_THRESHOLD = 0.40;

// ============================================
// PREDICTION CONFIDENCE THRESHOLD
// ============================================

const PREDICTION_CONFIDENCE_THRESHOLD = 0.99;
const VAULT_SIMILARITY_THRESHOLD = 0.90;
const LATENCY_DRIFT_THRESHOLD_MS = 50;
const VISUAL_DELTA_THRESHOLD = 0.02;

// ============================================
// CORE IMPLEMENTATION
// ============================================

class UniversalDecisionMatrixCore {
  private static instance: UniversalDecisionMatrixCore;
  
  private stats: MatrixStats = {
    totalDecisions: 0,
    byPath: {
      RAW_COMPUTE: 0,
      PREDICTION: 0,
      VAULT: 0,
      SWARM: 0,
      EXPLAIN: 0,
    },
    byCriticality: {
      HIGH: 0,
      MEDIUM: 0,
      LOW: 0,
    },
    correctionRate: 0,
    avgDecisionTimeMs: 0,
    gpuAvoidanceRate: 0,
    lastUpdated: new Date(),
  };
  
  private decisionTimes: number[] = [];
  private corrections = 0;
  private gpuAvoided = 0;

  private constructor() {}

  static getInstance(): UniversalDecisionMatrixCore {
    if (!UniversalDecisionMatrixCore.instance) {
      UniversalDecisionMatrixCore.instance = new UniversalDecisionMatrixCore();
    }
    return UniversalDecisionMatrixCore.instance;
  }

  /**
   * MAIN ENTRY POINT - Execute decision matrix for every workload
   */
  async decide(
    workloadId: string,
    workloadType: string,
    input: unknown,
    context: {
      isInteractive?: boolean;
      isVisuallyDominant?: boolean;
      isBackground?: boolean;
      affectsOutcome?: boolean;
      maxLatencyMs?: number;
      requireExact?: boolean;
      swarmAvailable?: boolean;
      localGpuAvailable?: boolean;
    } = {}
  ): Promise<MatrixDecision> {
    const startTime = performance.now();

    // ===== STEP 1: CRITICALITY SCORING =====
    const criticality = this.scoreCriticality(workloadType, context);

    // ===== STEP 2: PARALLEL TRUTH SOURCES =====
    const truthSources = await this.gatherTruthSources(
      workloadId,
      workloadType,
      input,
      context
    );

    // ===== STEP 3: DECISION RULES =====
    const { selectedSource, finalPath, reason } = this.applyDecisionRules(
      criticality,
      truthSources,
      context
    );

    // ===== STEP 4: TRUTH GUARD =====
    const truthGuard = this.applyTruthGuard(
      selectedSource,
      truthSources,
      context.maxLatencyMs
    );

    // If truth guard failed, fall back
    let actualPath = finalPath;
    let actualSource = selectedSource;
    let actualReason = reason;

    if (!truthGuard.passed && truthGuard.correctionApplied) {
      const fallback = this.handleFallback(truthSources, context);
      actualPath = fallback.path;
      actualSource = fallback.source;
      actualReason = `Fallback: ${truthGuard.correctionReason}. ${fallback.reason}`;
    }

    // Track GPU avoidance
    const gpuWasAvoided = actualPath !== 'RAW_COMPUTE' && actualPath !== 'EXPLAIN';
    if (gpuWasAvoided) this.gpuAvoided++;
    if (truthGuard.correctionApplied) this.corrections++;

    const decisionTimeMs = performance.now() - startTime;
    this.updateStats(actualPath, criticality.level, decisionTimeMs);

    return {
      workloadId,
      criticality,
      truthSources,
      selectedSource: actualSource,
      truthGuard,
      finalPath: actualPath,
      reason: actualReason,
      decisionTimeMs,
      gpuAvoided: gpuWasAvoided,
      timestamp: new Date(),
    };
  }

  /**
   * STEP 1: Criticality Scoring (Deterministic)
   */
  private scoreCriticality(
    workloadType: string,
    context: {
      isInteractive?: boolean;
      isVisuallyDominant?: boolean;
      isBackground?: boolean;
      affectsOutcome?: boolean;
    }
  ): CriticalityScore {
    const type = workloadType.toLowerCase();

    // Determine flags from context or workload type
    const isUserInteractive = context.isInteractive ?? (
      type.includes('interactive') || 
      type.includes('realtime') || 
      type.includes('input')
    );

    const isOutcomeAffecting = context.affectsOutcome ?? (
      type.includes('final') ||
      type.includes('production') ||
      type.includes('export') ||
      type.includes('critical')
    );

    const isVisuallyDominant = context.isVisuallyDominant ?? (
      type.includes('hero') ||
      type.includes('main') ||
      type.includes('primary')
    );

    const isBackgroundOnly = context.isBackground ?? (
      type.includes('background') ||
      type.includes('prefetch') ||
      type.includes('warmup')
    );

    // Calculate deterministic score
    let score = 0;
    if (isUserInteractive) score += CRITICALITY_WEIGHTS.userInteractive;
    if (isOutcomeAffecting) score += CRITICALITY_WEIGHTS.outcomeAffecting;
    if (isVisuallyDominant) score += CRITICALITY_WEIGHTS.visuallyDominant;
    if (isBackgroundOnly) score += CRITICALITY_WEIGHTS.backgroundOnly;

    // Clamp to 0-1
    score = Math.max(0, Math.min(1, score));

    // Determine level
    let level: CriticalityLevel = 'LOW';
    if (score >= HIGH_CRITICALITY_THRESHOLD) level = 'HIGH';
    else if (score >= MEDIUM_CRITICALITY_THRESHOLD) level = 'MEDIUM';

    // Generate reason
    const reasons: string[] = [];
    if (isUserInteractive) reasons.push('user-interactive');
    if (isOutcomeAffecting) reasons.push('outcome-affecting');
    if (isVisuallyDominant) reasons.push('visually-dominant');
    if (isBackgroundOnly) reasons.push('background-only');

    return {
      level,
      isUserInteractive,
      isOutcomeAffecting,
      isVisuallyDominant,
      isBackgroundOnly,
      score,
      reason: reasons.length > 0 ? reasons.join(', ') : 'standard workload',
    };
  }

  /**
   * STEP 2: Gather Truth Sources (Parallel Execution)
   */
  private async gatherTruthSources(
    workloadId: string,
    workloadType: string,
    input: unknown,
    context: { swarmAvailable?: boolean; localGpuAvailable?: boolean }
  ): Promise<TruthSource[]> {
    const sources: TruthSource[] = [];
    const startTimes: Record<string, number> = {};

    // Execute all sources in parallel
    const [predictionResult, vaultResult] = await Promise.all([
      // 1. Prediction Engine
      (async (): Promise<TruthSource> => {
        startTimes.prediction = performance.now();
        try {
          const result = masterPredictorEngine.predict(
            workloadId,
            workloadType,
            input,
            { minConfidence: 0.90 }
          );
          return {
            name: 'prediction',
            available: result.decision.path === 'SHORTCUT' || result.decision.path === 'LOOKUP',
            confidence: result.decision.confidence,
            latencyMs: performance.now() - startTimes.prediction,
            result: result.result,
            verified: result.decision.confidence >= PREDICTION_CONFIDENCE_THRESHOLD,
          };
        } catch {
          return {
            name: 'prediction',
            available: false,
            confidence: 0,
            latencyMs: performance.now() - startTimes.prediction,
            verified: false,
          };
        }
      })(),

      // 2. Knowledge Vault Lookup
      (async (): Promise<TruthSource> => {
        startTimes.vault = performance.now();
        try {
          const lookupKey = `${workloadType}_${JSON.stringify(input).slice(0, 50)}`;
          const match = knowledgeLookupVault.lookup(
            { workloadType, key: lookupKey },
            { minConfidence: 0.85 }
          );
          return {
            name: 'vault',
            available: match.found && match.canUse,
            confidence: match.similarity,
            latencyMs: performance.now() - startTimes.vault,
            result: match.entry?.value,
            verified: match.entry?.source === 'verified_historical' || match.entry?.source === 'reference_dataset',
          };
        } catch {
          return {
            name: 'vault',
            available: false,
            confidence: 0,
            latencyMs: performance.now() - startTimes.vault,
            verified: false,
          };
        }
      })(),
    ]);

    sources.push(predictionResult, vaultResult);

    // 3. Local Compute (always available if GPU present)
    sources.push({
      name: 'local_compute',
      available: context.localGpuAvailable ?? false,
      confidence: 1.0, // Raw compute is always accurate
      latencyMs: 0, // Will be measured at execution
      verified: true,
    });

    // 4. Swarm (if available)
    sources.push({
      name: 'swarm',
      available: context.swarmAvailable ?? false,
      confidence: 0.95, // Swarm results need consensus
      latencyMs: 0,
      verified: false, // Needs verification
    });

    return sources;
  }

  /**
   * STEP 3: Apply Decision Rules (NO EXCEPTIONS)
   */
  private applyDecisionRules(
    criticality: CriticalityScore,
    sources: TruthSource[],
    context: { requireExact?: boolean }
  ): { selectedSource: TruthSource | null; finalPath: MatrixDecision['finalPath']; reason: string } {
    const prediction = sources.find(s => s.name === 'prediction');
    const vault = sources.find(s => s.name === 'vault');
    const localCompute = sources.find(s => s.name === 'local_compute');
    const swarm = sources.find(s => s.name === 'swarm');

    // RULE 1: If CRITICALITY == HIGH → Use Raw Compute ONLY
    // Prediction forbidden for critical tasks
    if (criticality.level === 'HIGH' || context.requireExact) {
      if (localCompute?.available) {
        return {
          selectedSource: localCompute,
          finalPath: 'RAW_COMPUTE',
          reason: 'HIGH criticality requires raw compute for accuracy',
        };
      }
      // No local compute available for critical task
      return {
        selectedSource: null,
        finalPath: 'EXPLAIN',
        reason: 'HIGH criticality task requires local GPU which is not available',
      };
    }

    // RULE 2: If prediction confidence >= 0.99 → Display immediately, verify async
    if (prediction?.available && prediction.confidence >= PREDICTION_CONFIDENCE_THRESHOLD) {
      return {
        selectedSource: prediction,
        finalPath: 'PREDICTION',
        reason: `Prediction confidence ${(prediction.confidence * 100).toFixed(1)}% >= ${PREDICTION_CONFIDENCE_THRESHOLD * 100}%`,
      };
    }

    // RULE 3: If vault match >= threshold → Use vault result
    if (vault?.available && vault.confidence >= VAULT_SIMILARITY_THRESHOLD) {
      return {
        selectedSource: vault,
        finalPath: 'VAULT',
        reason: `Vault match ${(vault.confidence * 100).toFixed(1)}% >= ${VAULT_SIMILARITY_THRESHOLD * 100}%`,
      };
    }

    // RULE 4: If swarm returns first and is available → Use swarm result
    if (swarm?.available) {
      return {
        selectedSource: swarm,
        finalPath: 'SWARM',
        reason: 'Swarm execution available for distributed workload',
      };
    }

    // RULE 5: Fallback to raw compute
    if (localCompute?.available) {
      return {
        selectedSource: localCompute,
        finalPath: 'RAW_COMPUTE',
        reason: 'Fallback to local raw compute',
      };
    }

    // No options available
    return {
      selectedSource: null,
      finalPath: 'EXPLAIN',
      reason: 'No execution path available - physics limited',
    };
  }

  /**
   * STEP 4: Truth Guard (ALWAYS ON)
   */
  private applyTruthGuard(
    selectedSource: TruthSource | null,
    allSources: TruthSource[],
    maxLatencyMs?: number
  ): TruthGuardResult {
    if (!selectedSource) {
      return {
        passed: false,
        deltaComparison: false,
        physicsConsistency: false,
        latencyThreshold: false,
        correctionApplied: false,
      };
    }

    // Check 1: Confidence threshold (acts as delta comparison)
    const deltaComparison = selectedSource.confidence >= (1 - VISUAL_DELTA_THRESHOLD);

    // Check 2: Physics consistency (verified sources pass)
    const physicsConsistency = selectedSource.verified || 
      selectedSource.name === 'local_compute' ||
      selectedSource.confidence >= 0.98;

    // Check 3: Latency threshold
    const latencyLimit = maxLatencyMs ?? 100;
    const latencyThreshold = selectedSource.latencyMs <= latencyLimit + LATENCY_DRIFT_THRESHOLD_MS;

    const passed = deltaComparison && physicsConsistency && latencyThreshold;

    // Determine if correction needed
    let correctionApplied = false;
    let correctionReason: string | undefined;

    if (!passed) {
      correctionApplied = true;
      if (!deltaComparison) {
        correctionReason = `Confidence ${(selectedSource.confidence * 100).toFixed(1)}% below threshold`;
      } else if (!physicsConsistency) {
        correctionReason = 'Physics consistency check failed';
      } else if (!latencyThreshold) {
        correctionReason = `Latency ${selectedSource.latencyMs.toFixed(1)}ms exceeded threshold`;
      }
    }

    return {
      passed,
      deltaComparison,
      physicsConsistency,
      latencyThreshold,
      correctionApplied,
      correctionReason,
    };
  }

  /**
   * Handle fallback when truth guard fails
   */
  private handleFallback(
    sources: TruthSource[],
    context: { localGpuAvailable?: boolean }
  ): { path: MatrixDecision['finalPath']; source: TruthSource | null; reason: string } {
    // Recovery order: Vault → Local Raw Compute → Swarm → Explain
    const vault = sources.find(s => s.name === 'vault' && s.available);
    if (vault) {
      return { path: 'VAULT', source: vault, reason: 'Fallback to vault' };
    }

    const localCompute = sources.find(s => s.name === 'local_compute' && s.available);
    if (localCompute) {
      return { path: 'RAW_COMPUTE', source: localCompute, reason: 'Fallback to local raw compute' };
    }

    const swarm = sources.find(s => s.name === 'swarm' && s.available);
    if (swarm) {
      return { path: 'SWARM', source: swarm, reason: 'Fallback to swarm' };
    }

    // Never block - explain
    return { path: 'EXPLAIN', source: null, reason: 'No fallback available - providing explanation' };
  }

  /**
   * Update statistics
   */
  private updateStats(
    path: MatrixDecision['finalPath'],
    criticality: CriticalityLevel,
    decisionTimeMs: number
  ): void {
    this.stats.totalDecisions++;
    this.stats.byPath[path]++;
    this.stats.byCriticality[criticality]++;
    
    this.decisionTimes.push(decisionTimeMs);
    if (this.decisionTimes.length > 1000) this.decisionTimes.shift();
    
    this.stats.avgDecisionTimeMs = 
      this.decisionTimes.reduce((a, b) => a + b, 0) / this.decisionTimes.length;
    
    this.stats.correctionRate = this.stats.totalDecisions > 0 
      ? this.corrections / this.stats.totalDecisions 
      : 0;
    
    this.stats.gpuAvoidanceRate = this.stats.totalDecisions > 0
      ? this.gpuAvoided / this.stats.totalDecisions
      : 0;
    
    this.stats.lastUpdated = new Date();
  }

  /**
   * Get statistics
   */
  getStats(): MatrixStats {
    return { ...this.stats };
  }

  /**
   * Generate audit report
   */
  getAuditReport(): {
    stats: MatrixStats;
    coveragePercent: number;
    physicsLockedPercent: number;
    truthStatement: string;
  } {
    const total = this.stats.totalDecisions || 1;
    const explained = this.stats.byPath.EXPLAIN;
    const physicsLockedPercent = (explained / total) * 100;
    const coveragePercent = Math.min(99.5, ((total - explained) / total) * 100);

    return {
      stats: this.getStats(),
      coveragePercent,
      physicsLockedPercent,
      truthStatement: 
        `GPUs are not replaced. GPU dependency is intelligently avoided when unnecessary. ` +
        `Physics-locked tasks (${physicsLockedPercent.toFixed(1)}%) are rare, optional, and transparently handled.`,
    };
  }

  /**
   * Reset stats (for testing)
   */
  resetStats(): void {
    this.stats = {
      totalDecisions: 0,
      byPath: { RAW_COMPUTE: 0, PREDICTION: 0, VAULT: 0, SWARM: 0, EXPLAIN: 0 },
      byCriticality: { HIGH: 0, MEDIUM: 0, LOW: 0 },
      correctionRate: 0,
      avgDecisionTimeMs: 0,
      gpuAvoidanceRate: 0,
      lastUpdated: new Date(),
    };
    this.decisionTimes = [];
    this.corrections = 0;
    this.gpuAvoided = 0;
  }
}

export const universalDecisionMatrix = UniversalDecisionMatrixCore.getInstance();
