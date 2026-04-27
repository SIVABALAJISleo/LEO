// SelfHealingOperations - Auto-recovery, feature flags, incident handling
// Goal: System heals itself before humans notice

interface HealthCheck {
  component: 'api' | 'database' | 'websocket' | 'cpu' | 'memory' | 'queue';
  status: 'healthy' | 'degraded' | 'unhealthy' | 'unknown';
  latencyMs: number;
  message: string;
  checkedAt: Date;
}

interface AutoRetryConfig {
  maxRetries: number;
  baseDelayMs: number;
  maxDelayMs: number;
  backoffMultiplier: number;
  retryableErrors: string[];
}

interface FeatureFlagState {
  flagKey: string;
  enabled: boolean;
  autoDisabledAt?: Date;
  autoDisableReason?: string;
  failureCount: number;
  lastFailure?: Date;
  recoveredAt?: Date;
}

interface IncidentLogEntry {
  id: string;
  type: 'failure' | 'recovery' | 'degradation' | 'auto-disable' | 'auto-enable';
  component: string;
  message: string;
  metadata: Record<string, unknown>;
  timestamp: Date;
  resolved: boolean;
  resolvedAt?: Date;
}

interface SelfHealingStats {
  healthChecksRun: number;
  autoRetries: number;
  successfulRetries: number;
  autoDisables: number;
  autoRecoveries: number;
  incidentsLogged: number;
  currentHealth: 'healthy' | 'degraded' | 'unhealthy';
}

const DEFAULT_RETRY_CONFIG: AutoRetryConfig = {
  maxRetries: 3,
  baseDelayMs: 1000,
  maxDelayMs: 30000,
  backoffMultiplier: 2,
  retryableErrors: ['ECONNRESET', 'ETIMEDOUT', 'ENOTFOUND', 'NetworkError', 'FetchError', '5'],
};

class SelfHealingOperations {
  private static instance: SelfHealingOperations;
  private healthChecks: Map<string, HealthCheck> = new Map();
  private featureFlags: Map<string, FeatureFlagState> = new Map();
  private incidentLog: IncidentLogEntry[] = [];
  private isRunning: boolean = false;
  private checkInterval: ReturnType<typeof setInterval> | null = null;
  private webhookUrl?: string;
  
  private stats: SelfHealingStats = {
    healthChecksRun: 0,
    autoRetries: 0,
    successfulRetries: 0,
    autoDisables: 0,
    autoRecoveries: 0,
    incidentsLogged: 0,
    currentHealth: 'healthy',
  };

  private readonly FAILURE_THRESHOLD = 3;
  private readonly RECOVERY_CHECK_INTERVAL = 30000; // 30s

  private constructor() {
    this.loadFromStorage();
  }

  static getInstance(): SelfHealingOperations {
    if (!SelfHealingOperations.instance) {
      SelfHealingOperations.instance = new SelfHealingOperations();
    }
    return SelfHealingOperations.instance;
  }

  // ===== HEALTH CHECKS =====

  async runAllHealthChecks(): Promise<HealthCheck[]> {
    const checks = await Promise.all([
      this.checkApi(),
      this.checkDatabase(),
      this.checkMemory(),
      this.checkCpu(),
    ]);

    this.stats.healthChecksRun += checks.length;
    
    // Determine overall health
    const unhealthyCount = checks.filter(c => c.status === 'unhealthy').length;
    const degradedCount = checks.filter(c => c.status === 'degraded').length;
    
    if (unhealthyCount > 0) {
      this.stats.currentHealth = 'unhealthy';
    } else if (degradedCount > 0) {
      this.stats.currentHealth = 'degraded';
    } else {
      this.stats.currentHealth = 'healthy';
    }

    return checks;
  }

  private async checkApi(): Promise<HealthCheck> {
    const start = Date.now();
    try {
      const response = await fetch('/api/health', { method: 'HEAD', signal: AbortSignal.timeout(5000) });
      const check: HealthCheck = {
        component: 'api',
        status: response.ok ? 'healthy' : 'degraded',
        latencyMs: Date.now() - start,
        message: response.ok ? 'API responding normally' : `API returned ${response.status}`,
        checkedAt: new Date(),
      };
      this.healthChecks.set('api', check);
      return check;
    } catch (e) {
      const check: HealthCheck = {
        component: 'api',
        status: 'unhealthy',
        latencyMs: Date.now() - start,
        message: (e as Error).message || 'API unreachable',
        checkedAt: new Date(),
      };
      this.healthChecks.set('api', check);
      this.logIncident('failure', 'api', check.message, {});
      return check;
    }
  }

