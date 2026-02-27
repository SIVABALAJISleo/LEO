import { HealthMonitor } from './core/HealthMonitor';
import { MoERouter } from './intelligence/MoERouter';
import { ReliabilityOrchestrator } from './core/ReliabilityOrchestrator';

export interface BackendStatus {
    version: string;
    metrics: {
        requests: number;
        errors: number;
        latency_avg: number;
    };
    hardware: {
        cpu_load: number;
        memory_percent: number;
        disk_percent: number;
        memory_available_gb: number;
    };
    server_time: number;
}

export interface HealthStatus {
    status: 'healthy' | 'degraded';
    engines_available: boolean;
    timestamp: number;
}

export interface CoreTelemetry {
    sdgp_active: boolean;
    gpu_relevance_reduction: string;
    equivalent_vram_gb: number;
    sdgp_latency_ms: number;
    ray_logic_depth: number | string;
    dlss_s_active: boolean;
    perceptual_culling: string;
}

export interface OrchestrateResponse {
    status: string;
    job_id: string;
    mode: string;
    expert: string;
    result: string;
    timestamp: number;
    core: CoreTelemetry;
    agentic_intervention?: boolean;
    healer_action?: string;
}

/**
 * HYPER API Client
 * Integrated with ReliabilityOrchestrator for Pillar 6 & 7 compliance.
 */
export const hyperClient = {
    // Existing local-mock methods...
    async getHealth(): Promise<HealthStatus> {
        const health = await HealthMonitor.getInstance().getSystemHealth();
        return {
            status: health.status as 'healthy' | 'degraded',
            engines_available: true,
            timestamp: Date.now()
        };
    },

    async getStatus(): Promise<BackendStatus> {
        const health = await HealthMonitor.getInstance().getSystemHealth();
        return {
            version: '1.0.0-PROD',
            metrics: {
                requests: Math.floor(Math.random() * 1000),
                errors: 0,
                latency_avg: 0.12
            },
            hardware: {
                cpu_load: 15,
                memory_percent: Math.floor((health.memory.used / health.memory.total) * 100),
                disk_percent: 40,
                memory_available_gb: (health.memory.total - health.memory.used) / (1024 * 1024 * 1024)
            },
            server_time: Date.now()
        };
    },

    /**
     * BRIDGE: Execute on Python Core Backend
     */
    async executeRemote(query: string, metadata: any = {}): Promise<OrchestrateResponse> {
        const response = await fetch('http://localhost:8005/api/orchestrate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer AUDIT_MODE_TOKEN`
            },
            body: JSON.stringify({ query, metadata })
        });
        if (!response.ok) throw new Error(`Backend error: ${response.statusText}`);
        return response.json();
    },

    async uploadFile(file: File): Promise<any> {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('http://localhost:8005/api/ingest/upload', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer AUDIT_MODE_TOKEN`
            },
            // Note: browser sets boundary automatically for FormData
            body: formData
        });
        if (!response.ok) throw new Error(`Upload error: ${response.statusText}`);
        return response.json();
    },

    async queryRag(query: string, payload: any = {}) {
        return await ReliabilityOrchestrator.getInstance().execute('ai_inference', { query, ...payload });
    },

    async runExpert(query: string) {
        return await MoERouter.getInstance().process(query);
    },

    async orchestrate(action: string, payload: any = {}) {
        // Ensure action exists or default to ai_inference if payload suggests a query
        const targetAction = (action === 'chatbot' || !action) ? 'ai_inference' : action;
        const targetPayload = (typeof payload === 'string') ? { query: payload } : payload;

        return await ReliabilityOrchestrator.getInstance().execute(targetAction, targetPayload);
    },

    /**
     * Optimistic Execution (Pillar 7: Latency Masking)
     * Returns immediate optimistic result if available, processes real work async.
     */
    async optimisticExecute<T, R>(
        action: string,
        payload: T,
        onResult: (res: R) => void
    ): Promise<R | null> {
        // 1. Try to get an optimistic/cached result immediately
        const orchestrator = ReliabilityOrchestrator.getInstance();

        // This is a "dry run" or fast-lookup that Pillar 7 requires
        // We'll use the orchestrator's LKG (Last-Known-Good) as the optimistic response
        const optimisticResult = (orchestrator as any).lkgData?.get(action);

        if (optimisticResult) {
            console.log(`[Pillar 7] Serving optimistic response for ${action}`);
            // Return immediate response but keep processing
            setTimeout(async () => {
                const realResult = await orchestrator.execute<T, R>(action, payload);
                onResult(realResult);
            }, 0);
            return optimisticResult;
        }

        // 2. If no optimistic result, run normally
        const result = await orchestrator.execute<T, R>(action, payload);
        onResult(result);
        return result;
    }
};
