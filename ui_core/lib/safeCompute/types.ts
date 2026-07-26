// HYPER Safe-Compute Layer Types

export interface SafeComputeJob {
  id: string;
  userId: string;
  status: "queued" | "processing" | "completed" | "failed" | "paused";
  progress: number;
  priority: number;
  createdAt: Date;
  startedAt?: Date;
  completedAt?: Date;
  estimatedWaitTime: number; // in seconds
  offlineCapable: boolean;
  result?: unknown;
  error?: string;
}

export interface SystemLoad {
  cpuUsage: number;
  memoryUsage: number;
  gpuMemoryUsage: number;
  temperature: number;
  isOverheating: boolean;
  availableRam: number; // in MB
}

export interface ComputeConfig {
  maxConcurrentJobs: number;
  thermalThreshold: number; // Celsius
  memoryThreshold: number; // percentage
  autoDowngradeEnabled: boolean;
  offlineMode: boolean;
}

export interface ModelVariant {
  id: string;
  name: string;
  size: "tiny" | "small" | "medium" | "large";
  requiredRamMb: number;
  accuracy: number;
  speed: number;
}

export interface SafeComputeStatus {
  enabled: boolean;
  jobQueue: SafeComputeJob[];
  systemLoad: SystemLoad;
  config: ComputeConfig;
  activeModel: ModelVariant | null;
  thermalGuardActive: boolean;
  offlineJobsPending: number;
}

export interface JobQueueStats {
  queued: number;
  processing: number;
  completed: number;
  failed: number;
  averageWaitTime: number;
  estimatedTotalWaitTime: number;
}
