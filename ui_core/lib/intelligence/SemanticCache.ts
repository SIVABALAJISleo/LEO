import { VectorDatabase } from "./VectorDatabase";

export class SemanticCache {
  private static instance: SemanticCache;
  private db: VectorDatabase;
  private readonly SIMILARITY_THRESHOLD = 0.9; // High threshold for cache hits

  private constructor() {
    this.db = new VectorDatabase(384); // Assuming 384-dim embeddings (e.g., all-MiniLM-L6-v2)
  }

  static getInstance(): SemanticCache {
    if (!SemanticCache.instance) {
      SemanticCache.instance = new SemanticCache();
    }
    return SemanticCache.instance;
  }

  async get(queryVector: number[]): Promise<string | null> {
    const results = this.db.search(queryVector, 1, this.SIMILARITY_THRESHOLD);
    if (results.length > 0) {
      // Return cached response stored in metadata
      console.log(`[SemanticCache] Hit! Score: ${results[0].score.toFixed(4)}`);
      return results[0].metadata?.response || null;
    }
    return null;
  }

  set(query: string, queryVector: number[], response: string): void {
    // Check if similar query already exists to avoid duplicates
    const results = this.db.search(queryVector, 1, 0.98);
    if (results.length === 0) {
      this.db.add(query, queryVector, { response, timestamp: Date.now() });
    }
  }
}
