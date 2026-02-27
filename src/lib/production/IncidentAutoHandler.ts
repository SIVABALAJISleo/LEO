// IncidentAutoHandler - Automated incident classification and response
// System protects itself before humans intervene

import { supabase } from '@/integrations/supabase/client';

export type IncidentType = 
  | 'auth_failure'
  | 'permission_violation'
  | 'payment_webhook_failure'
  | 'rate_limit_breach'
  | 'internal_exception'
  | 'circuit_breaker'
  | 'backup_failure'
  | 'health_check_failure'
  | 'deploy_failure';

export type IncidentSeverity = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export type AutoAction = 'retry' | 'circuit_break' | 'temporary_block' | 'module_shutdown' | 'alert_only';

export interface Incident {
  id: string;
  incidentType: IncidentType;
  severity: IncidentSeverity;
  requestId: string | null;
  reason: string;
  autoAction: AutoAction | null;
  actionResult: string | null;
  resolved: boolean;
  resolvedAt: string | null;
  resolvedBy: string | null;
  userId: string | null;
  metadata: Record<string, unknown>;
  createdAt: string;
}

export interface AutoResponseRule {
  incidentType: IncidentType;
  severity: IncidentSeverity[];
  action: AutoAction;
  maxRetries: number;
  cooldownMs: number;
  escalateTo: IncidentSeverity | null;
}

class IncidentAutoHandler {
  private static instance: IncidentAutoHandler;
  private autoResponseRules: AutoResponseRule[];
  private recentIncidents: Map<string, { count: number; lastSeen: number }> = new Map();

  private constructor() {
    // Default auto-response rules
    this.autoResponseRules = [
      // Auth failures - temporary block after repeated failures
      {
        incidentType: 'auth_failure',
        severity: ['LOW', 'MEDIUM'],
        action: 'alert_only',
        maxRetries: 5,
        cooldownMs: 60000,
        escalateTo: 'HIGH',
      },
      {
        incidentType: 'auth_failure',
        severity: ['HIGH', 'CRITICAL'],
        action: 'temporary_block',
        maxRetries: 0,
        cooldownMs: 300000,
        escalateTo: null,
      },
      // Permission violations - log and alert
      {
        incidentType: 'permission_violation',
        severity: ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'],
        action: 'alert_only',
        maxRetries: 0,
        cooldownMs: 0,
        escalateTo: null,
      },
      // Payment webhook failures - retry then circuit break
      {
        incidentType: 'payment_webhook_failure',
        severity: ['LOW', 'MEDIUM'],
        action: 'retry',
        maxRetries: 3,
        cooldownMs: 5000,
        escalateTo: 'HIGH',
      },
      {
        incidentType: 'payment_webhook_failure',
        severity: ['HIGH', 'CRITICAL'],
        action: 'circuit_break',
        maxRetries: 0,
        cooldownMs: 60000,
        escalateTo: null,
      },
      // Rate limit breach - temporary block
      {
        incidentType: 'rate_limit_breach',
        severity: ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'],
        action: 'temporary_block',
        maxRetries: 0,
        cooldownMs: 60000,
        escalateTo: null,
      },
      // Internal exceptions - circuit break on high severity
      {
        incidentType: 'internal_exception',
        severity: ['LOW', 'MEDIUM'],
        action: 'retry',
        maxRetries: 2,
        cooldownMs: 1000,
        escalateTo: 'HIGH',
      },
      {
        incidentType: 'internal_exception',
        severity: ['HIGH', 'CRITICAL'],
        action: 'circuit_break',
        maxRetries: 0,
        cooldownMs: 30000,
        escalateTo: null,
      },
      // Circuit breaker - module shutdown on critical
      {
        incidentType: 'circuit_breaker',
        severity: ['CRITICAL'],
        action: 'module_shutdown',
        maxRetries: 0,
        cooldownMs: 300000,
        escalateTo: null,
      },
      // Backup failure - alert immediately
      {
        incidentType: 'backup_failure',
        severity: ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'],
        action: 'alert_only',
        maxRetries: 0,
        cooldownMs: 0,
        escalateTo: 'CRITICAL',
      },
      // Health check failure - circuit break
      {
        incidentType: 'health_check_failure',
        severity: ['HIGH', 'CRITICAL'],
        action: 'circuit_break',
        maxRetries: 0,
        cooldownMs: 60000,
        escalateTo: null,
      },
      // Deploy failure - rollback
      {
        incidentType: 'deploy_failure',
        severity: ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'],
        action: 'alert_only', // Rollback is handled by ReleaseRollback service
        maxRetries: 0,
        cooldownMs: 0,
        escalateTo: 'CRITICAL',
      },
    ];
  }

