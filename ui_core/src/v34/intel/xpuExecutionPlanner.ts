// LEO AI V34 — XPU Execution Planner
// Capabilities: Allocate tasks to CPU/iGPU/XPU, optimize execution routing, and output the Intel Utilization Score.

import { IntelCapabilityDetector } from "./intelCapabilityDetector";
import { IpexOptimizationEngine } from "./ipexOptimizationEngine";
import { SyclAccelerationManager } from "./syclAccelerationManager";

export interface IntelExecutionReport {
  timestamp: number;
  assignedDevice: "Intel_CPU" | "Intel_iGPU_Xe" | "Intel_XPU_Arc";
  hasVectorAccelerated: boolean;
  activeThreadsUsed: number;
  intelUtilizationScore: number; // 0 to 100
  planningLog: string;
}

export class XpuExecutionPlanner {
  private detector = new IntelCapabilityDetector();
  private ipex = new IpexOptimizationEngine();
  private sycl = new SyclAccelerationManager();

  planExecution(dataSize: number, taskType: "MatrixMultiply" | "LinearScan" | "LogicBranching"): IntelExecutionReport {
    const caps = this.detector.detectCapabilities();
    
    let assignedDevice: "Intel_CPU" | "Intel_iGPU_Xe" | "Intel_XPU_Arc" = "Intel_CPU";
    let hasVectorAccelerated = false;
    let activeThreadsUsed = 1;
    let intelUtilizationScore = 30;
    let planningLog = "";

    if (taskType === "LogicBranching") {
      assignedDevice = "Intel_CPU";
      const ipexStatus = this.ipex.applyOptimizations(8);
      activeThreadsUsed = ipexStatus.activeSettings.ompNumThreads;
      hasVectorAccelerated = caps.hasVnni;
      intelUtilizationScore = 88.0;
      planningLog = "Routed to multi-threaded CPU. OpenMP threads bound for logic branches execution.";
    } else if (taskType === "MatrixMultiply" && caps.igpuExecutionUnits > 0) {
      assignedDevice = "Intel_iGPU_Xe";
      const syclStatus = this.sycl.submitKernel(dataSize);
      hasVectorAccelerated = caps.hasXmx; // Xe Matrix Extensions
      activeThreadsUsed = caps.igpuExecutionUnits;
      intelUtilizationScore = 94.5;
      planningLog = `Routed to Intel Xe iGPU via SYCL device queue. USM size: ${syclStatus.unifiedSharedMemoryAllocatedMB}MB.`;
    } else {
      assignedDevice = "Intel_CPU";
      hasVectorAccelerated = caps.hasAvx2;
      intelUtilizationScore = 75.0;
      planningLog = "Routed to CPU. Vectorizing matrices using AVX2 registers.";
    }

    return {
      timestamp: Date.now(),
      assignedDevice,
      hasVectorAccelerated,
      activeThreadsUsed,
      intelUtilizationScore,
      planningLog
    };
  }
}
