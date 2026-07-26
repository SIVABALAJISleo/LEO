// HYPER Saturation Guard - Fail-fast when thresholds hit

type ResourceType = "gpu" | "memory" | "io" | "coordination";

interface ResourceThresholds {
  gpu: number; // 0-100%
  memory: number; // 0-100%
  io: number; // 0-100%
  coordination: number; // concurrent jobs
}

interface SaturationStatus {
  saturated: boolean;
  resource: ResourceType | null;
  currentLoad: number;
  threshold: number;
  action: "accept" | "queue" | "defer" | "reject";
}

const DEFAULT_THRESHOLDS: ResourceThresholds = {
  gpu: 85,
  memory: 80,
  io: 90,
  coordination: 3,
};

class SaturationGuardEngine {
  private static instance: SaturationGuardEngine;
  private thresholds: ResourceThresholds = { ...DEFAULT_THRESHOLDS };
  private currentLoads: Record<ResourceType, number> = {
    gpu: 0,
    memory: 0,
    io: 0,
    coordination: 0,
  };
  private listeners: Array<(status: SaturationStatus) => void> = [];

  private constructor() {}

  static getInstance(): SaturationGuardEngine {
    if (!SaturationGuardEngine.instance) {
      SaturationGuardEngine.instance = new SaturationGuardEngine();
    }
    return SaturationGuardEngine.instance;
  }

  updateLoad(resource: ResourceType, value: number): void {
    this.currentLoads[resource] = value;
    this.checkAndNotify();
  }

  private checkAndNotify(): void {
    const status = this.getStatus();
    if (status.saturated) {
      this.listeners.forEach((l) => l(status));
    }
  }

  getStatus(): SaturationStatus {
    // Check each resource
    for (const resource of ["gpu", "memory", "io", "coordination"] as ResourceType[]) {
      const current = this.currentLoads[resource];
      const threshold = this.thresholds[resource];

      if (current >= threshold) {
        return {
          saturated: true,
          resource,
          currentLoad: current,
          threshold,
          action: this.determineAction(resource, current, threshold),
        };
      }
    }

    return {
      saturated: false,
      resource: null,
      currentLoad: 0,
      threshold: 0,
      action: "accept",
    };
  }

  private determineAction(
    resource: ResourceType,
    current: number,
    threshold: number,
  ): "accept" | "queue" | "defer" | "reject" {
    const overloadPercent = ((current - threshold) / threshold) * 100;

    if (overloadPercent < 5) return "queue";
    if (overloadPercent < 15) return "defer";
    return "reject";
  }

  // Check if we can accept a new heavy job
  canAcceptHeavyJob(): { allowed: boolean; reason?: string } {
    const status = this.getStatus();

    if (!status.saturated) {
      return { allowed: true };
    }

    const reasons: Record<ResourceType, string> = {
      gpu: "GPU is at capacity",
      memory: "Memory limit reached",
      io: "Storage bandwidth saturated",
      coordination: "Maximum concurrent jobs reached",
    };

    return {
      allowed: false,
      reason: status.resource ? reasons[status.resource] : "System at capacity",
    };
  }

  // Subscribe to saturation events
  onSaturation(callback: (status: SaturationStatus) => void): () => void {
    this.listeners.push(callback);
    return () => {
      this.listeners = this.listeners.filter((l) => l !== callback);
    };
  }

  // Get user-friendly status text (no internals exposed)
  getStatusText(): string {
    const status = this.getStatus();

    if (!status.saturated) {
      return "System ready";
    }

    switch (status.action) {
      case "queue":
        return "Processing capacity limited. New tasks will be queued.";
      case "defer":
        return "System busy. Heavy tasks will be scheduled for later.";
      case "reject":
        return "System at capacity. Please try again shortly.";
      default:
        return "System ready";
    }
  }

  setThresholds(thresholds: Partial<ResourceThresholds>): void {
    this.thresholds = { ...this.thresholds, ...thresholds };
  }
}

export const saturationGuard = SaturationGuardEngine.getInstance();
export type { SaturationStatus, ResourceType, ResourceThresholds };
