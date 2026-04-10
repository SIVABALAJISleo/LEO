import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
};

// Validation constants
const MAX_JOB_NAME_LENGTH = 200;
const MAX_JOB_TYPE_LENGTH = 50;
const MAX_PAYLOAD_SIZE = 100000; // 100KB
const VALID_JOB_TIERS = ["light", "medium", "heavy"];
const MIN_PRIORITY = 1;
const MAX_PRIORITY = 10;
const MAX_MEMORY_MB = 49152; // 48GB max
const MAX_DURATION_SEC = 86400; // 24 hours max

// Input validation helpers
function validateString(value: unknown, maxLength: number): string | null {
  if (typeof value !== "string") return null;
  const trimmed = value.trim();
  if (trimmed.length === 0 || trimmed.length > maxLength) return null;
  return trimmed;
}

function validatePositiveInt(value: unknown, min: number, max: number, defaultVal: number): number {
  if (typeof value !== "number" || !Number.isInteger(value)) return defaultVal;
  if (value < min || value > max) return defaultVal;
  return value;
}

function validateJobTier(value: unknown): string {
  if (typeof value !== "string" || !VALID_JOB_TIERS.includes(value)) return "heavy";
  return value;
}

function validatePayload(value: unknown): Record<string, unknown> | null {
  if (typeof value !== "object" || value === null || Array.isArray(value)) return null;
  const jsonStr = JSON.stringify(value);
  if (jsonStr.length > MAX_PAYLOAD_SIZE) return null;
  return value as Record<string, unknown>;
}

function isValidUUID(str: string): boolean {
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
  return uuidRegex.test(str);
}

