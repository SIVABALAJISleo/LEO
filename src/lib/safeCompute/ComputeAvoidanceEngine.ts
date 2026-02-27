/**
 * COMPUTE AVOIDANCE ENGINE
 * 
 * Before allowing ANY GPU execution, this engine attempts to avoid it.
 * Success here means GPU work is SKIPPED entirely.
 * 
 * Strategies:
 * 1. Result reuse (hash identical workloads)
 * 2. Progressive rendering (low-res first, refine if needed)
 * 3. Perception equivalence (visually identical shortcuts)
 * 4. Early exit (stop when confidence met)
 */

import { workloadClassifier, WorkloadClassification, AvoidanceStrategy } from './WorkloadClassifier';
import { similarityCollapseEngine } from './SimilarityCollapseEngine';
import { perceptionEquivalence } from './PerceptionEquivalence';

export interface AvoidanceAttempt {
  workloadId: string;
  strategy: AvoidanceStrategy;
  success: boolean;
  resultSource?: 'cache' | 'collapse' | 'approximation' | 'early_exit' | 'perception';
  result?: unknown;
  gpuSaved: boolean;
  timeToResultMs: number;
  qualityScore: number;
}

export interface AvoidanceStats {
  totalAttempts: number;
  successfulAvoidances: number;
  byStrategy: Record<AvoidanceStrategy, { attempts: number; successes: number }>;
  estimatedGpuHoursSaved: number;
  avoidanceRate: number;
}

interface CacheEntry {
  hash: string;
  result: unknown;
  quality: number;
  timestamp: number;
  hitCount: number;
}

class ComputeAvoidanceEngine {
  private static instance: ComputeAvoidanceEngine;
  private cache: Map<string, CacheEntry> = new Map();
  private progressiveResults: Map<string, { lowRes: unknown; fullRes?: unknown }> = new Map();
  private earlyExitThresholds: Map<string, number> = new Map();
  private stats: AvoidanceStats = {
    totalAttempts: 0,
    successfulAvoidances: 0,
    byStrategy: {
      cache_hit: { attempts: 0, successes: 0 },
      similarity_collapse: { attempts: 0, successes: 0 },
      progressive_render: { attempts: 0, successes: 0 },
      perception_equivalent: { attempts: 0, successes: 0 },
      early_exit: { attempts: 0, successes: 0 },
      downscale: { attempts: 0, successes: 0 },
      temporal_batch: { attempts: 0, successes: 0 },
      defer: { attempts: 0, successes: 0 },
      none: { attempts: 0, successes: 0 },
    },
    estimatedGpuHoursSaved: 0,
    avoidanceRate: 0,
  };

  private constructor() {}

  static getInstance(): ComputeAvoidanceEngine {
    if (!ComputeAvoidanceEngine.instance) {
      ComputeAvoidanceEngine.instance = new ComputeAvoidanceEngine();
    }
    return ComputeAvoidanceEngine.instance;
  }

  /**
   * Attempt to avoid GPU computation for a workload
   * Returns result if avoidance succeeded, null if GPU is required
   */
  async attemptAvoidance(
    workloadId: string,
    workloadType: string,
    input: unknown,
    constraints: {
      maxLatencyMs?: number;
      requireExact?: boolean;
      qualityFloor?: number;
    } = {}
  ): Promise<AvoidanceAttempt> {
    const startTime = Date.now();
    
    // Get or create classification
    let classification = workloadClassifier.getClassification(workloadId);
    if (!classification) {
      classification = workloadClassifier.classify(workloadId, workloadType, input, constraints);
    }

    // If avoidance not possible, return immediately
    if (!classification.canAvoid) {
      return this.createAttempt(workloadId, 'none', false, startTime);
    }

    // Try each avoidance strategy in order
    for (const strategy of classification.avoidanceStrategies) {
      const result = await this.tryStrategy(strategy, workloadId, workloadType, input, classification);
      if (result.success) {
        return result;
      }
    }

    // All strategies failed, GPU is required
    return this.createAttempt(workloadId, 'none', false, startTime);
  }

