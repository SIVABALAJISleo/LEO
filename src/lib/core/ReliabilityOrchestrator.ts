import { v4 as uuidv4 } from 'uuid';
import { PerformanceController } from './PerformanceController';
import { SemanticCache } from '../intelligence/SemanticCache';
import { ApproximationService } from '../optimization/ApproximationService';

type ActionHandler<T = any, R = any> = (payload: T) => Promise<R>;

type CircuitState = 'CLOSED' | 'OPEN' | 'HALF_OPEN';

interface ReliabilityConfig {
    maxRetries: number;
    timeoutMs: number;
    initialBackoffMs: number;
    enableCircuitBreaker: boolean;
    circuitThreshold: number;
    resetTimeoutMs: number;
    rateLimitCount: number;
    rateLimitWindowMs: number;
}

interface AuditEntry {
    id: string;
    timestamp: string;
    actionType: string;
    durationMs: number;
    result: 'success' | 'degraded' | 'failed' | 'rejected' | 'circuit-open' | 'cached' | 'approximated';
    attempts: number;
    error?: string;
    quality?: string;
}

/**
 * ReliabilityOrchestrator (Pillar 6: Failure-Survival Architecture)
 * Enforces a rigorous fallback chain: Cache -> Approximation -> Last-Known-Good -> Error.
 */
export class ReliabilityOrchestrator {
    private static instance: ReliabilityOrchestrator;
    private perfController!: PerformanceController;
    private semanticCache: SemanticCache;
    private approx: ApproximationService;

    private handlers = new Map<string, ActionHandler>();
    private lkgData = new Map<string, any>(); // Last-Known-Good storage
    private activeExecutions = new Map<string, AbortController>();
    private auditLog: AuditEntry[] = [];

    private circuitBreakers = new Map<string, { state: CircuitState, failures: number, lastFailure: number }>();
    private rateLimiters = new Map<string, { timestamps: number[] }>();

    private readonly MAX_AUDIT_LOG_SIZE = 1000;

    private defaultConfig: ReliabilityConfig = {
        maxRetries: 3,
        initialBackoffMs: 100,
        timeoutMs: 5000,
        enableCircuitBreaker: true,
        circuitThreshold: 5,
        resetTimeoutMs: 30000,
        rateLimitCount: 50,
        rateLimitWindowMs: 60000
    };

    private constructor() {
        this.perfController = PerformanceController.getInstance();
        this.semanticCache = SemanticCache.getInstance();
        this.approx = ApproximationService.getInstance();
    }

    static getInstance(): ReliabilityOrchestrator {
        if (!ReliabilityOrchestrator.instance) {
            ReliabilityOrchestrator.instance = new ReliabilityOrchestrator();
        }
        return ReliabilityOrchestrator.instance;
    }

    register<T, R>(actionType: string, handler: ActionHandler<T, R>): void {
        this.handlers.set(actionType, handler);
    }

    async execute<T, R>(
        actionType: string,
        payload: T,
        options?: Partial<ReliabilityConfig> & { queryVector?: number[], idempotencyKey?: string }
    ): Promise<R> {
        return this.executeWithTrace<T, R>(actionType, payload, options).then(res => res.result);
    }

    async executeWithTrace<T, R>(
        actionType: string,
        payload: T,
        options?: Partial<ReliabilityConfig> & { queryVector?: number[], idempotencyKey?: string }
    ): Promise<{ result: R, trace: any[] }> {
        const config = { ...this.defaultConfig, ...options };
        const startTime = performance.now();
        const key = options?.idempotencyKey ? `${actionType}:${options.idempotencyKey}` : null;

        // --- PILLAR 6 FALLBACK CHAIN START ---

        // 1. CACHE LAYER
        if (options?.queryVector) {
            const cached = await this.semanticCache.get(options.queryVector);
            if (cached) {
                this.logAudit(actionType, performance.now() - startTime, 'cached', 0);
                return { result: JSON.parse(cached) as R, trace: [] };
            }
        }

        // --- PRIMARY EXECUTION PATH ---

        // A. Rate Limiting Check
        if (this.isRateLimited(actionType, config)) {
            const finalResult = await this.handleFailureChain<T, R>(actionType, payload, startTime, new Error('Rate limit exceeded'));
            return { result: finalResult, trace: [] };
        }

        // B. Circuit Breaker Check
        if (config.enableCircuitBreaker && this.isCircuitOpen(actionType, config)) {
            const finalResult = await this.handleFailureChain<T, R>(actionType, payload, startTime, new Error('Circuit breaker is OPEN'));
            return { result: finalResult, trace: [] };
        }

        // C. Concurrency Control
        if (key) {
            if (this.activeExecutions.has(key)) {
                this.activeExecutions.get(key)?.abort();
            }
            const controller = new AbortController();
            this.activeExecutions.set(key, controller);
        }

        let attempts = 0;
        let lastError: unknown;

        for (let i = 0; i <= config.maxRetries; i++) {
            attempts++;
            try {
                const result = await this.runWithTimeout(
                    () => this.getHandler(actionType)(payload),
                    config.timeoutMs
                );

                this.onSuccess(actionType);
                if (key) this.activeExecutions.delete(key);

                // Store as Last-Known-Good
                this.lkgData.set(actionType, result);

                this.logAudit(actionType, performance.now() - startTime, 'success', attempts);
                return { result, trace: [] };
            } catch (error) {
                lastError = error;
                this.onFailure(actionType, config);
                if (i < config.maxRetries) {
                    await this.delay(config.initialBackoffMs * Math.pow(2, i));
                }
            }
        }

        if (key) this.activeExecutions.delete(key);

        // --- PILLAR 6 FAILURE CHAIN ---
        const finalResult = await this.handleFailureChain<T, R>(actionType, payload, startTime, lastError as Error);
        return { result: finalResult, trace: [] };
    }

