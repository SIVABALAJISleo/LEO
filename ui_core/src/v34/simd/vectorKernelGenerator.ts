// LEO AI V34 — Vector Kernel Generator
// Capabilities: Schedule instruction plan sequences, compile execution loops, and output the SIMD Utilization Score.

import { AvxPlanner } from "./avxPlanner";
import { VnniPlanner } from "./vnniPlanner";

export interface SimdInstructionPlan {
  timestamp: number;
  arraySize: number;
  scheduledInstructionSet: "AVX2" | "AVX512" | "VNNI" | "Scalar";
  estimatedThroughputGflops: number;
  simdUtilizationScore: number; // 0 to 100
  planLog: string;
}

export class VectorKernelGenerator {
  private avx = new AvxPlanner();
  private vnni = new VnniPlanner();

  generateOptimizationKernel(
    arraySize: number,
    isQuantized: boolean,
    precision: "INT8" | "INT4" | "FP16",
    hasAvx512 = false,
  ): SimdInstructionPlan {
    let scheduledInstructionSet: "AVX2" | "AVX512" | "VNNI" | "Scalar" = "Scalar";
    let estimatedThroughputGflops = 1.5;
    let simdUtilizationScore = 15;
    let planLog = "";

    if (isQuantized && (precision === "INT8" || precision === "INT4")) {
      scheduledInstructionSet = "VNNI";
      const plan = this.vnni.planQuantizedOperation(precision);
      estimatedThroughputGflops = 120.0 * plan.opsThroughputMultiplier;
      simdUtilizationScore = plan.expectedMemoryBandwidthSavedPct + 20; // scales with savings pct
      planLog = `VNNI optimized loop compiled. ${plan.opsThroughputMultiplier}x cycle reductions aligned.`;
    } else {
      const plan = this.avx.planFloatingPointLoad(arraySize, hasAvx512);
      scheduledInstructionSet = plan.instructionWidth;
      estimatedThroughputGflops = plan.estimatedThroughputGflops;
      simdUtilizationScore =
        plan.instructionWidth === "AVX512" ? 92.5 : plan.instructionWidth === "AVX2" ? 72.0 : 20.0;
      planLog = `AVX kernel aligned. Unroll factor: ${plan.unrollFactor}, registers: ${plan.registerCountUsed}.`;
    }

    return {
      timestamp: Date.now(),
      arraySize,
      scheduledInstructionSet,
      estimatedThroughputGflops: parseFloat(estimatedThroughputGflops.toFixed(2)),
      simdUtilizationScore: parseFloat(simdUtilizationScore.toFixed(1)),
      planLog,
    };
  }
}
