// ============================================
// API Service Layer for AI GPU Optimization Platform
// All backend operations with strongly typed functions
// ============================================

import { firebaseClient as supabase } from "@/integrations/firebase/client";
import type {
  User,
  Profile,
  AuthResult,
  Model,
  CreateModelInput,
  InferenceJob,
  CreateInferenceJobInput,
  ModuleConfig,
  UpdateModuleConfigInput,
  PerformanceMetric,
  PerformanceMetricsFilter,
  SystemMetrics,
  Alert,
  AlertsFilter,
  ApiError,
} from "./types";
import type { Json } from "@/integrations/supabase/types";

// ============================================
// Helper Functions
// ============================================

function createApiError(code: string, message: string, details?: string): ApiError {
  return { code, message, details };
}

function handleSupabaseError(error: { message: string; code?: string }): never {
  throw createApiError(error.code || "SUPABASE_ERROR", error.message, "Database operation failed");
}

// Convert Record<string, unknown> to Json type
function toJson(obj: Record<string, unknown> | unknown[]): Json {
  return obj as Json;
}

// ============================================
// Authentication Functions
// ============================================

/**
 * Login with email and password
 * @throws ApiError on failure
 */
export async function login(email: string, password: string): Promise<AuthResult> {
  const { data, error } = await supabase.auth.signInWithPassword({
    email,
    password,
  });

  if (error) {
    throw createApiError("AUTH_ERROR", error.message, "Failed to sign in");
  }

  return {
    user: data.user as User,
    session: data.session as AuthResult["session"],
  };
}

/**
 * Sign up with email, password, and optional username
 * Creates user and profile row
 * @throws ApiError on failure
 */
export async function signup(
  email: string,
  password: string,
  fullName?: string,
): Promise<AuthResult> {
  const redirectUrl = `${window.location.origin}/`;

  const { data, error } = await supabase.auth.signUp({
    email,
    password,
    options: {
      emailRedirectTo: redirectUrl,
      data: {
        full_name: fullName,
      },
    },
  });

  if (error) {
    throw createApiError("AUTH_ERROR", error.message, "Failed to sign up");
  }

  return {
    user: data.user as User,
    session: data.session as AuthResult["session"],
  };
}

/**
 * Logout current user
 * @throws ApiError on failure
 */
export async function logout(): Promise<void> {
  const { error } = await supabase.auth.signOut();

  if (error) {
    throw createApiError("AUTH_ERROR", error.message, "Failed to sign out");
  }
}

/**
 * Get current authenticated user and profile
 * Returns null if not authenticated
 */
export async function getCurrentUser(): Promise<{ user: User; profile: Profile } | null> {
  const {
    data: { user },
    error: userError,
  } = await supabase.auth.getUser();

  if (userError || !user) {
    return null;
  }

  const { data: profile, error: profileError } = await supabase
    .from("profiles")
    .select("*")
    .eq("user_id", user.id)
    .maybeSingle();

  if (profileError) {
    console.error("Failed to fetch profile:", profileError);
  }

  return {
    user: user as User,
    profile: profile as Profile,
  };
}

// ============================================
// Model Functions
// ============================================

/**
 * List all models for current user
 * @throws ApiError on failure
 */
export async function listModels(): Promise<Model[]> {
  const { data, error } = await supabase
    .from("models")
    .select("*")
    .order("created_at", { ascending: false });

  if (error) handleSupabaseError(error);
  return (data || []) as unknown as Model[];
}

/**
 * Create a new model
 * @throws ApiError on failure
 */
export async function createModel(input: CreateModelInput): Promise<Model> {
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) throw createApiError("AUTH_ERROR", "Not authenticated");

  const { data, error } = await supabase
    .from("models")
    .insert({
      user_id: user.id,
      name: input.name,
      description: input.description || null,
      model_type: input.model_type,
      version: input.version,
      parameters: toJson(input.parameters || {}),
      storage_path: input.storage_path || null,
    })
    .select()
    .single();

  if (error) handleSupabaseError(error);
  return data as unknown as Model;
}

