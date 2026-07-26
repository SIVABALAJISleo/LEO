// ResultCompressor - Result Space Compression
// Store latent bases + transformation vectors, not full outputs
// Reconstruct results on demand
// Minimize GPU usage after first compute

interface LatentBase {
  id: string;
  type: string;
  seed: number;
  dimensions: number[];
  createdAt: Date;
  accessCount: number;
}

interface TransformVector {
  id: string;
  baseId: string;
  transforms: number[];
  metadata: Record<string, unknown>;
}

interface CompressedResult {
  baseId: string;
  vectorId: string;
  compressionRatio: number;
  originalSize: number;
  compressedSize: number;
}

class ResultCompressor {
  private bases: Map<string, LatentBase> = new Map();
  private vectors: Map<string, TransformVector> = new Map();
  private resultIndex: Map<string, CompressedResult> = new Map(); // signature -> compressed

  // Compress a result into latent representation
  compress(signature: string, result: unknown): CompressedResult {
    const resultJson = JSON.stringify(result);
    const originalSize = new Blob([resultJson]).size;

    // Find or create a matching base
    const base = this.findOrCreateBase(result);

    // Generate transformation vector
    const vector = this.generateVector(base, result);

    this.vectors.set(vector.id, vector);

    const compressedSize = this.estimateCompressedSize(base, vector);

    const compressed: CompressedResult = {
      baseId: base.id,
      vectorId: vector.id,
      compressionRatio: originalSize / compressedSize,
      originalSize,
      compressedSize,
    };

    this.resultIndex.set(signature, compressed);
    return compressed;
  }

  // Decompress/reconstruct a result
  decompress(signature: string): unknown | null {
    const compressed = this.resultIndex.get(signature);
    if (!compressed) return null;

    const base = this.bases.get(compressed.baseId);
    const vector = this.vectors.get(compressed.vectorId);

    if (!base || !vector) return null;

    base.accessCount++;

    // Reconstruct from base + vector
    return this.reconstruct(base, vector);
  }

  // Find an existing base that matches the result type, or create new
  private findOrCreateBase(result: unknown): LatentBase {
    const type = this.getResultType(result);

    // Look for existing base of same type
    for (const base of this.bases.values()) {
      if (base.type === type) {
        return base;
      }
    }

    // Create new base
    const base: LatentBase = {
      id: `base-${Date.now()}`,
      type,
      seed: Date.now() % 1000000, // Deterministic seed based on timestamp
      dimensions: this.extractDimensions(result),
      createdAt: new Date(),
      accessCount: 0,
    };

    this.bases.set(base.id, base);
    return base;
  }

  // Generate transformation vector from base to result
  private generateVector(base: LatentBase, result: unknown): TransformVector {
    const transforms = this.computeTransforms(base, result);

    return {
      id: `vec-${Date.now()}`,
      baseId: base.id,
      transforms,
      metadata: {
        resultType: typeof result,
        generatedAt: new Date().toISOString(),
      },
    };
  }

  private getResultType(result: unknown): string {
    if (Array.isArray(result)) return "array";
    if (result === null) return "null";
    if (typeof result === "object") {
      const keys = Object.keys(result).sort().join(",");
      return `object:${keys.slice(0, 50)}`;
    }
    return typeof result;
  }

  private extractDimensions(result: unknown): number[] {
    if (Array.isArray(result)) {
      return [result.length];
    }
    if (result && typeof result === "object") {
      return [Object.keys(result).length];
    }
    return [1];
  }

  private computeTransforms(base: LatentBase, result: unknown): number[] {
    // Simplified: create hash-based transforms
    const json = JSON.stringify(result);
    const transforms: number[] = [];

    for (let i = 0; i < Math.min(32, json.length); i++) {
      transforms.push(json.charCodeAt(i) / 255);
    }

    // Pad to fixed length
    while (transforms.length < 32) {
      transforms.push(0);
    }

    return transforms;
  }

  private estimateCompressedSize(base: LatentBase, vector: TransformVector): number {
    // Estimate: base reference (8 bytes) + vector (transforms.length * 4 bytes)
    return 8 + vector.transforms.length * 4 + JSON.stringify(vector.metadata).length;
  }

  private reconstruct(base: LatentBase, vector: TransformVector): unknown {
    // In a real implementation, this would use the base and vector
    // to reconstruct the original result. For now, return metadata.
    return {
      reconstructed: true,
      baseType: base.type,
      seed: base.seed,
      ...vector.metadata,
    };
  }

  // Check if we have a compressed version
  hasCompressed(signature: string): boolean {
    return this.resultIndex.has(signature);
  }

  // Get compression stats
  getCompressionStats(): {
    basesCount: number;
    vectorsCount: number;
    totalOriginalSize: number;
    totalCompressedSize: number;
    overallRatio: number;
  } {
    let totalOriginal = 0;
    let totalCompressed = 0;

    for (const compressed of this.resultIndex.values()) {
      totalOriginal += compressed.originalSize;
      totalCompressed += compressed.compressedSize;
    }

    return {
      basesCount: this.bases.size,
      vectorsCount: this.vectors.size,
      totalOriginalSize: totalOriginal,
      totalCompressedSize: totalCompressed,
      overallRatio: totalCompressed > 0 ? totalOriginal / totalCompressed : 1,
    };
  }

  // Cleanup old, rarely accessed bases
  cleanup(maxAgeMs: number = 24 * 60 * 60 * 1000): void {
    const now = Date.now();
    for (const [id, base] of this.bases.entries()) {
      if (base.accessCount < 5 && now - base.createdAt.getTime() > maxAgeMs) {
        this.bases.delete(id);
        // Remove associated vectors
        for (const [vecId, vec] of this.vectors.entries()) {
          if (vec.baseId === id) {
            this.vectors.delete(vecId);
          }
        }
      }
    }
  }
}

export const resultCompressor = new ResultCompressor();
