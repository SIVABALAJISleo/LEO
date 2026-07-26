// LEO AI V33 — Bottleneck Detector
// Capabilities: Highlight RAM bottlenecks, flag cache misses, detect PCIe transfer delays, and suggest resolution pathways.

export interface SystemBottleneck {
  id: string;
  source: "RAM_SPEED" | "CACHE_MISS_RATE" | "PCIE_TRANSFER" | "THERMAL_THROTTLING" | "NONE";
  severity: "critical" | "warning" | "low";
  metricValue: string;
  remediationAction: string;
}

export class BottleneckDetector {
  detectBottlenecks(
    cacheMissRatio: number,
    ramBandwidthGbSec: number,
    isPcieThrottled: boolean,
  ): SystemBottleneck[] {
    const list: SystemBottleneck[] = [];

    if (cacheMissRatio > 0.15) {
      list.push({
        id: "bn-cache-01",
        source: "CACHE_MISS_RATE",
        severity: "critical",
        metricValue: `Cache miss ratio at ${(cacheMissRatio * 100).toFixed(1)}%`,
        remediationAction:
          "Instruct cacheResidentInferenceEngine to force-evict cold weights and page-lock the active specialist.",
      });
    }

    if (ramBandwidthGbSec > 45.0) {
      list.push({
        id: "bn-ram-01",
        source: "RAM_SPEED",
        severity: "warning",
        metricValue: `RAM read throughput saturated at ${ramBandwidthGbSec.toFixed(1)} GB/s`,
        remediationAction:
          "Switch model routing to INT4 adaptive precision to restrict memory bus load.",
      });
    }

    if (isPcieThrottled) {
      list.push({
        id: "bn-pcie-01",
        source: "PCIE_TRANSFER",
        severity: "low",
        metricValue: "PCIE link throttling during MoE weight transfers",
        remediationAction:
          "Keep inactive experts in system RAM instead of writing/reading from disk storage.",
      });
    }

    return list;
  }
}