/**
 * Get model by ID
 * @throws ApiError on failure or not found
 */
export async function getModelById(id: string): Promise<Model> {
  const { data, error } = await supabase.from("models").select("*").eq("id", id).single();

  if (error) handleSupabaseError(error);
  if (!data) throw createApiError("NOT_FOUND", "Model not found");
  return data as unknown as Model;
}

/**
 * Update model by ID
 * @throws ApiError on failure
 */
export async function updateModel(id: string, updates: Partial<CreateModelInput>): Promise<Model> {
  const updateData: Record<string, unknown> = {};

  if (updates.name !== undefined) updateData.name = updates.name;
  if (updates.description !== undefined) updateData.description = updates.description;
  if (updates.model_type !== undefined) updateData.model_type = updates.model_type;
  if (updates.version !== undefined) updateData.version = updates.version;
  if (updates.storage_path !== undefined) updateData.storage_path = updates.storage_path;
  if (updates.parameters !== undefined) updateData.parameters = toJson(updates.parameters);

  const { data, error } = await supabase
    .from("models")
    .update(updateData)
    .eq("id", id)
    .select()
    .single();

  if (error) handleSupabaseError(error);
  return data as unknown as Model;
}

/**
 * Delete model by ID
 * @throws ApiError on failure
 */
export async function deleteModel(id: string): Promise<void> {
  const { error } = await supabase.from("models").delete().eq("id", id);

  if (error) handleSupabaseError(error);
}

// ============================================
// Inference Job Functions
// ============================================

/**
 * Create a new inference job
 * @throws ApiError on failure
 */
export async function createInferenceJob(input: CreateInferenceJobInput): Promise<InferenceJob> {
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) throw createApiError("AUTH_ERROR", "Not authenticated");

  const { data, error } = await supabase
    .from("inference_jobs")
    .insert({
      user_id: user.id,
      model_id: input.modelId,
      input_data: toJson(input.inputData),
      enabled_modules: toJson(input.enabledModules || []),
      optimization_options: toJson(input.options || {}),
    })
    .select()
    .single();

  if (error) handleSupabaseError(error);
  return data as unknown as InferenceJob;
}

/**
 * Get all active jobs (status: running or queued)
 * @throws ApiError on failure
 */
export async function getActiveJobs(): Promise<InferenceJob[]> {
  const { data, error } = await supabase
    .from("inference_jobs")
    .select("*")
    .in("status", ["running", "queued"])
    .order("created_at", { ascending: false });

  if (error) handleSupabaseError(error);
  return (data || []) as unknown as InferenceJob[];
}

/**
 * Get all jobs with optional status filter
 * @throws ApiError on failure
 */
export async function getJobs(status?: string): Promise<InferenceJob[]> {
  let query = supabase.from("inference_jobs").select("*").order("created_at", { ascending: false });

  if (status) {
    query = query.eq("status", status);
  }

  const { data, error } = await query;
  if (error) handleSupabaseError(error);
  return (data || []) as unknown as InferenceJob[];
}

/**
 * Get job by ID with related metrics
 * @throws ApiError on failure
 */
export async function getJobById(id: string): Promise<{
  job: InferenceJob;
  metrics: PerformanceMetric[];
}> {
  const { data: job, error: jobError } = await supabase
    .from("inference_jobs")
    .select("*")
    .eq("id", id)
    .single();

  if (jobError) handleSupabaseError(jobError);
  if (!job) throw createApiError("NOT_FOUND", "Job not found");

  const { data: metrics, error: metricsError } = await supabase
    .from("performance_metrics")
    .select("*")
    .eq("job_id", id)
    .order("recorded_at", { ascending: true });

  if (metricsError) handleSupabaseError(metricsError);

  return {
    job: job as unknown as InferenceJob,
    metrics: (metrics || []) as unknown as PerformanceMetric[],
  };
}

