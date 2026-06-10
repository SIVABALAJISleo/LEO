/**
 * Phase 15: Enterprise Hardening
 * Path: ui_core/src/enterprise/hardening.ts
 * Purpose: Simulates enterprise integrations including OpenTelemetry logging, Sentry error monitoring, rollback operations, and PagerDuty triggers.
 */

export interface TelemetryEvent {
  eventId: string;
  name: string;
  payload: string;
  severity: "info" | "warning" | "error" | "critical";
  timestamp: number;
}

export interface RollbackAction {
  targetVersion: string;
  activeRollbackTriggered: boolean;
  canaryWeightSet: number;
  reason: string;
}

export class HardeningTelemetry {
  private eventsLog: TelemetryEvent[] = [];
  private canaryWeight = 100;

  /**
   * Log OpenTelemetry spans.
   */
  public logTelemetry(name: string, payload: any, severity: "info" | "warning" | "error" | "critical" = "info"): TelemetryEvent {
    const event: TelemetryEvent = {
      eventId: "OTel-event-" + Math.floor(Math.random() * 10000),
      name,
      payload: JSON.stringify(payload),
      severity,
      timestamp: Date.now()
    };

    this.eventsLog.push(event);

    // If critical severity event, log to simulated Sentry and trigger PagerDuty alerts
    if (severity === "critical" || severity === "error") {
      this.triggerSentryAlert(event);
      this.triggerPagerDutyAlert(event);
    }

    return event;
  }

  /**
   * Simulates Sentry captureException.
   */
  private triggerSentryAlert(event: TelemetryEvent): void {
    console.error(`[SENTRY ERROR PORTAL] Captured Exception Event: ${event.eventId} - Name: ${event.name}.`);
  }

  /**
   * Simulates PagerDuty Incident triggers.
   */
  private triggerPagerDutyAlert(event: TelemetryEvent): string {
    const pdIncidentId = "PD-incident-" + Math.floor(Math.random() * 100000);
    console.warn(`[PAGERDUTY ALARM] Alerting SRE queue! Incident: ${pdIncidentId}. Severity: ${event.severity.toUpperCase()}. Details: ${event.name}`);
    return pdIncidentId;
  }

  /**
   * Handles rollback execution when system health drops below checks.
   */
  public executeRollback(version: string, reason: string): RollbackAction {
    this.canaryWeight = 0; // Immediately dump canary weight to isolate release
    this.logTelemetry("Canary Rollback Executed", { targetVersion: version, reason }, "critical");
    
    return {
      targetVersion: version,
      activeRollbackTriggered: true,
      canaryWeightSet: this.canaryWeight,
      reason
    };
  }

  public getEventsLog(): TelemetryEvent[] {
    return this.eventsLog;
  }

  public getCanaryWeight(): number {
    return this.canaryWeight;
  }

  public resetCanaryWeight(weight = 100): void {
    this.canaryWeight = weight;
  }
}

export interface IncidentAlertV16 {
  incidentId: string;
  source: string;
  canaryWeightSnapshot: number;
  triggeredRollback: boolean;
  resolved: boolean;
}

export class HardeningTelemetryV16 extends HardeningTelemetry {
  private alertsLog: IncidentAlertV16[] = [];

  public logV16Event(name: string, payload: any, severity: TelemetryEvent["severity"]): TelemetryEvent {
    const event = this.logTelemetry(name, payload, severity);
    if (severity === "critical") {
      const alert: IncidentAlertV16 = {
        incidentId: "PD-V16-incident-" + Math.floor(Math.random() * 10000),
        source: "V16 Substrate Governor",
        canaryWeightSnapshot: this.getCanaryWeight(),
        triggeredRollback: false,
        resolved: false
      };
      this.alertsLog.push(alert);
    }
    return event;
  }

  public triggerV16Rollback(reason: string): RollbackAction {
    const alert: IncidentAlertV16 = {
      incidentId: "PD-V16-incident-" + Math.floor(Math.random() * 10000),
      source: "V16 Substrate Governor",
      canaryWeightSnapshot: this.getCanaryWeight(),
      triggeredRollback: true,
      resolved: false
    };
    this.alertsLog.push(alert);

    const rollback = this.executeRollback("v16.0.0-rc1", reason);
    return rollback;
  }

  public getV16Alerts(): IncidentAlertV16[] {
    return this.alertsLog;
  }
}

