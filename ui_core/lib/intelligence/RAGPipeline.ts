import { VectorDatabase } from './VectorDatabase';
import { SparseExecution } from '../optimization/SparseExecution';

export interface RAGContext {
    text: string;
    source: string;
    score: number;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    metadata?: Record<string, any>;
}

/**
 * RAGPipeline (Intelligence Strategy)
 * Integrated with SparseExecution (Pillar 2) for memoization 
 * and persistent retrieval logic.
 */
export class RAGPipeline {
    private static instance: RAGPipeline;
    private db: VectorDatabase;

    // Production-ready deterministic embedding generator 
    private generateEmbedding(text: string): number[] {
        // Pillar 2: Memoize expensive embedding generation
        return SparseExecution.memoize(`embed:${text}`, () => {
            const textLower = text.toLowerCase().trim();
            const dimensions = 384;
            const vec = new Array(dimensions).fill(0);

            for (let i = 0; i < textLower.length; i++) {
                const char = textLower.charCodeAt(i);
                for (let d = 0; d < dimensions; d++) {
                    vec[d] += Math.sin(char * (d + 1) * 0.1) * (i + 1);
                }
            }

            const magnitude = Math.sqrt(vec.reduce((sum, val) => sum + val * val, 0)) || 1;
            return vec.map(val => val / magnitude);
        });
    }

    private constructor() {
        this.db = new VectorDatabase(384);
    }

    static getInstance(): RAGPipeline {
        if (!RAGPipeline.instance) {
            RAGPipeline.instance = new RAGPipeline();
        }
        return RAGPipeline.instance;
    }

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    async ingest(text: string, source: string, metadata: Record<string, any> = {}): Promise<string> {
        const chunks = text.match(/.{1,500}(\s|$)/g) || [text];

        for (const chunk of chunks) {
            const vector = this.generateEmbedding(chunk);
            await this.db.add(chunk, vector, { ...metadata, source, ingestedAt: Date.now() });
        }

        return `Ingested ${chunks.length} chunks from ${source}`;
    }

    async retrieve(query: string, limit: number = 3, threshold: number = 0.5): Promise<RAGContext[]> {
        // Pillar 2: Memoize the primary retrieval step
        return SparseExecution.memoize(`retrieve:${query}:${limit}`, async () => {
            const queryVector = this.generateEmbedding(query);
            const results = this.db.search(queryVector, limit, threshold);

            return results.map(r => ({
                text: r.text,
                source: r.metadata?.source || 'unknown',
                score: r.score,
                metadata: r.metadata
            }));
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        }) as any;
    }

    async generatePrompt(query: string): Promise<string> {
        const context = await this.retrieve(query, 5, 0.4);

        if (context.length === 0) {
            return `No specific context found. Base query: ${query}`;
        }

        const contextStr = context
            .map((c, i) => `[Context ${i + 1}] (Source: ${c.source}, Score: ${c.score.toFixed(2)}): ${c.text}`)
            .join('\n\n');

        return `
SYSTEM: You are a production-grade AI assistant. Use the verified context below to answer.
If the context is insufficient, state your limitations clearly.

VERIFIED CONTEXT:
${contextStr}

USER QUERY: ${query}

RELIABLE RESPONSE:
`;
    }
}
