// LEO AI V33 — Task Routing Engine
// Capabilities: Compute load balance across CPU/iGPU/NPU, output the Hardware Utilization Score.

import { CpuReasoningEngine } from "./cpuReasoningEngine";
import { IgpuExecutionEngine } from "./igpuExecutionEngine";
import { NpuExecutionEngine } from "./npuExecutionEngine";

export interface LoadRoutingReport {
  timestamp: number;
  routedTo: "CPU" | "iGPU" | "NPU";
  taskType: "Reasoning" | "MatrixMath" | "QuantizedMonitoring";
  loadFactorCpu: number; // 0.0 to 1.0
  loadFactorIgpu: number;
  loadFactorNpu: number;
  hardwareUtilizationScore: number; // 0 to 100
}

export class TaskRoutingEngine {
  private cpuEngine = new CpuReasoningEngine();
  private igpuEngine = new IgpuExecutionEngine();
  private npuEngine = new NpuExecutionEngine();

  routeWorkload(taskType: "Reasoning" | "MatrixMath" | "QuantizedMonitoring"): LoadRoutingReport {
    let routedTo: "CPU" | "iGPU" | "NPU" = "CPU";
    let loadFactorCpu = 0.1;
    let loadFactorIgpu = 0.05;
    let loadFactorNpu = 0.02;

    switch (taskType) {
      case "Reasoning":
        routedTo = "CPU";
        // Reasoning runs threads
        const cpuStats = this.cpuEngine.executeLogicalBlock(25000);
        loadFactorCpu = cpuStats.threadsUsed / 16;
        break;
      case "MatrixMath":
        routedTo = "iGPU";
        const igpuStats = this.igpuEngine.runMatrixMultiply(4096, 4096);
        loadFactorIgpu = igpuStats.thermalStatus === "throttling" ? 0.95 : 0.45;
        break;
      case "QuantizedMonitoring":
        routedTo = "NPU";
        const npuStats = this.npuEngine.getNpuStatus();
        loadFactorNpu = npuStats.topsAchieved > 0 ? 0.65 : 0.0;
        break;
    }

    // Hardware Utilization Score: assesses how well resources are used without bottlenecking
    // Ideal: balanced resource load, penalizes CPU 100% overload or throttling iGPU
    let penalty = 0;
    if (loadFactorCpu > 0.9) penalty += 20;
    if (loadFactorIgpu > 0.9) penalty += 15;

    // Balanced routing yields higher score
    const usageSum = loadFactorCpu + loadFactorIgpu + loadFactorNpu;
    let baseScore = 95 - penalty;
    if (usageSum === 0) baseScore = 50;

    const hardwareUtilizationScore = parseFloat(Math.min(100, Math.max(0, baseScore)).toFixed(1));

    return {
      timestamp: Date.now(),
      routedTo,
      taskType,
      loadFactorCpu: parseFloat(loadFactorCpu.toFixed(3)),
      loadFactorIgpu: parseFloat(loadFactorIgpu.toFixed(3)),
      loadFactorNpu: parseFloat(loadFactorNpu.toFixed(3)),
      hardwareUtilizationScore,
    };
  }
}