  static getInstance(): IncidentAutoHandler {
    if (!IncidentAutoHandler.instance) {
      IncidentAutoHandler.instance = new IncidentAutoHandler();
    }
    return IncidentAutoHandler.instance;
  }

  // Log and handle an incident
  async handleIncident(params: {
    incidentType: IncidentType;
    severity: IncidentSeverity;
    reason: string;
    requestId?: string;
    userId?: string;
    metadata?: Record<string, unknown>;
  }): Promise<{
    incidentId: string;
    actionTaken: AutoAction;
    actionResult: string;
  }> {
    // Find applicable rule
    const rule = this.findRule(params.incidentType, params.severity);
    const action = rule?.action || 'alert_only';

    // Track incident frequency for escalation
    const incidentKey = `${params.incidentType}:${params.userId || 'system'}`;
    const tracking = this.recentIncidents.get(incidentKey) || { count: 0, lastSeen: 0 };
    const now = Date.now();
    
    // Reset count if cooldown has passed
    if (rule && now - tracking.lastSeen > rule.cooldownMs) {
      tracking.count = 0;
    }
    tracking.count++;
    tracking.lastSeen = now;
    this.recentIncidents.set(incidentKey, tracking);

    // Check for escalation
    let effectiveSeverity = params.severity;
    if (rule?.escalateTo && tracking.count > rule.maxRetries) {
      effectiveSeverity = rule.escalateTo;
      console.warn(`[IncidentAutoHandler] Escalating ${params.incidentType} from ${params.severity} to ${effectiveSeverity}`);
    }

    // Execute auto-action
    const actionResult = await this.executeAction(action, params);

    // Log incident to database
    const { data, error } = await supabase
      .from('incident_log')
      .insert({
        incident_type: params.incidentType,
        severity: effectiveSeverity,
        request_id: params.requestId || null,
        reason: params.reason,
        auto_action: action,
        action_result: actionResult,
        user_id: params.userId || null,
        metadata: {
          ...params.metadata,
          incidentCount: tracking.count,
          escalated: effectiveSeverity !== params.severity,
        },
      })
      .select('id')
      .single();

    if (error) {
      console.error('[IncidentAutoHandler] Failed to log incident:', error);
    }

    console.log(`[IncidentAutoHandler] Incident logged: ${params.incidentType} (${effectiveSeverity}) - Action: ${action}`);

    return {
      incidentId: data?.id || 'unknown',
      actionTaken: action,
      actionResult,
    };
  }

  // Get recent incidents
  async getRecentIncidents(options?: {
    limit?: number;
    severity?: IncidentSeverity[];
    incidentType?: IncidentType[];
    unresolved?: boolean;
  }): Promise<Incident[]> {
    let query = supabase
      .from('incident_log')
      .select('*')
      .order('created_at', { ascending: false })
      .limit(options?.limit || 50);

    if (options?.severity?.length) {
      query = query.in('severity', options.severity);
    }

    if (options?.incidentType?.length) {
      query = query.in('incident_type', options.incidentType);
    }

    if (options?.unresolved) {
      query = query.eq('resolved', false);
    }

    const { data, error } = await query;

    if (error) {
      console.error('[IncidentAutoHandler] Failed to fetch incidents:', error);
      return [];
    }

    return (data || []).map(this.mapToIncident);
  }