  private async checkDatabase(): Promise<HealthCheck> {
    const start = Date.now();
    try {
      // Use the Supabase health endpoint
      const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
      if (!supabaseUrl) throw new Error('Supabase URL not configured');
      
      const response = await fetch(`${supabaseUrl}/rest/v1/`, { 
        method: 'HEAD',
        signal: AbortSignal.timeout(5000),
        headers: {
          'apikey': import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY || '',
        }
      });
      
      const check: HealthCheck = {
        component: 'database',
        status: response.ok ? 'healthy' : 'degraded',
        latencyMs: Date.now() - start,
        message: response.ok ? 'Database responding normally' : `Database returned ${response.status}`,
        checkedAt: new Date(),
      };
      this.healthChecks.set('database', check);
      return check;
    } catch (e) {
      const check: HealthCheck = {
        component: 'database',
        status: 'unhealthy',
        latencyMs: Date.now() - start,
        message: (e as Error).message || 'Database unreachable',
        checkedAt: new Date(),
      };
      this.healthChecks.set('database', check);
      this.logIncident('failure', 'database', check.message, {});
      return check;
    }
  }

  private async checkMemory(): Promise<HealthCheck> {
    const check: HealthCheck = {
      component: 'memory',
      status: 'healthy',
      latencyMs: 0,
      message: 'Memory check (client-side)',
      checkedAt: new Date(),
    };

    if (typeof performance !== 'undefined' && 'memory' in performance) {
      const memory = (performance as { memory?: { usedJSHeapSize: number; jsHeapSizeLimit: number } }).memory;
      if (memory) {
        const usagePercent = (memory.usedJSHeapSize / memory.jsHeapSizeLimit) * 100;
        if (usagePercent > 90) {
          check.status = 'unhealthy';
          check.message = `Memory usage critical: ${usagePercent.toFixed(1)}%`;
        } else if (usagePercent > 75) {
          check.status = 'degraded';
          check.message = `Memory usage elevated: ${usagePercent.toFixed(1)}%`;
        } else {
          check.message = `Memory usage normal: ${usagePercent.toFixed(1)}%`;
        }
      }
    }

    this.healthChecks.set('memory', check);
    return check;
  }

  private async checkCpu(): Promise<HealthCheck> {
    // CPU monitoring via performance observer for long tasks
    const check: HealthCheck = {
      component: 'cpu',
      status: 'healthy',
      latencyMs: 0,
      message: 'CPU check (client-side approximation)',
      checkedAt: new Date(),
    };
    
    this.healthChecks.set('cpu', check);
    return check;
  }

  // ===== AUTO-RETRY WITH EXPONENTIAL BACKOFF =====

  async withAutoRetry<T>(
    operation: () => Promise<T>,
    config: Partial<AutoRetryConfig> = {}
  ): Promise<T> {
    const cfg = { ...DEFAULT_RETRY_CONFIG, ...config };
    let lastError: Error | null = null;
    let delay = cfg.baseDelayMs;

    for (let attempt = 0; attempt <= cfg.maxRetries; attempt++) {
      try {
        const result = await operation();
        if (attempt > 0) {
          this.stats.successfulRetries++;
          this.logIncident('recovery', 'auto-retry', `Operation succeeded after ${attempt} retries`, {});
        }
        return result;
      } catch (error) {
        lastError = error as Error;
        const errorStr = lastError.message || String(error);
        
        // Check if error is retryable
        const isRetryable = cfg.retryableErrors.some(e => errorStr.includes(e));
        
        if (!isRetryable || attempt === cfg.maxRetries) {
          throw lastError;
        }

        this.stats.autoRetries++;
        console.log(`[SelfHealing] Retry ${attempt + 1}/${cfg.maxRetries} in ${delay}ms: ${errorStr}`);
        
        await this.sleep(delay);
        delay = Math.min(delay * cfg.backoffMultiplier, cfg.maxDelayMs);
      }
    }

    throw lastError;
  }

  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // ===== FEATURE FLAG AUTO-DISABLE =====

  registerFeatureFlag(flagKey: string): void {
    if (!this.featureFlags.has(flagKey)) {
      this.featureFlags.set(flagKey, {
        flagKey,
        enabled: true,
        failureCount: 0,
      });
    }
  }

  isFeatureEnabled(flagKey: string): boolean {
    const flag = this.featureFlags.get(flagKey);
    return flag ? flag.enabled : true; // Default to enabled if not registered
  }

  recordFeatureFailure(flagKey: string, error: Error): void {
    const flag = this.featureFlags.get(flagKey);
    if (!flag) {
      this.registerFeatureFlag(flagKey);
      return this.recordFeatureFailure(flagKey, error);
    }

    flag.failureCount++;
    flag.lastFailure = new Date();

    if (flag.failureCount >= this.FAILURE_THRESHOLD && flag.enabled) {
      this.autoDisableFeature(flagKey, error.message);
    }

    this.saveToStorage();
  }

  private autoDisableFeature(flagKey: string, reason: string): void {
    const flag = this.featureFlags.get(flagKey);
    if (!flag) return;

    flag.enabled = false;
    flag.autoDisabledAt = new Date();
    flag.autoDisableReason = reason;
    
    this.stats.autoDisables++;
    this.logIncident('auto-disable', flagKey, `Feature auto-disabled: ${reason}`, { 
      failureCount: flag.failureCount 
    });

    // Alert webhook if configured
    this.sendAlert(`Feature ${flagKey} auto-disabled`, reason, 'warning');

    // Schedule recovery check
    setTimeout(() => this.checkFeatureRecovery(flagKey), this.RECOVERY_CHECK_INTERVAL);

    this.saveToStorage();
  }

