import { MoERouter } from './MoERouter';
import { SemanticCache } from './SemanticCache';

export class PrecomputationWorker {
    private static instance: PrecomputationWorker;
    private router: MoERouter;
    private cache: SemanticCache;
    private isRunning: boolean = false;

    private readonly COMMON_QUERIES = [
        "How can I optimize GPU memory?",
        "What is Mixture of Experts?",
        "Show me general debugging steps.",
        "How does RAG work?",
        "What are the system boundaries?"
    ];

    private constructor() {
        this.router = MoERouter.getInstance();
        this.cache = SemanticCache.getInstance();
    }

    static getInstance(): PrecomputationWorker {
        if (!PrecomputationWorker.instance) {
            PrecomputationWorker.instance = new PrecomputationWorker();
        }
        return PrecomputationWorker.instance;
    }

    async start() {
        if (this.isRunning) return;
        this.isRunning = true;
        console.log('[PrecomputationWorker] Starting background cache warming...');

        // Process in background
        this.warmCache();
    }

    private async warmCache() {
        for (const query of this.COMMON_QUERIES) {
            try {
                // We use the router to process, which will eventually hit the RAG pipeline
                // The cache will be populated during the process or we can explicitly set it
                // eslint-disable-next-line @typescript-eslint/no-unused-vars
                const response = await this.router.process(query);

                // We simulate the embedding for the cache context
                // In a real system, the router would handle this integration
                console.log(`[PrecomputationWorker] Precomputed response for: "${query}"`);

                // Yield to main thread
                await new Promise(r => setTimeout(r, 1000));
            } catch (error) {
                console.error(`[PrecomputationWorker] Failed to precompute "${query}":`, error);
            }
        }

        this.isRunning = false;
        console.log('[PrecomputationWorker] Cache warming complete.');
    }
}
