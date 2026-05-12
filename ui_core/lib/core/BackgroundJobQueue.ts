import { ReliabilityOrchestrator } from './ReliabilityOrchestrator';

export interface Job {
    id: string;
    type: string;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    payload: any;
    priority: number;
    retries: number;
    status: 'pending' | 'processing' | 'completed' | 'failed';
    createdAt: number;
}

export class BackgroundJobQueue {
    private static instance: BackgroundJobQueue;
    private queue: Job[] = [];
    private orchestrator: ReliabilityOrchestrator;
    private isProcessing: boolean = false;

    private constructor() {
        this.orchestrator = ReliabilityOrchestrator.getInstance();
    }

    static getInstance(): BackgroundJobQueue {
        if (!BackgroundJobQueue.instance) {
            BackgroundJobQueue.instance = new BackgroundJobQueue();
        }
        return BackgroundJobQueue.instance;
    }

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    enqueue(type: string, payload: any, priority: number = 0) {
        const job: Job = {
            id: Math.random().toString(36).substr(2, 9),
            type,
            payload,
            priority,
            retries: 0,
            status: 'pending',
            createdAt: Date.now()
        };

        this.queue.push(job);
        this.queue.sort((a, b) => b.priority - a.priority || a.createdAt - b.createdAt);

        console.log(`[JobQueue] Enqueued job ${job.id} (${type})`);

        if (!this.isProcessing) {
            this.processNext();
        }

        return job.id;
    }

    private async processNext() {
        const nextJob = this.queue.find(j => j.status === 'pending');
        if (!nextJob) {
            this.isProcessing = false;
            return;
        }

        this.isProcessing = true;
        nextJob.status = 'processing';

        try {
            console.log(`[JobQueue] Processing job ${nextJob.id}...`);
            await this.orchestrator.execute(nextJob.type, nextJob.payload);
            nextJob.status = 'completed';
        } catch (error) {
            console.error(`[JobQueue] Job ${nextJob.id} failed:`, error);
            if (nextJob.retries < 3) {
                nextJob.retries++;
                nextJob.status = 'pending'; // Re-queue
            } else {
                nextJob.status = 'failed';
            }
        }

        // Delay between jobs to avoid CPU spikes
        setTimeout(() => this.processNext(), 500);
    }

    getStats() {
        return {
            total: this.queue.length,
            pending: this.queue.filter(j => j.status === 'pending').length,
            completed: this.queue.filter(j => j.status === 'completed').length,
            failed: this.queue.filter(j => j.status === 'failed').length
        };
    }
}
