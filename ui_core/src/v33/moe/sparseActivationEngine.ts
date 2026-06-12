// LEO AI V33 — Sparse Activation Engine
// Capabilities: Manage expert activation arrays, offload inactive weights, and calculate Expert Efficiency Score.

export interface ExpertState {
  expertId: string;
  name: string;
  isActive: boolean;
  loadState: "GPU_VRAM" | "SYSTEM_RAM" | "DISK";
  memoryRequiredBytes: number;
}

export interface ActivationStats {
  timestamp: number;
  activeBytes: number;
  totalBytes: number;
  expertEfficiencyScore: number; // 0 to 100
  experts: ExpertState[];
}

export class SparseActivationEngine {
  private expertMap = new Map<string, ExpertState>([
    ["exp-0", { expertId: "exp-0", name: "Reasoning Expert", isActive: false, loadState: "SYSTEM_RAM", memoryRequiredBytes: 500 * 1024 * 1024 }],
    ["exp-1", { expertId: "exp-1", name: "Math Expert", isActive: false, loadState: "SYSTEM_RAM", memoryRequiredBytes: 500 * 1024 * 1024 }],
    ["exp-2", { expertId: "exp-2", name: "Code Expert", isActive: false, loadState: "SYSTEM_RAM", memoryRequiredBytes: 500 * 1024 * 1024 }],
    ["exp-3", { expertId: "exp-3", name: "Language Expert", isActive: false, loadState: "SYSTEM_RAM", memoryRequiredBytes: 500 * 1024 * 1024 }],
    ["exp-4", { expertId: "exp-4", name: "Retrieval Expert", isActive: false, loadState: "SYSTEM_RAM", memoryRequiredBytes: 500 * 1024 * 1024 }]
  ]);

  activateExperts(activeIds: string[]): ActivationStats {
    let activeBytes = 0;
    let totalBytes = 0;

    this.expertMap.forEach((expert, id) => {
      totalBytes += expert.memoryRequiredBytes;
      if (activeIds.includes(id)) {
        expert.isActive = true;
        expert.loadState = "GPU_VRAM";
        activeBytes += expert.memoryRequiredBytes;
      } else {
        expert.isActive = false;
        expert.loadState = expert.loadState === "GPU_VRAM" ? "SYSTEM_RAM" : expert.loadState; // swap out to RAM
      }
      this.expertMap.set(id, expert);
    });

    // Expert Efficiency Score: fraction of weight memory successfully kept out of GPU VRAM
    // 100% means all experts are bypassed, 0% means all are loaded
    const bypassedBytes = totalBytes - activeBytes;
    const expertEfficiencyScore = totalBytes > 0 
      ? parseFloat(((bypassedBytes / totalBytes) * 100).toFixed(1))
      : 100.0;

    return {
      timestamp: Date.now(),
      activeBytes,
      totalBytes,
      expertEfficiencyScore,
      experts: Array.from(this.expertMap.values())
    };
  }

  getExpertStatus(): ExpertState[] {
    return Array.from(this.expertMap.values());
  }

  swapToDisk(id: string) {
    const expert = this.expertMap.get(id);
    if (expert) {
      expert.isActive = false;
      expert.loadState = "DISK";
      this.expertMap.set(id, expert);
    }
  }
}
