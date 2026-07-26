// GPU Job Management System Types

export type GpuJobStatus =
  "pending" | "queued" | "running" | "paused" | "completed" | "failed" | "too_large" | "cancelled";

export type GpuJobTier = "light" | "medium" | "heavy" | "very_heavy";

export interface GpuJob {
  id: string;
  user_id: string;
  job_type: string;
  job_name: string | null;
  job_tier: GpuJobTier | null;
  payload: Record<string, unknown>;
  status: GpuJobStatus;
  priority: number;
  memory_required_mb: number | null;
  estimated_duration_sec: number | null;
  progress: number;
  result_url: string | null;
  result_data: Record<string, unknown> | null;
  error_message: string | null;
  checkpoint_data: Record<string, unknown> | null;
  checkpoint_at: string | null;
  worker_id: string | null;
  worker_signature: string | null;
  thermal_paused: boolean;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface GpuSystemStatus {
  id: string;
  worker_id: string;
  gpu_temperature_celsius: number | null;
  gpu_memory_used_mb: number | null;
  gpu_memory_total_mb: number | null;
  gpu_utilization_percent: number | null;
  cpu_temperature_celsius: number | null;
  cpu_utilization_percent: number | null;
  is_online: boolean;
  is_thermal_throttled: boolean;
  active_job_id: string | null;
  jobs_completed_today: number;
  jobs_failed_today: number;
  last_heartbeat_at: string;
  created_at: string;
  updated_at: string;
}

export interface CreateGpuJobInput {
  job_type: string;
  job_name?: string;
  payload: Record<string, unknown>;
  priority?: number;
  memory_required_mb?: number;
  estimated_duration_sec?: number;
}

export interface MemoryReport {
  available_mb: number;
  total_mb: number;
  used_mb: number;
  can_accept_job: boolean;
  max_job_size_mb: number;
}

export interface ThermalStatus {
  gpu_temp: number;
  cpu_temp: number;
  is_safe: boolean;
  is_throttled: boolean;
  recommended_action: "continue" | "slow_down" | "pause" | "stop";
}

export const GPU_MEMORY_LIMIT_MB = 24576; // 24GB theoretical limit for job sizing
export const GPU_THERMAL_WARNING = 75; // °C
export const GPU_THERMAL_CRITICAL = 85; // °C
export const GPU_THERMAL_EMERGENCY = 95; // °C

export const JOB_TYPE_OPTIONS = [
  { value: "inference", label: "Model Inference", memoryEstimate: 4096 },
  { value: "training", label: "Model Training", memoryEstimate: 16384 },
  { value: "rendering", label: "3D Rendering", memoryEstimate: 8192 },
  { value: "video_processing", label: "Video Processing", memoryEstimate: 6144 },
  { value: "data_analysis", label: "Data Analysis", memoryEstimate: 2048 },
  { value: "compression", label: "Model Compression", memoryEstimate: 4096 },
  { value: "optimization", label: "GPU Optimization", memoryEstimate: 3072 },
] as const;

export function getStatusColor(status: GpuJobStatus): string {
  switch (status) {
    case "pending":
      return "text-yellow-500";
    case "queued":
      return "text-blue-500";
    case "running":
      return "text-primary";
    case "paused":
      return "text-orange-500";
    case "completed":
      return "text-green-500";
    case "failed":
      return "text-red-500";
    case "too_large":
      return "text-red-400";
    case "cancelled":
      return "text-muted-foreground";
    default:
      return "text-muted-foreground";
  }
}

export function getStatusBadgeVariant(
  status: GpuJobStatus,
): "default" | "secondary" | "destructive" | "outline" {
  switch (status) {
    case "completed":
      return "default";
    case "running":
      return "default";
    case "failed":
    case "too_large":
      return "destructive";
    case "pending":
    case "queued":
    case "paused":
      return "secondary";
    default:
      return "outline";
  }
}

export function getStatusMessage(status: GpuJobStatus, position?: number): string {
  switch (status) {
    case "pending":
      return "Your job is being prepared...";
    case "queued":
      return position ? `Your job is queued (Position #${position})` : "Your job is queued";
    case "running":
      return "Your job is running on HYPER Engine...";
    case "paused":
      return "Job paused for thermal protection";
    case "completed":
      return "Completed! Download your results below.";
    case "failed":
      return "Job failed. Check error details.";
    case "too_large":
      return "Rejected: Job requires too much GPU memory";
    case "cancelled":
      return "Job was cancelled";
    default:
      return "Unknown status";
  }
}
