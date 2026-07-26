import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;

interface HealthReport {
  status: "healthy" | "degraded" | "critical";
  timestamp: string;
  checks: HealthCheck[];
  auto_fixes: AutoFix[];
  metrics: SystemHealthMetrics;
}

interface HealthCheck {
  name: string;
  status: "pass" | "warn" | "fail";
  message: string;
  duration_ms: number;
}

interface AutoFix {
  issue: string;
  action: string;
  success: boolean;
  timestamp: string;
}

interface SystemHealthMetrics {
  database_latency_ms: number;
  active_connections: number;
  queued_jobs: number;
  running_jobs: number;
  failed_jobs_24h: number;
  error_rate_percent: number;
}

serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY);
    const { action } = await req.json().catch(() => ({ action: "full_check" }));

    console.log(`[HealthMonitor] Action: ${action}`);

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    let result: any = {};

    switch (action) {
      case "full_check":
        result = await runFullHealthCheck(supabase);
        break;
      case "quick_check":
        result = await runQuickCheck(supabase);
        break;
      case "auto_heal":
        result = await runAutoHeal(supabase);
        break;
      case "cleanup":
        result = await runCleanup(supabase);
        break;
      case "recover_stuck_jobs":
        result = await recoverStuckJobs(supabase);
        break;
      default:
        result = await runFullHealthCheck(supabase);
    }

    return new Response(JSON.stringify(result), {
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  } catch (error: unknown) {
    console.error("[HealthMonitor] Error:", error);
    // Return generic error to client, log details server-side only
    return new Response(
      JSON.stringify({ error: "An internal error occurred", status: "critical" }),
      {
        status: 500,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      },
    );
  }
});

