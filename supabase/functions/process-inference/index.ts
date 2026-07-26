import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};

// Simulated processing speeds by job type
const PROCESSING_SPEEDS: Record<string, number> = {
  text_generation: 50,
  image_classification: 100,
  object_detection: 150,
  sentiment_analysis: 30,
  translation: 80,
  summarization: 60,
  embedding: 20,
  custom: 100,
};

serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: corsHeaders });
  }

  if (req.method !== "POST") {
    return new Response(JSON.stringify({ error: "Method not allowed" }), {
      status: 405,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
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

    const token = authHeader.replace("Bearer ", "");
    const {
      data: { user },
      error: authError,
    } = await supabase.auth.getUser(token);

    if (authError || !user) {
      return new Response(JSON.stringify({ error: "Invalid token" }), {
        status: 401,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    const body = await req.json();
    const { job_id, simulate_progress } = body;

    if (!job_id) {
      return new Response(JSON.stringify({ error: "job_id required" }), {
        status: 400,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    // Fetch the job
    const { data: job, error: jobError } = await supabase
      .from("inference_jobs")
      .select("*, model:models(*)")
      .eq("id", job_id)
      .eq("user_id", user.id)
      .single();

    if (jobError || !job) {
      return new Response(JSON.stringify({ error: "Job not found" }), {
        status: 404,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    if (!["queued", "pending"].includes(job.status)) {
      return new Response(
        JSON.stringify({ error: "Job cannot be processed", current_status: job.status }),
        {
          status: 400,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        },
      );
    }

    const startTime = Date.now();

    // Update job to running
    await supabase
      .from("inference_jobs")
      .update({
        status: "running",
        started_at: new Date().toISOString(),
        progress: 0,
      })
      .eq("id", job_id);

    // Get enabled modules
    const enabledModules = (job.enabled_modules as string[]) || [];
    // eslint-disable-next-line @typescript-eslint/no-unused-vars, @typescript-eslint/no-explicit-any
    const optimizationOptions = (job.optimization_options as Record<string, any>) || {};

    // Simulate processing with progress updates
    if (simulate_progress) {
      const jobType = job.model?.model_type || "custom";
      const baseLatency = PROCESSING_SPEEDS[jobType] || 100;

      // Calculate optimizations
      let speedup = 1.0;
      let compressionRatio = 1.0;

      if (enabledModules.includes("Quantization")) {
        speedup *= 1.5;
        compressionRatio *= 2.0;
      }
      if (enabledModules.includes("Kernel Optimization")) {
        speedup *= 1.3;
      }
      if (enabledModules.includes("Memory Compression")) {
        compressionRatio *= 1.5;
      }
      if (enabledModules.includes("Cache Optimization")) {
        speedup *= 1.2;
      }
      if (enabledModules.includes("Parallel Execution")) {
        speedup *= 1.4;
      }

      const effectiveLatency = Math.round(baseLatency / speedup);
      const steps = 10;
      const stepDelay = Math.max(50, effectiveLatency / steps);

      // Progress simulation
      for (let i = 1; i <= steps; i++) {
        await new Promise((resolve) => setTimeout(resolve, stepDelay));
        await supabase
          .from("inference_jobs")
          .update({
            progress: i * 10,
          })
          .eq("id", job_id);
      }

      // Generate output based on job type
      const output = generateOutput(job, enabledModules);
      const totalLatency = Date.now() - startTime;

      // Complete the job
      await supabase
        .from("inference_jobs")
        .update({
          status: "completed",
          progress: 100,
          output_data: output,
          latency_ms: totalLatency,
          speedup: Math.round(speedup * 100) / 100,
          compression_ratio: Math.round(compressionRatio * 100) / 100,
          completed_at: new Date().toISOString(),
        })
        .eq("id", job_id);

      // Record performance metrics
      await supabase.from("performance_metrics").insert({
        user_id: user.id,
        job_id: job_id,
        metric_name: "inference_latency",
        metric_value: totalLatency,
        latency_ms: totalLatency,
        throughput_rps: Math.round((1000 / totalLatency) * 100) / 100,
        cache_hit_ratio: enabledModules.includes("Cache Optimization") ? 0.85 : 0.5,
        module_name: enabledModules[0] || null,
        metadata: {
          speedup,
          compression_ratio: compressionRatio,
          enabled_modules: enabledModules,
        },
      });

      // Update module stats
      for (const moduleName of enabledModules) {
        const { data: config } = await supabase
          .from("module_configs")
          .select("*")
          .eq("user_id", user.id)
          .eq("module_name", moduleName)
          .single();

        if (config) {
          const currentSpeedup = config.speedup_achieved || 1;
          const currentCompression = config.compression_ratio_achieved || 1;

          await supabase
            .from("module_configs")
            .update({
              speedup_achieved: Math.max(currentSpeedup, speedup),
              compression_ratio_achieved: Math.max(currentCompression, compressionRatio),
              updated_at: new Date().toISOString(),
            })
            .eq("id", config.id);
        }
      }

      return new Response(
        JSON.stringify({
          success: true,
          job_id,
          status: "completed",
          latency_ms: totalLatency,
          speedup,
          compression_ratio: compressionRatio,
          output,
        }),
        {
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        },
      );
    } else {
      // Quick processing without progress simulation
      const output = generateOutput(job, enabledModules);
      const latency = Date.now() - startTime;

      await supabase
        .from("inference_jobs")
        .update({
          status: "completed",
          progress: 100,
          output_data: output,
          latency_ms: latency,
          speedup: 1.5,
          compression_ratio: 1.2,
          completed_at: new Date().toISOString(),
        })
        .eq("id", job_id);

      return new Response(
        JSON.stringify({
          success: true,
          job_id,
          status: "completed",
          latency_ms: latency,
          output,
        }),
        {
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        },
      );
    }
  } catch (error) {
    console.error("Process inference error:", error);
    // Return generic error to client, log details server-side only
    return new Response(
      JSON.stringify({
        error: "An internal error occurred",
      }),
      {
        status: 500,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      },
    );
  }
});

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function generateOutput(job: any, enabledModules: string[]) {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const inputData = job.input_data as Record<string, any>;
  const modelType = job.model?.model_type || "custom";

  switch (modelType) {
    case "text_generation":
      return {
        generated_text: `AI-generated response for: "${inputData.prompt?.slice(0, 50) || "input"}..."`,
        tokens_generated: Math.floor(Math.random() * 200) + 50,
        finish_reason: "stop",
      };

    case "image_classification":
      return {
        predictions: [
          { label: "category_a", confidence: 0.85 + Math.random() * 0.1 },
          { label: "category_b", confidence: 0.1 + Math.random() * 0.05 },
          { label: "category_c", confidence: 0.02 + Math.random() * 0.03 },
        ],
        processing_info: {
          modules_used: enabledModules,
          optimizations_applied: enabledModules.length,
        },
      };

    case "object_detection":
      return {
        detections: [
          { class: "object_1", bbox: [100, 100, 200, 200], confidence: 0.92 },
          { class: "object_2", bbox: [300, 150, 450, 350], confidence: 0.87 },
        ],
        total_objects: 2,
        inference_mode: enabledModules.includes("Quantization") ? "INT8" : "FP32",
      };

    case "sentiment_analysis":
      // eslint-disable-next-line no-case-declarations
      const sentiments = ["positive", "negative", "neutral"];
      return {
        sentiment: sentiments[Math.floor(Math.random() * sentiments.length)],
        confidence: 0.75 + Math.random() * 0.2,
        aspects: {
          quality: 0.8 + Math.random() * 0.2,
          service: 0.7 + Math.random() * 0.25,
        },
      };

    case "translation":
      return {
        translated_text: `[Translated] ${inputData.text?.slice(0, 100) || "Sample translation"}`,
        source_language: inputData.source_lang || "auto",
        target_language: inputData.target_lang || "en",
        confidence: 0.9 + Math.random() * 0.1,
      };

    case "summarization":
      return {
        summary: `Summary of input: ${inputData.text?.slice(0, 50) || "content"}...`,
        compression_ratio: 0.3 + Math.random() * 0.2,
        key_points: ["Point 1", "Point 2", "Point 3"],
      };

    case "embedding":
      return {
        embedding: Array.from({ length: 768 }, () => Math.random() * 2 - 1),
        dimension: 768,
        model_version: "v2",
      };

    default:
      return {
        result: "processed",
        input_size: JSON.stringify(inputData).length,
        output_generated_at: new Date().toISOString(),
        modules_applied: enabledModules,
      };
  }
}
