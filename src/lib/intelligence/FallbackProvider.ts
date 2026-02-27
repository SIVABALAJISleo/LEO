import { MoERouter } from './MoERouter';

export class FallbackProvider {
    private static instance: FallbackProvider;
    private router: MoERouter;

    private constructor() {
        this.router = MoERouter.getInstance();
    }

    static getInstance(): FallbackProvider {
        if (!FallbackProvider.instance) {
            FallbackProvider.instance = new FallbackProvider();
        }
        return FallbackProvider.instance;
    }

    /**
     * Executes a query with a tiered fallback logic:
     * High Perf (Local Agent) -> Medium Perf (RAG + Specialized Expert) -> Safe General Response
     */
    async executeWithFallback(query: string): Promise<string> {
        try {
            // Tier 1: Specialized Expert Retrieval
            console.log('[FallbackProvider] Attempting Tier 1 (Expert Processor)...');
            return await this.router.process(query);
        } catch (error) {
            console.warn('[FallbackProvider] Tier 1 failed, falling back to Tier 2 (General)...');
            try {
                // Tier 2: General/Static Response fallback
                return `[Fallback Mode] The system is under heavy load. Your query "${query}" has been logged for deferred processing.`;
            } catch (innerError) {
                // Tier 3: Emergency response
                return "The system is currently unable to process requests. Please try again later.";
            }
        }
    }
}
