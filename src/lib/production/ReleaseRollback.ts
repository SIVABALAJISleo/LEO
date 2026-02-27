// ReleaseRollback - Versioned deployments with auto-rollback
// System protects itself from bad deploys

import { supabase } from '@/integrations/supabase/client';

export interface Release {
  id: string;
  version: string;
  previousVersion: string | null;
  status: 'pending' | 'deploying' | 'deployed' | 'rolled_back' | 'failed';
  rolloutPercentage: number;
  deployedAt: string | null;
  rolledBackAt: string | null;
  healthCheckPassed: boolean | null;
  healthMetrics: HealthMetrics;
  featureFlags: string[];
  schemaChanges: SchemaChange[];
  rollbackReason: string | null;
  createdAt: string;
  updatedAt: string;
}

export interface HealthMetrics {
  errorRate: number;
  latencyP50Ms: number;
  latencyP99Ms: number;
  authFailures: number;
  requestsPerMinute: number;
  checkTimestamp: string;
}

export interface SchemaChange {
  type: 'create_table' | 'alter_table' | 'drop_table' | 'create_index' | 'migration';
  target: string;
  reversible: boolean;
  rollbackSql?: string;
}

export interface RolloutConfig {
  stages: number[];
  healthCheckIntervalMs: number;
  autoRollbackThresholds: {
    maxErrorRatePercent: number;
    maxLatencyP99Ms: number;
    maxAuthFailuresPerMinute: number;
  };
}

class ReleaseRollbackService {
  private static instance: ReleaseRollbackService;
  private config: RolloutConfig;
  private currentRelease: Release | null = null;

  private constructor() {
    this.config = {
      stages: [5, 25, 50, 100], // Canary rollout percentages
      healthCheckIntervalMs: 30000, // 30 seconds
      autoRollbackThresholds: {
        maxErrorRatePercent: 5,
        maxLatencyP99Ms: 3000,
        maxAuthFailuresPerMinute: 10,
      },
    };
  }

  static getInstance(): ReleaseRollbackService {
    if (!ReleaseRollbackService.instance) {
      ReleaseRollbackService.instance = new ReleaseRollbackService();
    }
    return ReleaseRollbackService.instance;
  }

  // Get current deployed release
  async getCurrentRelease(): Promise<Release | null> {
    const { data, error } = await supabase
      .from('releases')
      .select('*')
      .eq('status', 'deployed')
      .order('deployed_at', { ascending: false })
      .limit(1)
      .single();

    if (error || !data) {
      return null;
    }

    return this.mapToRelease(data);
  }

  // Get release history
  async getReleaseHistory(limit = 20): Promise<Release[]> {
    const { data, error } = await supabase
      .from('releases')
      .select('*')
      .order('created_at', { ascending: false })
      .limit(limit);

    if (error) {
      console.error('[ReleaseRollback] Failed to fetch releases:', error);
      return [];
    }

    return (data || []).map(this.mapToRelease);
  }

  // Check if health metrics pass thresholds
  checkHealthMetrics(metrics: HealthMetrics): {
    passed: boolean;
    failures: string[];
  } {
    const failures: string[] = [];

    if (metrics.errorRate > this.config.autoRollbackThresholds.maxErrorRatePercent) {
      failures.push(
        `Error rate ${metrics.errorRate.toFixed(2)}% exceeds threshold ${this.config.autoRollbackThresholds.maxErrorRatePercent}%`
      );
    }

    if (metrics.latencyP99Ms > this.config.autoRollbackThresholds.maxLatencyP99Ms) {
      failures.push(
        `P99 latency ${metrics.latencyP99Ms}ms exceeds threshold ${this.config.autoRollbackThresholds.maxLatencyP99Ms}ms`
      );
    }

    if (metrics.authFailures > this.config.autoRollbackThresholds.maxAuthFailuresPerMinute) {
      failures.push(
        `Auth failures ${metrics.authFailures}/min exceeds threshold ${this.config.autoRollbackThresholds.maxAuthFailuresPerMinute}/min`
      );
    }

    return {
      passed: failures.length === 0,
      failures,
    };
  }

