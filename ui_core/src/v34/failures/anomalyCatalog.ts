// LEO AI V34 — Anomaly Catalog
// Capabilities: Log unexpected telemetry values, index regression files, and record anomalies.

export interface AnomalyRecord {
  anomalyId: string;
  observedMetric: string;
  expectedValue: string;
  actualValue: string;
  timestamp: number;
}

export class AnomalyCatalog {
  private anomalies: AnomalyRecord[] = [];

  logAnomaly(metric: string, expected: string, actual: string): AnomalyRecord {
    const anomaly: AnomalyRecord = {
      anomalyId: `anom-v34-${Math.random().toString(36).substring(7)}`,
      observedMetric: metric,
      expectedValue: expected,
      actualValue: actual,
      timestamp: Date.now(),
    };
    this.anomalies.push(anomaly);
    return anomaly;
  }

  getAnomalies(): AnomalyRecord[] {
    return this.anomalies;
  }
}