/**
 * Cancel a job by setting status to cancelled
 * @throws ApiError on failure
 */
export async function cancelJob(id: string): Promise<InferenceJob> {
  const { data, error } = await supabase
    .from("inference_jobs")
    .update({ status: "cancelled" })
    .eq("id", id)
    .select()
    .single();

  if (error) handleSupabaseError(error);
  return data as unknown as InferenceJob;
}

/**
 * Update job progress
 * @throws ApiError on failure
 */
export async function updateJobProgress(id: string, progress: number): Promise<InferenceJob> {
  const { data, error } = await supabase
    .from("inference_jobs")
    .update({ progress })
    .eq("id", id)
    .select()
    .single();

  if (error) handleSupabaseError(error);
  return data as unknown as InferenceJob;
}

// ============================================
// Module Config Functions
// ============================================

/**
 * Get module configurations for current user
 * @throws ApiError on failure
 */
export async function getModuleConfigs(): Promise<ModuleConfig[]> {
  const { data, error } = await supabase
    .from("module_configs")
    .select("*")
    .order("module_name", { ascending: true });

  if (error) handleSupabaseError(error);
  return (data || []) as unknown as ModuleConfig[];
}

/**
 * Update module configuration
 * @throws ApiError on failure
 */
export async function updateModuleConfig(
  id: string,
  patch: UpdateModuleConfigInput,
): Promise<ModuleConfig> {
  const updateData: Record<string, unknown> = {};
  if (patch.enabled !== undefined) updateData.enabled = patch.enabled;
  if (patch.config !== undefined) updateData.config = toJson(patch.config);

  const { data, error } = await supabase
    .from("module_configs")
    .update(updateData)
    .eq("id", id)
    .select()
    .single();

  if (error) handleSupabaseError(error);
  return data as unknown as ModuleConfig;
}

/**
 * Create or update module config (upsert)
 * @throws ApiError on failure
 */
export async function upsertModuleConfig(
  moduleName: string,
  moduleType: string,
  config: Record<string, unknown>,
  enabled: boolean = true,
): Promise<ModuleConfig> {
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) throw createApiError("AUTH_ERROR", "Not authenticated");

  const { data, error } = await supabase
    .from("module_configs")
    .upsert(
      {
        user_id: user.id,
        module_name: moduleName,
        module_type: moduleType,
        config: toJson(config),
        enabled,
      },
      {
        onConflict: "user_id,module_name",
      },
    )
    .select()
    .single();

  if (error) handleSupabaseError(error);
  return data as unknown as ModuleConfig;
}

// ============================================
// Performance Metrics Functions
// ============================================

/**
 * Get performance metrics with optional filters
 * @throws ApiError on failure
 */
export async function getPerformanceMetrics(
  filters: PerformanceMetricsFilter = {},
): Promise<PerformanceMetric[]> {
  let query = supabase
    .from("performance_metrics")
    .select("*")
    .order("recorded_at", { ascending: false });

  if (filters.startDate) {
    query = query.gte("recorded_at", filters.startDate);
  }
  if (filters.endDate) {
    query = query.lte("recorded_at", filters.endDate);
  }
  if (filters.moduleName) {
    query = query.eq("module_name", filters.moduleName);
  }
  if (filters.modelId) {
    query = query.eq("model_id", filters.modelId);
  }
  if (filters.jobId) {
    query = query.eq("job_id", filters.jobId);
  }
  if (filters.metricName) {
    query = query.eq("metric_name", filters.metricName);
  }
  if (filters.limit) {
    query = query.limit(filters.limit);
  }

  const { data, error } = await query;
  if (error) handleSupabaseError(error);
  return (data || []) as unknown as PerformanceMetric[];
}

// ============================================
// System Metrics Functions
// ============================================

/**
 * Get recent system metrics
 * @throws ApiError on failure
 */
