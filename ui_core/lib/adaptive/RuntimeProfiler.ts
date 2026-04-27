import { SystemMetrics } from '../observability/SystemMetrics';

export interface TaskProfile {
    taskType: string;
    avgLatencyMs: number;
    maxLatencyMs: number;
    minLatencyMs: number;
    avgMemoryMb: number;
    executionCount: number;
    lastExecuted: number;
}

export class RuntimeProfiler {
    private static instance: RuntimeProfiler;
    private profiles: Map<string, TaskProfile> = new Map();
    private metrics: SystemMetrics;

    private constructor() {
        this.metrics = SystemMetrics.getInstance();
    }

    static getInstance(): RuntimeProfiler {
        if (!RuntimeProfiler.instance) {
            RuntimeProfiler.instance = new RuntimeProfiler();
        }
        return RuntimeProfiler.instance;
    }

    startMeasure(taskType: string): () => void {
        const startTime = performance.now();
        const startMemory = this.getMemoryUsage();

        return () => {
            const duration = performance.now() - startTime;
            const memoryUsed = this.getMemoryUsage() - startMemory;
            this.recordMeasurement(taskType, duration, memoryUsed);
        };
    }

    private recordMeasurement(taskType: string, latencyMs: number, memoryMb: number) {
        const existing = this.profiles.get(taskType);

        if (existing) {
            const count = existing.executionCount + 1;
            this.profiles.set(taskType, {
                taskType,
                avgLatencyMs: (existing.avgLatencyMs * existing.executionCount + latencyMs) / count,
                maxLatencyMs: Math.max(existing.maxLatencyMs, latencyMs),
                minLatencyMs: Math.min(existing.minLatencyMs, latencyMs),
                avgMemoryMb: (existing.avgMemoryMb * existing.executionCount + memoryMb) / count,
                executionCount: count,
                lastExecuted: Date.now()
            });
        } else {
            this.profiles.set(taskType, {
                taskType,
                avgLatencyMs: latencyMs,
                maxLatencyMs: latencyMs,
                minLatencyMs: latencyMs,
                avgMemoryMb: memoryMb,
                executionCount: 1,
                lastExecuted: Date.now()
            });
        }

        this.metrics.histogram('task_latency', latencyMs, { taskType });
        this.metrics.gauge('task_memory', memoryMb, { taskType });
    }

    getProfile(taskType: string): TaskProfile | null {
        return this.profiles.get(taskType) || null;
    }

    getAllProfiles(): TaskProfile[] {
        return Array.from(this.profiles.values());
    }

    private getMemoryUsage(): number {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        if (typeof (performance as any).memory !== 'undefined') {
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            return (performance as any).memory.usedJSHeapSize / (1024 * 1024);
        }
        return 0;
    }
}
