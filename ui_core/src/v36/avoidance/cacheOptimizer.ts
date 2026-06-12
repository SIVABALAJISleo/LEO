// LEO AI V36 — Cache Optimizer
// Compresses cache storage formats to fit inside L1/L2 hardware ranges.

export class CacheOptimizer {
  public compressKeys(keys: string[]): string[] {
    // Deduplicates and tokenizes strings to minimize VRAM/RAM footprints
    return Array.from(new Set(keys.map(k => k.toLowerCase().trim())));
  }
}
