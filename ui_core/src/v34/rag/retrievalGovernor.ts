// LEO AI V34 — Retrieval Governor
// Capabilities: Evaluate semantic confidence of retrieved facts, and determine whether reasoning cycles can be bypassed.

import { RetrievalChunk } from "./externalMemoryEngine";

export interface GovernorResolution {
  query: string;
  hasBypassedReasoning: boolean;
  confidenceScore: number;
  selectedChunkIds: string[];
  resolvedAnswer: string;
}

export class RetrievalGovernor {
  evaluateRetrieval(query: string, chunks: RetrievalChunk[]): GovernorResolution {
    const topChunk = chunks[0];
    
    // If we have a highly relevant chunk (>0.85 similarity), we bypass neural reasoning completely
    const hasBypassedReasoning = topChunk ? topChunk.relevanceScore > 0.85 : false;
    const confidenceScore = topChunk ? topChunk.relevanceScore : 0.0;
    const selectedChunkIds = chunks.map(c => c.chunkId);
    
    const resolvedAnswer = hasBypassedReasoning && topChunk
      ? `[RETRIEVED ANSWER] Resolved via External RAG Index: ${topChunk.content}`
      : `[NEURAL FALLBACK] Insufficient retrieval confidence. Escalated to reasoning core.`;

    return {
      query,
      hasBypassedReasoning,
      confidenceScore,
      selectedChunkIds,
      resolvedAnswer
    };
  }
}