  private async tryStrategy(
    strategy: AvoidanceStrategy,
    workloadId: string,
    workloadType: string,
    input: unknown,
    classification: WorkloadClassification
  ): Promise<AvoidanceAttempt> {
    const startTime = Date.now();
    this.stats.totalAttempts++;
    this.stats.byStrategy[strategy].attempts++;

    switch (strategy) {
      case 'cache_hit':
        return this.tryCacheHit(workloadId, input, startTime);

      case 'similarity_collapse':
        return this.trySimilarityCollapse(workloadId, input, startTime);

      case 'progressive_render':
        return this.tryProgressiveRender(workloadId, workloadType, input, classification, startTime);

      case 'perception_equivalent':
        return this.tryPerceptionEquivalent(workloadId, workloadType, input, classification, startTime);

      case 'early_exit':
        return this.tryEarlyExit(workloadId, workloadType, classification, startTime);

      case 'downscale':
        // Downscale doesn't avoid GPU, just reduces load
        return this.createAttempt(workloadId, strategy, false, startTime);

      case 'temporal_batch':
        // Batching doesn't avoid GPU, just consolidates
        return this.createAttempt(workloadId, strategy, false, startTime);

      case 'defer':
        // Deferral doesn't avoid GPU, just delays
        return this.createAttempt(workloadId, strategy, false, startTime);

      default:
        return this.createAttempt(workloadId, 'none', false, startTime);
    }
  }

  private tryCacheHit(workloadId: string, input: unknown, startTime: number): AvoidanceAttempt {
    const hash = this.hashInput(input);
    const cached = this.cache.get(hash);

    if (cached && cached.quality >= 0.8) {
      cached.hitCount++;
      this.recordSuccess('cache_hit');
      return {
        workloadId,
        strategy: 'cache_hit',
        success: true,
        resultSource: 'cache',
        result: cached.result,
        gpuSaved: true,
        timeToResultMs: Date.now() - startTime,
        qualityScore: cached.quality,
      };
    }

    return this.createAttempt(workloadId, 'cache_hit', false, startTime);
  }

  private trySimilarityCollapse(workloadId: string, input: unknown, startTime: number): AvoidanceAttempt {
    const collapseResult = similarityCollapseEngine.checkCollapse(workloadId, input);

    if (collapseResult.collapsed && collapseResult.similarityScore >= 0.85) {
      this.recordSuccess('similarity_collapse');
      return {
        workloadId,
        strategy: 'similarity_collapse',
        success: true,
        resultSource: 'collapse',
        result: { collapsedInto: collapseResult.parentWorkloadId, method: collapseResult.method },
        gpuSaved: true,
        timeToResultMs: Date.now() - startTime,
        qualityScore: collapseResult.similarityScore,
      };
    }

    return this.createAttempt(workloadId, 'similarity_collapse', false, startTime);
  }

  private async tryProgressiveRender(
    workloadId: string,
    workloadType: string,
    input: unknown,
    classification: WorkloadClassification,
    startTime: number
  ): Promise<AvoidanceAttempt> {
    // Only for perceptual-tolerant workloads
    if (!classification.categories.includes('perceptual_tolerant')) {
      return this.createAttempt(workloadId, 'progressive_render', false, startTime);
    }

    // Generate quick low-res version (CPU-based approximation)
    const lowResResult = this.generateLowResApproximation(workloadType, input);
    
    this.progressiveResults.set(workloadId, { lowRes: lowResResult });
    this.recordSuccess('progressive_render');

    return {
      workloadId,
      strategy: 'progressive_render',
      success: true,
      resultSource: 'approximation',
      result: { 
        preview: lowResResult, 
        isProgressive: true,
        fullResAvailable: false,
        message: 'Quick preview ready. Full resolution requires GPU.',
      },
      gpuSaved: true,
      timeToResultMs: Date.now() - startTime,
      qualityScore: 0.65,
    };
  }