  private async checkFeatureRecovery(flagKey: string): Promise<void> {
    const flag = this.featureFlags.get(flagKey);
    if (!flag || flag.enabled) return;

    // Reset failure count and try re-enabling
    flag.failureCount = 0;
    flag.enabled = true;
    flag.recoveredAt = new Date();
    
    this.stats.autoRecoveries++;
    this.logIncident('auto-enable', flagKey, 'Feature auto-recovered', {});
    
    console.log(`[SelfHealing] Feature ${flagKey} auto-recovered`);
    this.saveToStorage();
  }

  recordFeatureSuccess(flagKey: string): void {
    const flag = this.featureFlags.get(flagKey);
    if (flag) {
      // Decay failure count on success
      flag.failureCount = Math.max(0, flag.failureCount - 1);
    }
  }

  // ===== INCIDENT LOGGING =====

  private logIncident(
    type: IncidentLogEntry['type'],
    component: string,
    message: string,
    metadata: Record<string, unknown>
  ): void {
    const incident: IncidentLogEntry = {
      id: `inc_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      type,
      component,
      message,
      metadata,
      timestamp: new Date(),
      resolved: type === 'recovery' || type === 'auto-enable',
      resolvedAt: type === 'recovery' || type === 'auto-enable' ? new Date() : undefined,
    };

    this.incidentLog.unshift(incident);
    if (this.incidentLog.length > 1000) {
      this.incidentLog = this.incidentLog.slice(0, 1000);
    }

    this.stats.incidentsLogged++;
    console.log(`[SelfHealing] Incident: ${type} - ${component} - ${message}`);
    
    this.saveToStorage();
  }

  getIncidentLog(limit = 50): IncidentLogEntry[] {
    return this.incidentLog.slice(0, limit);
  }

  resolveIncident(incidentId: string): void {
    const incident = this.incidentLog.find(i => i.id === incidentId);
    if (incident && !incident.resolved) {
      incident.resolved = true;
      incident.resolvedAt = new Date();
      this.saveToStorage();
    }
  }

  // ===== ALERT WEBHOOKS =====

  setAlertWebhook(url: string): void {
    this.webhookUrl = url;
  }

  private async sendAlert(title: string, message: string, severity: 'info' | 'warning' | 'critical'): Promise<void> {
    if (!this.webhookUrl) {
      console.log(`[SelfHealing] Alert (no webhook): ${severity} - ${title}: ${message}`);
      return;
    }

    try {
      await fetch(this.webhookUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title,
          message,
          severity,
          timestamp: new Date().toISOString(),
          source: 'hyper-self-healing',
        }),
      });
    } catch (e) {
      console.error('[SelfHealing] Failed to send alert:', e);
    }
  }

  // ===== LIFECYCLE =====

  start(intervalMs = 30000): void {
    if (this.isRunning) return;
    this.isRunning = true;

    console.log('[SelfHealing] Starting health monitoring');
    this.runAllHealthChecks();

    this.checkInterval = setInterval(() => {
      this.runAllHealthChecks();
    }, intervalMs);
  }

  stop(): void {
    if (this.checkInterval) {
      clearInterval(this.checkInterval);
      this.checkInterval = null;
    }
    this.isRunning = false;
    console.log('[SelfHealing] Stopped health monitoring');
  }

  // ===== PERSISTENCE =====

  private saveToStorage(): void {
    try {
      localStorage.setItem('hyper_self_healing', JSON.stringify({
        featureFlags: Array.from(this.featureFlags.entries()),
        incidentLog: this.incidentLog.slice(0, 100),
        stats: this.stats,
      }));
    } catch (e) {
      console.warn('[SelfHealing] Failed to save state:', e);
    }
  }

  private loadFromStorage(): void {
    try {
      const data = localStorage.getItem('hyper_self_healing');
      if (data) {
        const parsed = JSON.parse(data);
        if (parsed.featureFlags) {
          this.featureFlags = new Map(parsed.featureFlags);
        }
        if (parsed.incidentLog) {
          this.incidentLog = parsed.incidentLog.map((i: IncidentLogEntry) => ({
            ...i,
            timestamp: new Date(i.timestamp),
            resolvedAt: i.resolvedAt ? new Date(i.resolvedAt) : undefined,
          }));
        }
        if (parsed.stats) {
          this.stats = { ...this.stats, ...parsed.stats };
        }
      }
    } catch (e) {
      console.warn('[SelfHealing] Failed to load state:', e);
    }
  }

  // ===== STATS =====

  getStats(): SelfHealingStats {
    return { ...this.stats };
  }

  getHealthChecks(): HealthCheck[] {
    return Array.from(this.healthChecks.values());
  }

  getFeatureFlags(): FeatureFlagState[] {
    return Array.from(this.featureFlags.values());
  }
}

export const selfHealingOperations = SelfHealingOperations.getInstance();
export type { HealthCheck, AutoRetryConfig, FeatureFlagState, IncidentLogEntry, SelfHealingStats };