serve(async (req) => {
  // Handle CORS
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
    const supabaseKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
    const supabase = createClient(supabaseUrl, supabaseKey);

    // Get auth header
    const authHeader = req.headers.get("Authorization");
    if (!authHeader) {
      return new Response(JSON.stringify({ error: "Unauthorized" }), {
        status: 401,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    // Verify user
    const token = authHeader.replace("Bearer ", "");
    const { data: { user }, error: authError } = await supabase.auth.getUser(token);
    
    if (authError || !user) {
      return new Response(JSON.stringify({ error: "Invalid token" }), {
        status: 401,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    const url = new URL(req.url);
    const pathParts = url.pathname.split("/").filter(Boolean);
    const jobId = pathParts.length > 1 ? pathParts[1] : null;

    // Validate jobId if provided
    if (jobId && !isValidUUID(jobId)) {
      return new Response(JSON.stringify({ error: "Invalid job ID format" }), {
        status: 400,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    // POST /jobs - Create a new job
    if (req.method === "POST" && !jobId) {
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
      
      // Validate required fields
      const job_type = validateString(reqBody.job_type, MAX_JOB_TYPE_LENGTH);
      if (!job_type) {
        return new Response(JSON.stringify({ error: `job_type is required and must be 1-${MAX_JOB_TYPE_LENGTH} characters` }), {
          status: 400,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        });
      }

      const payload = validatePayload(reqBody.payload);
      if (!payload) {
        return new Response(JSON.stringify({ error: `payload is required and must be an object under ${MAX_PAYLOAD_SIZE} bytes` }), {
          status: 400,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        });
      }

      // Validate optional fields
      const job_name = validateString(reqBody.job_name, MAX_JOB_NAME_LENGTH) || `${job_type} Job`;
      const priority = validatePositiveInt(reqBody.priority as number, MIN_PRIORITY, MAX_PRIORITY, 5);
      const tier = validateJobTier(reqBody.job_tier);
      const memory_required_mb = reqBody.memory_required_mb !== undefined 
        ? validatePositiveInt(reqBody.memory_required_mb as number, 1, MAX_MEMORY_MB, 4096)
        : undefined;
      const estimated_duration_sec = reqBody.estimated_duration_sec !== undefined
        ? validatePositiveInt(reqBody.estimated_duration_sec as number, 1, MAX_DURATION_SEC, 300)
        : undefined;

      console.log(`Creating job: type=${job_type}, tier=${tier}, user=${user.id}`);

      // Light jobs: run immediately (text processing, metadata)
      if (tier === "light") {
        const result = await processLightJob(job_type, payload);
        
        const { data: job, error } = await supabase
          .from("gpu_jobs")
          .insert({
            user_id: user.id,
            job_type,
            job_name,
            payload,
            priority,
            job_tier: "light",
            status: "completed",
            progress: 100,
            result_data: result,
            started_at: new Date().toISOString(),
            completed_at: new Date().toISOString(),
          })
          .select()
          .single();

        if (error) throw error;

        console.log(`Light job completed: ${job.id}`);
        return new Response(JSON.stringify({ job, result }), {
          status: 201,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        });
      }

      // Medium and heavy jobs go to queue
      const { data: job, error } = await supabase
        .from("gpu_jobs")
        .insert({
          user_id: user.id,
          job_type,
          job_name,
          payload,
          priority,
          job_tier: tier,
          memory_required_mb,
          estimated_duration_sec,
          status: "queued",
        })
        .select()
        .single();

      if (error) throw error;

      // Add to job queue for heavy jobs
      if (tier === "heavy") {
        await supabase.from("job_queue").insert({
          job_id: job.id,
          priority,
        });
      }

      console.log(`Job queued: ${job.id}, tier=${tier}`);
      return new Response(JSON.stringify({ job }), {
        status: 201,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    // GET /jobs - List user's jobs
    if (req.method === "GET" && !jobId) {
      const limit = Math.min(Math.max(parseInt(url.searchParams.get("limit") || "50") || 50, 1), 100);
      const offset = Math.max(parseInt(url.searchParams.get("offset") || "0") || 0, 0);
      const status = url.searchParams.get("status");
      const tier = url.searchParams.get("tier");

      let query = supabase
        .from("gpu_jobs")
        .select("*", { count: "exact" })
        .eq("user_id", user.id)
        .order("created_at", { ascending: false })
        .range(offset, offset + limit - 1);

      if (status && typeof status === "string" && status.length <= 20) {
        query = query.eq("status", status);
      }
      if (tier && VALID_JOB_TIERS.includes(tier)) {
        query = query.eq("job_tier", tier);
      }

      const { data: jobs, count, error } = await query;

      if (error) throw error;

      return new Response(JSON.stringify({ jobs, total: count }), {
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    // GET /jobs/:id - Get specific job
    if (req.method === "GET" && jobId) {
      const { data: job, error } = await supabase
        .from("gpu_jobs")
        .select("*")
        .eq("id", jobId)
        .eq("user_id", user.id)
        .single();

      if (error || !job) {
        return new Response(JSON.stringify({ error: "Job not found" }), {
          status: 404,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        });
      }

      // Get job logs
      const { data: logs } = await supabase
        .from("job_logs")
        .select("*")
        .eq("job_id", jobId)
        .order("ts", { ascending: false })
        .limit(100);

      // Get job results if completed
      const { data: results } = await supabase
        .from("job_results")
        .select("*")
        .eq("job_id", jobId)
        .single();

      return new Response(JSON.stringify({ job, logs: logs || [], results }), {
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    // POST /jobs/:id/cancel - Cancel a job
    if (req.method === "POST" && jobId && url.pathname.endsWith("/cancel")) {
      const { data: job, error: fetchError } = await supabase
        .from("gpu_jobs")
        .select("*")
        .eq("id", jobId)
        .eq("user_id", user.id)
        .single();

      if (fetchError || !job) {
        return new Response(JSON.stringify({ error: "Job not found" }), {
          status: 404,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        });
      }

      if (!["pending", "queued"].includes(job.status)) {
        return new Response(JSON.stringify({ error: "Job cannot be cancelled" }), {
          status: 400,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        });
      }

      const { error } = await supabase
        .from("gpu_jobs")
        .update({ status: "cancelled" })
        .eq("id", jobId);

      if (error) throw error;

      // Remove from queue
      await supabase.from("job_queue").delete().eq("job_id", jobId);

      console.log(`Job cancelled: ${jobId}`);
      return new Response(JSON.stringify({ success: true }), {
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    return new Response(JSON.stringify({ error: "Not found" }), {
      status: 404,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });

  } catch (error) {
    console.error("Jobs function error:", error);
    // Return generic error to client, log details server-side only
    return new Response(JSON.stringify({ error: "An internal error occurred" }), {
      status: 500,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }
});

// Process light jobs immediately (no GPU needed)
async function processLightJob(jobType: string, payload: Record<string, unknown>) {
  switch (jobType) {
    case "text_analysis":
      return { 
        word_count: String(payload.text || "").split(/\s+/).length,
        char_count: String(payload.text || "").length,
        processed_at: new Date().toISOString(),
      };
    case "metadata_extraction":
      return {
        keys: Object.keys(payload),
        processed_at: new Date().toISOString(),
      };
    case "validation":
      return {
        is_valid: true,
        processed_at: new Date().toISOString(),
      };
    default:
      return {
        status: "processed",
        processed_at: new Date().toISOString(),
      };
  }
}
