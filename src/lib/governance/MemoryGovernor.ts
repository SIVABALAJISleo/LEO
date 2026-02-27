/**
 * ═══════════════════════════════════════════════════════════════
 *  MEMORY GOVERNOR — Memory Lifecycle Management
 * ═══════════════════════════════════════════════════════════════
 *  Handles: compress, archive, or delete low-value entries.
 *  Integrates with NoveltyDetector memory for lifecycle control.
 * ═══════════════════════════════════════════════════════════════
 */

import {
    GovernedMemoryEntry,
} from './types';

export class MemoryGovernor {
    private static instance: MemoryGovernor;
    private memories = new Map<string, GovernedMemoryEntry>();
    private readonly MAX_MEMORIES = 5000;
    private readonly LOW_VALUE_THRESHOLD = 0.2;
    private readonly STALE_THRESHOLD_MS = 86400000 * 7; // 7 days
    private readonly COMPRESS_AGE_MS = 86400000 * 3;     // 3 days

    private constructor() {
        this.startLifecycleMonitor();
    }

    static getInstance(): MemoryGovernor {
        if (!MemoryGovernor.instance) {
            MemoryGovernor.instance = new MemoryGovernor();
        }
        return MemoryGovernor.instance;
    }

    /** Store a new memory entry */
    store(entry: GovernedMemoryEntry): void {
        this.memories.set(entry.id, entry);

        // Enforce capacity
        if (this.memories.size > this.MAX_MEMORIES) {
            this.evictLowestValue();
        }
    }

    /** Retrieve a memory and update access time */
    retrieve(id: string): GovernedMemoryEntry | null {
        const entry = this.memories.get(id);
        if (!entry) return null;

        // Update access metadata (create new immutable entry)
        const updated: GovernedMemoryEntry = {
            ...entry,
            usageCount: entry.usageCount + 1,
            lastAccessedAt: Date.now(),
        };
        this.memories.set(id, updated);
        return updated;
    }

    /** Check if a memory should be used based on its value score */
    isUsable(id: string): boolean {
        const entry = this.memories.get(id);
        if (!entry) return false;

        const value = this.computeValueScore(entry);
        return value >= this.LOW_VALUE_THRESHOLD;
    }

    /** Get memory statistics */
    getStats(): {
        total: number;
        byDomain: Record<string, number>;
        avgValue: number;
        staleCount: number;
    } {
        const byDomain: Record<string, number> = {};
        let totalValue = 0;
        let staleCount = 0;
        const now = Date.now();

        this.memories.forEach(entry => {
            byDomain[entry.domain] = (byDomain[entry.domain] || 0) + 1;
            totalValue += this.computeValueScore(entry);
            if (now - entry.lastAccessedAt > this.STALE_THRESHOLD_MS) staleCount++;
        });

        return {
            total: this.memories.size,
            byDomain,
            avgValue: this.memories.size > 0 ? totalValue / this.memories.size : 0,
            staleCount,
        };
    }

    /** Force a lifecycle sweep */
    sweep(): { deleted: number; compressed: number } {
        let deleted = 0;
        let compressed = 0;
        const now = Date.now();

        const toDelete: string[] = [];

        this.memories.forEach((entry, id) => {
            const value = this.computeValueScore(entry);
            const age = now - entry.createdAt;

            // Delete: stale and low-value
            if (age > this.STALE_THRESHOLD_MS && value < this.LOW_VALUE_THRESHOLD) {
                toDelete.push(id);
                deleted++;
                return;
            }

            // Delete: negative feedback score
            if (entry.feedbackScore !== null && entry.feedbackScore < 0) {
                toDelete.push(id);
                deleted++;
                return;
            }

            // Compress: old but still somewhat valuable (reduce embedding precision)
            if (age > this.COMPRESS_AGE_MS && entry.embedding.length > 0) {
                const compressedEntry: GovernedMemoryEntry = {
                    ...entry,
                    embedding: this.compressEmbedding(entry.embedding),
                };
                this.memories.set(id, compressedEntry);
                compressed++;
            }
        });

        toDelete.forEach(id => this.memories.delete(id));

        return { deleted, compressed };
    }

    // ──────────────────── Private Helpers ────────────────────

    private computeValueScore(entry: GovernedMemoryEntry): number {
        const now = Date.now();
        const ageHours = (now - entry.createdAt) / 3600000;
        const recencyHours = (now - entry.lastAccessedAt) / 3600000;

        // Factors: usage frequency, recency, feedback, reliability
        const usageScore = Math.min(1.0, entry.usageCount / 10);
        const recencyScore = Math.exp(-recencyHours / 168); // Decay over 1 week
        const feedbackScore = entry.feedbackScore !== null
            ? Math.max(0, (entry.feedbackScore + 1) / 2) // Normalize -1..1 to 0..1
            : 0.5; // Unknown = neutral
        const reliabilityScore = entry.reliability;

        return (
            usageScore * 0.3 +
            recencyScore * 0.25 +
            feedbackScore * 0.25 +
            reliabilityScore * 0.2
        );
    }

    private evictLowestValue(): void {
        let lowestId: string | null = null;
        let lowestValue = Infinity;

        this.memories.forEach((entry, id) => {
            const value = this.computeValueScore(entry);
            if (value < lowestValue) {
                lowestValue = value;
                lowestId = id;
            }
        });

        if (lowestId) {
            this.memories.delete(lowestId);
        }
    }

    private compressEmbedding(embedding: number[]): number[] {
        // Reduce dimensionality by averaging pairs
        const compressed: number[] = [];
        for (let i = 0; i < embedding.length; i += 2) {
            if (i + 1 < embedding.length) {
                compressed.push((embedding[i] + embedding[i + 1]) / 2);
            } else {
                compressed.push(embedding[i]);
            }
        }
        return compressed;
    }

    private startLifecycleMonitor(): void {
        // Run sweep every 10 minutes
        setInterval(() => {
            const result = this.sweep();
            if (result.deleted > 0 || result.compressed > 0) {
                console.log(
                    `[MemoryGovernor] Lifecycle sweep: deleted=${result.deleted}, compressed=${result.compressed}`
                );
            }
        }, 600000);
    }
}
