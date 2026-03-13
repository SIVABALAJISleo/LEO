import { SemanticCache } from '../intelligence/SemanticCache';

interface CacheEntry {
    query: string;
    vector: number[];
    response: string;
    timestamp: number;
    accessCount: number;
}

export class PersistentCache {
    private static instance: PersistentCache;
    private memoryCache: SemanticCache;
    private readonly STORAGE_KEY = 'persistent_semantic_cache';
    private readonly MAX_SIZE = 100; // Max entries to persist

    private constructor() {
        this.memoryCache = SemanticCache.getInstance();
        this.loadFromStorage();
    }

    static getInstance(): PersistentCache {
        if (!PersistentCache.instance) {
            PersistentCache.instance = new PersistentCache();
        }
        return PersistentCache.instance;
    }

    async get(queryVector: number[]): Promise<string | null> {
        // First check memory cache
        const memResult = await this.memoryCache.get(queryVector);
        if (memResult) {
            console.log('[PersistentCache] Memory hit');
            return memResult;
        }

        // Then check persistent storage
        const stored = this.getStoredEntries();
        const bestMatch = this.findBestMatch(queryVector, stored);

        if (bestMatch) {
            console.log('[PersistentCache] Storage hit');
            // Re-warm memory cache
            this.memoryCache.set(bestMatch.query, bestMatch.vector, bestMatch.response);
            this.incrementAccessCount(bestMatch);
            return bestMatch.response;
        }

        return null;
    }

    set(query: string, queryVector: number[], response: string): void {
        // Set in memory cache
        this.memoryCache.set(query, queryVector, response);

        // Also persist to storage
        const entries = this.getStoredEntries();
        entries.push({
            query,
            vector: queryVector,
            response,
            timestamp: Date.now(),
            accessCount: 1
        });

        // Keep only top N by access count
        const sorted = entries.sort((a, b) => b.accessCount - a.accessCount).slice(0, this.MAX_SIZE);
        this.saveToStorage(sorted);
    }

    private loadFromStorage() {
        try {
            const stored = localStorage.getItem(this.STORAGE_KEY);
            if (stored) {
                const entries: CacheEntry[] = JSON.parse(stored);
                console.log(`[PersistentCache] Loaded ${entries.length} entries from storage`);
            }
        } catch (e) {
            console.warn('[PersistentCache] Failed to load from storage:', e);
        }
    }

    private getStoredEntries(): CacheEntry[] {
        try {
            const stored = localStorage.getItem(this.STORAGE_KEY);
            return stored ? JSON.parse(stored) : [];
        } catch {
            return [];
        }
    }

    private saveToStorage(entries: CacheEntry[]) {
        try {
            localStorage.setItem(this.STORAGE_KEY, JSON.stringify(entries));
        } catch (e) {
            console.warn('[PersistentCache] Failed to save to storage:', e);
        }
    }

    private findBestMatch(queryVector: number[], entries: CacheEntry[]): CacheEntry | null {
        let best: CacheEntry | null = null;
        let bestScore = 0.9; // Require high similarity

        for (const entry of entries) {
            const score = this.cosineSimilarity(queryVector, entry.vector);
            if (score > bestScore) {
                bestScore = score;
                best = entry;
            }
        }

        return best;
    }

    private cosineSimilarity(a: number[], b: number[]): number {
        let dot = 0, normA = 0, normB = 0;
        for (let i = 0; i < a.length; i++) {
            dot += a[i] * b[i];
            normA += a[i] * a[i];
            normB += b[i] * b[i];
        }
        return dot / (Math.sqrt(normA) * Math.sqrt(normB));
    }

    private incrementAccessCount(entry: CacheEntry) {
        const entries = this.getStoredEntries();
        const found = entries.find(e => e.query === entry.query);
        if (found) {
            found.accessCount++;
            this.saveToStorage(entries);
        }
    }
}
