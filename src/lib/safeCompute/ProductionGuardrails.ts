// ProductionGuardrails - Automated system protection
// System stops itself before humans are needed

export interface GuardrailConfig {
  // Rate limiting
  maxRequestsPerMinute: number;
  maxRequestsPerHour: number;
  
  // Job quotas
  maxConcurrentJobs: number;
  maxJobsPerDay: number;
  maxJobDurationMs: number;
  
  // Cost ceilings
  maxDailyCostUsd: number;
  maxMonthlyCostUsd: number;
  
  // Resource limits
  maxMemoryMb: number;
  maxCpuPercent: number;
  
  // Circuit breaker
  failureThreshold: number;
  recoveryTimeMs: number;
}

export interface GuardrailState {
  isHealthy: boolean;
  circuitBreakerOpen: boolean;
  currentLimits: {
    requestsThisMinute: number;
    requestsThisHour: number;
    concurrentJobs: number;
    jobsToday: number;
    dailyCostUsd: number;
    monthlyCostUsd: number;
  };
  violations: GuardrailViolation[];
  lastCheck: string;
}

export interface GuardrailViolation {
  id: string;
  timestamp: string;
  type: 'rate_limit' | 'job_quota' | 'cost_ceiling' | 'resource_limit' | 'circuit_breaker';
  metric: string;
  currentValue: number;
  limitValue: number;
  action: 'blocked' | 'throttled' | 'warned';
  message: string;
}

class ProductionGuardrails {
  private static instance: ProductionGuardrails;
  private config: GuardrailConfig;
  private state: GuardrailState;
  private requestTimestamps: number[] = [];
  private failureCount = 0;
  private circuitBreakerOpenedAt: number | null = null;
  private violations: GuardrailViolation[] = [];

  private constructor() {
    // Default production config
    this.config = {
      maxRequestsPerMinute: 60,
      maxRequestsPerHour: 1000,
      maxConcurrentJobs: 10,
      maxJobsPerDay: 500,
      maxJobDurationMs: 300000, // 5 minutes
      maxDailyCostUsd: 100,
      maxMonthlyCostUsd: 2000,
      maxMemoryMb: 4096,
      maxCpuPercent: 80,
      failureThreshold: 5,
      recoveryTimeMs: 60000, // 1 minute
    };

    this.state = {
      isHealthy: true,
      circuitBreakerOpen: false,
      currentLimits: {
        requestsThisMinute: 0,
        requestsThisHour: 0,
        concurrentJobs: 0,
        jobsToday: 0,
        dailyCostUsd: 0,
        monthlyCostUsd: 0,
      },
      violations: [],
      lastCheck: new Date().toISOString(),
    };
  }

  static getInstance(): ProductionGuardrails {
    if (!ProductionGuardrails.instance) {
      ProductionGuardrails.instance = new ProductionGuardrails();
    }
    return ProductionGuardrails.instance;
  }

  // Check if request is allowed
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  checkRequest(userId?: string): { allowed: boolean; reason?: string; violation?: GuardrailViolation } {
    const now = Date.now();

    // Check circuit breaker
    if (this.state.circuitBreakerOpen) {
      if (this.circuitBreakerOpenedAt && now - this.circuitBreakerOpenedAt > this.config.recoveryTimeMs) {
        this.closeCircuitBreaker();
      } else {
        const violation = this.createViolation('circuit_breaker', 'circuit_state', 1, 0, 'blocked');
        return { allowed: false, reason: 'Circuit breaker open', violation };
      }
    }

    // Clean old timestamps
    const oneMinuteAgo = now - 60000;
    const oneHourAgo = now - 3600000;
    this.requestTimestamps = this.requestTimestamps.filter(t => t > oneHourAgo);

    // Count recent requests
    const requestsThisMinute = this.requestTimestamps.filter(t => t > oneMinuteAgo).length;
    const requestsThisHour = this.requestTimestamps.length;

    // Rate limit check
    if (requestsThisMinute >= this.config.maxRequestsPerMinute) {
      const violation = this.createViolation(
        'rate_limit', 
        'requests_per_minute', 
        requestsThisMinute, 
        this.config.maxRequestsPerMinute, 
        'blocked'
      );
      this.violations.push(violation);
      return { allowed: false, reason: 'Rate limit exceeded (per minute)', violation };
    }

    if (requestsThisHour >= this.config.maxRequestsPerHour) {
      const violation = this.createViolation(
        'rate_limit', 
        'requests_per_hour', 
        requestsThisHour, 
        this.config.maxRequestsPerHour, 
        'blocked'
      );
      this.violations.push(violation);
      return { allowed: false, reason: 'Rate limit exceeded (per hour)', violation };
    }

    // Record request
    this.requestTimestamps.push(now);
    this.state.currentLimits.requestsThisMinute = requestsThisMinute + 1;
    this.state.currentLimits.requestsThisHour = requestsThisHour + 1;

    return { allowed: true };
  }

