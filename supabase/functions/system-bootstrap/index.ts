import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

const DEFAULT_MODULES = [
  { name: "TensorRT Optimizer", version: "8.6.1", status: "active" },
  { name: "CUDA Accelerator", version: "12.0", status: "active" },
  { name: "Memory Manager", version: "2.4.0", status: "active" },
  { name: "Batch Processor", version: "3.1.0", status: "active" },
  { name: "Cache Engine", version: "1.8.2", status: "inactive" },
  { name: "Load Balancer", version: "2.0.0", status: "active" },
  { name: "Thermal Guardian", version: "1.5.0", status: "active" },
  { name: "Queue Manager", version: "2.2.1", status: "active" },
];

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: corsHeaders });
  }

  const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
  const supabaseServiceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
  const supabase = createClient(supabaseUrl, supabaseServiceKey);

  try {
    // Authenticate user
    const authHeader = req.headers.get("authorization");
    if (!authHeader) {
      return new Response(
        JSON.stringify({ error: "Authorization required" }),
        { status: 401, headers: { ...corsHeaders, "Content-Type": "application/json" } }
      );
    }

    const token = authHeader.replace("Bearer ", "");
    const { data: { user }, error: authError } = await supabase.auth.getUser(token);

    if (authError || !user) {
      return new Response(
        JSON.stringify({ error: "Invalid token" }),
        { status: 401, headers: { ...corsHeaders, "Content-Type": "application/json" } }
      );
    }

    const userId = user.id;
    const results: Record<string, unknown> = {
      user_id: userId,
      initialized: [],
      existing: [],
      errors: [],
    };

    console.log(`[system-bootstrap] Starting bootstrap for user ${userId}`);

    // 1. Initialize system_health if missing
    const { data: existingHealth } = await supabase
      .from("system_health")
      .select("id")
      .eq("user_id", userId)
      .single();

    if (!existingHealth) {
      const { error } = await supabase.from("system_health").insert({
        user_id: userId,
        health_score: 100,
        status: "healthy",
        checks_passed: 0,
        checks_failed: 0,
        issues: "[]",
        recommendations: "[]",
      });
      if (error) {
        (results.errors as string[]).push(`system_health: ${error.message}`);
      } else {
        (results.initialized as string[]).push("system_health");
      }
    } else {
      (results.existing as string[]).push("system_health");
    }

    // 2. Initialize default modules
    for (const mod of DEFAULT_MODULES) {
      const { data: existingModule } = await supabase
        .from("module_status")
        .select("id")
        .eq("user_id", userId)
        .eq("module_name", mod.name)
        .single();

      if (!existingModule) {
        const { error } = await supabase.from("module_status").insert({
          user_id: userId,
          module_name: mod.name,
          status: mod.status,
          version: mod.version,
          error_count: 0,
          success_count: 0,
          config: {},
        });
        if (error) {
          (results.errors as string[]).push(`module ${mod.name}: ${error.message}`);
        } else {
          (results.initialized as string[]).push(`module:${mod.name}`);
        }
      } else {
        (results.existing as string[]).push(`module:${mod.name}`);
      }
    }

    // 3. Ensure subscription exists
    const { data: existingSub } = await supabase
      .from("billing_subscriptions")
      .select("id")
      .eq("user_id", userId)
      .single();

    if (!existingSub) {
      const { error } = await supabase.from("billing_subscriptions").insert({
        user_id: userId,
        plan: "free",
        status: "active",
        started_at: new Date().toISOString(),
      });
      if (error) {
        (results.errors as string[]).push(`subscription: ${error.message}`);
      } else {
        (results.initialized as string[]).push("subscription");
      }
    } else {
      (results.existing as string[]).push("subscription");
    }

    // 4. Ensure profile exists
    const { data: existingProfile } = await supabase
      .from("profiles")
      .select("id")
      .eq("user_id", userId)
      .single();

    if (!existingProfile) {
      const { error } = await supabase.from("profiles").insert({
        user_id: userId,
        full_name: user.email?.split("@")[0] || "User",
      });
      if (error && !error.message.includes("duplicate")) {
        (results.errors as string[]).push(`profile: ${error.message}`);
      } else {
        (results.initialized as string[]).push("profile");
      }
    } else {
      (results.existing as string[]).push("profile");
    }

    // 5. Seed initial metrics if none exist
    const { data: existingMetrics, error: metricsError } = await supabase
      .from("system_metrics")
      .select("id")
      .eq("user_id", userId)
      .limit(1);

    if (!metricsError && (!existingMetrics || existingMetrics.length === 0)) {
      const { error } = await supabase.from("system_metrics").insert({
        user_id: userId,
        gpu_utilization: 45,
        memory_usage: 62,
        temperature: 58,
        power_draw: 180,
        throughput: 1250,
        cpu_percent: 35,
        disk_gb: 45,
        active_jobs: 0,
        total_requests: 0,
        status: "active",
        metadata: { source: "bootstrap" },
      });
      if (error) {
        (results.errors as string[]).push(`initial_metrics: ${error.message}`);
      } else {
        (results.initialized as string[]).push("initial_metrics");
      }
    } else {
      (results.existing as string[]).push("metrics");
    }

    // 6. Verify system integrity
    const integrityChecks = await runIntegrityChecks(supabase, userId);
    results.integrity = integrityChecks;

    console.log(`[system-bootstrap] Completed for user ${userId}:`, results);

    return new Response(
      JSON.stringify({
        success: true,
        ...results,
        timestamp: new Date().toISOString(),
      }),
      { status: 200, headers: { ...corsHeaders, "Content-Type": "application/json" } }
    );

  } catch (error) {
    console.error("[system-bootstrap] Error:", error);
    // Return generic error to client, log details server-side only
    return new Response(
      JSON.stringify({ error: "An internal error occurred" }),
      { status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" } }
    );
  }
});

// deno-lint-ignore no-explicit-any
async function runIntegrityChecks(
  supabase: any,
  userId: string
): Promise<Record<string, boolean>> {
  const checks: Record<string, boolean> = {};

  // Check profile
  const { data: profile } = await supabase
    .from("profiles")
    .select("id")
    .eq("user_id", userId)
    .single();
  checks.profile_exists = !!profile;

  // Check subscription
  const { data: sub } = await supabase
    .from("billing_subscriptions")
    .select("id")
    .eq("user_id", userId)
    .single();
  checks.subscription_exists = !!sub;

  // Check system health
  const { data: health } = await supabase
    .from("system_health")
    .select("id")
    .eq("user_id", userId)
    .single();
  checks.health_tracking = !!health;

  // Check modules
  const { data: modules } = await supabase
    .from("module_status")
    .select("id")
    .eq("user_id", userId);
  checks.modules_configured = (modules?.length ?? 0) > 0;

  // Check metrics
  const { data: metrics } = await supabase
    .from("system_metrics")
    .select("id")
    .eq("user_id", userId)
    .limit(1);
  checks.metrics_available = (metrics?.length ?? 0) > 0;

  return checks;
}
