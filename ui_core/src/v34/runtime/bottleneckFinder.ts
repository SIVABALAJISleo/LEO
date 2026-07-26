// LEO AI V34 — Bottleneck Finder
// Capabilities: Diagnoses RAM pressure, thread concurrency blocks, and cache page faults.

export interface SystemBottleneck {
  id: string;
  source: "RAM_SPEED" | "CACHE_FAULT" | "THREAD_BLOCK" | "XPU_CONGESTION" | "NONE";
  severity: "critical" | "warning" | "low";
  metricValue: string;
  remediationAction: string;
}

export class BottleneckFinder {
  findBottlenecks(
    cacheMissRatio: number,
    ramBandwidthGbSec: number,
    isThreadBlocked: boolean,
  ): SystemBottleneck[] {
    const list: SystemBottleneck[] = [];

    if (cacheMissRatio > 0.12) {
      list.push({
        id: "bn-cache-v34-01",
        source: "CACHE_FAULT",
        severity: "critical",
        metricValue: `Cache miss ratio at ${(cacheMissRatio * 100).toFixed(1)}%`,
        remediationAction:
          "Instruct cacheResidencyAnalyzer to force-evict cold weights and page-lock the active specialist.",
      });
    }

    if (ramBandwidthGbSec > 38.0) {
      list.push({
        id: "bn-ram-v34-01",
        source: "RAM_SPEED",
        severity: "warning",
        metricValue: `RAM read throughput saturated at ${ramBandwidthGbSec.toFixed(1)} GB/s`,
        remediationAction:
          "Switch model routing to INT4 adaptive precision to restrict memory bus load.",
      });
    }

    if (isThreadBlocked) {
      list.push({
        id: "bn-thread-v34-01",
        source: "THREAD_BLOCK",
        severity: "low",
        metricValue: "OpenMP threads scheduling bottleneck",
        remediationAction:
          "Reconfigure OMP_NUM_THREADS affinity options to isolate execution cores.",
      });
    }

    return list;
  }
}