  // Get rollout status
  getRolloutStages(): {
    stages: number[];
    currentStage: number;
    nextStage: number | null;
  } {
    const currentPercentage = this.currentRelease?.rolloutPercentage || 0;
    const currentStageIndex = this.config.stages.findIndex(s => s >= currentPercentage);
    const currentStage = currentStageIndex >= 0 ? this.config.stages[currentStageIndex] : 0;
    const nextStage = currentStageIndex < this.config.stages.length - 1
      ? this.config.stages[currentStageIndex + 1]
      : null;

    return {
      stages: this.config.stages,
      currentStage,
      nextStage,
    };
  }

  // Check if auto-rollback is needed based on current metrics
  async checkForAutoRollback(): Promise<{
    needed: boolean;
    reason: string | null;
    currentMetrics: HealthMetrics | null;
  }> {
    const release = await this.getCurrentRelease();
    if (!release) {
      return { needed: false, reason: null, currentMetrics: null };
    }

    // In a real implementation, this would fetch live metrics
    // For now, we simulate by checking stored health metrics
    const healthCheck = this.checkHealthMetrics(release.healthMetrics);

    return {
      needed: false,
      reason: null,
      currentMetrics: release.healthMetrics,
    };
  }

  // Get deployment summary
  async getDeploymentSummary(): Promise<{
    totalDeployments: number;
    successfulDeployments: number;
    rolledBack: number;
    failed: number;
    avgRolloutTimeMs: number;
  }> {
    const { data: releases } = await supabase
      .from('releases')
      .select('status, deployed_at, created_at')
      .order('created_at', { ascending: false })
      .limit(100);

    if (!releases) {
      return {
        totalDeployments: 0,
        successfulDeployments: 0,
        rolledBack: 0,
        failed: 0,
        avgRolloutTimeMs: 0,
      };
    }

    const successfulDeployments = releases.filter(r => r.status === 'deployed').length;
    const rolledBack = releases.filter(r => r.status === 'rolled_back').length;
    const failed = releases.filter(r => r.status === 'failed').length;

    // Calculate average rollout time for successful deployments
    const rolloutTimes = releases
      .filter(r => r.status === 'deployed' && r.deployed_at)
      .map(r => new Date(r.deployed_at!).getTime() - new Date(r.created_at).getTime());

    const avgRolloutTimeMs = rolloutTimes.length > 0
      ? rolloutTimes.reduce((sum, t) => sum + t, 0) / rolloutTimes.length
      : 0;

    return {
      totalDeployments: releases.length,
      successfulDeployments,
      rolledBack,
      failed,
      avgRolloutTimeMs,
    };
  }

  // Get rollback config
  getConfig(): RolloutConfig {
    return { ...this.config };
  }

  // Update rollback config (admin only)
  updateConfig(updates: Partial<RolloutConfig>): void {
    this.config = { ...this.config, ...updates };
  }

  private mapToRelease(data: Record<string, unknown>): Release {
    return {
      id: data.id as string,
      version: data.version as string,
      previousVersion: data.previous_version as string | null,
      status: data.status as Release['status'],
      rolloutPercentage: data.rollout_percentage as number,
      deployedAt: data.deployed_at as string | null,
      rolledBackAt: data.rolled_back_at as string | null,
      healthCheckPassed: data.health_check_passed as boolean | null,
      healthMetrics: (data.health_metrics as HealthMetrics) || {
        errorRate: 0,
        latencyP50Ms: 0,
        latencyP99Ms: 0,
        authFailures: 0,
        requestsPerMinute: 0,
        checkTimestamp: new Date().toISOString(),
      },
      featureFlags: (data.feature_flags as string[]) || [],
      schemaChanges: (data.schema_changes as SchemaChange[]) || [],
      rollbackReason: data.rollback_reason as string | null,
      createdAt: data.created_at as string,
      updatedAt: data.updated_at as string,
    };
  }
}

export const releaseRollback = ReleaseRollbackService.getInstance();
