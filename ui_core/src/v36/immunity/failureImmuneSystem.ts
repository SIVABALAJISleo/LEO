// LEO AI V36 — Failure Immune System
// Catalogs failures and triggers automatic vaccine regressions.

export interface AnomalyReport {
  id: string;
  moduleName: string;
  errorLog: string;
  severity: "critical" | "warning";
  timestamp: number;
}

export class FailureImmuneSystem {
  private log: AnomalyReport[] = [];

  public reportFailure(moduleName: string, errorLog: string, severity: AnomalyReport["severity"]): void {
    this.log.push({
      id: `err-${(100 + Math.random() * 900).toFixed(0)}`,
      moduleName,
      errorLog,
      severity,
      timestamp: Date.now()
    });
  }

  public getLoggedFailures(): AnomalyReport[] {
    return this.log;
  }
}
