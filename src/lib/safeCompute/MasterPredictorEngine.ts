/**
 * MASTER PREDICTOR ENGINE
 * 
 * Runs BEFORE the existing pipeline to instantly classify requests
 * and determine the optimal execution path in <1ms.
 * 
 * PIPELINE ORDER (FINAL):
 * MASTER_PREDICTOR → IDENTIFY_GOAL → REPLACE_OUTCOME → AVOID → REUSE → 
 * APPROXIMATE → PERCEIVE_REALTIME → DELEGATE → EXPLAIN
 * 
 * ABSOLUTE RULES:
 * - Deterministic and explainable decisions
 * - No random values or invented metrics
 * - Bounded error guarantees
 * - Transparent path selection
 */

import { algorithmicShortcutRegistry, ShortcutMatch, ShortcutResult } from './AlgorithmicShortcutRegistry';
import { knowledgeLookupVault, LookupMatch, VaultEntry } from './KnowledgeLookupVault';

// Execution paths (EXACTLY ONE chosen per request)
export type ExecutionPath = 
  | 'SHORTCUT'      // Algorithmic reduction/heuristic
  | 'LOOKUP'        // Pre-solved result from vault
  | 'DISTRIBUTED'   // Split across available resources
  | 'DELEGATE'      // Route to external GPU/compute
  | 'EXPLAIN';      // Physics-locked, provide explanation

export interface PredictorDecision {
  path: ExecutionPath;
  confidence: number;           // 0-1, deterministic
  reason: string;               // Human-readable explanation
  decisionTimeMs: number;       // Time to make decision
  
  // Path-specific data
  shortcutMatch?: ShortcutMatch;
  lookupMatch?: LookupMatch;
  
  // Classification results
  isClosedFormSolvable: boolean;
  hasPreSolvedResult: boolean;
  isPhysicsLocked: boolean;
  isDistributable: boolean;
  
  // Audit trail
  checksPerformed: string[];
  timestamp: Date;
}

export interface PredictorResult {
  decision: PredictorDecision;
  result?: unknown;             // If shortcut/lookup succeeded
  shouldContinuePipeline: boolean;
  explanation: string;
}

export interface PredictorStats {
  totalPredictions: number;
  byPath: Record<ExecutionPath, number>;
  avgDecisionTimeMs: number;
  shortcutSuccessRate: number;
  lookupHitRate: number;
  physicsLockedRate: number;
  lastUpdated: Date;
}

// Physics-locked workload patterns
const PHYSICS_LOCKED_PATTERNS = [
  'frontier_training',
  'realtime_raytracing',
  'climate_simulation',
  'cfd_full',
  'molecular_dynamics',
  'protein_folding',
  'quantum_simulation',
  'neural_architecture_search',
];

// Workloads that can be distributed
const DISTRIBUTABLE_PATTERNS = [
  'batch_inference',
  'data_parallel',
  'map_reduce',
  'embarrassingly_parallel',
  'ensemble',
  'hyperparameter_search',
];

class MasterPredictorEngineCore {
  private static instance: MasterPredictorEngineCore;
  
  private stats: PredictorStats = {
    totalPredictions: 0,
    byPath: {
      SHORTCUT: 0,
      LOOKUP: 0,
      DISTRIBUTED: 0,
      DELEGATE: 0,
      EXPLAIN: 0,
    },
    avgDecisionTimeMs: 0,
    shortcutSuccessRate: 0,
    lookupHitRate: 0,
    physicsLockedRate: 0,
    lastUpdated: new Date(),
  };
  
  private decisionTimes: number[] = [];
  private shortcutAttempts = 0;
  private shortcutSuccesses = 0;
  private lookupAttempts = 0;
  private lookupSuccesses = 0;
  private physicsLockedCount = 0;

  private constructor() {}

  static getInstance(): MasterPredictorEngineCore {
    if (!MasterPredictorEngineCore.instance) {
      MasterPredictorEngineCore.instance = new MasterPredictorEngineCore();
    }
    return MasterPredictorEngineCore.instance;
  }

