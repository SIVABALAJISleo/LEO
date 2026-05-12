// HYPER Similarity Collapse Engine - Collapse near-identical workloads

interface WorkloadSignature {
  id: string;
  semanticHash: string;
  structuralHash: string;
  timestamp: number;
  collapsed: boolean;
  parentId?: string;
}

interface CollapseResult {
  collapsed: boolean;
  parentWorkloadId?: string;
  similarityScore: number;
  method: 'exact' | 'semantic' | 'structural' | 'none';
}

interface PendingWorkload {
  id: string;
  signature: WorkloadSignature;
  resolvers: Array<(result: unknown) => void>;
}

class SimilarityCollapseEngine {
  private static instance: SimilarityCollapseEngine;
  private signatures: Map<string, WorkloadSignature> = new Map();
  private pendingWorkloads: Map<string, PendingWorkload> = new Map();
  private collapseCount = 0;
  private totalWorkloads = 0;

  private constructor() {}

  static getInstance(): SimilarityCollapseEngine {
    if (!SimilarityCollapseEngine.instance) {
      SimilarityCollapseEngine.instance = new SimilarityCollapseEngine();
    }
    return SimilarityCollapseEngine.instance;
  }

  // Generate semantic hash from input
  private generateSemanticHash(input: unknown): string {
    const normalized = this.normalizeInput(input);
    return this.simpleHash(normalized);
  }

  // Generate structural hash (ignores minor variations)
  private generateStructuralHash(input: unknown): string {
    const structure = this.extractStructure(input);
    return this.simpleHash(structure);
  }

  private normalizeInput(input: unknown): string {
    if (typeof input === 'string') {
      return input.toLowerCase().trim().replace(/\s+/g, ' ');
    }
    return JSON.stringify(input);
  }

  private extractStructure(input: unknown): string {
    if (typeof input === 'object' && input !== null) {
      const keys = Object.keys(input).sort();
      return keys.join('|');
    }
    return typeof input;
  }

  private simpleHash(str: string): string {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash;
    }
    return Math.abs(hash).toString(36);
  }

  // Check if workload can be collapsed with existing one
  checkCollapse(workloadId: string, input: unknown): CollapseResult {
    this.totalWorkloads++;
    
    const semanticHash = this.generateSemanticHash(input);
    const structuralHash = this.generateStructuralHash(input);

    // Check for exact match
    for (const [id, sig] of this.signatures) {
      if (sig.semanticHash === semanticHash && sig.structuralHash === structuralHash) {
        this.collapseCount++;
        return {
          collapsed: true,
          parentWorkloadId: id,
          similarityScore: 1.0,
          method: 'exact',
        };
      }
    }

    // Check for semantic similarity
    for (const [id, sig] of this.signatures) {
      if (sig.semanticHash === semanticHash) {
        this.collapseCount++;
        return {
          collapsed: true,
          parentWorkloadId: id,
          similarityScore: 0.95,
          method: 'semantic',
        };
      }
    }

    // Check for structural similarity (within time window)
    const recentThreshold = Date.now() - 60000; // 1 minute
    for (const [id, sig] of this.signatures) {
      if (sig.structuralHash === structuralHash && sig.timestamp > recentThreshold) {
        this.collapseCount++;
        return {
          collapsed: true,
          parentWorkloadId: id,
          similarityScore: 0.85,
          method: 'structural',
        };
      }
    }

    // Register new signature
    this.signatures.set(workloadId, {
      id: workloadId,
      semanticHash,
      structuralHash,
      timestamp: Date.now(),
      collapsed: false,
    });

    return {
      collapsed: false,
      similarityScore: 0,
      method: 'none',
    };
  }

  // Register a pending workload that others can collapse into
  registerPending(workloadId: string, input: unknown): void {
    const semanticHash = this.generateSemanticHash(input);
    const structuralHash = this.generateStructuralHash(input);

    this.pendingWorkloads.set(workloadId, {
      id: workloadId,
      signature: {
        id: workloadId,
        semanticHash,
        structuralHash,
        timestamp: Date.now(),
        collapsed: false,
      },
      resolvers: [],
    });
  }

  // Fan-out result to all collapsed workloads
  fanOutResult(workloadId: string, result: unknown): number {
    const pending = this.pendingWorkloads.get(workloadId);
    if (!pending) return 0;

    const count = pending.resolvers.length;
    pending.resolvers.forEach(resolve => resolve(result));
    this.pendingWorkloads.delete(workloadId);

    return count;
  }

  // Get collapse statistics
  getStats(): { total: number; collapsed: number; ratio: number } {
    return {
      total: this.totalWorkloads,
      collapsed: this.collapseCount,
      ratio: this.totalWorkloads > 0 ? this.collapseCount / this.totalWorkloads : 0,
    };
  }

  // Cleanup old signatures
  cleanup(maxAgeMs: number = 300000): void {
    const threshold = Date.now() - maxAgeMs;
    for (const [id, sig] of this.signatures) {
      if (sig.timestamp < threshold) {
        this.signatures.delete(id);
      }
    }
  }
}

export const similarityCollapseEngine = SimilarityCollapseEngine.getInstance();
export type { CollapseResult, WorkloadSignature };
