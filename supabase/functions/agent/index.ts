// @ts-nocheck
import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "@supabase/supabase-js";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers":
    "authorization, x-client-info, apikey, content-type, x-agent-token",
  "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
};

// Validation constants
const MAX_AGENT_NAME_LENGTH = 100;
const MAX_SECRET_LENGTH = 256;
const MAX_WORKER_ID_LENGTH = 100;
const MAX_MESSAGE_LENGTH = 1000;
const MAX_LOG_MESSAGE_LENGTH = 5000;
const MAX_CHECKPOINT_SIZE = 1000000; // 1MB
const MIN_TEMP = -50;
const MAX_TEMP = 150;
const MAX_VRAM_MB = 100000;
const MAX_CPU_PERCENT = 100;

// Input validation helpers
function validateString(value: unknown, maxLength: number): string | null {
  if (typeof value !== "string") return null;
  const trimmed = value.trim();
  if (trimmed.length === 0 || trimmed.length > maxLength) return null;
  return trimmed;
}

function validateNumber(value: unknown, min: number, max: number): number | null {
  if (typeof value !== "number" || isNaN(value)) return null;
  if (value < min || value > max) return null;
  return value;
}

function validateOptionalNumber(value: unknown, min: number, max: number): number | undefined {
  if (value === undefined || value === null) return undefined;
  const result = validateNumber(value, min, max);
  return result !== null ? result : undefined;
}

function isValidUUID(str: unknown): boolean {
  if (typeof str !== "string") return false;
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
  return uuidRegex.test(str);
}

function validateCheckpointData(value: unknown): Record<string, unknown> | null {
  if (typeof value !== "object" || value === null) return null;
  const jsonStr = JSON.stringify(value);
  if (jsonStr.length > MAX_CHECKPOINT_SIZE) return null;
  return value as Record<string, unknown>;
}

function validateLogLevel(value: unknown): string {
  const validLevels = ["debug", "info", "warn", "error"];
  if (typeof value !== "string" || !validLevels.includes(value)) return "info";
  return value;
}

