import { SystemMetrics } from '../observability/SystemMetrics';

type AlgorithmFn<T, R> = (input: T) => Promise<R>;

export interface StrategyOption<T, R> {
    name: string;
    algorithm: AlgorithmFn<T, R>;
    priority: number;
}

export class StrategySwapper {
    private static instance: StrategySwapper;
    private metrics: SystemMetrics;
    private failureCount: Map<string, number> = new Map();

    private constructor() {
        this.metrics = SystemMetrics.getInstance();
    }

    static getInstance(): StrategySwapper {
        if (!StrategySwapper.instance) {
            StrategySwapper.instance = new StrategySwapper();
        }
        return StrategySwapper.instance;
    }

    async executeWithFallback<T, R>(
        taskName: string,
        input: T,
        strategies: StrategyOption<T, R>[]
    ): Promise<R> {
        const sorted = strategies.sort((a, b) => b.priority - a.priority);

        for (const strategy of sorted) {
            try {
                const startTime = Date.now();
                const result = await strategy.algorithm(input);
                const duration = Date.now() - startTime;

                this.metrics.histogram('strategy_duration', duration, {
                    task: taskName,
                    strategy: strategy.name
                });

                // Reset failure count on success
                this.failureCount.set(`${taskName}:${strategy.name}`, 0);

                console.log(`[StrategySwapper] Success with ${strategy.name} in ${duration}ms`);
                return result;
            } catch (error) {
                const failKey = `${taskName}:${strategy.name}`;
                const count = (this.failureCount.get(failKey) || 0) + 1;
                this.failureCount.set(failKey, count);

                this.metrics.increment('strategy_failure', 1, {
                    task: taskName,
                    strategy: strategy.name
                });

                console.warn(`[StrategySwapper] ${strategy.name} failed (${count} failures), trying next...`);

                // If this is the last strategy, throw
                if (strategy === sorted[sorted.length - 1]) {
                    throw error;
                }
            }
        }

        throw new Error('All strategies failed');
    }
}
