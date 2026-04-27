// InputNormalizer - Demand Collapse Layer
// Converts all inputs into canonical semantic form
// Merge equivalent prompts into identical compute signatures
// One compute result serves thousands of requests

interface CanonicalInput {
  signature: string;
  canonicalForm: unknown;
  originalHash: string;
  normalizedAt: Date;
}

interface SignatureMatch {
  signature: string;
  matchCount: number;
  cachedResultId?: string;
  confidence: number;
}

class InputNormalizer {
  private signatureCache: Map<string, CanonicalInput> = new Map();
  private resultCache: Map<string, { result: unknown; createdAt: Date; hitCount: number }> = new Map();
  private pendingSignatures: Map<string, Set<string>> = new Map(); // signature -> set of waiting job ids

  // Normalize input to canonical form
  normalize(input: unknown): CanonicalInput {
    const originalHash = this.hashInput(input);
    
    // Check if we already have this exact input
    if (this.signatureCache.has(originalHash)) {
      return this.signatureCache.get(originalHash)!;
    }

    const canonicalForm = this.toCanonicalForm(input);
    const signature = this.generateSemanticSignature(canonicalForm);

    const canonical: CanonicalInput = {
      signature,
      canonicalForm,
      originalHash,
      normalizedAt: new Date(),
    };

    this.signatureCache.set(originalHash, canonical);
    return canonical;
  }

  // Convert input to canonical form (strips noise, normalizes structure)
  private toCanonicalForm(input: unknown): unknown {
    if (typeof input === 'string') {
      return this.normalizeText(input);
    }
    
    if (Array.isArray(input)) {
      return input.map(item => this.toCanonicalForm(item));
    }
    
    if (input && typeof input === 'object') {
      const sorted: Record<string, unknown> = {};
      const keys = Object.keys(input).sort();
      for (const key of keys) {
        const normalizedKey = key.toLowerCase().replace(/[_-]/g, '');
        sorted[normalizedKey] = this.toCanonicalForm((input as Record<string, unknown>)[key]);
      }
      return sorted;
    }
    
    return input;
  }

  // Normalize text: lowercase, trim, remove extra whitespace, normalize punctuation
  private normalizeText(text: string): string {
    return text
      .toLowerCase()
      .trim()
      .replace(/\s+/g, ' ')
      .replace(/['']/g, "'")
      .replace(/[""]/g, '"')
      .replace(/[…]/g, '...')
      .replace(/\s*([,.!?;:])\s*/g, '$1 ')
      .trim();
  }

  // Generate semantic signature for deduplication
  private generateSemanticSignature(canonicalForm: unknown): string {
    const json = JSON.stringify(canonicalForm);
    // Use a simple hash for signature
    return this.simpleHash(json);
  }

  // Simple hash function
  private simpleHash(str: string): string {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32bit integer
    }
    return Math.abs(hash).toString(36) + '-' + str.length.toString(36);
  }

  private hashInput(input: unknown): string {
    return this.simpleHash(JSON.stringify(input));
  }

  // Check if we have a cached result for this signature
  getCachedResult(signature: string): { result: unknown; confidence: number } | null {
    const cached = this.resultCache.get(signature);
    if (cached) {
      cached.hitCount++;
      // Confidence increases with hit count
      const confidence = Math.min(0.99, 0.85 + (cached.hitCount * 0.01));
      return { result: cached.result, confidence };
    }
    return null;
  }

  // Store result for a signature
  cacheResult(signature: string, result: unknown): void {
    this.resultCache.set(signature, {
      result,
      createdAt: new Date(),
      hitCount: 1,
    });
    
    // Notify any waiting jobs
    const waiting = this.pendingSignatures.get(signature);
    if (waiting) {
      this.pendingSignatures.delete(signature);
    }
  }

  // Register a job as waiting for a signature
  registerPending(signature: string, jobId: string): void {
    if (!this.pendingSignatures.has(signature)) {
      this.pendingSignatures.set(signature, new Set());
    }
    this.pendingSignatures.get(signature)!.add(jobId);
  }

  // Check if another job is already computing this signature
  isBeingComputed(signature: string): boolean {
    const pending = this.pendingSignatures.get(signature);
    return pending ? pending.size > 0 : false;
  }

  // Get all pending jobs for a signature
  getPendingJobs(signature: string): string[] {
    const pending = this.pendingSignatures.get(signature);
    return pending ? Array.from(pending) : [];
  }

  // Get signature match info
  getSignatureMatch(input: unknown): SignatureMatch {
    const canonical = this.normalize(input);
    const pending = this.pendingSignatures.get(canonical.signature);
    const cached = this.resultCache.get(canonical.signature);
    
    return {
      signature: canonical.signature,
      matchCount: (pending?.size || 0) + (cached?.hitCount || 0),
      cachedResultId: cached ? canonical.signature : undefined,
      confidence: cached ? Math.min(0.99, 0.85 + (cached.hitCount * 0.01)) : 0,
    };
  }

  // Get compression stats
  getCompressionStats(): { 
    uniqueSignatures: number; 
    totalRequests: number; 
    compressionRatio: number;
    cacheHitRate: number;
  } {
    const uniqueSignatures = this.resultCache.size;
    const totalRequests = Array.from(this.resultCache.values())
      .reduce((sum, r) => sum + r.hitCount, 0);
    
    return {
      uniqueSignatures,
      totalRequests,
      compressionRatio: uniqueSignatures > 0 ? totalRequests / uniqueSignatures : 1,
      cacheHitRate: totalRequests > 0 ? (totalRequests - uniqueSignatures) / totalRequests : 0,
    };
  }

  // Clear old entries
  cleanup(maxAgeMs: number = 24 * 60 * 60 * 1000): void {
    const now = Date.now();
    for (const [key, value] of this.resultCache.entries()) {
      if (now - value.createdAt.getTime() > maxAgeMs) {
        this.resultCache.delete(key);
      }
    }
  }
}

export const inputNormalizer = new InputNormalizer();