export async function getSystemMetricsRecent(limit: number = 50): Promise<SystemMetrics[]> {
  const { data, error } = await supabase
    .from("system_metrics")
    .select("*")
    .order("recorded_at", { ascending: false })
    .limit(limit);

  if (error) handleSupabaseError(error);
  return (data || []) as unknown as SystemMetrics[];
}

/**
 * Insert system metrics
 * @throws ApiError on failure
 */
export async function insertSystemMetrics(
  metrics: Omit<SystemMetrics, "id" | "user_id" | "recorded_at">,
): Promise<SystemMetrics> {
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) throw createApiError("AUTH_ERROR", "Not authenticated");

  const { data, error } = await supabase
    .from("system_metrics")
    .insert({
      user_id: user.id,
      gpu_utilization: metrics.gpu_utilization,
      memory_usage: metrics.memory_usage,
      temperature: metrics.temperature,
      power_draw: metrics.power_draw,
      throughput: metrics.throughput,
      metadata: toJson(metrics.metadata || {}),
    })
    .select()
    .single();

  if (error) handleSupabaseError(error);
  return data as unknown as SystemMetrics;
}

// ============================================
// Alert Functions
// ============================================

/**
 * Get alerts with optional filters
 * @throws ApiError on failure
 */
export async function getAlerts(filters: AlertsFilter = {}): Promise<Alert[]> {
  let query = supabase.from("alerts").select("*").order("created_at", { ascending: false });

  if (filters.severity) {
    query = query.eq("severity", filters.severity);
  }
  if (filters.resolved !== undefined) {
    query = query.eq("resolved", filters.resolved);
  }
  if (filters.alertType) {
    query = query.eq("alert_type", filters.alertType);
  }
  if (filters.limit) {
    query = query.limit(filters.limit);
  }

  const { data, error } = await query;
  if (error) handleSupabaseError(error);
  return (data || []) as unknown as Alert[];
}

/**
 * Resolve an alert
 * @throws ApiError on failure
 */
export async function resolveAlert(id: string): Promise<Alert> {
  const { data, error } = await supabase
    .from("alerts")
    .update({
      resolved: true,
      resolved_at: new Date().toISOString(),
    })
    .eq("id", id)
    .select()
    .single();

  if (error) handleSupabaseError(error);
  return data as unknown as Alert;
}

/**
 * Create a new alert
 * @throws ApiError on failure
 */
export async function createAlert(
  alertType: string,
  title: string,
  message: string,
  severity: Alert["severity"] = "info",
  metadata: Record<string, unknown> = {},
): Promise<Alert> {
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) throw createApiError("AUTH_ERROR", "Not authenticated");

  const { data, error } = await supabase
    .from("alerts")
    .insert({
      user_id: user.id,
      alert_type: alertType,
      title,
      message,
      severity,
      metadata: toJson(metadata),
    })
    .select()
    .single();

  if (error) handleSupabaseError(error);
  return data as unknown as Alert;
}

// ============================================
// Module Status Functions
// ============================================

/**
 * Get module status for all modules
 * @throws ApiError on failure
 */
export async function getModuleStatuses(): Promise<import("./types").ModuleStatus[]> {
  const { data, error } = await supabase
    .from("module_status")
    .select("*")
    .order("module_name", { ascending: true });

  if (error) handleSupabaseError(error);
  return (data || []) as unknown as import("./types").ModuleStatus[];
}

/**
 * Update module status
 * @throws ApiError on failure
 */
export async function updateModuleStatus(
  moduleName: string,
  status: import("./types").ModuleStatusType,
  currentJobId?: string | null,
): Promise<import("./types").ModuleStatus> {
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) throw createApiError("AUTH_ERROR", "Not authenticated");

  const { data, error } = await supabase
    .from("module_status")
    .upsert(
      {
        user_id: user.id,
        module_name: moduleName,
        status,
        current_job_id: currentJobId ?? null,
      },
      {
        onConflict: "user_id,module_name",
      },
    )
    .select()
    .single();

  if (error) handleSupabaseError(error);
  return data as unknown as import("./types").ModuleStatus;
}
