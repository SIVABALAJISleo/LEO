import { SystemMetrics } from '../observability/SystemMetrics';

export enum QualityLevel {
    HIGH = 'HIGH',
    MEDIUM = 'MEDIUM',
    LOW = 'LOW'
}

export interface PerformanceConfig {
    enableCache: boolean;
    deferTasks: boolean;
    mediaQuality: 'high' | 'low';
    physicsFidelity: 'full' | 'simple';
    batchSize: number;
    modelSize: 'large' | 'small';
}

/**
 * PerformanceController (Pillar 9: Resource Awareness)
 * Detects system capability and adapts algorithm paths dynamically.
 */
export class PerformanceController {
    private static instance: PerformanceController;
    private metrics: SystemMetrics;
    private currentQuality: QualityLevel = QualityLevel.HIGH;

    // Detected Capabilities (Pillar 9)
    private capabilities = {
        hasCuda: false,
        ramGb: 8,
        isLowPower: false
    };

    private readonly DEGRADE_THRESHOLD = 200; // ms
    private readonly RECOVERY_THRESHOLD = 80;  // ms

    private constructor() {
        this.metrics = SystemMetrics.getInstance();
        this.detectRuntimeResources();
        this.startMonitoring();
    }

    static getInstance(): PerformanceController {
        if (!PerformanceController.instance) {
            PerformanceController.instance = new PerformanceController();
        }
        return PerformanceController.instance;
    }

    /**
     * Pillar 9: Sync with real backend hardware telemetry.
     */
    async syncWithBackend(): Promise<void> {
        try {
            const response = await fetch('/status');
            if (!response.ok) throw new Error('Status endpoint unreachable');
            const data = await response.json();

            this.capabilities.ramGb = data.hardware.total_gb;
            this.capabilities.isLowPower = data.hardware.cpu_load > 85;

            // Logical Adaptation (Pillar 9)
            if (this.capabilities.ramGb <= 4 || this.capabilities.isLowPower) {
                this.currentQuality = QualityLevel.LOW;
            } else if (this.capabilities.ramGb < 8) {
                this.currentQuality = QualityLevel.MEDIUM;
            } else {
                this.currentQuality = QualityLevel.HIGH;
            }

            console.log('[Pillar 9] Hardware Sync:', this.capabilities, 'Current Quality:', this.currentQuality);
        } catch (error) {
            console.error('Failed to sync hardware capabilities:', error);
            // Fallback to browser detection
            this.detectRuntimeResources();
        }
    }

    /**
     * Pillar 9: Detect RAM and power state at runtime.
     * Note: Full hardware access is limited in browser; we use available hints.
     */
    private detectRuntimeResources() {
        if ('deviceMemory' in navigator) {
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            this.capabilities.ramGb = (navigator as any).deviceMemory || 8;
        }

        // Logical Adaptation
        if (this.capabilities.ramGb <= 4) {
            this.capabilities.isLowPower = true;
            this.currentQuality = QualityLevel.LOW;
        }

        console.log('[Pillar 9] Runtime Detected:', this.capabilities);
    }

    getQuality(): QualityLevel {
        return this.currentQuality;
    }

    /**
     * Pillar 9: Adapt model/batch size dynamically based on load.
     */
    getConfig(): PerformanceConfig {
        const base = {
            enableCache: true,
            deferTasks: this.currentQuality !== QualityLevel.HIGH,
            mediaQuality: this.currentQuality === QualityLevel.HIGH ? 'high' : 'low' as 'high' | 'low',
            physicsFidelity: this.currentQuality === QualityLevel.HIGH ? 'full' : 'simple' as 'full' | 'simple',
            batchSize: 1,
            modelSize: 'small' as 'large' | 'small'
        };

        if (this.currentQuality === QualityLevel.HIGH) {
            return { ...base, batchSize: 10, modelSize: 'large' };
        } else if (this.currentQuality === QualityLevel.MEDIUM) {
            return { ...base, batchSize: 5, modelSize: 'small' };
        } else {
            return { ...base, batchSize: 1, modelSize: 'small' };
        }
    }

    private startMonitoring() {
        setInterval(() => this.evaluatePerformance(), 5000);
    }

    private evaluatePerformance() {
        const latencies = this.metrics.getMetrics('response_time');
        if (latencies.length === 0) return;

        const recent = latencies.slice(-5);
        const avg = recent.reduce((sum, m) => sum + m.value, 0) / recent.length;

        if (avg > this.DEGRADE_THRESHOLD) {
            this.downgrade();
        } else if (avg < this.RECOVERY_THRESHOLD) {
            this.upgrade();
        }
    }

    private downgrade() {
        if (this.currentQuality === QualityLevel.HIGH) {
            this.currentQuality = QualityLevel.MEDIUM;
            console.warn('[PerfController] Dynamic Adaptation: MEDIUM (Load high)');
        } else if (this.currentQuality === QualityLevel.MEDIUM) {
            this.currentQuality = QualityLevel.LOW;
            console.warn('[PerfController] Dynamic Adaptation: LOW (Critical load)');
        }
    }

    private upgrade() {
        if (this.currentQuality === QualityLevel.LOW && !this.capabilities.isLowPower) {
            this.currentQuality = QualityLevel.MEDIUM;
            console.info('[PerfController] Dynamic Adaptation: MEDIUM (Recovery)');
        } else if (this.currentQuality === QualityLevel.MEDIUM && this.capabilities.ramGb > 6) {
            this.currentQuality = QualityLevel.HIGH;
            console.info('[PerfController] Dynamic Adaptation: HIGH (Resource headroom available)');
        }
    }
}
