import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type, x-agent-token",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
};

serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
    const supabaseKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
    const supabase = createClient(supabaseUrl, supabaseKey);

    // Validate agent token
    const agentToken = req.headers.get("x-agent-token");
    if (!agentToken) {
      return new Response(JSON.stringify({ error: "Agent token required" }), {
        status: 401,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    // Hash the provided token
    const encoder = new TextEncoder();
    const tokenData = encoder.encode(agentToken);
    const tokenHashBuffer = await crypto.subtle.digest("SHA-256", tokenData);
    const tokenHashArray = Array.from(new Uint8Array(tokenHashBuffer));
    const tokenHash = tokenHashArray.map(b => b.toString(16).padStart(2, "0")).join("");

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

    const url = new URL(req.url);
    const action = url.pathname.split("/").pop();

    // POST /offline/package - Get list of models/files to pre-download
    if (req.method === "POST" && action === "package") {
      const body = await req.json();
      const { job_types, include_checkpoints = true } = body;

      // Define model requirements for each job type
      const modelManifest: Record<string, { models: string[], files: string[], size_mb: number }> = {
        inference: {
          models: [
            "models/llama-3.2-1b-instruct-q4_k_m.gguf",
            "models/llama-3.2-3b-instruct-q4_k_m.gguf",
          ],
          files: [
            "tokenizers/llama-tokenizer.json",
          ],
          size_mb: 2500,
        },
        training: {
          models: [
            "models/base-model-7b-fp16.safetensors",
          ],
          files: [
            "configs/training-config.yaml",
            "optimizers/adamw-state.pt",
          ],
          size_mb: 14000,
        },
        rendering: {
          models: [
            "models/upscaler-4x.onnx",
            "models/denoiser-v2.onnx",
          ],
          files: [
            "luts/filmic-lut.cube",
          ],
          size_mb: 800,
        },
        video_processing: {
          models: [
            "models/video-interpolation.onnx",
            "models/frame-dedup.onnx",
          ],
          files: [],
          size_mb: 1200,
        },
        compression: {
          models: [
            "models/quantizer-int8.onnx",
          ],
          files: [],
          size_mb: 200,
        },
      };

      // Build package list
      const requestedTypes = job_types || Object.keys(modelManifest);
      const package_items: Array<{
        type: string;
        path: string;
        size_mb: number;
        priority: number;
        checksum?: string;
      }> = [];

      let totalSizeMb = 0;

      for (const jobType of requestedTypes) {
        const manifest = modelManifest[jobType];
        if (!manifest) continue;

        for (const model of manifest.models) {
          package_items.push({
            type: "model",
            path: model,
            size_mb: Math.round(manifest.size_mb / manifest.models.length),
            priority: 1,
          });
        }

        for (const file of manifest.files) {
          package_items.push({
            type: "file",
            path: file,
            size_mb: 10,
            priority: 2,
          });
        }

        totalSizeMb += manifest.size_mb;
      }

      // Include checkpoints if requested
      if (include_checkpoints) {
        const { data: checkpointJobs } = await supabase
          .from("gpu_jobs")
          .select("id, job_type, checkpoint_data")
          .not("checkpoint_data", "is", null)
          .limit(10);

        for (const job of checkpointJobs || []) {
          package_items.push({
            type: "checkpoint",
            path: `checkpoints/${job.id}.pt`,
            size_mb: 100,
            priority: 3,
          });
          totalSizeMb += 100;
        }
      }

      return new Response(JSON.stringify({
        package_items,
        total_size_mb: totalSizeMb,
        estimated_download_time_minutes: Math.ceil(totalSizeMb / 50), // Assume 50MB/min
        generated_at: new Date().toISOString(),
      }), {
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    // GET /offline/status - Check which models are available
    if (req.method === "GET" && action === "status") {
      // This would normally check actual file availability
      // For now, return a mock status
      return new Response(JSON.stringify({
        ready_models: [
          "models/llama-3.2-1b-instruct-q4_k_m.gguf",
        ],
        pending_downloads: [],
        last_sync: new Date().toISOString(),
      }), {
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    return new Response(JSON.stringify({ error: "Not found" }), {
      status: 404,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });

  } catch (error) {
    console.error("Error:", error);
    // Return generic error to client, log details server-side only
    return new Response(JSON.stringify({ error: "An internal error occurred" }), {
      status: 500,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }
});
