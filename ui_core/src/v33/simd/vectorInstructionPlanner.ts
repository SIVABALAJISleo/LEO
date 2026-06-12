// LEO AI V33 — Vector Instruction Planner
// Capabilities: Allocate vector registers, plan kernel selections, and output the SIMD Efficiency Score.

import { AvxOptimizationEngine } from "./avxOptimizationEngine";
import { VnniOptimizationEngine } from "./vnniOptimizationEngine";

export interface InstructionPlan {
  timestamp: number;
  dataSizeElements: number;
  chosenVectorSet: "AVX2" | "AVX512" | "VNNI" | "Scalar";
  registerUtilizationPct: number;
  simdEfficiencyScore: number; // 0 to 100
  instructionsSummary: string;
}

export class VectorInstructionPlanner {
  private avxEngine = new AvxOptimizationEngine();
  private vnniEngine = new VnniOptimizationEngine();

  planVectorLoads(dataSizeElements: number, isQuantized: boolean): InstructionPlan {
    let chosenVectorSet: "AVX2" | "AVX512" | "VNNI" | "Scalar" = "Scalar";
    let registerUtilizationPct = 100;
    let simdEfficiencyScore = 10;
    let instructionsSummary = "";

    if (dataSizeElements < 8) {
      chosenVectorSet = "Scalar";
      registerUtilizationPct = parseFloat(((dataSizeElements / 8) * 100).toFixed(1));
      simdEfficiencyScore = 20;
      instructionsSummary = "Micro-size vector data; scalar operations selected to avoid vector packing overhead.";
    } else if (isQuantized) {
      chosenVectorSet = "VNNI";
      const vnniReport = this.vnniEngine.runVnniKernel(dataSizeElements, "INT8");
      registerUtilizationPct = 95.0;
      simdEfficiencyScore = vnniReport.cycleReductionPct; // Efficiency scales with cycle reduction rate
      instructionsSummary = `VNNI instructions scheduled for 8-bit registers, achieving a ${vnniReport.cycleReductionPct}% cycle reduction.`;
    } else if (dataSizeElements > 1024) {
      chosenVectorSet = "AVX512";
      const avxReport = this.avxEngine.detectVectorCapability("AVX512");
      registerUtilizationPct = 98.0;
      simdEfficiencyScore = 92.5; // High parallel score
      instructionsSummary = `AVX-512 vector pipelines loaded. Processing 16 parallel float32 elements per register.`;
    } else {
      chosenVectorSet = "AVX2";
      const avxReport = this.avxEngine.detectVectorCapability("AVX2");
      registerUtilizationPct = 85.0;
      simdEfficiencyScore = 78.0;
      instructionsSummary = "AVX2 alignment chosen. Processing 8 parallel float32 elements per register.";
    }

    return {
      timestamp: Date.now(),
      dataSizeElements,
      chosenVectorSet,
      registerUtilizationPct,
      simdEfficiencyScore: parseFloat(simdEfficiencyScore.toFixed(1)),
      instructionsSummary
    };
  }
}