// eslint-disable-next-line @typescript-eslint/no-explicit-any
async function runFullHealthCheck(supabase: any): Promise<HealthReport> {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const startTime = Date.now();
  const checks: HealthCheck[] = [];
  const autoFixes: AutoFix[] = [];

  // Check 1: Database connectivity
  const dbCheck = await checkDatabaseHealth(supabase);
  checks.push(dbCheck);

  // Check 2: Job queue health
  const queueCheck = await checkJobQueueHealth(supabase);
  checks.push(queueCheck);

  // Check 3: Stuck jobs
  const stuckCheck = await checkStuckJobs(supabase);
  checks.push(stuckCheck);
  if (stuckCheck.status === "fail") {
    const fix = await recoverStuckJobs(supabase);
    autoFixes.push({
      issue: "Stuck jobs detected",
      action: "Reset stuck jobs to queued status",
      success: fix.recovered > 0,
      timestamp: new Date().toISOString(),
    });
  }

  // Check 4: Error rate
  const errorCheck = await checkErrorRate(supabase);
  checks.push(errorCheck);

  // Check 5: System metrics freshness
  const metricsCheck = await checkMetricsFreshness(supabase);
  checks.push(metricsCheck);

  // Check 6: Module health
  const moduleCheck = await checkModuleHealth(supabase);
  checks.push(moduleCheck);

  // Calculate overall status
  const failCount = checks.filter((c) => c.status === "fail").length;
  const warnCount = checks.filter((c) => c.status === "warn").length;

  let overallStatus: "healthy" | "degraded" | "critical" = "healthy";
  if (failCount > 0) {
    overallStatus = failCount > 2 ? "critical" : "degraded";
  } else if (warnCount > 2) {
    overallStatus = "degraded";
  }

  // Get system metrics
  const metrics = await getSystemHealthMetrics(supabase);

  // Store health report
  await supabase.from("system_settings").upsert(
    {
      setting_key: "last_health_check",
      setting_value: {
        status: overallStatus,
        timestamp: new Date().toISOString(),
        checks_passed: checks.filter((c) => c.status === "pass").length,
        checks_total: checks.length,
      },
    },
    { onConflict: "setting_key" },
  );

  return {
    status: overallStatus,
    timestamp: new Date().toISOString(),
    checks,
    auto_fixes: autoFixes,
    metrics,
  };
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
async function runQuickCheck(supabase: any) {
  const startTime = Date.now();

  // Quick database ping
  const { error } = await supabase.from("system_settings").select("id").limit(1);

  // Quick job count
  const { count: queuedCount } = await supabase
    .from("gpu_jobs")
    .select("*", { count: "exact", head: true })
    .in("status", ["pending", "queued"]);

  const { count: runningCount } = await supabase
    .from("gpu_jobs")
    .select("*", { count: "exact", head: true })
    .eq("status", "running");

  return {
    status: error ? "degraded" : "healthy",
    timestamp: new Date().toISOString(),
    latency_ms: Date.now() - startTime,
    queue: {
      pending: queuedCount || 0,
      running: runningCount || 0,
    },
    database: error ? "error" : "connected",
  };
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
async function runAutoHeal(supabase: any) {
  const fixes: AutoFix[] = [];

  // Fix 1: Recover stuck jobs
  const stuckFix = await recoverStuckJobs(supabase);
  if (stuckFix.recovered > 0) {
    fixes.push({
      issue: `${stuckFix.recovered} stuck jobs found`,
      action: "Reset to queued status",
      success: true,
      timestamp: new Date().toISOString(),
    });
  }

  // Fix 2: Reset unhealthy modules
  const { data: unhealthyModules } = await supabase
    .from("module_status")
    .select("*")
    .eq("status", "error");

  if (unhealthyModules && unhealthyModules.length > 0) {
    const { error } = await supabase
      .from("module_status")
      .update({
        status: "idle",
        health_score: 80,
        error_message: null,
        last_checked: new Date().toISOString(),
      })
      .eq("status", "error");

    fixes.push({
      issue: `${unhealthyModules.length} modules in error state`,
      action: "Reset to idle with health score 80",
      success: !error,
      timestamp: new Date().toISOString(),
    });
  }

  // Fix 3: Clean old data
  const cleanupResult = await runCleanup(supabase);
  if (cleanupResult.deleted > 0) {
    fixes.push({
      issue: "Old data accumulation",
      action: `Deleted ${cleanupResult.deleted} old records`,
      success: true,
      timestamp: new Date().toISOString(),
    });
  }

  // Fix 4: Ensure GPU system status exists
  const { data: gpuStatus } = await supabase.from("gpu_system_status").select("*").limit(1);

  if (!gpuStatus || gpuStatus.length === 0) {
    await supabase.from("gpu_system_status").insert({
      worker_id: "gpu-worker-primary",
      is_online: true,
      gpu_utilization_percent: 30,
      gpu_memory_used_mb: 4000,
      gpu_memory_total_mb: 24576,
      gpu_temperature_celsius: 55,
      cpu_utilization_percent: 25,
      cpu_temperature_celsius: 50,
      is_thermal_throttled: false,
      jobs_completed_today: 0,
      jobs_failed_today: 0,
      last_heartbeat_at: new Date().toISOString(),
    });

    fixes.push({
      issue: "Missing GPU system status",
      action: "Created default GPU system status",
      success: true,
      timestamp: new Date().toISOString(),
    });
  }

  return {
    status: "completed",
    timestamp: new Date().toISOString(),
    fixes,
    fixes_applied: fixes.filter((f) => f.success).length,
  };
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
async function runCleanup(supabase: any) {
  let totalDeleted = 0;

  // Delete old system metrics (keep last 7 days)
  const sevenDaysAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString();

  const { count: metricsDeleted } = await supabase
    .from("system_metrics")
    .delete()
    .lt("recorded_at", sevenDaysAgo)
    .select("*", { count: "exact", head: true });
  totalDeleted += metricsDeleted || 0;

  // Delete old performance metrics (keep last 7 days)
  const { count: perfDeleted } = await supabase
    .from("performance_metrics")
    .delete()
    .lt("recorded_at", sevenDaysAgo)
    .select("*", { count: "exact", head: true });
  totalDeleted += perfDeleted || 0;

  // Delete old error logs (keep last 30 days)
  const thirtyDaysAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString();
  const { count: logsDeleted } = await supabase
    .from("error_logs")
    .delete()
    .lt("created_at", thirtyDaysAgo)
    .select("*", { count: "exact", head: true });
  totalDeleted += logsDeleted || 0;

  // Delete completed/cancelled jobs older than 30 days
  const { count: jobsDeleted } = await supabase
    .from("gpu_jobs")
    .delete()
    .lt("created_at", thirtyDaysAgo)
    .in("status", ["completed", "cancelled", "failed"])
    .select("*", { count: "exact", head: true });
  totalDeleted += jobsDeleted || 0;

  return {
    status: "completed",
    deleted: totalDeleted,
    details: {
      system_metrics: metricsDeleted || 0,
      performance_metrics: perfDeleted || 0,
      error_logs: logsDeleted || 0,
      old_jobs: jobsDeleted || 0,
    },
  };
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
async function recoverStuckJobs(supabase: any) {
  // Jobs that have been running for more than 1 hour are considered stuck
  const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000).toISOString();

  // Find and recover stuck GPU jobs
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const { data: stuckGpuJobs, error: gpuError } = await supabase
    .from("gpu_jobs")
    .update({
      status: "queued",
      progress: 0,
      started_at: null,
      worker_id: null,
      error_message: "Recovered from stuck state",
    })
    .eq("status", "running")
    .lt("started_at", oneHourAgo)
    .select("id");

  // Find and recover stuck inference jobs
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const { data: stuckInferenceJobs, error: inferenceError } = await supabase
    .from("inference_jobs")
    .update({
      status: "queued",
      progress: 0,
      started_at: null,
      error_message: "Recovered from stuck state",
    })
    .eq("status", "running")
    .lt("started_at", oneHourAgo)
    .select("id");

  const recovered = (stuckGpuJobs?.length || 0) + (stuckInferenceJobs?.length || 0);

  if (recovered > 0) {
    console.log(`[HealthMonitor] Recovered ${recovered} stuck jobs`);

    // Create alerts for recovered jobs
    await supabase.from("alerts").insert({
      alert_type: "job_recovery",
      severity: "warning",
      title: "Stuck Jobs Recovered",
      message: `${recovered} jobs were stuck and have been reset to queued status.`,
      metadata: {
        gpu_jobs: stuckGpuJobs?.map((j: { id: string }) => j.id) || [],
        inference_jobs: stuckInferenceJobs?.map((j: { id: string }) => j.id) || [],
      },
    });
  }

  return {
    recovered,
    gpu_jobs: stuckGpuJobs?.length || 0,
    inference_jobs: stuckInferenceJobs?.length || 0,
  };
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
async function checkDatabaseHealth(supabase: any): Promise<HealthCheck> {
  const startTime = Date.now();

  const { error } = await supabase.from("system_settings").select("id").limit(1);
  const duration = Date.now() - startTime;

  return {
    name: "Database Connectivity",
    status: error ? "fail" : duration > 500 ? "warn" : "pass",
    message: error ? `Database error: ${error.message}` : `Connected (${duration}ms)`,
    duration_ms: duration,
  };
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
async function checkJobQueueHealth(supabase: any): Promise<HealthCheck> {
  const startTime = Date.now();

  const { count: queuedCount } = await supabase
    .from("gpu_jobs")
    .select("*", { count: "exact", head: true })
    .in("status", ["pending", "queued"]);

  const { count: runningCount } = await supabase
    .from("gpu_jobs")
    .select("*", { count: "exact", head: true })
    .eq("status", "running");

  const duration = Date.now() - startTime;
  const queued = queuedCount || 0;
  const running = runningCount || 0;

  let status: "pass" | "warn" | "fail" = "pass";
  let message = `${queued} queued, ${running} running`;

  if (queued > 100) {
    status = "fail";
    message = `Queue overloaded: ${queued} jobs waiting`;
  } else if (queued > 50) {
    status = "warn";
    message = `High queue: ${queued} jobs waiting`;
  }

  return { name: "Job Queue", status, message, duration_ms: duration };
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
async function checkStuckJobs(supabase: any): Promise<HealthCheck> {
  const startTime = Date.now();
  const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000).toISOString();

  const { count: stuckCount } = await supabase
    .from("gpu_jobs")
    .select("*", { count: "exact", head: true })
    .eq("status", "running")
    .lt("started_at", oneHourAgo);

  const duration = Date.now() - startTime;
  const stuck = stuckCount || 0;

  return {
    name: "Stuck Jobs",
    status: stuck > 0 ? "fail" : "pass",
    message: stuck > 0 ? `${stuck} jobs appear stuck (running > 1hr)` : "No stuck jobs",
    duration_ms: duration,
  };
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
async function checkErrorRate(supabase: any): Promise<HealthCheck> {
  const startTime = Date.now();
  const oneDayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();

  const { count: totalJobs } = await supabase
    .from("gpu_jobs")
    .select("*", { count: "exact", head: true })
    .gte("created_at", oneDayAgo);

  const { count: failedJobs } = await supabase
    .from("gpu_jobs")
    .select("*", { count: "exact", head: true })
    .eq("status", "failed")
    .gte("created_at", oneDayAgo);

  const duration = Date.now() - startTime;
  const errorRate = totalJobs ? ((failedJobs || 0) / totalJobs) * 100 : 0;

  let status: "pass" | "warn" | "fail" = "pass";
  if (errorRate > 20) {
    status = "fail";
  } else if (errorRate > 10) {
    status = "warn";
  }

  return {
    name: "Error Rate (24h)",
    status,
    message: `${errorRate.toFixed(1)}% error rate (${failedJobs || 0}/${totalJobs || 0} jobs)`,
    duration_ms: duration,
  };
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
async function checkMetricsFreshness(supabase: any): Promise<HealthCheck> {
  const startTime = Date.now();

  const { data: latestMetric } = await supabase
    .from("system_metrics")
    .select("recorded_at")
    .order("recorded_at", { ascending: false })
    .limit(1)
    .single();

  const duration = Date.now() - startTime;

  if (!latestMetric) {
    return {
      name: "Metrics Freshness",
      status: "warn",
      message: "No system metrics found",
      duration_ms: duration,
    };
  }

  const age = Date.now() - new Date(latestMetric.recorded_at).getTime();
  const ageMinutes = Math.floor(age / 60000);

  let status: "pass" | "warn" | "fail" = "pass";
  if (ageMinutes > 30) {
    status = "fail";
  } else if (ageMinutes > 15) {
    status = "warn";
  }

  return {
    name: "Metrics Freshness",
    status,
    message: `Last metric: ${ageMinutes} minutes ago`,
    duration_ms: duration,
  };
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
async function checkModuleHealth(supabase: any): Promise<HealthCheck> {
  const startTime = Date.now();

  const { data: modules } = await supabase.from("module_status").select("status, health_score");

  const duration = Date.now() - startTime;

  if (!modules || modules.length === 0) {
    return {
      name: "Module Health",
      status: "warn",
      message: "No modules found",
      duration_ms: duration,
    };
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const avgHealth =
    modules.reduce((sum: number, m: any) => sum + (m.health_score || 0), 0) / modules.length;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const errorModules = modules.filter((m: any) => m.status === "error").length;

  let status: "pass" | "warn" | "fail" = "pass";
  let message = `Avg health: ${avgHealth.toFixed(0)}%`;

  if (errorModules > 0) {
    status = "fail";
    message = `${errorModules} modules in error state`;
  } else if (avgHealth < 70) {
    status = "warn";
    message = `Low average health: ${avgHealth.toFixed(0)}%`;
  }

  return { name: "Module Health", status, message, duration_ms: duration };
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
async function getSystemHealthMetrics(supabase: any): Promise<SystemHealthMetrics> {
  const oneDayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();

  // Database latency
  const dbStart = Date.now();
  await supabase.from("system_settings").select("id").limit(1);
  const dbLatency = Date.now() - dbStart;

  // Job counts
  const { count: queuedCount } = await supabase
    .from("gpu_jobs")
    .select("*", { count: "exact", head: true })
    .in("status", ["pending", "queued"]);

  const { count: runningCount } = await supabase
    .from("gpu_jobs")
    .select("*", { count: "exact", head: true })
    .eq("status", "running");

  const { count: failedCount } = await supabase
    .from("gpu_jobs")
    .select("*", { count: "exact", head: true })
    .eq("status", "failed")
    .gte("created_at", oneDayAgo);

  const { count: totalCount } = await supabase
    .from("gpu_jobs")
    .select("*", { count: "exact", head: true })
    .gte("created_at", oneDayAgo);

  const errorRate = totalCount ? ((failedCount || 0) / totalCount) * 100 : 0;

  return {
    database_latency_ms: dbLatency,
    active_connections: 1, // Edge function uses single connection
    queued_jobs: queuedCount || 0,
    running_jobs: runningCount || 0,
    failed_jobs_24h: failedCount || 0,
    error_rate_percent: Math.round(errorRate * 10) / 10,
  };
}
