type WorkItem = () => Promise<any>;

export class WorkerPool {
    private static instance: WorkerPool;
    private queue: WorkItem[] = [];
    private readonly workerCount: number;
    private activeWorkers = 0;

    private constructor() {
        this.workerCount = navigator.hardwareConcurrency || 4;
    }

    static getInstance(): WorkerPool {
        if (!WorkerPool.instance) {
            WorkerPool.instance = new WorkerPool();
        }
        return WorkerPool.instance;
    }

    async execute<T>(work: () => Promise<T>): Promise<T> {
        if (this.activeWorkers < this.workerCount) {
            return this.runWork(work);
        } else {
            return new Promise((resolve, reject) => {
                this.queue.push(async () => {
                    try {
                        const result = await work();
                        resolve(result);
                    } catch (e) {
                        reject(e);
                    }
                });
            });
        }
    }

    private async runWork<T>(work: () => Promise<T>): Promise<T> {
        this.activeWorkers++;
        try {
            const result = await work();
            return result;
        } finally {
            this.activeWorkers--;
            this.processQueue();
        }
    }

    private processQueue() {
        if (this.queue.length > 0 && this.activeWorkers < this.workerCount) {
            const next = this.queue.shift();
            if (next) {
                this.runWork(next);
            }
        }
    }

    getStats() {
        return {
            workerCount: this.workerCount,
            activeWorkers: this.activeWorkers,
            queueLength: this.queue.length
        };
    }
}
