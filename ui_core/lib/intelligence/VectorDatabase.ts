import { v4 as uuidv4 } from 'uuid';

export interface VectorDocument {
    id: string;
    text: string;
    vector: number[];
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    metadata?: Record<string, any>;
}

export interface SearchResult extends VectorDocument {
    score: number;
}

export class VectorDatabase {
    private documents: VectorDocument[] = [];
    private readonly dimension: number;

    constructor(dimension: number = 384) {
        this.dimension = dimension;
    }

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    add(text: string, vector: number[], metadata?: Record<string, any>): string {
        if (vector.length !== this.dimension) {
            throw new Error(`Vector dimension mismatch. Expected ${this.dimension}, got ${vector.length}`);
        }

        const doc: VectorDocument = {
            id: uuidv4(),
            text,
            vector,
            metadata,
        };
        this.documents.push(doc);
        return doc.id;
    }

    search(queryVector: number[], limit: number = 5, threshold: number = 0.7): SearchResult[] {
        if (queryVector.length !== this.dimension) {
            throw new Error(`Query vector dimension mismatch. Expected ${this.dimension}, got ${queryVector.length}`);
        }

        return this.documents
            .map(doc => ({
                ...doc,
                score: this.cosineSimilarity(queryVector, doc.vector)
            }))
            .filter(result => result.score >= threshold)
            .sort((a, b) => b.score - a.score)
            .slice(0, limit);
    }

    private cosineSimilarity(veca: number[], vecb: number[]): number {
        let dot = 0;
        let normA = 0;
        let normB = 0;
        for (let i = 0; i < veca.length; i++) {
            dot += veca[i] * vecb[i];
            normA += veca[i] * veca[i];
            normB += vecb[i] * vecb[i];
        }
        return dot / (Math.sqrt(normA) * Math.sqrt(normB));
    }

    // Debug/Stats
    getStats() {
        return {
            count: this.documents.length,
            dimension: this.dimension
        };
    }
}
