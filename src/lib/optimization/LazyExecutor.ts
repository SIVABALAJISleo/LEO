import { v4 as uuidv4 } from 'uuid';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type Task<T = any> = () => Promise<T>;

interface LazyTask {
    id: string;
    task: Task;
    priority: number; // Higher is more important
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    resolve: (value: any) => void;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    reject: (reason: any) => void;
    createdAt: number;
}

export class LazyExecutor {
    private static instance: LazyExecutor;
    private queue: LazyTask[] = [];
    private isProcessing = false;
    private readonly IDLE_TIMEOUT = 50; // ms

    private constructor() { }

    static getInstance(): LazyExecutor {
        if (!LazyExecutor.instance) {
            LazyExecutor.instance = new LazyExecutor();
        }
        return LazyExecutor.instance;
    }

    // Defer a task to be executed later (e.g. when idle or in batch)
    defer<T>(task: Task<T>, priority: number = 1): Promise<T> {
        return new Promise((resolve, reject) => {
            const lazyTask: LazyTask = {
                id: uuidv4(),
                task,
                priority,
                resolve,
                reject,
                createdAt: Date.now()
            };

            this.queue.push(lazyTask);
            this.queue.sort((a, b) => b.priority - a.priority); // Sort by priority desc

            this.scheduleProcessing();
        });
    }

    private scheduleProcessing() {
        if (this.isProcessing) return;

        // Use requestIdleCallback if available, otherwise setTimeout
        if (typeof window !== 'undefined' && 'requestIdleCallback' in window) {
            // eslint-disable-next-line @typescript-eslint/ban-ts-comment
            // @ts-ignore
            window.requestIdleCallback((deadline) => {
                this.processQueue(deadline);
            });
        } else {
            setTimeout(() => {
                // Mock deadline for non-browser env
                this.processQueue({
                    timeRemaining: () => 50,
                    didTimeout: false
                });
            }, this.IDLE_TIMEOUT);
        }
    }

    private async processQueue(deadline: { timeRemaining: () => number, didTimeout: boolean }) {
        this.isProcessing = true;

        while (this.queue.length > 0 && (deadline.timeRemaining() > 0 || deadline.didTimeout)) {
            const item = this.queue.shift();
            if (!item) break;

            try {
                const result = await item.task();
                item.resolve(result);
            } catch (error) {
                item.reject(error);
            }
        }

        this.isProcessing = false;

        if (this.queue.length > 0) {
            this.scheduleProcessing();
        }
    }
}
