import { SystemMetrics } from "./SystemMetrics";
import ReliabilityOrchestrator from "../core/ReliabilityOrchestrator";

export class DashboardReport {
  private static instance: DashboardReport;
  private metrics: SystemMetrics;
  private orchestrator: ReliabilityOrchestrator;

  private constructor() {
    this.metrics = SystemMetrics.getInstance();
    this.orchestrator = ReliabilityOrchestrator.getInstance();
  }

  static getInstance(): DashboardReport {
    if (!DashboardReport.instance) {
      DashboardReport.instance = new DashboardReport();
    }
    return DashboardReport.instance;
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  generateReport(): any {
    const metricsSummary = this.metrics.getSummary();
    const auditLog = this.orchestrator.getAuditLog(10); // Last 10 entries

    return {
      timestamp: new Date().toISOString(),
      system_health: {
        status: "operational", // Could derive from metrics
        uptime_seconds: process.uptime ? process.uptime() : 0,
      },
      performance: {
        metrics: metricsSummary,
      },
      recent_activity: auditLog.map((entry) => ({
        action: entry.actionType,
        result: entry.result,
        duration_ms: entry.durationMs.toFixed(2),
      })),
      components: {
        intelligence: "active",
        optimization: "active",
        media: "active",
      },
    };
  }
}