  private tryPerceptionEquivalent(
    workloadId: string,
    workloadType: string,
    input: unknown,
    classification: WorkloadClassification,
    startTime: number
  ): AvoidanceAttempt {
    const check = perceptionEquivalence.checkApplicability(workloadId, {
      outputConsumer: 'human',
      perceptionThresholdMet: classification.qualityFloor <= 0.85,
      allowsSilentCorrection: true,
      category: workloadType,
      requiresDeterminism: classification.categories.includes('precision_critical'),
    });

    if (check.isApplicable) {
      this.recordSuccess('perception_equivalent');
      return {
        workloadId,
        strategy: 'perception_equivalent',
        success: true,
        resultSource: 'perception',
        result: {
          method: 'perception_equivalent',
          classification: check.classification,
          message: 'Perceptually equivalent result delivered',
        },
        gpuSaved: true,
        timeToResultMs: Date.now() - startTime,
        qualityScore: 0.88,
      };
    }

    return this.createAttempt(workloadId, 'perception_equivalent', false, startTime);
  }

  private tryEarlyExit(
    workloadId: string,
    workloadType: string,
    classification: WorkloadClassification,
    startTime: number
  ): AvoidanceAttempt {
    // Early exit only works during actual computation
    // This sets up the threshold for actual execution
    this.earlyExitThresholds.set(workloadId, classification.qualityFloor);
    
    // Can't avoid GPU entirely, but will exit early
    return this.createAttempt(workloadId, 'early_exit', false, startTime);
  }

  /**
   * Store result in cache for future reuse
   */
  cacheResult(input: unknown, result: unknown, quality: number): void {
    const hash = this.hashInput(input);
    this.cache.set(hash, {
      hash,
      result,
      quality,
      timestamp: Date.now(),
      hitCount: 0,
    });
  }

  /**
   * Get current avoidance statistics
   */
  getStats(): AvoidanceStats {
    this.stats.avoidanceRate = this.stats.totalAttempts > 0 
      ? this.stats.successfulAvoidances / this.stats.totalAttempts 
      : 0;
    return { ...this.stats };
  }

  /**
   * Get early exit threshold for a workload
   */
  getEarlyExitThreshold(workloadId: string): number {
    return this.earlyExitThresholds.get(workloadId) || 0.9;
  }

  private generateLowResApproximation(workloadType: string, input: unknown): unknown {
    const type = workloadType.toLowerCase();
    
    if (type.includes('image')) {
      return { type: 'image_preview', resolution: '256x256', format: 'thumbnail', approximated: true };
    }
    if (type.includes('video')) {
      return { type: 'video_preview', frames: 1, resolution: '480p', approximated: true };
    }
    if (type.includes('render')) {
      return { type: 'render_preview', quality: 'draft', samples: 16, approximated: true };
    }
    if (type.includes('inference')) {
      return { type: 'inference_preview', tokens: 50, model: 'lightweight', approximated: true };
    }

    return { type: 'generic_preview', approximated: true, input: typeof input };
  }

  private hashInput(input: unknown): string {
    const str = JSON.stringify(input);
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash;
    }
    return `cache_${Math.abs(hash).toString(36)}`;
  }

  private createAttempt(
    workloadId: string,
    strategy: AvoidanceStrategy,
    success: boolean,
    startTime: number
  ): AvoidanceAttempt {
    return {
      workloadId,
      strategy,
      success,
      gpuSaved: success,
      timeToResultMs: Date.now() - startTime,
      qualityScore: 0,
    };
  }

  private recordSuccess(strategy: AvoidanceStrategy): void {
    this.stats.successfulAvoidances++;
    this.stats.byStrategy[strategy].successes++;
    // Estimate ~0.001 GPU hours saved per avoidance
    this.stats.estimatedGpuHoursSaved += 0.001;
  }

  /**
   * Cleanup old cache entries
   */
  cleanup(maxAgeMs: number = 3600000): void {
    const cutoff = Date.now() - maxAgeMs;
    for (const [hash, entry] of this.cache) {
      if (entry.timestamp < cutoff && entry.hitCount < 3) {
        this.cache.delete(hash);
      }
    }
  }
}

export const computeAvoidanceEngine = ComputeAvoidanceEngine.getInstance();
