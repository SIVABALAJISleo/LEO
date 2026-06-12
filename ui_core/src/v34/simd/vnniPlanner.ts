// LEO AI V34 — VNNI Planner
// Capabilities: Plan VNNI instruction cycles, configure execution registers, and compute cycle savings.

export interface VnniPlan {
  vnniActive: boolean;
  cyclesPerDotProduct: number;
  opsThroughputMultiplier: number;
  expectedMemoryBandwidthSavedPct: number;
}

export class VnniPlanner {
  planQuantizedOperation(precision: "INT8" | "INT4" | "FP16"): VnniPlan {
    if (precision === "FP16") {
      return {
        vnniActive: false,
        cyclesPerDotProduct: 4,
        opsThroughputMultiplier: 1.0,
        expectedMemoryBandwidthSavedPct: 0.0
      };
    }

    const vnniActive = true;
    const cyclesPerDotProduct = precision === "INT4" ? 1 : 2; // Intel VNNI accumulates 4x INT4 or 2x INT8 elements per cycle
    const opsThroughputMultiplier = precision === "INT4" ? 4.0 : 3.0;
    const expectedMemoryBandwidthSavedPct = precision === "INT4" ? 75.0 : 50.0;

    return {
      vnniActive,
      cyclesPerDotProduct,
      opsThroughputMultiplier,
      expectedMemoryBandwidthSavedPct
    };
  }
}
