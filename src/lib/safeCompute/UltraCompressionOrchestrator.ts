// UltraCompressionOrchestrator - Main orchestration layer
// Combines all compression layers into unified pipeline
// Routes jobs through proper classification

import { inputNormalizer } from './InputNormalizer';
import { temporalBatcher } from './TemporalBatcher';
import { resultCompressor } from './ResultCompressor';
import { probabilisticEngine, type ProcessingMethod, type ConfidenceResult } from './ProbabilisticEngine';
import { deviceCapabilityDetector, type ComputeRouting } from './DeviceCapabilityDetector';
import { veryHeavySimulator, type VeryHeavySimulation } from './VeryHeavySimulator';
import { stateCompressor } from './StateCompressor';

export type JobClassification = 'light' | 'medium' | 'heavy' | 'very_heavy';

interface ClassifiedJob {
  id: string;
  classification: JobClassification;
  signature: string;
  originalInput: unknown;
  routingInfo: ComputeRouting | null;
  statusLabel: string;
}

interface ProcessingResult {
  jobId: string;
  classification: JobClassification;
  result: unknown;
  confidence: number;
  processingMethod: ProcessingMethod;
  estimatedAccuracy: number;
  wasFromCache: boolean;
  batchSize: number;
  disclaimer?: string;
  canRefine: boolean;
  simulation?: VeryHeavySimulation;
}

interface CompressionMetrics {
  compressionRatio: number;
  cacheHitRate: number;
  averageBatchSize: number;
  freshGpuJobsToday: number;
  totalJobsProcessed: number;
  computesSaved: number;
}

class UltraCompressionOrchestrator {
  private dailyGpuBudget = 40;
  private gpuJobsToday = 0;
  private totalJobsProcessed = 0;
  private listeners: Set<(metrics: CompressionMetrics) => void> = new Set();

  constructor() {
    // Reset daily counter at midnight
    this.scheduleDailyReset();
  }

  // Classify incoming job
  classifyJob(
    jobType: string,
    input: unknown,
    memoryMb: number = 0,
    estimatedDurationSec: number = 0
  ): ClassifiedJob {
    const normalized = inputNormalizer.normalize(input);
    const routing = deviceCapabilityDetector.getComputeRouting();
    
    let classification: JobClassification;
    let statusLabel: string;

    // Check for very heavy first
    if (veryHeavySimulator.isVeryHeavy(jobType, memoryMb, estimatedDurationSec)) {
      classification = 'very_heavy';
      statusLabel = 'Simulated / Estimated';
    }
    // Light jobs: no GPU, instant
    else if (this.isLightJob(jobType, memoryMb)) {
      classification = 'light';
      statusLabel = 'Instant';
    }
    // Medium: can run on client
    else if (routing.canRunQuantized || routing.canRunProgressive) {
      classification = 'medium';
      statusLabel = 'Client-Computed';
    }
    // Heavy: needs server GPU
    else {
      classification = 'heavy';
      statusLabel = 'Queued';
    }

    return {
      id: crypto.randomUUID(),
      classification,
      signature: normalized.signature,
      originalInput: input,
      routingInfo: routing,
      statusLabel,
    };
  }

  // Process job through compression pipeline
  async processJob(classifiedJob: ClassifiedJob): Promise<ProcessingResult> {
    const { classification, signature, originalInput, id } = classifiedJob;
    this.totalJobsProcessed++;

    // Create checkpoint
    stateCompressor.checkpoint(id, 0, { classification }, originalInput);

    switch (classification) {
      case 'light':
        return this.processLight(id, signature, originalInput);
      
      case 'medium':
        return this.processMedium(id, signature, originalInput);
      
      case 'heavy':
        return this.processHeavy(id, signature, originalInput);
      
      case 'very_heavy':
        return this.processVeryHeavy(id, signature, originalInput);
      
      default:
        throw new Error(`Unknown classification: ${classification}`);
    }
  }

