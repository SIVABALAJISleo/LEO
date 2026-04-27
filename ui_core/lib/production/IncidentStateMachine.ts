// IncidentStateMachine - Automated incident classification and response
// System auto-classifies and responds without human intervention

export type IncidentState = 'NORMAL' | 'DEGRADED' | 'LIMITED' | 'LOCKDOWN';

export interface IncidentContext {
  state: IncidentState;
  triggeredAt: string | null;
  triggeredBy: string | null;
  autoDisabledFeatures: string[];
  activeAlerts: number;
  errorRate: number;
  latencyP99Ms: number;
  failedJobs24h: number;
  lastStateChange: string;
}

export interface IncidentThresholds {
  degraded: {
    errorRatePercent: number;
    latencyP99Ms: number;
    failedJobsPercent: number;
  };
  limited: {
    errorRatePercent: number;
    latencyP99Ms: number;
    failedJobsPercent: number;
  };
  lockdown: {
    errorRatePercent: number;
    latencyP99Ms: number;
    failedJobsPercent: number;
  };
}

export interface IncidentTransition {
  id: string;
  timestamp: string;
  fromState: IncidentState;
  toState: IncidentState;
  reason: string;
  triggeredBy: 'auto' | 'manual';
  metadata: Record<string, unknown>;
}

class IncidentStateMachine {
  private static instance: IncidentStateMachine;
  private context: IncidentContext;
  private thresholds: IncidentThresholds;
  private transitions: IncidentTransition[] = [];
  private featureFlagsToDisable: Map<IncidentState, string[]>;

  private constructor() {
    this.context = {
      state: 'NORMAL',
      triggeredAt: null,
      triggeredBy: null,
      autoDisabledFeatures: [],
      activeAlerts: 0,
      errorRate: 0,
      latencyP99Ms: 0,
      failedJobs24h: 0,
      lastStateChange: new Date().toISOString(),
    };

    this.thresholds = {
      degraded: {
        errorRatePercent: 5,
        latencyP99Ms: 2000,
        failedJobsPercent: 10,
      },
      limited: {
        errorRatePercent: 15,
        latencyP99Ms: 5000,
        failedJobsPercent: 25,
      },
      lockdown: {
        errorRatePercent: 50,
        latencyP99Ms: 10000,
        failedJobsPercent: 50,
      },
    };

    // Features to auto-disable at each state
    this.featureFlagsToDisable = new Map([
      ['DEGRADED', ['non_critical_jobs', 'batch_processing']],
      ['LIMITED', ['non_critical_jobs', 'batch_processing', 'new_registrations', 'heavy_inference']],
      ['LOCKDOWN', ['all_jobs', 'new_registrations', 'api_access', 'heavy_inference', 'batch_processing']],
    ]);
  }

  static getInstance(): IncidentStateMachine {
    if (!IncidentStateMachine.instance) {
      IncidentStateMachine.instance = new IncidentStateMachine();
    }
    return IncidentStateMachine.instance;
  }

  // Update metrics and auto-evaluate state
  updateMetrics(metrics: {
    errorRate: number;
    latencyP99Ms: number;
    failedJobs24h: number;
    totalJobs24h: number;
    activeAlerts: number;
  }): IncidentState {
    this.context.errorRate = metrics.errorRate;
    this.context.latencyP99Ms = metrics.latencyP99Ms;
    this.context.failedJobs24h = metrics.failedJobs24h;
    this.context.activeAlerts = metrics.activeAlerts;

    const failedJobsPercent = metrics.totalJobs24h > 0 
      ? (metrics.failedJobs24h / metrics.totalJobs24h) * 100 
      : 0;

    // Evaluate state based on thresholds
    const newState = this.evaluateState(metrics.errorRate, metrics.latencyP99Ms, failedJobsPercent);
    
    if (newState !== this.context.state) {
      this.transitionTo(newState, `Auto-triggered: errorRate=${metrics.errorRate}%, latency=${metrics.latencyP99Ms}ms, failedJobs=${failedJobsPercent.toFixed(1)}%`);
    }

    return this.context.state;
  }

