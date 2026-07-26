// LEO AI V36 — Freshness Monitor
// Monitors aging cycles and decays confidence levels.

export class FreshnessMonitor {
  public calculateDecay(lastUpdated: number, baseConfidence: number): number {
    const deltaMs = Date.now() - lastUpdated;
    const daysElapsed = deltaMs / (1000 * 60 * 60 * 24);

    if (daysElapsed > 90) {
      return parseFloat((baseConfidence * 0.75).toFixed(3)); // Outdated
    }
    if (daysElapsed > 30) {
      return parseFloat((baseConfidence * 0.9).toFixed(3)); // Aging
    }
    return baseConfidence; // Fresh
  }
}
