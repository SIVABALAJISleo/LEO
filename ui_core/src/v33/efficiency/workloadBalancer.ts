// LEO AI V33 — Workload Balancer
// Capabilities: Balance computing constraints, throttle execution threads on high TDP thresholds, and manage energy profiles.

export interface BalancerDirective {
  powerConstraintMode: "eco" | "balanced" | "max_power";
  cpuCoreLimit: number;
  gpuBatchThrottlingMs: number;
  npuPriorityLevel: "high" | "medium" | "low";
}

export class WorkloadBalancer {
  computeBalancingDirective(batteryPct: number, currentTempCelsius: number): BalancerDirective {
    let powerConstraintMode: "eco" | "balanced" | "max_power" = "balanced";
    let cpuCoreLimit = 8;
    let gpuBatchThrottlingMs = 0;
    let npuPriorityLevel: "high" | "medium" | "low" = "medium";

    if (batteryPct < 25.0 || currentTempCelsius > 85.0) {
      powerConstraintMode = "eco";
      cpuCoreLimit = 3; // cap active cores to restrict heat/draw
      gpuBatchThrottlingMs = 25; // delay execution calls
      npuPriorityLevel = "high"; // prefer NPU because it's ultra energy efficient
    } else if (batteryPct > 80.0 && currentTempCelsius < 65.0) {
      powerConstraintMode = "max_power";
      cpuCoreLimit = 8;
      gpuBatchThrottlingMs = 0;
      npuPriorityLevel = "low"; // standard GPU/CPU compute allowed
    }

    return {
      powerConstraintMode,
      cpuCoreLimit,
      gpuBatchThrottlingMs,
      npuPriorityLevel
    };
  }
}
