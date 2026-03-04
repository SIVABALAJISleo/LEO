/**
 * Failure-Safe Fallback Graph
 * Routes failed operations to nearest valid approximation path.
 */

export interface FallbackNode {
    id: string;
    quality: number; // 0-1
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    execute: (input: any) => Promise<any>;
    fallbacks: string[]; // Node IDs to try if this fails
}

export class FallbackGraph {
    private static instance: FallbackGraph;
    private nodes = new Map<string, FallbackNode>();
    private executionHistory: Array<{ node: string; success: boolean }> = [];

    private constructor() { }

    static getInstance(): FallbackGraph {
        if (!FallbackGraph.instance) {
            FallbackGraph.instance = new FallbackGraph();
        }
        return FallbackGraph.instance;
    }

    /**
     * Register computation node with fallbacks
     */
    registerNode(node: FallbackNode): void {
        this.nodes.set(node.id, node);
    }

    /**
     * Execute with automatic fallback on failure
     */
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    async execute(nodeId: string, input: any): Promise<{ result: any; path: string[] }> {
        const visited = new Set<string>();
        const path: string[] = [];

        return this.tryNode(nodeId, input, visited, path);
    }

    private async tryNode(
        nodeId: string,
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        input: any,
        visited: Set<string>,
        path: string[]
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    ): Promise<{ result: any; path: string[] }> {
        if (visited.has(nodeId)) {
            throw new Error(`Cycle detected: ${nodeId}`);
        }

        visited.add(nodeId);
        path.push(nodeId);

        const node = this.nodes.get(nodeId);
        if (!node) {
            throw new Error(`Node not found: ${nodeId}`);
        }

        try {
            console.log(`[FallbackGraph] Trying ${nodeId} (quality: ${node.quality})`);
            const result = await node.execute(input);

            this.executionHistory.push({ node: nodeId, success: true });
            console.log(`[FallbackGraph] Success: ${path.join(' → ')}`);

            return { result, path };
        } catch (error) {
            console.warn(`[FallbackGraph] ${nodeId} failed:`, error);
            this.executionHistory.push({ node: nodeId, success: false });

            // Try fallbacks in order
            for (const fallbackId of node.fallbacks) {
                try {
                    return await this.tryNode(fallbackId, input, visited, [...path]);
                } catch {
                    continue;
                }
            }

            throw new Error(`All fallbacks exhausted for ${nodeId}`);
        }
    }

    /**
     * Get recommended path based on history
     */
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    getRecommendedPath(startNode: string): string[] {
        // Simple heuristic: find most successful path
        const successRate = new Map<string, number>();

        for (const record of this.executionHistory) {
            const rate = successRate.get(record.node) || 0;
            successRate.set(record.node, rate + (record.success ? 1 : 0));
        }

        // Return nodes sorted by success rate
        return Array.from(successRate.entries())
            .sort((a, b) => b[1] - a[1])
            .map(([node]) => node);
    }

    /**
     * Build approximation chain: exact → fast → cached
     */
    buildApproximationChain(
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        exact: () => Promise<any>,
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        fast: () => Promise<any>,
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        cached: () => Promise<any>
    ): void {
        this.registerNode({
            id: 'exact',
            quality: 1.0,
            execute: exact,
            fallbacks: ['fast']
        });

        this.registerNode({
            id: 'fast',
            quality: 0.9,
            execute: fast,
            fallbacks: ['cached']
        });

        this.registerNode({
            id: 'cached',
            quality: 0.7,
            execute: cached,
            fallbacks: []
        });
    }
}
