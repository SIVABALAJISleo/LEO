import { SemanticCache } from '../intelligence/SemanticCache';

export class MultiLevelCache {
    private static instance: MultiLevelCache;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    private l1: Map<string, any> = new Map(); // Memory Cache
    private l2: SemanticCache; // Semantic L2

    private readonly MAX_L1_SIZE = 500;

    private constructor() {
        this.l2 = SemanticCache.getInstance();
    }

    static getInstance(): MultiLevelCache {
        if (!MultiLevelCache.instance) {
            MultiLevelCache.instance = new MultiLevelCache();
        }
        return MultiLevelCache.instance;
    }

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    async get(key: string, vector?: number[]): Promise<any | null> {
        // Check L1
        if (this.l1.has(key)) {
            console.log(`[MultiLevelCache] L1 Hit for ${key}`);
            return this.l1.get(key);
        }

        // Check L2 (Semantic) if vector provided
        if (vector) {
            const semanticResult = await this.l2.get(vector);
            if (semanticResult) {
                console.log(`[MultiLevelCache] L2 (Semantic) Hit for ${key}`);
                this.setL1(key, semanticResult);
                return semanticResult;
            }
        }

        return null;
    }

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    set(key: string, value: any, vector?: number[]) {
        this.setL1(key, value);
        if (vector) {
            this.l2.set(key, vector, typeof value === 'string' ? value : JSON.stringify(value));
        }
    }

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    private setL1(key: string, value: any) {
        if (this.l1.size >= this.MAX_L1_SIZE) {
            const firstKey = this.l1.keys().next().value;
            if (typeof firstKey === 'string') {
                this.l1.delete(firstKey);
            }
        }
        this.l1.set(key, value);
    }
}
