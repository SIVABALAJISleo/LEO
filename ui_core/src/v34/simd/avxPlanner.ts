// LEO AI V34 — AVX Planner
// Capabilities: Plan AVX2 vs AVX512 registers mapping, evaluate thread speedups, and schedule vector width loads.

export interface AvxAllocationPlan {
  instructionWidth: "AVX2" | "AVX512" | "Scalar";
  registerCountUsed: number;
  unrollFactor: number;
  estimatedThroughputGflops: number;
}

export class AvxPlanner {
  planFloatingPointLoad(arraySizeCount: number, hasAvx512: boolean): AvxAllocationPlan {
    let instructionWidth: "AVX2" | "AVX512" | "Scalar" = "Scalar";
    let registerCountUsed = 0;
    let unrollFactor = 1;
    let estimatedThroughputGflops = 1.2; // scalar speed baseline

    if (arraySizeCount < 16) {
      instructionWidth = "Scalar";
      registerCountUsed = 1;
      unrollFactor = 1;
      estimatedThroughputGflops = 1.5;
    } else if (hasAvx512) {
      instructionWidth = "AVX512";
      registerCountUsed = 32; // all 32 zmm registers
      unrollFactor = 4;
      estimatedThroughputGflops = 145.2;
    } else {
      instructionWidth = "AVX2";
      registerCountUsed = 16; // 16 ymm registers
      unrollFactor = 2;
      estimatedThroughputGflops = 62.4;
    }

    return {
      instructionWidth,
      registerCountUsed,
      unrollFactor,
      estimatedThroughputGflops
    };
  }
}
