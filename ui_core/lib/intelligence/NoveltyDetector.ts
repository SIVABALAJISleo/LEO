/**
 * Novelty Detector
 * Classifies inputs as NEW/SIMILAR/SAME to avoid redundant computation.
 */

import { VectorDatabase } from "../intelligence/VectorDatabase";

export enum NoveltyState {
  SAME = "SAME", // >0.95 similarity - return cached
  SIMILAR = "SIMILAR", // 0.7-0.95 - lightweight reasoning
  NEW = "NEW", // <0.7 - full inference
}

export interface NoveltyResult {
  state: NoveltyState;
  similarity: number;
  matchedId?: string;
  matchedText?: string;
}

export class NoveltyDetector {
  private static instance: NoveltyDetector;
  private vectorDb: VectorDatabase;

  private readonly SAME_THRESHOLD = 0.95;
  private readonly SIMILAR_THRESHOLD = 0.7;

  private constructor() {
    this.vectorDb = new VectorDatabase(384); // Standard embedding size
  }

  static getInstance(): NoveltyDetector {
    if (!NoveltyDetector.instance) {
      NoveltyDetector.instance = new NoveltyDetector();
    }
    return NoveltyDetector.instance;
  }

  /**
   * Detect novelty of input by comparing with memory
   */
  async detect(input: string, embedding: number[]): Promise<NoveltyResult> {
    // Search for similar entries
    const matches = this.vectorDb.search(embedding, 1, 0);

    if (matches.length === 0) {
      console.log("[NoveltyDetector] NEW - no similar entries found");
      return {
        state: NoveltyState.NEW,
        similarity: 0,
      };
    }

    const bestMatch = matches[0];
    const similarity = bestMatch.score;

    if (similarity >= this.SAME_THRESHOLD) {
      console.log(`[NoveltyDetector] SAME - ${similarity.toFixed(3)} similarity`);
      return {
        state: NoveltyState.SAME,
        similarity,
        matchedId: bestMatch.id,
        matchedText: bestMatch.text,
      };
    }

    if (similarity >= this.SIMILAR_THRESHOLD) {
      console.log(`[NoveltyDetector] SIMILAR - ${similarity.toFixed(3)} similarity`);
      return {
        state: NoveltyState.SIMILAR,
        similarity,
        matchedId: bestMatch.id,
        matchedText: bestMatch.text,
      };
    }

    console.log(`[NoveltyDetector] NEW - ${similarity.toFixed(3)} below threshold`);
    return {
      state: NoveltyState.NEW,
      similarity,
    };
  }

  /**
   * Store processed input in memory
   */
  store(input: string, embedding: number[], response: string): string {
    return this.vectorDb.add(input, embedding, {
      response,
      timestamp: Date.now(),
      usageCount: 0,
    });
  }

  /**
   * Retrieve cached response
   */
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  retrieve(id: string): any {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const doc = this.vectorDb["documents"].find((d: any) => d.id === id);
    return doc?.metadata?.response || null;
  }

  /**
   * Get statistics
   */
  getStats() {
    return this.vectorDb.getStats();
  }
}
