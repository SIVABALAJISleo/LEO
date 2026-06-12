// LEO AI V34 — Heterogeneous Compute Orchestrator
// Dynamic scheduler mapping execution tasks across CPU, iGPU, and NPU devices.

export type DeviceType = "CPU" | "iGPU" | "NPU";

export interface TaskProfile {
  id: string;
  name: string;
  type: "reasoning" | "graph_traversal" | "symbolic" | "vector_ops" | "embeddings" | "quant_inference" | "background_agent";
  complexity: "low" | "medium" | "high";
}

export interface DeviceTelemetry {
  latencyMs: number;
  energyJoules: number;
  throughputTokensSec: number;
  deviceAssigned: DeviceType;
}

export class HeterogeneousComputeOrchestrator {
  /**
   * Evaluates a task and maps it to the optimal device on consumer profiles.
   */
  public routeTask(task: TaskProfile): DeviceTelemetry {
    let deviceAssigned: DeviceType = "CPU";

    // Dynamic Scheduler Heuristics:
    switch (task.type) {
      case "reasoning":
      case "graph_traversal":
      case "symbolic":
        // CPU excels in heavy branching, logic pointer traversals, and symbolic processing
        deviceAssigned = "CPU";
        break;
      case "vector_ops":
      case "embeddings":
        // iGPU is optimal for parallel vector math operations & embedding calculations
        deviceAssigned = "iGPU";
        break;
      case "quant_inference":
      case "background_agent":
        // NPU is optimal for hardware-accelerated quantized logic and concurrent agents
        deviceAssigned = "NPU";
        break;
      default:
        deviceAssigned = "CPU";
    }

    // Determine latency, energy, and throughput metrics based on device characteristics
    let latencyMs = 15;
    let energyJoules = 0.5;
    let throughputTokensSec = 45;

    const scale = task.complexity === "high" ? 3 : (task.complexity === "medium" ? 1.8 : 0.8);

    if (deviceAssigned === "CPU") {
      // 12th Gen Core i5 performance simulation
      latencyMs = Math.round(18 * scale);
      energyJoules = parseFloat((0.85 * scale).toFixed(3));
      throughputTokensSec = Math.round(55 / scale);
    } else if (deviceAssigned === "iGPU") {
      // Intel UHD execution units simulation
      latencyMs = Math.round(25 * scale);
      energyJoules = parseFloat((1.2 * scale).toFixed(3));
      throughputTokensSec = Math.round(75 / scale);
    } else if (deviceAssigned === "NPU") {
      // Int8 optimized background pipeline
      latencyMs = Math.round(10 * scale);
      energyJoules = parseFloat((0.15 * scale).toFixed(3));
      throughputTokensSec = Math.round(120 / scale);
    }

    return {
      latencyMs,
      energyJoules,
      throughputTokensSec,
      deviceAssigned
    };
  }
}
