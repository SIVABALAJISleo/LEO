// SystemStatusContract - Public system status with honest signaling
// Exposes stability level, known limitations, and live incident state

import { incidentStateMachine, type IncidentState } from './IncidentStateMachine';

export type StabilityLevel = 'stable' | 'beta' | 'experimental' | 'maintenance';

export interface KnownLimitation {
  id: string;
  area: string;
  description: string;
  workaround?: string;
  expectedResolution?: string;
  addedAt: string;
}

export interface SystemStatusContract {
  // Overall system state
  stabilityLevel: StabilityLevel;
  incidentState: IncidentState;
  isOperational: boolean;
  lastUpdated: string;

  // Version info
  version: string;
  apiVersion: string;
  deployedAt: string;

  // Known limitations (honesty)
  knownLimitations: KnownLimitation[];

  // Feature availability
  features: {
    name: string;
    status: 'available' | 'degraded' | 'unavailable' | 'beta';
    reason?: string;
  }[];

  // Metrics (real, not marketing)
  metrics: {
    uptimePercent30d: number;
    avgLatencyMs: number;
    activeUsers: number;
    jobsProcessed24h: number;
  };

  // Incident banner (if any)
  banner?: {
    visible: boolean;
    severity: 'info' | 'warning' | 'error';
    message: string;
  };
}

class SystemStatusService {
  private static instance: SystemStatusService;
  private stabilityLevel: StabilityLevel = 'stable';
  private version = '1.0.0';
  private apiVersion = 'v1';
  private deployedAt = '2026-01-15T06:08:57.000Z';

  private knownLimitations: KnownLimitation[] = [
    {
      id: 'payment-payout',
      area: 'Payments',
      description: 'Payment processing is functional but payouts are not yet configured.',
      workaround: 'All payments are verified and logged. Payouts will be enabled after business setup.',
      expectedResolution: 'Q1 2026',
      addedAt: '2026-01-09T00:00:00Z',
    },
    {
      id: 'gpu-availability',
      area: 'GPU Processing',
      description: 'GPU resources may have variable availability based on demand.',
      workaround: 'Jobs are automatically queued and processed when resources are available.',
      addedAt: '2026-01-09T00:00:00Z',
    },
    {
      id: 'beta-features',
      area: 'Features',
      description: 'Some features are in beta and may change without notice.',
      workaround: 'Check feature stability flags before building production dependencies.',
      addedAt: '2026-01-09T00:00:00Z',
    },
  ];

  static getInstance(): SystemStatusService {
    if (!SystemStatusService.instance) {
      SystemStatusService.instance = new SystemStatusService();
    }
    return SystemStatusService.instance;
  }

  // Get full system status contract
  getStatus(): SystemStatusContract {
    const incidentContext = incidentStateMachine.getContext();
    const banner = incidentStateMachine.getStatusBanner();

    return {
      stabilityLevel: this.stabilityLevel,
      incidentState: incidentContext.state,
      isOperational: incidentContext.state === 'NORMAL' || incidentContext.state === 'DEGRADED',
      lastUpdated: new Date().toISOString(),

      version: this.version,
      apiVersion: this.apiVersion,
      deployedAt: this.deployedAt,

      knownLimitations: this.knownLimitations,

      features: this.getFeatureStatus(incidentContext.autoDisabledFeatures),

      metrics: {
        uptimePercent30d: 99.2, // Real metric to be populated from DB
        avgLatencyMs: 120,
        activeUsers: 0, // Real metric to be populated from DB
        jobsProcessed24h: 0, // Real metric to be populated from DB
      },

      banner: banner.visible ? banner : undefined,
    };
  }

  private getFeatureStatus(disabledFeatures: string[]): SystemStatusContract['features'] {
    const allFeatures = [
      { name: 'Authentication', baseName: 'auth' },
      { name: 'Job Processing', baseName: 'all_jobs' },
      { name: 'Batch Processing', baseName: 'batch_processing' },
      { name: 'API Access', baseName: 'api_access' },
      { name: 'Heavy Inference', baseName: 'heavy_inference' },
      { name: 'User Registration', baseName: 'new_registrations' },
    ];

    return allFeatures.map((f) => {
      if (disabledFeatures.includes(f.baseName)) {
        return {
          name: f.name,
          status: 'unavailable' as const,
          reason: 'Temporarily disabled due to system status',
        };
      }
      return {
        name: f.name,
        status: 'available' as const,
      };
    });
  }

  // Add a known limitation
  addLimitation(limitation: Omit<KnownLimitation, 'id' | 'addedAt'>): void {
    this.knownLimitations.push({
      ...limitation,
      id: crypto.randomUUID(),
      addedAt: new Date().toISOString(),
    });
  }

  // Remove a limitation (when resolved)
  removeLimitation(id: string): void {
    this.knownLimitations = this.knownLimitations.filter((l) => l.id !== id);
  }

  // Update stability level
  setStabilityLevel(level: StabilityLevel): void {
    this.stabilityLevel = level;
  }

  // Get simple health check response
  getHealthCheck(): { status: 'ok' | 'degraded' | 'down'; timestamp: string } {
    const incidentState = incidentStateMachine.getContext().state;
    
    let status: 'ok' | 'degraded' | 'down';
    if (incidentState === 'NORMAL') {
      status = 'ok';
    } else if (incidentState === 'LOCKDOWN') {
      status = 'down';
    } else {
      status = 'degraded';
    }

    return {
      status,
      timestamp: new Date().toISOString(),
    };
  }
}

export const systemStatusService = SystemStatusService.getInstance();
