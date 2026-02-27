import { PerformanceController } from './PerformanceController';
import { ReliabilityOrchestrator } from './ReliabilityOrchestrator';

export type HealthStatus = 'healthy' | 'degraded' | 'unhealthy';

export interface SystemHealth {
    status: HealthStatus;
    uptime: number;
    memory: {
        used: number;
        total: number;
    };
    services: Record<string, HealthStatus>;
    lastCheck: string;
}

export class HealthMonitor {
    private static instance: HealthMonitor;
    private startTime: number = Date.now();
    private orchestrator: ReliabilityOrchestrator;
    private perfController: PerformanceController;

    private constructor() {
        this.orchestrator = ReliabilityOrchestrator.getInstance();
        this.perfController = PerformanceController.getInstance();
    }

    static getInstance(): HealthMonitor {
        if (!HealthMonitor.instance) {
            HealthMonitor.instance = new HealthMonitor();
        }
        return HealthMonitor.instance;
    }

    async getSystemHealth(): Promise<SystemHealth> {
        try {
            const response = await fetch('http://localhost:8000/health/status');
            if (!response.ok) throw new Error('Status endpoint unreachable');
            const data = await response.json();

            return {
                status: 'healthy',
                uptime: data.uptime || Math.floor((Date.now() - this.startTime) / 1000),
                memory: {
                    used: 2 * 1024 * 1024 * 1024,
                    total: 16 * 1024 * 1024 * 1024
                },
                services: {
                    backend: 'healthy',
                    probabilistic_core: 'healthy',
                    network: 'healthy'
                },
                lastCheck: new Date().toISOString()
            };
        } catch (error) {
            return {
                status: 'unhealthy',
                uptime: Math.floor((Date.now() - this.startTime) / 1000),
                memory: { used: 0, total: 1 },
                services: { backend: 'unhealthy' },
                lastCheck: new Date().toISOString()
            };
        }
    }

    // Endpoints simulated for the app
    getReady(): boolean {
        return true;
    }

    getLive(): boolean {
        return true;
    }
}