    /**
     * Optimistic Execution: Returns a predicted result immediately,
     * then resolves with the actual server result later.
     */
    async optimisticExecute<T, R>(
        actionType: string,
        payload: T,
        predictor: (p: T) => R,
        onUpdate: (res: R, isOptimistic: boolean) => void
    ): Promise<void> {
        // 1. Emit optimistic result
        const predicted = predictor(payload);
        onUpdate(predicted, true);

        // 2. Perform real execution
        try {
            const actual = await this.execute<T, R>(actionType, payload);
            // 3. Reconcile
            onUpdate(actual, false);
        } catch (error) {
            console.error(`Optimistic reconciliation failed for ${actionType}`, error);
            // Optional: rollback to safe state or notify user
        }
    }

    private async handleFailureChain<T, R>(actionType: string, payload: T, startTime: number, lastError: Error): Promise<R> {
        // 2. APPROXIMATION LAYER (Pillar 6)
        if (typeof payload === 'number') {
            const approxValue = this.approx.estimate(payload as number);
            this.logAudit(actionType, performance.now() - startTime, 'approximated', 0, 'Used estimation');
            return approxValue as unknown as R;
        }

        // 3. LAST-KNOWN-GOOD (Pillar 6)
        const lkg = this.lkgData.get(actionType);
        if (lkg !== undefined) {
            this.logAudit(actionType, performance.now() - startTime, 'degraded', 0, 'Used LKG data');
            return lkg as R;
        }

        // 4. ERROR (Final stage)
        this.logAudit(actionType, performance.now() - startTime, 'failed', 1, String(lastError));
        throw lastError;
    }

    private isRateLimited(type: string, config: ReliabilityConfig): boolean {
        const now = Date.now();
        const limiter = this.rateLimiters.get(type) || { timestamps: [] };
        limiter.timestamps = limiter.timestamps.filter(t => now - t < config.rateLimitWindowMs);
        if (limiter.timestamps.length >= config.rateLimitCount) return true;
        limiter.timestamps.push(now);
        this.rateLimiters.set(type, limiter);
        return false;
    }

    private isCircuitOpen(type: string, config: ReliabilityConfig): boolean {
        const cb = this.circuitBreakers.get(type);
        if (!cb || cb.state === 'CLOSED') return false;
        if (cb.state === 'OPEN') {
            if (Date.now() - cb.lastFailure > config.resetTimeoutMs) {
                cb.state = 'HALF_OPEN';
                this.circuitBreakers.set(type, cb);
                return false;
            }
            return true;
        }
        return false;
    }

    private onSuccess(type: string) {
        const cb = this.circuitBreakers.get(type);
        if (cb && (cb.state === 'HALF_OPEN' || cb.failures > 0)) {
            this.circuitBreakers.set(type, { state: 'CLOSED', failures: 0, lastFailure: 0 });
        }
    }

    private onFailure(type: string, config: ReliabilityConfig) {
        const cb = this.circuitBreakers.get(type) || { state: 'CLOSED' as CircuitState, failures: 0, lastFailure: 0 };
        cb.failures++;
        cb.lastFailure = Date.now();
        if (cb.failures >= config.circuitThreshold) {
            cb.state = 'OPEN';
        }
        this.circuitBreakers.set(type, cb);
    }

    private getHandler(actionType: string): ActionHandler {
        const handler = this.handlers.get(actionType);
        if (!handler) {
            console.warn(`[Reliability] Unknown action type: ${actionType}. Falling back to ai_inference.`);
            const fallback = this.handlers.get('ai_inference');
            if (fallback) return fallback;
            throw new Error(`Unknown action type: ${actionType} and no fallback available.`);
        }
        return handler;
    }

    private runWithTimeout<T>(fn: () => Promise<T>, timeoutMs: number): Promise<T> {
        return Promise.race([
            fn(),
            new Promise<T>((_, reject) => setTimeout(() => reject(new Error('Operation timed out')), timeoutMs))
        ]);
    }

    private delay(ms: number): Promise<void> {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    private logAudit(type: string, dur: number, res: AuditEntry['result'], att: number, err?: string): void {
        this.auditLog.push({
            id: uuidv4(),
            timestamp: new Date().toISOString(),
            actionType: type,
            durationMs: dur,
            result: res,
            attempts: att,
            error: err,
            quality: this.perfController.getQuality()
        });
        if (this.auditLog.length > this.MAX_AUDIT_LOG_SIZE) this.auditLog.shift();
    }
}

export default ReliabilityOrchestrator;
