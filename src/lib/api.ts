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

const BACKEND_URL = 'http://localhost:8005/api/v1';

/**
 * HYPER API Client
 * Unified production interface for the Project HYPER Backend.
 */
export const hyperClient = {
    async getHealth(): Promise<HealthStatus> {
        try {
            const response = await fetch(`${BACKEND_URL}/health`);
            if (response.ok) {
                const health = await response.json();
                return {
                    status: health.status === 'ok' ? 'healthy' : 'degraded',
                    engines_available: true,
                    timestamp: health.timestamp * 1000
                };
            }
        } catch (error) {
            console.error("Backend health probe failed.", error);
        }
        return { 
            status: 'degraded', 
            engines_available: false, 
            timestamp: Date.now() 
        };
    },

    async getStatus(): Promise<BackendStatus> {
        try {
            const response = await fetch(`${BACKEND_URL}/compute/telemetry`, {
                headers: { 'Authorization': `Bearer AUDIT_MODE_TOKEN` }
            });
            if (response.ok) {
                const telemetry = await response.json();
                return {
                    version: '1.0.0-PROD',
                    metrics: {
                        requests: 0,
                        errors: 0,
                        latency_avg: 0.12
                    },
                    hardware: {
                        cpu_load: telemetry.cpu.average_utilization,
                        memory_percent: telemetry.memory.percent_used,
                        disk_percent: 40,
                        memory_available_gb: telemetry.memory.total_gb - telemetry.memory.used_gb
                    },
                    server_time: Date.now() / 1000
                };
            }
        } catch (error) {
            console.error("Telemetry fetch failed.", error);
        }

        return {
            version: '1.0.0-PROD',
            metrics: { requests: 0, errors: 0, latency_avg: 0 },
            hardware: { cpu_load: 0, memory_percent: 0, disk_percent: 0, memory_available_gb: 0 },
            server_time: Date.now() / 1000
        };
    },

    /**
     * CORE: Execute on Python Backend (Orchestration)
     */
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    async executeRemote(query: string, metadata: any = {}): Promise<any> {
        const response = await fetch(`${BACKEND_URL}/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer AUDIT_MODE_TOKEN`
            },
            body: JSON.stringify({ 
                question: query, 
                workspace_id: metadata.workspace_id || "default" 
            })
        });
        if (!response.ok) {
            const err = await response.json().catch(() => ({ detail: response.statusText }));
            throw new Error(err.detail || `Backend error: ${response.statusText}`);
        }
        return response.json();
    },

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    async uploadFile(file: File): Promise<any> {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${BACKEND_URL}/documents`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer AUDIT_MODE_TOKEN`
            },
            body: formData
        });
        if (!response.ok) throw new Error(`Upload error: ${response.statusText}`);
        return response.json();
    },

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    async orchestrate(action: string, payload: any = {}) {
        const query = typeof payload === 'string' ? payload : (payload.query || action);
        return this.executeRemote(query);
    },

    async runExpert(query: string) {
        return this.executeRemote(query);
    },

    async queryRag(query: string, payload: any = {}) {
        return this.executeRemote(query, payload);
    },

    async optimisticExecute<T, R>(
        action: string,
        payload: T,
        onResult: (res: R) => void
    ): Promise<R | null> {
        try {
            const query = (payload as any).query || action;
            const result = await this.executeRemote(query);
            onResult(result as unknown as R);
            return result as unknown as R;
        } catch (error) {
            console.error("Optimistic execution failed", error);
            return null;
        }
    }
};
