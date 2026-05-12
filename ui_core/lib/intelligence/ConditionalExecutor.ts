/**
 * Conditional Execution Controller
 * Routes execution based on novelty to minimize redundant computation.
 */

import { NoveltyDetector, NoveltyState } from './NoveltyDetector';
import { RAGPipeline } from './RAGPipeline';
import { SystemMetrics } from '../observability/SystemMetrics';

export interface ExecutionResult<T> {
    result: T;
    mode: 'cached' | 'lightweight' | 'full';
    computeTime: number;
    noveltyState: NoveltyState;
}

export class ConditionalExecutor {
    private static instance: ConditionalExecutor;
    private novelty: NoveltyDetector;
    private rag: RAGPipeline;
    private metrics: SystemMetrics;

    private constructor() {
        this.novelty = NoveltyDetector.getInstance();
        this.rag = RAGPipeline.getInstance();
        this.metrics = SystemMetrics.getInstance();
    }

    static getInstance(): ConditionalExecutor {
        if (!ConditionalExecutor.instance) {
            ConditionalExecutor.instance = new ConditionalExecutor();
        }
        return ConditionalExecutor.instance;
    }

    /**
     * Smart inference with novelty-based routing
     */
    async execute<T>(
        input: string,
        fullInference: (input: string, context?: string) => Promise<T>,
        lightInference?: (input: string, context: string) => Promise<T>
    ): Promise<ExecutionResult<T>> {
        const startTime = performance.now();

        // Generate embedding (mock for now)
        const embedding = this.generateEmbedding(input);

        // Detect novelty
        const noveltyResult = await this.novelty.detect(input, embedding);

        let result: T;
        let mode: 'cached' | 'lightweight' | 'full';

        switch (noveltyResult.state) {
            case NoveltyState.SAME:
                // Return cached answer immediately
                result = this.novelty.retrieve(noveltyResult.matchedId!) as T;
                mode = 'cached';
                this.metrics.increment('conditional_exec_cached');
                console.log('[ConditionalExecutor] Using cached response');
                break;

            case NoveltyState.SIMILAR:
                // Lightweight reasoning with retrieved context
                // eslint-disable-next-line no-case-declarations
                const contextItems = await this.rag.retrieve(input, 3);
                // eslint-disable-next-line no-case-declarations
                const context = contextItems.map(c => `${c.text} (source: ${c.source}, score: ${c.score})`).join('\n');

                if (lightInference) {
                    result = await lightInference(input, context);
                } else {
                    // Fallback to full with context
                    result = await fullInference(input, context);
                }

                mode = 'lightweight';
                this.metrics.increment('conditional_exec_lightweight');
                console.log('[ConditionalExecutor] Lightweight reasoning');

                // Store for future use
                // eslint-disable-next-line @typescript-eslint/no-explicit-any
                this.novelty.store(input, embedding, result as any);
                break;

            case NoveltyState.NEW:
                // Full inference
                result = await fullInference(input);
                mode = 'full';
                this.metrics.increment('conditional_exec_full');
                console.log('[ConditionalExecutor] Full inference');

                // Store in memory
                // eslint-disable-next-line @typescript-eslint/no-explicit-any
                this.novelty.store(input, embedding, result as any);
                break;
        }

        const computeTime = performance.now() - startTime;
        this.metrics.histogram('conditional_exec_time', computeTime, { mode });

        return {
            result,
            mode,
            computeTime,
            noveltyState: noveltyResult.state
        };
    }

    private generateEmbedding(text: string): number[] {
        // Mock embedding - real implementation would use a model
        const embedding = new Array(384).fill(0);
        for (let i = 0; i < text.length && i < 384; i++) {
            embedding[i] = text.charCodeAt(i) / 255;
        }
        return embedding;
    }
}