  // Check if job can be started
  checkJobStart(): { allowed: boolean; reason?: string; violation?: GuardrailViolation } {
    if (this.state.currentLimits.concurrentJobs >= this.config.maxConcurrentJobs) {
      const violation = this.createViolation(
        'job_quota',
        'concurrent_jobs',
        this.state.currentLimits.concurrentJobs,
        this.config.maxConcurrentJobs,
        'blocked'
      );
      this.violations.push(violation);
      return { allowed: false, reason: 'Max concurrent jobs reached', violation };
    }

    if (this.state.currentLimits.jobsToday >= this.config.maxJobsPerDay) {
      const violation = this.createViolation(
        'job_quota',
        'jobs_per_day',
        this.state.currentLimits.jobsToday,
        this.config.maxJobsPerDay,
        'blocked'
      );
      this.violations.push(violation);
      return { allowed: false, reason: 'Daily job limit reached', violation };
    }

    this.state.currentLimits.concurrentJobs++;
    this.state.currentLimits.jobsToday++;
    return { allowed: true };
  }

  // Record job completion
  recordJobComplete(): void {
    this.state.currentLimits.concurrentJobs = Math.max(0, this.state.currentLimits.concurrentJobs - 1);
  }

  // Check cost ceiling
  checkCost(additionalCostUsd: number): { allowed: boolean; reason?: string; violation?: GuardrailViolation } {
    const projectedDaily = this.state.currentLimits.dailyCostUsd + additionalCostUsd;
    const projectedMonthly = this.state.currentLimits.monthlyCostUsd + additionalCostUsd;

    if (projectedDaily > this.config.maxDailyCostUsd) {
      const violation = this.createViolation(
        'cost_ceiling',
        'daily_cost_usd',
        projectedDaily,
        this.config.maxDailyCostUsd,
        'blocked'
      );
      this.violations.push(violation);
      return { allowed: false, reason: 'Daily cost ceiling reached', violation };
    }

    if (projectedMonthly > this.config.maxMonthlyCostUsd) {
      const violation = this.createViolation(
        'cost_ceiling',
        'monthly_cost_usd',
        projectedMonthly,
        this.config.maxMonthlyCostUsd,
        'blocked'
      );
      this.violations.push(violation);
      return { allowed: false, reason: 'Monthly cost ceiling reached', violation };
    }

    return { allowed: true };
  }

  // Record cost
  recordCost(costUsd: number): void {
    this.state.currentLimits.dailyCostUsd += costUsd;
    this.state.currentLimits.monthlyCostUsd += costUsd;
  }

  // Record failure (for circuit breaker)
  recordFailure(): void {
    this.failureCount++;
    if (this.failureCount >= this.config.failureThreshold) {
      this.openCircuitBreaker();
    }
  }

  // Record success (resets failure count)
  recordSuccess(): void {
    this.failureCount = 0;
  }

  private openCircuitBreaker(): void {
    this.state.circuitBreakerOpen = true;
    this.state.isHealthy = false;
    this.circuitBreakerOpenedAt = Date.now();
    const violation = this.createViolation(
      'circuit_breaker',
      'failure_count',
      this.failureCount,
      this.config.failureThreshold,
      'blocked'
    );
    this.violations.push(violation);
  }

  private closeCircuitBreaker(): void {
    this.state.circuitBreakerOpen = false;
    this.state.isHealthy = true;
    this.circuitBreakerOpenedAt = null;
    this.failureCount = 0;
  }

  private createViolation(
    type: GuardrailViolation['type'],
    metric: string,
    currentValue: number,
    limitValue: number,
    action: GuardrailViolation['action']
  ): GuardrailViolation {
    return {
      id: crypto.randomUUID(),
      timestamp: new Date().toISOString(),
      type,
      metric,
      currentValue,
      limitValue,
      action,
      message: `${type}: ${metric} (${currentValue}/${limitValue})`,
    };
  }

  // Get current state
  getState(): GuardrailState {
    this.state.lastCheck = new Date().toISOString();
    this.state.violations = this.violations.slice(-100); // Last 100 violations
    return { ...this.state };
  }

  // Get config
  getConfig(): GuardrailConfig {
    return { ...this.config };
  }

  // Update config (admin only)
  updateConfig(updates: Partial<GuardrailConfig>): void {
    this.config = { ...this.config, ...updates };
  }

  // Reset daily counters
  resetDailyCounters(): void {
    this.state.currentLimits.jobsToday = 0;
    this.state.currentLimits.dailyCostUsd = 0;
    this.state.currentLimits.requestsThisMinute = 0;
    this.state.currentLimits.requestsThisHour = 0;
  }

  // Reset monthly counters
  resetMonthlyCounters(): void {
    this.state.currentLimits.monthlyCostUsd = 0;
  }

  // Get violations for reporting
  getViolations(since?: Date): GuardrailViolation[] {
    if (since) {
      return this.violations.filter(v => new Date(v.timestamp) > since);
    }
    return [...this.violations];
  }

  // Clear violations (admin only)
  clearViolations(): void {
    this.violations = [];
  }
}

export const productionGuardrails = ProductionGuardrails.getInstance();