serve(async (req: Request) => {
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
    const supabaseKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
    const supabase = createClient(supabaseUrl, supabaseKey);

    const url = new URL(req.url);
    const action = url.pathname.split("/").pop();

    // POST /agent/register - Register a new agent
    if (req.method === "POST" && action === "register") {
      let body: unknown;
      try {
        body = await req.json();
      } catch {
        return new Response(JSON.stringify({ error: "Invalid JSON body" }), {
          status: 400,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        });
      }

      if (typeof body !== "object" || body === null) {
        return new Response(JSON.stringify({ error: "Request body must be an object" }), {
          status: 400,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        });
      }

      const reqBody = body as Record<string, unknown>;
      const agent_name = validateString(reqBody.agent_name, MAX_AGENT_NAME_LENGTH);
      const secret = validateString(reqBody.secret, MAX_SECRET_LENGTH);

      if (!agent_name) {
        return new Response(
          JSON.stringify({ error: `agent_name is required (max ${MAX_AGENT_NAME_LENGTH} chars)` }),
          {
            status: 400,
            headers: { ...corsHeaders, "Content-Type": "application/json" },
          },
        );
      }

      if (!secret || secret.length < 32) {
        return new Response(
          JSON.stringify({ error: "secret is required and must be at least 32 characters" }),
          {
            status: 400,
            headers: { ...corsHeaders, "Content-Type": "application/json" },
          },
        );
      }

      // Hash the secret
      const encoder = new TextEncoder();
      const data = encoder.encode(secret);
      const hashBuffer = await crypto.subtle.digest("SHA-256", data);
      const hashArray = Array.from(new Uint8Array(hashBuffer));
      const secretHash = hashArray.map((b) => b.toString(16).padStart(2, "0")).join("");

      const { data: token, error } = await supabase
        .from("agent_tokens")
        .insert({
          agent_name,
          secret_hash: secretHash,
          allowed_until: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString(),
        })
        .select()
        .single();

      if (error) throw error;

      console.log(`Agent registered: ${agent_name}`);
      return new Response(
        JSON.stringify({
          token_id: token.id,
          agent_name: token.agent_name,
          message: "Agent registered. Store your secret securely - it cannot be retrieved later.",
        }),
        {
          status: 201,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        },
      );
    }

    // Validate agent token for other endpoints
    const agentToken = req.headers.get("x-agent-token");
    if (!agentToken || agentToken.length > MAX_SECRET_LENGTH) {
      return new Response(JSON.stringify({ error: "Valid agent token required" }), {
        status: 401,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    // Hash the provided token
    const encoder = new TextEncoder();
    const tokenData = encoder.encode(agentToken);
    const tokenHashBuffer = await crypto.subtle.digest("SHA-256", tokenData);
    const tokenHashArray = Array.from(new Uint8Array(tokenHashBuffer));
    const tokenHash = tokenHashArray.map((b) => b.toString(16).padStart(2, "0")).join("");

    // Find matching agent
    const { data: agent, error: agentError } = await supabase
      .from("agent_tokens")
      .select("*")
      .eq("secret_hash", tokenHash)
      .eq("is_active", true)
      .single();

    if (agentError || !agent) {
      return new Response(JSON.stringify({ error: "Invalid agent token" }), {
        status: 401,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    // Check if token is expired
    if (agent.allowed_until && new Date(agent.allowed_until) < new Date()) {
      return new Response(JSON.stringify({ error: "Agent token expired" }), {
        status: 401,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    // Update last used
    await supabase
      .from("agent_tokens")
      .update({ last_used_at: new Date().toISOString() })
      .eq("id", agent.id);

    // Parse and validate request body for POST endpoints
    let reqBody: Record<string, unknown> = {};
    if (req.method === "POST") {
      try {
        const parsed = await req.json();
        if (typeof parsed === "object" && parsed !== null) {
          reqBody = parsed as Record<string, unknown>;
        }
      } catch {
        return new Response(JSON.stringify({ error: "Invalid JSON body" }), {
          status: 400,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        });
      }
    }

    // POST /agent/poll - Get next job from queue
    if (req.method === "POST" && action === "poll") {
      const worker_id = validateString(reqBody.worker_id, MAX_WORKER_ID_LENGTH);
      if (!worker_id) {
        return new Response(JSON.stringify({ error: "worker_id is required" }), {
          status: 400,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        });
      }

      const gpu_temp = validateOptionalNumber(reqBody.gpu_temp, MIN_TEMP, MAX_TEMP);
      const gpu_vram_used = validateOptionalNumber(reqBody.gpu_vram_used, 0, MAX_VRAM_MB);
      const gpu_vram_total = validateOptionalNumber(reqBody.gpu_vram_total, 0, MAX_VRAM_MB);
      const cpu_temp = validateOptionalNumber(reqBody.cpu_temp, MIN_TEMP, MAX_TEMP);
      const cpu_usage = validateOptionalNumber(reqBody.cpu_usage, 0, MAX_CPU_PERCENT);

      // Record heartbeat
      await supabase.from("agent_heartbeats").insert({
        agent_token_id: agent.id,
        worker_id,
        gpu_temp_celsius: gpu_temp,
        gpu_vram_used_mb: gpu_vram_used,
        gpu_vram_total_mb: gpu_vram_total,
        cpu_temp_celsius: cpu_temp,
        cpu_usage_percent: cpu_usage,
        is_processing: false,
      });

      // Get system settings
      const { data: settings } = await supabase.from("system_settings").select("*");

      const settingsMap = Object.fromEntries((settings || []).map((s) => [s.key, s.value]));

      const thermalWarning = settingsMap.gpu_thermal_warning?.celsius || 80;
      const thermalCritical = settingsMap.gpu_thermal_critical?.celsius || 85;
      const vramLimitPercent = settingsMap.gpu_vram_limit_percent?.percent || 80;

      // Check thermal status
      if (gpu_temp && gpu_temp >= thermalCritical) {
        console.log(`Agent ${agent.agent_name} thermal critical: ${gpu_temp}°C`);
        return new Response(
          JSON.stringify({
            job: null,
            reason: "thermal_critical",
            message: `GPU temperature ${gpu_temp}°C exceeds critical threshold ${thermalCritical}°C`,
          }),
          {
            headers: { ...corsHeaders, "Content-Type": "application/json" },
          },
        );
      }

      // Check VRAM availability
      const vramAvailable = gpu_vram_total ? gpu_vram_total - (gpu_vram_used || 0) : 24576;
      const maxJobVram = gpu_vram_total ? (gpu_vram_total * vramLimitPercent) / 100 : 19660;

      // Check if agent is already processing a job
      const { data: runningJobs } = await supabase
        .from("gpu_jobs")
        .select("*")
        .eq("worker_id", worker_id)
        .eq("status", "running")
        .limit(1);

      if (runningJobs && runningJobs.length > 0) {
        return new Response(
          JSON.stringify({
            job: null,
            reason: "already_processing",
            current_job_id: runningJobs[0].id,
          }),
          {
            headers: { ...corsHeaders, "Content-Type": "application/json" },
          },
        );
      }

      // Get next job from queue
      const { data: queueItems, error: queueError } = await supabase
        .from("job_queue")
        .select(
          `
          *,
          job:gpu_jobs(*)
        `,
        )
        .order("priority", { ascending: false })
        .order("enqueued_at", { ascending: true })
        .limit(10);

      if (queueError) throw queueError;

      // Find a job that fits in available VRAM
      let selectedJob = null;
      for (const item of queueItems || []) {
        const job = item.job;
        if (!job || job.status !== "queued") continue;

        const jobMemory = job.memory_required_mb || 4096;
        if (jobMemory <= vramAvailable && jobMemory <= maxJobVram) {
          selectedJob = job;
          break;
        }
      }

      if (!selectedJob) {
        return new Response(
          JSON.stringify({
            job: null,
            reason: "no_suitable_jobs",
            vram_available_mb: vramAvailable,
            max_job_vram_mb: maxJobVram,
          }),
          {
            headers: { ...corsHeaders, "Content-Type": "application/json" },
          },
        );
      }

      // Claim the job
      const { error: claimError } = await supabase
        .from("gpu_jobs")
        .update({
          status: "running",
          worker_id,
          worker_signature: agent.agent_name,
          started_at: new Date().toISOString(),
        })
        .eq("id", selectedJob.id)
        .eq("status", "queued");

      if (claimError) throw claimError;

      // Remove from queue
      await supabase.from("job_queue").delete().eq("job_id", selectedJob.id);

      // Log job start
      await supabase.from("job_logs").insert({
        job_id: selectedJob.id,
        level: "info",
        message: `Job claimed by agent ${agent.agent_name} on worker ${worker_id}`,
      });

      // Update heartbeat to show processing
      await supabase.from("agent_heartbeats").insert({
        agent_token_id: agent.id,
        worker_id,
        gpu_temp_celsius: gpu_temp,
        gpu_vram_used_mb: gpu_vram_used,
        gpu_vram_total_mb: gpu_vram_total,
        cpu_temp_celsius: cpu_temp,
        cpu_usage_percent: cpu_usage,
        is_processing: true,
        current_job_id: selectedJob.id,
      });

      console.log(`Job ${selectedJob.id} claimed by ${agent.agent_name}`);
      return new Response(
        JSON.stringify({
          job: selectedJob,
          thermal_warning: gpu_temp !== undefined && gpu_temp >= thermalWarning,
        }),
        {
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        },
      );
    }

    // POST /agent/complete - Mark job as completed
    if (req.method === "POST" && action === "complete") {
      if (!isValidUUID(reqBody.job_id)) {
        return new Response(JSON.stringify({ error: "Valid job_id required" }), {
          status: 400,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        });
      }

      const job_id = reqBody.job_id as string;
      const result_data = typeof reqBody.result_data === "object" ? reqBody.result_data : null;
      const result_url = validateString(reqBody.result_url, 2000);
      const artifacts = Array.isArray(reqBody.artifacts) ? reqBody.artifacts : [];
      const log = validateString(reqBody.log, MAX_LOG_MESSAGE_LENGTH) || "";

      // Update job status
      const { error: updateError } = await supabase
        .from("gpu_jobs")
        .update({
          status: "completed",
          progress: 100,
          result_data,
          result_url,
          completed_at: new Date().toISOString(),
        })
        .eq("id", job_id);

      if (updateError) throw updateError;

      // Save results
      await supabase.from("job_results").insert({
        job_id,
        log,
        artifacts_json: artifacts,
      });

      // Log completion
      await supabase.from("job_logs").insert({
        job_id,
        level: "info",
        message: "Job completed successfully",
      });

      console.log(`Job ${job_id} completed`);
      return new Response(JSON.stringify({ success: true }), {
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    // POST /agent/log - Add log entry for a job
    if (req.method === "POST" && action === "log") {
      if (!isValidUUID(reqBody.job_id)) {
        return new Response(JSON.stringify({ error: "Valid job_id required" }), {
          status: 400,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        });
      }

      const message = validateString(reqBody.message, MAX_LOG_MESSAGE_LENGTH);
      if (!message) {
        return new Response(JSON.stringify({ error: "message is required" }), {
          status: 400,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        });
      }

      const job_id = reqBody.job_id as string;
      const level = validateLogLevel(reqBody.level);
      const metadata =
        typeof reqBody.metadata === "object" && reqBody.metadata !== null ? reqBody.metadata : {};

      // Also update progress if provided
      const progress = validateOptionalNumber(reqBody.progress, 0, 100);
      if (progress !== undefined) {
        await supabase.from("gpu_jobs").update({ progress }).eq("id", job_id);
      }

      const { error } = await supabase.from("job_logs").insert({
        job_id,
        level,
        message,
        metadata,
      });

      if (error) throw error;

      return new Response(JSON.stringify({ success: true }), {
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    // POST /agent/checkpoint - Save checkpoint for job recovery
    if (req.method === "POST" && action === "checkpoint") {
      if (!isValidUUID(reqBody.job_id)) {
        return new Response(JSON.stringify({ error: "Valid job_id required" }), {
          status: 400,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        });
      }

      const checkpoint_data = validateCheckpointData(reqBody.checkpoint_data);
      if (!checkpoint_data) {
        return new Response(
          JSON.stringify({ error: `checkpoint_data required (max ${MAX_CHECKPOINT_SIZE} bytes)` }),
          {
            status: 400,
            headers: { ...corsHeaders, "Content-Type": "application/json" },
          },
        );
      }

      const job_id = reqBody.job_id as string;
      const progress = validateOptionalNumber(reqBody.progress, 0, 100);

      const { error } = await supabase
        .from("gpu_jobs")
        .update({
          checkpoint_data,
          checkpoint_at: new Date().toISOString(),
          progress: progress || undefined,
        })
        .eq("id", job_id);

      if (error) throw error;

      await supabase.from("job_logs").insert({
        job_id,
        level: "info",
        message: `Checkpoint saved at ${progress || 0}% progress`,
      });

      console.log(`Checkpoint saved for job ${job_id}`);
      return new Response(JSON.stringify({ success: true }), {
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    // POST /agent/fail - Mark job as failed with optional retry
    if (req.method === "POST" && action === "fail") {
      if (!isValidUUID(reqBody.job_id)) {
        return new Response(JSON.stringify({ error: "Valid job_id required" }), {
          status: 400,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        });
      }

      const job_id = reqBody.job_id as string;
      const error_message =
        validateString(reqBody.error_message, MAX_MESSAGE_LENGTH) || "Unknown error";
      const should_retry = reqBody.should_retry !== false;

      // Get current job state
      const { data: job } = await supabase.from("gpu_jobs").select("*").eq("id", job_id).single();

      if (!job) {
        return new Response(JSON.stringify({ error: "Job not found" }), {
          status: 404,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        });
      }

      const retryCount = (job.retry_count || 0) + 1;
      const maxRetries = job.max_retries || 3;

      if (should_retry && retryCount <= maxRetries) {
        // Requeue the job
        await supabase
          .from("gpu_jobs")
          .update({
            status: "queued",
            worker_id: null,
            worker_signature: null,
            retry_count: retryCount,
            error_message: `Retry ${retryCount}/${maxRetries}: ${error_message}`,
          })
          .eq("id", job_id);

        await supabase.from("job_queue").insert({
          job_id,
          priority: job.priority,
        });

        await supabase.from("job_logs").insert({
          job_id,
          level: "warn",
          message: `Job failed, retrying (${retryCount}/${maxRetries}): ${error_message}`,
        });

        console.log(`Job ${job_id} failed, retry ${retryCount}/${maxRetries}`);
        return new Response(
          JSON.stringify({ success: true, retried: true, retry_count: retryCount }),
          {
            headers: { ...corsHeaders, "Content-Type": "application/json" },
          },
        );
      }

      // Mark as permanently failed
      await supabase
        .from("gpu_jobs")
        .update({
          status: "failed",
          error_message,
          completed_at: new Date().toISOString(),
        })
        .eq("id", job_id);

      await supabase.from("job_logs").insert({
        job_id,
        level: "error",
        message: `Job failed permanently: ${error_message}`,
      });

      console.log(`Job ${job_id} failed permanently`);
      return new Response(JSON.stringify({ success: true, retried: false }), {
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    // POST /agent/thermal-pause - Pause job due to thermal issues
    if (req.method === "POST" && action === "thermal-pause") {
      if (!isValidUUID(reqBody.job_id)) {
        return new Response(JSON.stringify({ error: "Valid job_id required" }), {
          status: 400,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        });
      }

      const job_id = reqBody.job_id as string;
      const gpu_temp = validateOptionalNumber(reqBody.gpu_temp, MIN_TEMP, MAX_TEMP);
      const checkpoint_data = validateCheckpointData(reqBody.checkpoint_data);

      const { error } = await supabase
        .from("gpu_jobs")
        .update({
          thermal_paused: true,
          checkpoint_data: checkpoint_data || undefined,
          checkpoint_at: checkpoint_data ? new Date().toISOString() : undefined,
        })
        .eq("id", job_id);

      if (error) throw error;

      await supabase.from("job_logs").insert({
        job_id,
        level: "warn",
        message: `Job thermally paused${gpu_temp ? ` at ${gpu_temp}°C` : ""}`,
      });

      console.log(`Job ${job_id} thermally paused`);
      return new Response(JSON.stringify({ success: true }), {
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    return new Response(JSON.stringify({ error: "Not found" }), {
      status: 404,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  } catch (error) {
    console.error("Agent function error:", error);
    // Return generic error to client, log details server-side only
    return new Response(JSON.stringify({ error: "An internal error occurred" }), {
      status: 500,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }
});
