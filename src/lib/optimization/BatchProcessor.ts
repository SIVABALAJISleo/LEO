type BatchTask<T, R> = {
    payload: T;
    resolve: (value: R) => void;
    reject: (reason: any) => void;
}

export class BatchProcessor<T, R> {
    private queue: BatchTask<T, R>[] = [];
    private readonly batchSize: number;
    private readonly waitTime: number;
    private timeout: any = null;
    private processor: (items: T[]) => Promise<R[]>;

    constructor(processor: (items: T[]) => Promise<R[]>, batchSize: number = 10, waitTime: number = 50) {
        this.processor = processor;
        this.batchSize = batchSize;
        this.waitTime = waitTime;
    }

    add(payload: T): Promise<R> {
        return new Promise((resolve, reject) => {
            this.queue.push({ payload, resolve, reject });

            if (this.queue.length >= this.batchSize) {
                this.flush();
            } else if (!this.timeout) {
                this.timeout = setTimeout(() => this.flush(), this.waitTime);
            }
        });
    }

    private async flush() {
        if (this.timeout) {
            clearTimeout(this.timeout);
            this.timeout = null;
        }

        if (this.queue.length === 0) return;

        const currentBatch = this.queue.splice(0, this.batchSize);
        const payloads = currentBatch.map(item => item.payload);

        try {
            const results = await this.processor(payloads);

            if (results.length !== currentBatch.length) {
                throw new Error('Batch processor returned incorrect number of results');
            }

            currentBatch.forEach((item, index) => {
                item.resolve(results[index]);
            });
        } catch (error) {
            currentBatch.forEach(item => {
                item.reject(error);
            });
        }
    }
}