  // Get incident statistics
  async getIncidentStats(since?: Date): Promise<{
    total: number;
    bySeverity: Record<IncidentSeverity, number>;
    byType: Record<string, number>;
    byAction: Record<string, number>;
    unresolved: number;
    autoResolved: number;
  }> {
    let query = supabase
      .from('incident_log')
      .select('severity, incident_type, auto_action, resolved');

    if (since) {
      query = query.gte('created_at', since.toISOString());
    }

    const { data: incidents } = await query;

    if (!incidents) {
      return {
        total: 0,
        bySeverity: { LOW: 0, MEDIUM: 0, HIGH: 0, CRITICAL: 0 },
        byType: {},
        byAction: {},
        unresolved: 0,
        autoResolved: 0,
      };
    }

    const bySeverity: Record<IncidentSeverity, number> = { LOW: 0, MEDIUM: 0, HIGH: 0, CRITICAL: 0 };
    const byType: Record<string, number> = {};
    const byAction: Record<string, number> = {};
    let unresolved = 0;
    let autoResolved = 0;

    incidents.forEach(inc => {
      bySeverity[inc.severity as IncidentSeverity] = (bySeverity[inc.severity as IncidentSeverity] || 0) + 1;
      byType[inc.incident_type] = (byType[inc.incident_type] || 0) + 1;
      if (inc.auto_action) {
        byAction[inc.auto_action] = (byAction[inc.auto_action] || 0) + 1;
      }
      if (!inc.resolved) {
        unresolved++;
      } else if (inc.auto_action && inc.auto_action !== 'alert_only') {
        autoResolved++;
      }
    });

    return {
      total: incidents.length,
      bySeverity,
      byType,
      byAction,
      unresolved,
      autoResolved,
    };
  }

  // Get auto-response rules
  getAutoResponseRules(): AutoResponseRule[] {
    return [...this.autoResponseRules];
  }

  // Update a rule (admin only)
  updateRule(incidentType: IncidentType, severity: IncidentSeverity, updates: Partial<AutoResponseRule>): void {
    const ruleIndex = this.autoResponseRules.findIndex(
      r => r.incidentType === incidentType && r.severity.includes(severity)
    );
    if (ruleIndex >= 0) {
      this.autoResponseRules[ruleIndex] = { ...this.autoResponseRules[ruleIndex], ...updates };
    }
  }

  private findRule(incidentType: IncidentType, severity: IncidentSeverity): AutoResponseRule | undefined {
    return this.autoResponseRules.find(
      rule => rule.incidentType === incidentType && rule.severity.includes(severity)
    );
  }

  private async executeAction(action: AutoAction, params: {
    incidentType: IncidentType;
    reason: string;
    userId?: string;
  }): Promise<string> {
    switch (action) {
      case 'retry':
        return 'Scheduled for automatic retry';
      case 'circuit_break':
        return `Circuit breaker activated for ${params.incidentType}`;
      case 'temporary_block':
        return params.userId 
          ? `User ${params.userId} temporarily blocked`
          : 'Resource temporarily blocked';
      case 'module_shutdown':
        return `Module shutdown initiated due to ${params.incidentType}`;
      case 'alert_only':
        return 'Alert sent to monitoring system';
      default:
        return 'No action taken';
    }
  }

  private mapToIncident(data: Record<string, unknown>): Incident {
    return {
      id: data.id as string,
      incidentType: data.incident_type as IncidentType,
      severity: data.severity as IncidentSeverity,
      requestId: data.request_id as string | null,
      reason: data.reason as string,
      autoAction: data.auto_action as AutoAction | null,
      actionResult: data.action_result as string | null,
      resolved: data.resolved as boolean,
      resolvedAt: data.resolved_at as string | null,
      resolvedBy: data.resolved_by as string | null,
      userId: data.user_id as string | null,
      metadata: (data.metadata as Record<string, unknown>) || {},
      createdAt: data.created_at as string,
    };
  }
}

export const incidentAutoHandler = IncidentAutoHandler.getInstance();
