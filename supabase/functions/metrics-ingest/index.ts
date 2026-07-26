import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers":
    "authorization, x-client-info, apikey, content-type, x-device-token",
};

interface MetricsPayload {
  cpu_usage_percent?: number;
  memory_usage_percent?: number;
  memory_total_mb?: number;
  memory_used_mb?: number;
  disk_usage_percent?: number;
  gpu_usage_percent?: number;
  gpu_memory_used_mb?: number;
  gpu_memory_total_mb?: number;
  gpu_temperature_celsius?: number;
  cpu_temperature_celsius?: number;
  network_rx_bytes?: number;
  network_tx_bytes?: number;
  // Legacy field mappings
  gpu_utilization?: number;
  memory_usage?: number;
  temperature?: number;
  power_draw?: number;
  throughput?: number;
}

Deno.serve(async (req) => {
  // Handle CORS preflight
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: corsHeaders });
  }

  const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
  const supabaseServiceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
  const supabase = createClient(supabaseUrl, supabaseServiceKey);

  try {
    // Validate authorization
    const authHeader = req.headers.get("authorization");
    const deviceToken = req.headers.get("x-device-token");

    if (!authHeader && !deviceToken) {
      console.error("[metrics-ingest] Missing authentication");
      return new Response(JSON.stringify({ error: "Authentication required" }), {
        status: 401,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    let userId: string | null = null;
    let deviceId: string | null = null;

    // Authenticate via JWT
    if (authHeader) {
      const token = authHeader.replace("Bearer ", "");
      const {
        data: { user },
        error,
      } = await supabase.auth.getUser(token);
      if (error || !user) {
        console.error("[metrics-ingest] Invalid JWT:", error?.message);
        return new Response(JSON.stringify({ error: "Invalid token" }), {
          status: 401,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        });
      }
      userId = user.id;
    }

    // Validate device token if provided
    if (deviceToken) {
      const { data: device, error } = await supabase
        .from("device_registry")
        .select("id, user_id, is_active")
        .eq("device_token", deviceToken)
        .single();

      if (error || !device) {
        console.error("[metrics-ingest] Invalid device token");
        return new Response(JSON.stringify({ error: "Invalid device token" }), {
          status: 401,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        });
      }

      if (!device.is_active) {
        return new Response(JSON.stringify({ error: "Device is deactivated" }), {
          status: 403,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        });
      }

      deviceId = device.id;
      userId = userId || device.user_id;

      // Update device last seen
      await supabase
        .from("device_registry")
        .update({ last_seen_at: new Date().toISOString() })
        .eq("id", deviceId);
    }

    if (!userId) {
      return new Response(JSON.stringify({ error: "Could not determine user" }), {
        status: 401,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    // Parse and validate metrics
    const payload: MetricsPayload = await req.json();

    // Validate numeric ranges
    const validateRange = (value: number | undefined, min: number, max: number): boolean => {
      if (value === undefined || value === null) return true;
      return typeof value === "number" && value >= min && value <= max;
    };

    if (
      !validateRange(payload.cpu_usage_percent, 0, 100) ||
      !validateRange(payload.memory_usage_percent, 0, 100) ||
      !validateRange(payload.gpu_usage_percent, 0, 100) ||
      !validateRange(payload.disk_usage_percent, 0, 100) ||
      !validateRange(payload.gpu_temperature_celsius, -50, 150) ||
      !validateRange(payload.cpu_temperature_celsius, -50, 150)
    ) {
      console.error("[metrics-ingest] Invalid metric values");
      return new Response(JSON.stringify({ error: "Invalid metric values - check ranges" }), {
        status: 400,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    // Check for completely empty payload
    const hasData = Object.values(payload).some((v) => v !== undefined && v !== null);
    if (!hasData) {
      return new Response(JSON.stringify({ error: "Empty metrics payload" }), {
        status: 400,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    // Insert into system_metrics (supporting both new and legacy fields)
    const { data: insertedMetric, error: insertError } = await supabase
      .from("system_metrics")
      .insert({
        user_id: userId,
        device_id: deviceId,
        gpu_utilization: payload.gpu_usage_percent ?? payload.gpu_utilization,
        memory_usage: payload.memory_usage_percent ?? payload.memory_usage,
        temperature: payload.gpu_temperature_celsius ?? payload.temperature,
        power_draw: payload.power_draw ?? 0,
        throughput: payload.throughput ?? 0,
        cpu_percent: payload.cpu_usage_percent ?? 0,
        disk_gb: payload.disk_usage_percent ? Math.round(payload.disk_usage_percent) : 0,
        active_jobs: 0,
        total_requests: 0,
        status: "active",
        metadata: {
          memory_total_mb: payload.memory_total_mb,
          memory_used_mb: payload.memory_used_mb,
          gpu_memory_used_mb: payload.gpu_memory_used_mb,
          gpu_memory_total_mb: payload.gpu_memory_total_mb,
          cpu_temperature_celsius: payload.cpu_temperature_celsius,
          network_rx_bytes: payload.network_rx_bytes,
          network_tx_bytes: payload.network_tx_bytes,
        },
        recorded_at: new Date().toISOString(),
      })
      .select()
      .single();

    if (insertError) {
      console.error("[metrics-ingest] Insert error:", insertError);
      return new Response(
        JSON.stringify({ error: "Failed to store metrics", details: insertError.message }),
        { status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" } },
      );
    }

    // Update system health based on metrics
    const healthScore = calculateHealthScore(payload);
    await updateSystemHealth(supabase, userId, healthScore, payload);

    console.log(
      `[metrics-ingest] Stored metrics for user ${userId}, device ${deviceId || "direct"}`,
    );

    return new Response(
      JSON.stringify({
        success: true,
        metric_id: insertedMetric.id,
        health_score: healthScore,
        timestamp: new Date().toISOString(),
      }),
      { status: 200, headers: { ...corsHeaders, "Content-Type": "application/json" } },
    );
  } catch (error) {
    console.error("[metrics-ingest] Unexpected error:", error);
    return new Response(JSON.stringify({ error: "Internal server error" }), {
      status: 500,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }
});

function calculateHealthScore(metrics: MetricsPayload): number {
  let score = 100;

  // CPU penalties
  const cpu = metrics.cpu_usage_percent ?? 0;
  if (cpu > 90) score -= 30;
  else if (cpu > 80) score -= 15;
  else if (cpu > 70) score -= 5;

  // Memory penalties
  const mem = metrics.memory_usage_percent ?? 0;
  if (mem > 95) score -= 25;
  else if (mem > 85) score -= 10;
  else if (mem > 75) score -= 5;

  // GPU temperature penalties
  const temp = metrics.gpu_temperature_celsius ?? metrics.temperature ?? 0;
  if (temp > 90) score -= 30;
  else if (temp > 80) score -= 15;
  else if (temp > 70) score -= 5;

  // Disk penalties
  const disk = metrics.disk_usage_percent ?? 0;
  if (disk > 95) score -= 20;
  else if (disk > 85) score -= 10;

  return Math.max(0, Math.min(100, score));
}

// deno-lint-ignore no-explicit-any
async function updateSystemHealth(
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  supabase: any,
  userId: string,
  healthScore: number,
  metrics: MetricsPayload,
) {
  const issues: string[] = [];
  const recommendations: string[] = [];

  const cpu = metrics.cpu_usage_percent ?? 0;
  const mem = metrics.memory_usage_percent ?? 0;
  const temp = metrics.gpu_temperature_celsius ?? metrics.temperature ?? 0;
  const disk = metrics.disk_usage_percent ?? 0;

  if (cpu > 90) {
    issues.push("Critical CPU usage");
    recommendations.push("Consider stopping non-essential processes");
  }
  if (mem > 95) {
    issues.push("Memory nearly exhausted");
    recommendations.push("Free up memory or add more RAM");
  }
  if (temp > 85) {
    issues.push("GPU overheating");
    recommendations.push("Improve cooling or reduce workload");
  }
  if (disk > 90) {
    issues.push("Disk space low");
    recommendations.push("Clean up temporary files");
  }

  const status = healthScore >= 80 ? "healthy" : healthScore >= 50 ? "degraded" : "critical";

  // Upsert system health
  const { error } = await supabase.from("system_health").upsert(
    {
      user_id: userId,
      health_score: healthScore,
      status,
      checks_passed: issues.length === 0 ? 1 : 0,
      checks_failed: issues.length,
      last_check_at: new Date().toISOString(),
      issues: JSON.stringify(issues),
      recommendations: JSON.stringify(recommendations),
    },
    { onConflict: "user_id" },
  );

  if (error) {
    console.error("[metrics-ingest] Failed to update system health:", error);
  }
}
