import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.39.7";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "GET, OPTIONS",
};

interface HealthResponse {
  status: "ok" | "degraded" | "down";
  timestamp: string;
  version: string;
  checks: {
    database: "ok" | "error";
    auth: "ok" | "error";
  };
  metadata?: {
    build?: string;
    region?: string;
  };
}

serve(async (req: Request) => {
  // Handle CORS preflight
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: corsHeaders });
  }

  if (req.method !== "GET") {
    return new Response(JSON.stringify({ error: "Method not allowed" }), {
      status: 405,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }

  const response: HealthResponse = {
    status: "ok",
    timestamp: new Date().toISOString(),
    version: "1.0.0",
    checks: {
      database: "ok",
      auth: "ok",
    },
    metadata: {
      region: Deno.env.get("DENO_REGION") || "unknown",
    },
  };

  try {
    // Check database connectivity
    const supabaseUrl = Deno.env.get("SUPABASE_URL");
    const supabaseKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");

    if (!supabaseUrl || !supabaseKey) {
      response.checks.database = "error";
      response.status = "degraded";
    } else {
      const supabase = createClient(supabaseUrl, supabaseKey);

      // Simple query to check database
      const { error } = await supabase.from("profiles").select("count").limit(1);

      if (error) {
        response.checks.database = "error";
        response.status = "degraded";
      }
    }

    // Check auth service
    if (!supabaseUrl || !supabaseKey) {
      response.checks.auth = "error";
      if (response.status === "ok") {
        response.status = "degraded";
      }
    }

    // If both checks fail, mark as down
    if (response.checks.database === "error" && response.checks.auth === "error") {
      response.status = "down";
    }

    return new Response(JSON.stringify(response), {
      status: response.status === "ok" ? 200 : response.status === "degraded" ? 200 : 503,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
  } catch (error) {
    response.status = "down";
    response.checks.database = "error";

    return new Response(JSON.stringify(response), {
      status: 503,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }
});
