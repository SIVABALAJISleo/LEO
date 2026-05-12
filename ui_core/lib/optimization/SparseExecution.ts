/**
 * SparseExecution (Pillar 2: Sparse Execution Engine)
 * Provides utilities for lazy evaluation and memoization to ensure 
 * minimal code paths are executed.
 */

export class SparseExecution {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    private static memoCache = new Map<string, any>();

    /**
     * Memoizes a function result based on its arguments.
     * Satisfies "memoization for repeated queries".
     */
    static memoize<T>(key: string, fn: () => T): T {
        if (this.memoCache.has(key)) {
            console.log(`[SparseExecution] Memo Hit: ${key}`);
            return this.memoCache.get(key);
        }
        const result = fn();
        this.memoCache.set(key, result);
        return result;
    }

    /**
     * Wraps a value in a lazy-evaluator.
     * Satisfies "add lazy evaluation everywhere".
     */
    static lazy<T>(fn: () => T): () => T {
        let value: T | undefined;
        let executed = false;
        return () => {
            if (!executed) {
                console.log('[SparseExecution] Lazy Evaluation Triggered');
                value = fn();
                executed = true;
            }
            return value!;
        };
    }

    /**
     * Clears the memoization cache.
     */
    static clearCache(): void {
        this.memoCache.clear();
    }
}
