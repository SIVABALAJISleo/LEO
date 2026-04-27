/**
 * Progressive Computation Pipeline
 * Returns instant rough result then refines in background with cancelable stages.
 */

export interface ComputeStage<T> {
    name: string;
    quality: number; // 0-1
    compute: (previous?: T) => Promise<T>;
}

export interface ProgressiveResult<T> {
    result: T;
    quality: number;
    stage: string;
    cancel: () => void;
    onUpdate: (callback: (result: T, quality: number, stage: string) => void) => void;
}

export class ProgressivePipeline {
    private static instance: ProgressivePipeline;
    private activePipelines = new Map<string, AbortController>();

    private constructor() { }

    static getInstance(): ProgressivePipeline {
        if (!ProgressivePipeline.instance) {
            ProgressivePipeline.instance = new ProgressivePipeline();
        }
        return ProgressivePipeline.instance;
    }

    async compute<T>(
        id: string,
        stages: ComputeStage<T>[]
    ): Promise<ProgressiveResult<T>> {
        // Cancel any existing pipeline with this ID
        this.cancel(id);

        const controller = new AbortController();
        this.activePipelines.set(id, controller);

        const callbacks: Array<(result: T, quality: number, stage: string) => void> = [];

        let currentResult: T | undefined;
        let currentQuality = 0;
        let currentStage = 'none';

        // Start background refinement
        (async () => {
            for (const stage of stages) {
                if (controller.signal.aborted) {
                    console.log(`[ProgressivePipeline] ${id} cancelled at ${stage.name}`);
                    break;
                }

                try {
                    const result = await stage.compute(currentResult);
                    currentResult = result;
                    currentQuality = stage.quality;
                    currentStage = stage.name;

                    // Notify all listeners
                    callbacks.forEach(cb => cb(result, stage.quality, stage.name));
                } catch (error) {
                    console.error(`[ProgressivePipeline] Stage ${stage.name} failed:`, error);
                    break;
                }
            }

            this.activePipelines.delete(id);
        })();

        // Wait for first stage to complete
        const firstResult = await stages[0].compute();
        currentResult = firstResult;
        // eslint-disable-next-line @typescript-eslint/no-unused-vars
        currentQuality = stages[0].quality;
        // eslint-disable-next-line @typescript-eslint/no-unused-vars
        currentStage = stages[0].name;

        return {
            result: firstResult,
            quality: stages[0].quality,
            stage: stages[0].name,
            cancel: () => this.cancel(id),
            onUpdate: (callback) => {
                callbacks.push(callback);
            }
        };
    }

    cancel(id: string): void {
        const controller = this.activePipelines.get(id);
        if (controller) {
            controller.abort();
            this.activePipelines.delete(id);
        }
    }

    cancelAll(): void {
        this.activePipelines.forEach(controller => controller.abort());
        this.activePipelines.clear();
    }
}
