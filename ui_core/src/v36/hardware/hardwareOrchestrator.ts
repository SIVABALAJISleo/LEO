// LEO AI V36 — Hardware Orchestrator
// Coordinates thread allocation boundaries dynamically across CPU, iGPU, and NPU targets.

export class HardwareOrchestrator {
  public selectBestDevice(
    taskWeightMillionParams: number,
    preferIgpu: boolean = false
  ): "CPU" | "iGPU" | "NPU" {
    if (taskWeightMillionParams > 10000) return "CPU"; // CPU for massive paging
    if (preferIgpu || taskWeightMillionParams > 2000) return "iGPU";
    return "NPU";
  }
}