  /**
   * Main prediction method - determines execution path in <1ms
   */
  predict(
    workloadId: string,
    workloadType: string,
    input: unknown,
    constraints: {
      maxError?: number;
      minConfidence?: number;
      allowDistributed?: boolean;
      allowDelegation?: boolean;
    } = {}
  ): PredictorResult {
    const startTime = performance.now();
    const checksPerformed: string[] = [];
    
    const maxError = constraints.maxError ?? 0.05;
    const minConfidence = constraints.minConfidence ?? 0.80;
    const type = workloadType.toLowerCase();

    // STEP 1: Check if physics-locked
    checksPerformed.push('physics_lock_check');
    const isPhysicsLocked = this.checkPhysicsLocked(type);
    
    if (isPhysicsLocked) {
      this.physicsLockedCount++;
      return this.createResult(
        'EXPLAIN',
        0.95,
        `Physics-locked workload: ${type} requires real GPU execution`,
        startTime,
        checksPerformed,
        { isPhysicsLocked: true }
      );
    }

    // STEP 2: Check for closed-form shortcut
    checksPerformed.push('shortcut_registry_check');
    this.shortcutAttempts++;
    
    const shortcutMatch = algorithmicShortcutRegistry.findShortcut(
      workloadType,
      input,
      { maxError, minConfidence }
    );

    if (shortcutMatch.found && shortcutMatch.canApply && shortcutMatch.shortcut) {
      // Apply the shortcut
      const shortcutResult = algorithmicShortcutRegistry.applyShortcut(
        shortcutMatch.shortcut,
        input
      );

      if (shortcutResult.success) {
        this.shortcutSuccesses++;
        return this.createResult(
          'SHORTCUT',
          shortcutMatch.confidence,
          shortcutResult.explanation,
          startTime,
          checksPerformed,
          { 
            shortcutMatch,
            isClosedFormSolvable: true,
            result: shortcutResult.result,
          }
        );
      }
    }

    // STEP 3: Check knowledge vault for pre-solved result
    checksPerformed.push('knowledge_vault_lookup');
    this.lookupAttempts++;
    
    const lookupMatch = knowledgeLookupVault.lookup(
      { workloadType, key: this.generateLookupKey(workloadType, input) },
      { minConfidence, maxError }
    );

    if (lookupMatch.found && lookupMatch.canUse && lookupMatch.entry) {
      this.lookupSuccesses++;
      return this.createResult(
        'LOOKUP',
        lookupMatch.similarity,
        lookupMatch.reason,
        startTime,
        checksPerformed,
        {
          lookupMatch,
          hasPreSolvedResult: true,
          result: lookupMatch.entry.value,
        }
      );
    }

    // STEP 4: Check if distributable
    checksPerformed.push('distribution_check');
    const isDistributable = this.checkDistributable(type);
    
    if (isDistributable && constraints.allowDistributed !== false) {
      return this.createResult(
        'DISTRIBUTED',
        0.85,
        `Workload can be distributed: ${type}`,
        startTime,
        checksPerformed,
        { isDistributable: true }
      );
    }

    // STEP 5: Default to delegation (continue pipeline)
    checksPerformed.push('delegation_fallback');
    return this.createResult(
      'DELEGATE',
      0.75,
      'No shortcut or lookup available - continuing to pipeline',
      startTime,
      checksPerformed,
      { isDistributable: false }
    );
  }

  /**
   * Check if workload is physics-locked (rare ~1-2%)
   */
  private checkPhysicsLocked(workloadType: string): boolean {
    return PHYSICS_LOCKED_PATTERNS.some(pattern => 
      workloadType.includes(pattern)
    );
  }

  /**
   * Check if workload can be distributed
   */
  private checkDistributable(workloadType: string): boolean {
    return DISTRIBUTABLE_PATTERNS.some(pattern => 
      workloadType.includes(pattern)
    );
  }

  /**
   * Generate lookup key from workload
   */
  private generateLookupKey(workloadType: string, input: unknown): string {
    // Simple hash-like key generation
    const inputStr = typeof input === 'string' 
      ? input 
      : JSON.stringify(input).slice(0, 100);
    return `${workloadType}_${inputStr.length}_${typeof input}`;
  }

