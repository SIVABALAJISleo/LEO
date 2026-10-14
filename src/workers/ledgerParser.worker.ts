/**
 * src/workers/ledgerParser.worker.ts
 * Web Worker for offloading large cryptographic certificate ledger parsing
 * and live computation-avoidance graph metrics calculation off the main UI thread.
 * Guarantees 60 FPS dashboard responsiveness during heavy background telemetry updates.
 */

export interface LedgerWorkerInput {
  rawLedgerData: any;
  filterDomain?: string;
}

export interface LedgerWorkerOutput {
  totalCertificates: number;
  verifiedCount: number;
  workEliminatedTotal: number;
  averageLatencyMs: number;
  domainBreakdown: Record<string, { count: number; passRate: number }>;
  processedAt: number;
}

self.onmessage = (event: MessageEvent<LedgerWorkerInput>) => {
  const { rawLedgerData, filterDomain } = event.data;

  try {
    const records = Array.isArray(rawLedgerData)
      ? rawLedgerData
      : (rawLedgerData?.certificates || rawLedgerData?.records || []);

    let total = 0;
    let verified = 0;
    let totalLatency = 0;
    let workEliminated = 0;
    const breakdown: Record<string, { count: number; passed: number }> = {};

    for (let i = 0; i < records.length; i++) {
      const rec = records[i];
      if (filterDomain && rec.domain && rec.domain !== filterDomain) {
        continue;
      }

      total++;
      const isPassed = rec.status === "PASS" || rec.verified === true;
      if (isPassed) {
        verified++;
      }

      totalLatency += Number(rec.latency_ms || rec.measured_latency_ms || 0);
      workEliminated += Number(rec.work_eliminated_pct || 0);

      const domain = rec.domain || rec.workload_family || "GENERAL";
      if (!breakdown[domain]) {
        breakdown[domain] = { count: 0, passed: 0 };
      }
      breakdown[domain].count++;
      if (isPassed) {
        breakdown[domain].passed++;
      }
    }

    const domainBreakdown: Record<string, { count: number; passRate: number }> = {};
    for (const [dom, stat] of Object.entries(breakdown)) {
      domainBreakdown[dom] = {
        count: stat.count,
        passRate: stat.count > 0 ? (stat.passed / stat.count) * 100 : 0,
      };
    }

    const result: LedgerWorkerOutput = {
      totalCertificates: total,
      verifiedCount: verified,
      workEliminatedTotal: total > 0 ? workEliminated / total : 0,
      averageLatencyMs: total > 0 ? totalLatency / total : 0,
      domainBreakdown,
      processedAt: Date.now(),
    };

    self.postMessage({ success: true, result });
  } catch (err: any) {
    self.postMessage({ success: false, error: err?.message || String(err) });
  }
};
