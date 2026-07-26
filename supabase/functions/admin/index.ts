import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.39.7";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers":
    "authorization, x-client-info, apikey, content-type, x-admin-secret",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
};

// Admin secret - REQUIRED, no fallback
const ADMIN_SECRET = Deno.env.get("ADMIN_SECRET");

interface GPUJob {
  id: string;
  status: string;
  job_tier: string;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
}

interface AgentHeartbeat {
  worker_id: string;
  recorded_at: string;
  is_processing: boolean;
  current_job_id: string | null;
  gpu_temp_celsius: number;
  gpu_vram_used_mb: number;
}

interface AgentToken {
  id: string;
  agent_name: string;
  is_active: boolean;
  last_used_at: string | null;
}

// Input validation helpers
function validatePositiveInt(value: string | null, defaultVal: number, max: number): number {
  if (!value) return defaultVal;
  const parsed = parseInt(value, 10);
  if (isNaN(parsed) || parsed < 0) return defaultVal;
  return Math.min(parsed, max);
}

serve(async (req: Request) => {
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
    const supabaseKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
    const supabase = createClient(supabaseUrl, supabaseKey);

    // Verify admin secret header (only if ADMIN_SECRET is configured)
    const adminSecret = req.headers.get("x-admin-secret");
    const secretValid = ADMIN_SECRET && adminSecret === ADMIN_SECRET;

    if (!secretValid) {
      // Fallback to authenticated admin user check
      const authHeader = req.headers.get("Authorization");
      if (!authHeader) {
        console.log("Admin access denied: No authorization provided");
        return new Response(JSON.stringify({ error: "Unauthorized" }), {
          status: 401,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        });
      }

      const token = authHeader.replace("Bearer ", "");
      const {
        data: { user },
        error: authError,
      } = await supabase.auth.getUser(token);

      if (authError || !user) {
        console.log("Admin access denied: Invalid token");
        return new Response(JSON.stringify({ error: "Invalid token" }), {
          status: 401,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        });
      }

      // Check if user has admin role
      const { data: roles } = await supabase
        .from("user_roles")
        .select("role")
        .eq("user_id", user.id)
        .eq("role", "admin");

      if (!roles || roles.length === 0) {
        console.log(`Admin access denied: User ${user.id} lacks admin role`);
        return new Response(JSON.stringify({ error: "Admin access required" }), {
          status: 403,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        });
      }
    }

    const url = new URL(req.url);
    const action = url.pathname.split("/").pop();

    // GET /admin/summary - Get system summary
    if (req.method === "GET" && action === "summary") {
      console.log("Admin: Fetching system summary");

      // Get job statistics
      const { data: allJobs } = (await supabase
        .from("gpu_jobs")
        .select("id, status, job_tier, created_at, started_at, completed_at")
        .order("created_at", { ascending: false })
        .limit(1000)) as { data: GPUJob[] | null };

      const jobs = (allJobs || []) as GPUJob[];

      const stats = {
        total_jobs: jobs.length,
        pending: jobs.filter((j: GPUJob) => j.status === "pending").length,
        queued: jobs.filter((j: GPUJob) => j.status === "queued").length,
        running: jobs.filter((j: GPUJob) => j.status === "running").length,
        completed: jobs.filter((j: GPUJob) => j.status === "completed").length,
        failed: jobs.filter((j: GPUJob) => j.status === "failed").length,
        cancelled: jobs.filter((j: GPUJob) => j.status === "cancelled").length,
        by_tier: {
          light: jobs.filter((j: GPUJob) => j.job_tier === "light").length,
          medium: jobs.filter((j: GPUJob) => j.job_tier === "medium").length,
          heavy: jobs.filter((j: GPUJob) => j.job_tier === "heavy").length,
        },
      };

      // Calculate average runtime for completed jobs
      const completedJobs = jobs.filter(
        (j: GPUJob) => j.status === "completed" && j.started_at && j.completed_at,
      );
      let avgRuntimeMs = 0;
      if (completedJobs.length > 0) {
        const totalRuntime = completedJobs.reduce((acc: number, j: GPUJob) => {
          return acc + (new Date(j.completed_at!).getTime() - new Date(j.started_at!).getTime());
        }, 0);
        avgRuntimeMs = totalRuntime / completedJobs.length;
      }

      // Get queue depth
      const { count: queueDepth } = await supabase
        .from("job_queue")
        .select("*", { count: "exact", head: true });

      // Get active agents
      const { data: recentHeartbeats } = (await supabase
        .from("agent_heartbeats")
        .select("worker_id, recorded_at, is_processing, current_job_id, gpu_temp_celsius")
        .order("recorded_at", { ascending: false })
        .limit(100)) as { data: AgentHeartbeat[] | null };

      // Get unique workers with recent heartbeats (last 60 seconds)
      const now = Date.now();
      const activeWorkers = new Map<string, AgentHeartbeat>();
      for (const hb of recentHeartbeats || []) {
        const age = now - new Date(hb.recorded_at).getTime();
        if (age < 60000 && !activeWorkers.has(hb.worker_id)) {
          activeWorkers.set(hb.worker_id, hb);
        }
      }

      // Get agent tokens
      const { data: agents } = (await supabase
        .from("agent_tokens")
        .select("id, agent_name, is_active, last_used_at")
        .eq("is_active", true)) as { data: AgentToken[] | null };

      return new Response(
        JSON.stringify({
          stats,
          queue_depth: queueDepth || 0,
          avg_runtime_ms: Math.round(avgRuntimeMs),
          avg_runtime_formatted: formatDuration(avgRuntimeMs),
          active_workers: Array.from(activeWorkers.values()),
          registered_agents: agents || [],
          timestamp: new Date().toISOString(),
        }),
        {
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        },
      );
    }

    // GET /admin/jobs - Get all jobs (admin view)
    if (req.method === "GET" && action === "jobs") {
      const limit = validatePositiveInt(url.searchParams.get("limit"), 100, 500);
      const offset = validatePositiveInt(url.searchParams.get("offset"), 0, 100000);

      console.log(`Admin: Fetching jobs (limit=${limit}, offset=${offset})`);

      const {
        data: jobs,
        count,
        error,
      } = (await supabase
        .from("gpu_jobs")
        .select("*", { count: "exact" })
        .order("created_at", { ascending: false })
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        .range(offset, offset + limit - 1)) as {
        data: GPUJob[] | null;
        count: number | null;
        error: any;
      };

      if (error) throw error;

      return new Response(JSON.stringify({ jobs, total: count }), {
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    // GET /admin/agents - Get agent status
    if (req.method === "GET" && action === "agents") {
      console.log("Admin: Fetching agent status");

      const { data: agents } = (await supabase
        .from("agent_tokens")
        .select("*")
        .order("last_used_at", { ascending: false })) as { data: AgentToken[] | null };

      // Get latest heartbeat for each agent
      const agentsWithStatus = await Promise.all(
        (agents || []).map(async (agent) => {
          const { data: heartbeats } = await supabase
            .from("agent_heartbeats")
            .select("*")
            .eq("agent_token_id", agent.id)
            .order("recorded_at", { ascending: false })
            .limit(1);

          const latestHeartbeat = heartbeats?.[0];
          const isOnline =
            latestHeartbeat && Date.now() - new Date(latestHeartbeat.recorded_at).getTime() < 60000;

          return {
            ...agent,
            is_online: isOnline,
            latest_heartbeat: latestHeartbeat,
          };
        }),
      );

      return new Response(JSON.stringify({ agents: agentsWithStatus }), {
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    // GET /admin/metrics - Get system metrics
    if (req.method === "GET" && action === "metrics") {
      const hours = validatePositiveInt(url.searchParams.get("hours"), 24, 168);
      const since = new Date(Date.now() - hours * 60 * 60 * 1000).toISOString();

      console.log(`Admin: Fetching metrics (hours=${hours})`);

      // Jobs created in time window
      const { data: recentJobs } = (await supabase
        .from("gpu_jobs")
        .select("id, status, job_tier, created_at, completed_at")
        .gte("created_at", since)) as { data: GPUJob[] | null };

      // Agent heartbeats in time window
      const { data: heartbeats } = (await supabase
        .from("agent_heartbeats")
        .select("gpu_temp_celsius, gpu_vram_used_mb, recorded_at")
        .gte("recorded_at", since)
        .order("recorded_at", { ascending: true })) as { data: AgentHeartbeat[] | null };

      // Calculate metrics
      const jobs = recentJobs || [];
      const successRate =
        jobs.length > 0
          ? (
              (jobs.filter((j: GPUJob) => j.status === "completed").length / jobs.length) *
              100
            ).toFixed(1)
          : "0.0";

      // Average GPU temp over time
      const temps = (heartbeats || [])
        .map((h: AgentHeartbeat) => h.gpu_temp_celsius)
        .filter((t: number) => t != null);
      const avgTemp =
        temps.length > 0
          ? (temps.reduce((a: number, b: number) => a + b, 0) / temps.length).toFixed(1)
          : null;

      return new Response(
        JSON.stringify({
          time_window_hours: hours,
          jobs_created: jobs.length,
          jobs_completed: jobs.filter((j: GPUJob) => j.status === "completed").length,
          jobs_failed: jobs.filter((j: GPUJob) => j.status === "failed").length,
          success_rate_percent: successRate,
          avg_gpu_temp: avgTemp,
          heartbeat_count: heartbeats?.length || 0,
        }),
        {
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        },
      );
    }

    return new Response(JSON.stringify({ error: "Not found" }), {
      status: 404,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  } catch (error) {
    console.error("Admin function error:", error);
    // Return generic error to client, log details server-side only
    return new Response(JSON.stringify({ error: "An internal error occurred" }), {
      status: 500,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }
});

function formatDuration(ms: number): string {
  if (ms < 1000) return `${ms}ms`;
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
  if (ms < 3600000) return `${(ms / 60000).toFixed(1)}m`;
  return `${(ms / 3600000).toFixed(1)}h`;
}
