// ProbabilisticEngine - Probabilistic Satisfaction
// Attach confidence score to every result
// If confidence ≥ 0.85 → deliver immediately
// If < 0.85 → offer optional refinement (queued)

type ProcessingMethod = 
  | 'cached' 
  | 'blended' 
  | 'client' 
  | 'fresh_gpu' 
  | 'approximated'  // Renamed from 'simulated' - honest terminology
  | 'interpolated';

interface ConfidenceResult {
  result: unknown;
  confidence: number;
  processingMethod: ProcessingMethod;
  estimatedAccuracy: number;
  canRefine: boolean;
  refinementQueuePosition?: number;
  metadata: {
    source: string;
    cacheHits: number;
    batchSize: number;
    computeTime: number;
  };
}

interface RefinementRequest {
  id: string;
  originalSignature: string;
  requestedAt: Date;
  priority: number;
  status: 'queued' | 'processing' | 'completed';
}

class ProbabilisticEngine {
  private readonly CONFIDENCE_THRESHOLD = 0.85;
  private refinementQueue: RefinementRequest[] = [];
  private confidenceHistory: Map<string, number[]> = new Map();

  // Evaluate and return result with confidence
  evaluateResult(
    signature: string,
    result: unknown,
    source: {
      method: ProcessingMethod;
      cacheHits?: number;
      batchSize?: number;
      computeTimeMs?: number;
    }
  ): ConfidenceResult {
    const confidence = this.calculateConfidence(signature, result, source);
    const estimatedAccuracy = this.estimateAccuracy(source.method, confidence);
    
    // Track confidence history
    if (!this.confidenceHistory.has(signature)) {
      this.confidenceHistory.set(signature, []);
    }
    this.confidenceHistory.get(signature)!.push(confidence);
    
    const canRefine = confidence < this.CONFIDENCE_THRESHOLD;
    
    return {
      result,
      confidence,
      processingMethod: source.method,
      estimatedAccuracy,
      canRefine,
      refinementQueuePosition: canRefine ? this.refinementQueue.length + 1 : undefined,
      metadata: {
        source: source.method,
        cacheHits: source.cacheHits || 0,
        batchSize: source.batchSize || 1,
        computeTime: source.computeTimeMs || 0,
      },
    };
  }

  // Calculate confidence based on processing method and source
  private calculateConfidence(
    signature: string, 
    result: unknown, 
    source: { method: ProcessingMethod; cacheHits?: number; batchSize?: number }
  ): number {
    let baseConfidence: number;
    
    switch (source.method) {
      case 'fresh_gpu':
        baseConfidence = 0.98;
        break;
      case 'cached':
        // More cache hits = higher confidence
        const hits = source.cacheHits || 1;
        baseConfidence = Math.min(0.95, 0.85 + (hits * 0.02));
        break;
      case 'blended':
        baseConfidence = 0.88;
        break;
      case 'client':
        baseConfidence = 0.90;
        break;
      case 'interpolated':
        baseConfidence = 0.82;
        break;
      case 'approximated':
        baseConfidence = 0.75; // Honest: approximations have bounded accuracy
        break;
      default:
        baseConfidence = 0.75;
    }
    
    // Adjust based on result validity
    if (result === null || result === undefined) {
      baseConfidence *= 0.5;
    }
    
    // Historical adjustment
    const history = this.confidenceHistory.get(signature) || [];
    if (history.length > 0) {
      const avgHistorical = history.reduce((a, b) => a + b, 0) / history.length;
      baseConfidence = baseConfidence * 0.7 + avgHistorical * 0.3;
    }
    
    return Math.min(0.99, Math.max(0.1, baseConfidence));
  }

  // Estimate accuracy based on method
  private estimateAccuracy(method: ProcessingMethod, confidence: number): number {
    const methodMultipliers: Record<ProcessingMethod, number> = {
      fresh_gpu: 1.0,
      cached: 0.98,
      client: 0.95,
      blended: 0.92,
      interpolated: 0.85,
      approximated: 0.80, // Honest: approximations have bounded accuracy
    };
    
    return confidence * (methodMultipliers[method] || 0.8);
  }

  // Request refinement for a low-confidence result
  requestRefinement(signature: string, priority: number = 5): RefinementRequest {
    const request: RefinementRequest = {
      id: `refine-${Date.now()}`,
      originalSignature: signature,
      requestedAt: new Date(),
      priority,
      status: 'queued',
    };
    
    this.refinementQueue.push(request);
    this.refinementQueue.sort((a, b) => b.priority - a.priority);
    
    return request;
  }

  // Get next refinement to process
  getNextRefinement(): RefinementRequest | null {
    return this.refinementQueue.find(r => r.status === 'queued') || null;
  }

  // Complete a refinement
  completeRefinement(id: string): void {
    const request = this.refinementQueue.find(r => r.id === id);
    if (request) {
      request.status = 'completed';
    }
  }

  // Get refinement queue stats
  getRefinementQueueStats(): {
    queueLength: number;
    processing: number;
    completed: number;
  } {
    return {
      queueLength: this.refinementQueue.filter(r => r.status === 'queued').length,
      processing: this.refinementQueue.filter(r => r.status === 'processing').length,
      completed: this.refinementQueue.filter(r => r.status === 'completed').length,
    };
  }

  // Should deliver immediately based on confidence?
  shouldDeliverImmediately(confidence: number): boolean {
    return confidence >= this.CONFIDENCE_THRESHOLD;
  }

  // Get friendly status label
  getStatusLabel(method: ProcessingMethod): string {
    const labels: Record<ProcessingMethod, string> = {
      cached: 'Instant (Cached)',
      blended: 'Blended Results',
      client: 'Client-Computed',
      fresh_gpu: 'Fresh GPU Compute',
      approximated: 'Approximated',
      interpolated: 'Interpolated',
    };
    return labels[method] || 'Unknown';
  }

  // Get processing method icon name
  getMethodIcon(method: ProcessingMethod): string {
    const icons: Record<ProcessingMethod, string> = {
      cached: 'zap',
      blended: 'layers',
      client: 'monitor',
      fresh_gpu: 'cpu',
      approximated: 'target',
      interpolated: 'git-merge',
    };
    return icons[method] || 'help-circle';
  }

  // Cleanup old history
  cleanup(): void {
    // Keep only last 100 entries per signature
    for (const [sig, history] of this.confidenceHistory.entries()) {
      if (history.length > 100) {
        this.confidenceHistory.set(sig, history.slice(-100));
      }
    }
    
    // Remove completed refinements older than 1 hour
    const oneHourAgo = Date.now() - 60 * 60 * 1000;
    this.refinementQueue = this.refinementQueue.filter(r => 
      r.status !== 'completed' || r.requestedAt.getTime() > oneHourAgo
    );
  }
}

export const probabilisticEngine = new ProbabilisticEngine();
export type { ProcessingMethod, ConfidenceResult };