  // Light job: instant, cached
  private async processLight(jobId: string, signature: string, input: unknown): Promise<ProcessingResult> {
    // Check cache first
    const cached = inputNormalizer.getCachedResult(signature);
    if (cached) {
      const evaluation = probabilisticEngine.evaluateResult(signature, cached.result, {
        method: 'cached',
        cacheHits: 1,
        batchSize: 1,
        computeTimeMs: 0,
      });

      stateCompressor.checkpoint(jobId, 100, { completed: true }, input);
      
      return {
        jobId,
        classification: 'light',
        result: cached.result,
        confidence: cached.confidence,
        processingMethod: 'cached',
        estimatedAccuracy: evaluation.estimatedAccuracy,
        wasFromCache: true,
        batchSize: 1,
        canRefine: false,
      };
    }

    // Process instantly
    const result = { processed: true, input, timestamp: new Date().toISOString() };
    inputNormalizer.cacheResult(signature, result);
    
    const evaluation = probabilisticEngine.evaluateResult(signature, result, {
      method: 'cached',
      cacheHits: 0,
      batchSize: 1,
      computeTimeMs: 10,
    });

    stateCompressor.checkpoint(jobId, 100, { completed: true }, input);

    return {
      jobId,
      classification: 'light',
      result,
      confidence: evaluation.confidence,
      processingMethod: 'cached',
      estimatedAccuracy: evaluation.estimatedAccuracy,
      wasFromCache: false,
      batchSize: 1,
      canRefine: false,
    };
  }

  // Medium job: client-side compute
  private async processMedium(jobId: string, signature: string, input: unknown): Promise<ProcessingResult> {
    // Check cache first
    const cached = inputNormalizer.getCachedResult(signature);
    if (cached) {
      return {
        jobId,
        classification: 'medium',
        result: cached.result,
        confidence: cached.confidence,
        processingMethod: 'cached',
        estimatedAccuracy: cached.confidence * 0.98,
        wasFromCache: true,
        batchSize: 1,
        canRefine: false,
      };
    }

    // Simulate client-side processing
    const result = await this.simulateClientCompute(input);
    inputNormalizer.cacheResult(signature, result);

    const evaluation = probabilisticEngine.evaluateResult(signature, result, {
      method: 'client',
      cacheHits: 0,
      batchSize: 1,
      computeTimeMs: 500,
    });

    stateCompressor.checkpoint(jobId, 100, { completed: true }, input);

    return {
      jobId,
      classification: 'medium',
      result,
      confidence: evaluation.confidence,
      processingMethod: 'client',
      estimatedAccuracy: evaluation.estimatedAccuracy,
      wasFromCache: false,
      batchSize: 1,
      canRefine: evaluation.canRefine,
    };
  }

  // Heavy job: batched, GPU queued
  private async processHeavy(jobId: string, signature: string, input: unknown): Promise<ProcessingResult> {
    // Check cache first
    const cached = inputNormalizer.getCachedResult(signature);
    if (cached) {
      return {
        jobId,
        classification: 'heavy',
        result: cached.result,
        confidence: cached.confidence,
        processingMethod: 'cached',
        estimatedAccuracy: cached.confidence * 0.98,
        wasFromCache: true,
        batchSize: 1,
        canRefine: false,
      };
    }

    // Check if another job is computing this
    if (inputNormalizer.isBeingComputed(signature)) {
      // Wait for existing computation
      return new Promise((resolve) => {
        inputNormalizer.registerPending(signature, jobId);
        
        const checkInterval = setInterval(() => {
          const result = inputNormalizer.getCachedResult(signature);
          if (result) {
            clearInterval(checkInterval);
            resolve({
              jobId,
              classification: 'heavy',
              result: result.result,
              confidence: result.confidence,
              processingMethod: 'blended',
              estimatedAccuracy: result.confidence * 0.95,
              wasFromCache: true,
              batchSize: 1,
              canRefine: false,
            });
          }
        }, 1000);
      });
    }

    // Use temporal batching
    return new Promise((resolve) => {
      inputNormalizer.registerPending(signature, jobId);
      
      temporalBatcher.addJob(jobId, signature, input, (batchResult) => {
        const batchStats = temporalBatcher.getBatchingStats();
        
        inputNormalizer.cacheResult(signature, batchResult);
        this.gpuJobsToday++;
        
        const evaluation = probabilisticEngine.evaluateResult(signature, batchResult, {
          method: 'fresh_gpu',
          cacheHits: 0,
          batchSize: batchStats.averageBatchSize,
          computeTimeMs: 2000,
        });

        stateCompressor.checkpoint(jobId, 100, { completed: true }, input);
        this.notifyListeners();

        resolve({
          jobId,
          classification: 'heavy',
          result: batchResult,
          confidence: evaluation.confidence,
          processingMethod: 'fresh_gpu',
          estimatedAccuracy: evaluation.estimatedAccuracy,
          wasFromCache: false,
          batchSize: Math.round(batchStats.averageBatchSize),
          canRefine: false,
        });
      });
    });
  }