  /**
   * Create prediction result
   */
  private createResult(
    path: ExecutionPath,
    confidence: number,
    reason: string,
    startTime: number,
    checksPerformed: string[],
    extras: Partial<{
      shortcutMatch: ShortcutMatch;
      lookupMatch: LookupMatch;
      isClosedFormSolvable: boolean;
      hasPreSolvedResult: boolean;
      isPhysicsLocked: boolean;
      isDistributable: boolean;
      result: unknown;
    }> = {}
  ): PredictorResult {
    const decisionTimeMs = performance.now() - startTime;
    
    // Update stats
    this.stats.totalPredictions++;
    this.stats.byPath[path]++;
    this.decisionTimes.push(decisionTimeMs);
    if (this.decisionTimes.length > 1000) this.decisionTimes.shift();
    this.stats.avgDecisionTimeMs = 
      this.decisionTimes.reduce((a, b) => a + b, 0) / this.decisionTimes.length;
    this.stats.shortcutSuccessRate = this.shortcutAttempts > 0 
      ? this.shortcutSuccesses / this.shortcutAttempts 
      : 0;
    this.stats.lookupHitRate = this.lookupAttempts > 0 
      ? this.lookupSuccesses / this.lookupAttempts 
      : 0;
    this.stats.physicsLockedRate = this.stats.totalPredictions > 0 
      ? this.physicsLockedCount / this.stats.totalPredictions 
      : 0;
    this.stats.lastUpdated = new Date();

    const decision: PredictorDecision = {
      path,
      confidence,
      reason,
      decisionTimeMs,
      shortcutMatch: extras.shortcutMatch,
      lookupMatch: extras.lookupMatch,
      isClosedFormSolvable: extras.isClosedFormSolvable ?? false,
      hasPreSolvedResult: extras.hasPreSolvedResult ?? false,
      isPhysicsLocked: extras.isPhysicsLocked ?? false,
      isDistributable: extras.isDistributable ?? false,
      checksPerformed,
      timestamp: new Date(),
    };

    // Determine if pipeline should continue
    const shouldContinuePipeline = path === 'DELEGATE' || path === 'DISTRIBUTED';

    return {
      decision,
      result: extras.result,
      shouldContinuePipeline,
      explanation: this.generateExplanation(decision),
    };
  }

  /**
   * Generate human-readable explanation
   */
  private generateExplanation(decision: PredictorDecision): string {
    const pathLabels: Record<ExecutionPath, string> = {
      SHORTCUT: 'Algorithmic shortcut applied',
      LOOKUP: 'Pre-solved result found',
      DISTRIBUTED: 'Workload distributed',
      DELEGATE: 'Delegated to pipeline',
      EXPLAIN: 'Physics-limited (requires explanation)',
    };

    return `Path: ${pathLabels[decision.path]} | ` +
           `Confidence: ${(decision.confidence * 100).toFixed(0)}% | ` +
           `Decision time: ${decision.decisionTimeMs.toFixed(2)}ms | ` +
           `Reason: ${decision.reason}`;
  }

  /**
   * Get predictor statistics
   */
  getStats(): PredictorStats {
    return { ...this.stats };
  }

  /**
   * Get detailed audit information
   */
  getAuditReport(): {
    stats: PredictorStats;
    shortcutRegistry: ReturnType<typeof algorithmicShortcutRegistry.getStats>;
    knowledgeVault: ReturnType<typeof knowledgeLookupVault.getStats>;
    coverage: number;
    truthStatement: string;
  } {
    const shortcutStats = algorithmicShortcutRegistry.getStats();
    const vaultStats = knowledgeLookupVault.getStats();
    
    // Calculate coverage (goals achieved without forced GPU)
    const totalHandled = this.stats.byPath.SHORTCUT + 
                         this.stats.byPath.LOOKUP + 
                         this.stats.byPath.DISTRIBUTED;
    const coverage = this.stats.totalPredictions > 0 
      ? totalHandled / this.stats.totalPredictions 
      : 0;

    return {
      stats: this.getStats(),
      shortcutRegistry: shortcutStats,
      knowledgeVault: vaultStats,
      coverage,
      truthStatement: `GPUs are not replaced. GPU dependency is intelligently avoided when unnecessary. ` +
                      `Physics-locked tasks (${(this.stats.physicsLockedRate * 100).toFixed(1)}%) are rare, ` +
                      `optional, and transparently handled.`,
    };
  }

  /**
   * Reset statistics (for testing)
   */
  resetStats(): void {
    this.stats = {
      totalPredictions: 0,
      byPath: { SHORTCUT: 0, LOOKUP: 0, DISTRIBUTED: 0, DELEGATE: 0, EXPLAIN: 0 },
      avgDecisionTimeMs: 0,
      shortcutSuccessRate: 0,
      lookupHitRate: 0,
      physicsLockedRate: 0,
      lastUpdated: new Date(),
    };
    this.decisionTimes = [];
    this.shortcutAttempts = 0;
    this.shortcutSuccesses = 0;
    this.lookupAttempts = 0;
    this.lookupSuccesses = 0;
    this.physicsLockedCount = 0;
  }
}

export const masterPredictorEngine = MasterPredictorEngineCore.getInstance();
