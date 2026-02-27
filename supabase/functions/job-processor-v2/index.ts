import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: corsHeaders });
  }

  const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
  const supabaseServiceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
  // deno-lint-ignore no-explicit-any
  const supabase = createClient(supabaseUrl, supabaseServiceKey) as any;

  try {
    const { action, job_id, max_jobs = 5 } = await req.json();
    console.log(`[job-processor-v2] Action: ${action}`);

    if (action === "process_next") {
      const { data: jobs } = await supabase
        .from("gpu_jobs")
        .select("*")
        .eq("status", "queued")
        .order("priority", { ascending: false })
        .limit(max_jobs);

      const processed: string[] = [];
      for (const job of jobs || []) {
        await supabase.from("gpu_jobs").update({ 
          status: "running", 
          started_at: new Date().toISOString(),
          progress: 0 
        }).eq("id", job.id);

        // Simulate processing
        for (let i = 1; i <= 5; i++) {
          await new Promise(r => setTimeout(r, 100));
          await supabase.from("gpu_jobs").update({ progress: i * 20 }).eq("id", job.id);
        }

        await supabase.from("gpu_jobs").update({
          status: "completed",
          progress: 100,
          completed_at: new Date().toISOString(),
          result_data: { completed: true, processing_time_ms: 500 },
        }).eq("id", job.id);

        processed.push(job.id);
      }

      return new Response(JSON.stringify({ success: true, processed }), 
        { headers: { ...corsHeaders, "Content-Type": "application/json" } });
    }

    if (action === "retry_failed") {
      const { data: failedJobs } = await supabase
        .from("gpu_jobs")
        .select("id, retry_count")
        .eq("status", "failed")
        .lt("retry_count", 3)
        .limit(max_jobs);

      const retried: string[] = [];
      for (const job of failedJobs || []) {
        await supabase.from("gpu_jobs").update({
          status: "queued",
          retry_count: (job.retry_count || 0) + 1,
        }).eq("id", job.id);
        retried.push(job.id);
      }

      return new Response(JSON.stringify({ success: true, retried }), 
        { headers: { ...corsHeaders, "Content-Type": "application/json" } });
    }

    return new Response(JSON.stringify({ error: "Unknown action" }), 
      { status: 400, headers: { ...corsHeaders, "Content-Type": "application/json" } });

  } catch (error) {
    console.error("[job-processor-v2] Error:", error);
    // Return generic error to client, log details server-side only
    return new Response(JSON.stringify({ error: "An internal error occurred" }), 
      { status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" } });
  }
});
