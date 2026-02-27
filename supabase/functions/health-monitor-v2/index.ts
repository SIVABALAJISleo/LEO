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
    const { action, user_id } = await req.json();
    console.log(`[health-monitor-v2] Action: ${action}`);

    if (action === "check") {
      const { data: stuckJobs } = await supabase
        .from("gpu_jobs")
        .select("id")
        .eq("status", "running")
        .lt("updated_at", new Date(Date.now() - 30 * 60 * 1000).toISOString());

      const { data: queuedJobs } = await supabase
        .from("gpu_jobs")
        .select("id")
        .eq("status", "queued");

      return new Response(JSON.stringify({
        success: true,
        overall_status: (stuckJobs?.length || 0) > 0 ? "degraded" : "healthy",
        stuck_jobs: stuckJobs?.length || 0,
        queue_depth: queuedJobs?.length || 0,
        timestamp: new Date().toISOString(),
      }), { headers: { ...corsHeaders, "Content-Type": "application/json" } });
    }

    if (action === "heal") {
      const stuckThreshold = new Date(Date.now() - 30 * 60 * 1000).toISOString();
      const { data: stuckJobs } = await supabase
        .from("gpu_jobs")
        .select("id")
        .eq("status", "running")
        .lt("updated_at", stuckThreshold);

      let healed = 0;
      for (const job of stuckJobs || []) {
        await supabase.from("gpu_jobs").update({ status: "queued" }).eq("id", job.id);
        healed++;
      }

      return new Response(JSON.stringify({ success: true, healed }), 
        { headers: { ...corsHeaders, "Content-Type": "application/json" } });
    }

    if (action === "cleanup") {
      const threshold = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString();
      await supabase.from("system_metrics").delete().lt("recorded_at", threshold);
      return new Response(JSON.stringify({ success: true }), 
        { headers: { ...corsHeaders, "Content-Type": "application/json" } });
    }

    return new Response(JSON.stringify({ error: "Unknown action" }), 
      { status: 400, headers: { ...corsHeaders, "Content-Type": "application/json" } });

  } catch (error) {
    console.error("[health-monitor-v2] Error:", error);
    // Return generic error to client, log details server-side only
    return new Response(JSON.stringify({ error: "An internal error occurred" }), 
      { status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" } });
  }
});