  private evaluateState(errorRate: number, latencyP99Ms: number, failedJobsPercent: number): IncidentState {
    // Check LOCKDOWN first (most severe)
    if (
      errorRate >= this.thresholds.lockdown.errorRatePercent ||
      latencyP99Ms >= this.thresholds.lockdown.latencyP99Ms ||
      failedJobsPercent >= this.thresholds.lockdown.failedJobsPercent
    ) {
      return 'LOCKDOWN';
    }

    // Check LIMITED
    if (
      errorRate >= this.thresholds.limited.errorRatePercent ||
      latencyP99Ms >= this.thresholds.limited.latencyP99Ms ||
      failedJobsPercent >= this.thresholds.limited.failedJobsPercent
    ) {
      return 'LIMITED';
    }

    // Check DEGRADED
    if (
      errorRate >= this.thresholds.degraded.errorRatePercent ||
      latencyP99Ms >= this.thresholds.degraded.latencyP99Ms ||
      failedJobsPercent >= this.thresholds.degraded.failedJobsPercent
    ) {
      return 'DEGRADED';
    }

    return 'NORMAL';
  }

  private transitionTo(newState: IncidentState, reason: string): void {
    const transition: IncidentTransition = {
      id: crypto.randomUUID(),
      timestamp: new Date().toISOString(),
      fromState: this.context.state,
      toState: newState,
      reason,
      triggeredBy: 'auto',
      metadata: {
        errorRate: this.context.errorRate,
        latencyP99Ms: this.context.latencyP99Ms,
        failedJobs24h: this.context.failedJobs24h,
      },
    };

    this.transitions.push(transition);
    
    // Update context
    this.context.state = newState;
    this.context.lastStateChange = transition.timestamp;
    this.context.triggeredAt = transition.timestamp;
    this.context.triggeredBy = reason;

    // Auto-disable features
    this.context.autoDisabledFeatures = this.featureFlagsToDisable.get(newState) || [];

    console.log(`[IncidentStateMachine] State transition: ${transition.fromState} → ${transition.toState}. Reason: ${reason}`);
  }

  // Manual state override (admin only)
  manualTransition(newState: IncidentState, reason: string): void {
    const transition: IncidentTransition = {
      id: crypto.randomUUID(),
      timestamp: new Date().toISOString(),
      fromState: this.context.state,
      toState: newState,
      reason: `Manual: ${reason}`,
      triggeredBy: 'manual',
      metadata: {},
    };

    this.transitions.push(transition);
    this.context.state = newState;
    this.context.lastStateChange = transition.timestamp;
    this.context.autoDisabledFeatures = this.featureFlagsToDisable.get(newState) || [];
  }

  // Check if a feature is allowed in current state
  isFeatureAllowed(featureName: string): boolean {
    return !this.context.autoDisabledFeatures.includes(featureName);
  }

  // Get human-readable status for UI banner
  getStatusBanner(): { visible: boolean; severity: 'info' | 'warning' | 'error'; message: string } {
    switch (this.context.state) {
      case 'NORMAL':
        return { visible: false, severity: 'info', message: '' };
      case 'DEGRADED':
        return {
          visible: true,
          severity: 'warning',
          message: 'System experiencing degraded performance. Some features may be slower than usual.',
        };
      case 'LIMITED':
        return {
          visible: true,
          severity: 'warning',
          message: 'System operating in limited mode. Non-critical features temporarily disabled.',
        };
      case 'LOCKDOWN':
        return {
          visible: true,
          severity: 'error',
          message: 'System in emergency lockdown. Only essential operations available.',
        };
    }
  }

  // Get current context
  getContext(): IncidentContext {
    return { ...this.context };
  }

  // Get recent transitions
  getTransitions(limit = 50): IncidentTransition[] {
    return this.transitions.slice(-limit);
  }

  // Get thresholds
  getThresholds(): IncidentThresholds {
    return { ...this.thresholds };
  }

  // Update thresholds (admin only)
  updateThresholds(updates: Partial<IncidentThresholds>): void {
    this.thresholds = { ...this.thresholds, ...updates };
  }
}

export const incidentStateMachine = IncidentStateMachine.getInstance();
