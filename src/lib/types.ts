// ============================================
// API Types for AI GPU Optimization Platform
// ============================================

// User & Auth Types
export interface User {
  id: string;
  email: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  user_metadata?: Record<string, any>;
  created_at: string;
}

export interface Profile {
  id: string;
  user_id: string;
  full_name: string | null;
  company: string | null;
  avatar_url: string | null;
  created_at: string;
  updated_at: string;
}

export interface AuthSession {
  access_token: string;
  refresh_token: string;
  expires_in: number;
  expires_at?: number;
  user: User;
}

export interface AuthResult {
  user: User | null;
  session: AuthSession | null;
  error?: ApiError;
}

// Model Types
export interface Model {
  id: string;
  user_id: string;
  name: string;
  description: string | null;
  model_type: string;
  version: string;
  parameters: Record<string, unknown>;
  storage_path: string | null;
  file_path: string | null;
  size_mb: number | null;
  status: 'active' | 'inactive' | 'archived';
  created_at: string;
  updated_at: string;
}

export interface CreateModelInput {
  name: string;
  description?: string;
  model_type: string;
  version: string;
  parameters?: Record<string, unknown>;
  storage_path?: string;
  file_path?: string;
  size_mb?: number;
}

// Inference Job Types
export type JobStatus = 'queued' | 'running' | 'completed' | 'failed' | 'cancelled';

export interface InferenceJob {
  id: string;
  user_id: string;
  model_id: string;
  input_data: Record<string, unknown>;
  output_data: Record<string, unknown> | null;
  enabled_modules: string[];
  optimization_options: Record<string, unknown>;
  status: JobStatus;
  priority: number;
  progress: number;
  latency_ms: number | null;
  speedup: number | null;
  compression_ratio: number | null;
  error_message: string | null;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface CreateInferenceJobInput {
  modelId: string;
  inputData: Record<string, unknown>;
  enabledModules?: string[];
  options?: Record<string, unknown>;
}

// Module Config Types
export interface ModuleConfig {
  id: string;
  user_id: string;
  module_name: string;
  module_type: string;
  enabled: boolean;
  config: Record<string, unknown>;
  settings: Record<string, unknown>;
  speedup_achieved: number | null;
  compression_ratio_achieved: number | null;
  created_at: string;
  updated_at: string;
}

export interface UpdateModuleConfigInput {
  enabled?: boolean;
  config?: Record<string, unknown>;
  settings?: Record<string, unknown>;
}

// Performance Metrics Types
export interface PerformanceMetric {
  id: string;
  user_id: string;
  job_id: string | null;
  model_id: string | null;
  module_name: string | null;
  metric_name: string;
  metric_value: number;
  cpu_usage_percent: number | null;
  memory_mb: number | null;
  latency_ms: number | null;
  throughput_rps: number | null;
  cache_hit_ratio: number | null;
  metadata: Record<string, unknown>;
  recorded_at: string;
}

export interface PerformanceMetricsFilter {
  startDate?: string;
  endDate?: string;
  moduleName?: string;
  modelId?: string;
  jobId?: string;
  metricName?: string;
  limit?: number;
}

// System Metrics Types
export type SystemStatus = 'healthy' | 'warning' | 'critical';

export interface SystemMetrics {
  id: string;
  user_id: string;
  gpu_utilization: number | null;
  memory_usage: number | null;
  temperature: number | null;
  power_draw: number | null;
  throughput: number | null;
  cpu_percent: number | null;
  disk_gb: number | null;
  active_jobs: number;
  total_requests: number;
  status: SystemStatus;
  metadata: Record<string, unknown>;
  recorded_at: string;
}

// Alert Types
export type AlertSeverity = 'info' | 'warning' | 'error' | 'critical';

export interface Alert {
  id: string;
  user_id: string;
  alert_type: string;
  severity: AlertSeverity;
  title: string;
  message: string;
  module_name: string | null;
  metadata: Record<string, unknown>;
  resolved: boolean;
  resolved_at: string | null;
  created_at: string;
}

export interface AlertsFilter {
  severity?: AlertSeverity;
  resolved?: boolean;
  alertType?: string;
  moduleName?: string;
  limit?: number;
}

// Module Status Types
export type ModuleStatusType = 'idle' | 'running' | 'error' | 'warming_up' | 'cooling_down' | 'operational' | 'degraded' | 'offline';

export interface ModuleStatus {
  id: string;
  user_id: string;
  module_name: string;
  status: ModuleStatusType;
  current_job_id: string | null;
  health_score: number;
  last_checked: string;
  error_message: string | null;
  metadata: Record<string, unknown>;
  updated_at: string;
}

// Error Types
export interface ApiError {
  code: string;
  message: string;
  details?: string;
}

// Real-time Subscription Types
export type RealtimePayload<T> = {
  eventType: 'INSERT' | 'UPDATE' | 'DELETE';
  new: T;
  old: T | null;
};

export type UnsubscribeFn = () => void;