  // Very heavy job: approximation only (honest - no simulation claims)
  private async processVeryHeavy(jobId: string, signature: string, input: unknown): Promise<ProcessingResult> {
    // Determine very heavy type
    const jobType = (input as { type?: string })?.type || 'llm_training';
    const simulation = veryHeavySimulator.simulate(jobType as Parameters<typeof veryHeavySimulator.simulate>[0], input as Record<string, unknown>);

    const evaluation = probabilisticEngine.evaluateResult(signature, simulation, {
      method: 'approximated', // Honest: this is an approximation, not a real simulation
      cacheHits: 0,
      batchSize: 1,
      computeTimeMs: 100,
    });

    stateCompressor.checkpoint(jobId, 100, { approximated: true }, input);

    return {
      jobId,
      classification: 'very_heavy',
      result: simulation,
      confidence: evaluation.confidence,
      processingMethod: 'approximated', // Honest terminology
      estimatedAccuracy: evaluation.estimatedAccuracy,
      wasFromCache: false,
      batchSize: 1,
      disclaimer: simulation.disclaimer,
      canRefine: false,
      simulation,
    };
  }

  // Simulate client-side compute
  private async simulateClientCompute(input: unknown): Promise<unknown> {
    await new Promise(resolve => setTimeout(resolve, 200));
    return {
      clientProcessed: true,
      input,
      timestamp: new Date().toISOString(),
      device: deviceCapabilityDetector.getLevelLabel(),
    };
  }

  private isLightJob(jobType: string, memoryMb: number): boolean {
    const lightTypes = ['text_analysis', 'metadata', 'validation', 'search', 'format'];
    return lightTypes.some(t => jobType.toLowerCase().includes(t)) || memoryMb < 100;
  }

  // Get compression metrics
  getMetrics(): CompressionMetrics {
    const inputStats = inputNormalizer.getCompressionStats();
    const batchStats = temporalBatcher.getBatchingStats();
    
    return {
      compressionRatio: inputStats.compressionRatio,
      cacheHitRate: inputStats.cacheHitRate,
      averageBatchSize: batchStats.averageBatchSize,
      freshGpuJobsToday: this.gpuJobsToday,
      totalJobsProcessed: this.totalJobsProcessed,
      computesSaved: batchStats.totalComputesSaved + 
        Math.floor(this.totalJobsProcessed * inputStats.cacheHitRate),
    };
  }

  // Check if can accept new GPU job
  canAcceptGpuJob(): boolean {
    return this.gpuJobsToday < this.dailyGpuBudget;
  }

  // Get remaining GPU budget
  getRemainingGpuBudget(): number {
    return Math.max(0, this.dailyGpuBudget - this.gpuJobsToday);
  }

  // Schedule daily reset
  private scheduleDailyReset(): void {
    const now = new Date();
    const tomorrow = new Date(now.getFullYear(), now.getMonth(), now.getDate() + 1);
    const msUntilMidnight = tomorrow.getTime() - now.getTime();
    
    setTimeout(() => {
      this.gpuJobsToday = 0;
      this.notifyListeners();
      this.scheduleDailyReset();
    }, msUntilMidnight);
  }

  subscribe(listener: (metrics: CompressionMetrics) => void): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  private notifyListeners(): void {
    const metrics = this.getMetrics();
    this.listeners.forEach(l => l(metrics));
  }
}

export const ultraCompressionOrchestrator = new UltraCompressionOrchestrator();
export type { ProcessingResult, CompressionMetrics };
