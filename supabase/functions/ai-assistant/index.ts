import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};

interface ChatMessage {
  role: "user" | "assistant" | "system";
  content: string;
}

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
    const LOVABLE_API_KEY = Deno.env.get("LOVABLE_API_KEY");
    if (!LOVABLE_API_KEY) {
      throw new Error("LOVABLE_API_KEY is not configured");
    }

    const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
    const supabaseKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
    const supabase = createClient(supabaseUrl, supabaseKey);

    const body = await req.json();
    const { messages, type, context } = body;

    // Validate input
    if (!messages || !Array.isArray(messages)) {
      return new Response(JSON.stringify({ error: "messages array required" }), {
        status: 400,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    // Get user context if authenticated
    let userContext = "";
    const authHeader = req.headers.get("Authorization");
    if (authHeader) {
      const token = authHeader.replace("Bearer ", "");
      const { data: { user } } = await supabase.auth.getUser(token);
      
      if (user) {
        // Fetch user's recent activity for context
        const [jobsRes, alertsRes, metricsRes] = await Promise.all([
          supabase.from("gpu_jobs").select("job_type, status, created_at").eq("user_id", user.id).order("created_at", { ascending: false }).limit(5),
          supabase.from("alerts").select("title, severity, resolved").eq("user_id", user.id).eq("resolved", false).limit(3),
          supabase.from("system_metrics").select("gpu_utilization, memory_usage, active_jobs").eq("user_id", user.id).order("recorded_at", { ascending: false }).limit(1)
        ]);

        userContext = `
User Context:
- Recent Jobs: ${JSON.stringify(jobsRes.data || [])}
- Active Alerts: ${JSON.stringify(alertsRes.data || [])}
- Current Metrics: ${JSON.stringify(metricsRes.data?.[0] || {})}
`;
      }
    }

    // Build system prompt based on type
    let systemPrompt = "";
    
    switch (type) {
      case "job_optimization":
        systemPrompt = `You are an AI GPU optimization expert assistant for the HyperInference platform. 
You help users optimize their GPU jobs, understand performance metrics, and troubleshoot issues.
${userContext}
Provide concise, actionable advice. When suggesting optimizations, explain the expected impact.
Focus on practical GPU optimization techniques like quantization, kernel fusion, memory management, and batch processing.`;
        break;
        
      case "troubleshooting":
        systemPrompt = `You are a technical support AI for the HyperInference GPU platform.
You help diagnose and resolve issues with GPU jobs, system performance, and configuration.
${userContext}
When troubleshooting:
1. First identify the likely root cause
2. Provide step-by-step resolution instructions
3. Suggest preventive measures
Be specific and reference actual system components like job queues, modules, and metrics.`;
        break;
        
      case "system_analysis":
        systemPrompt = `You are a system performance analyst AI for the HyperInference platform.
You analyze GPU utilization, job performance, and system health metrics.
${userContext}
Provide data-driven insights about:
- Resource utilization patterns
- Performance bottlenecks
- Optimization opportunities
- Cost efficiency improvements
Use specific numbers and percentages when available.`;
        break;
        
      case "code_generation":
        systemPrompt = `You are an AI coding assistant specialized in GPU computing and ML optimization.
You help users write code for:
- Job payload configuration
- API integration
- Performance monitoring
- Custom optimization pipelines
${userContext}
Provide clean, well-documented code examples. Explain key parts of the implementation.`;
        break;
        
      default:
        systemPrompt = `You are a helpful AI assistant for the HyperInference GPU optimization platform.
You can help with:
- Understanding GPU job types and optimization
- Troubleshooting performance issues
- Explaining system metrics and alerts
- Providing best practices for ML inference
${userContext}
Be concise but thorough. Reference specific platform features when relevant.`;
    }

    // Add context if provided
    if (context) {
      systemPrompt += `\n\nAdditional Context: ${JSON.stringify(context)}`;
    }

    const aiMessages: ChatMessage[] = [
      { role: "system", content: systemPrompt },
      ...messages
    ];

    // Check if streaming is requested
    const stream = body.stream === true;

    if (stream) {
      // Streaming response
      const response = await fetch("https://ai.gateway.lovable.dev/v1/chat/completions", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${LOVABLE_API_KEY}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          model: body.model || "google/gemini-2.5-flash",
          messages: aiMessages,
          stream: true,
          max_tokens: body.max_tokens || 2000,
          temperature: body.temperature || 0.7
        }),
      });

      if (!response.ok) {
        if (response.status === 429) {
          return new Response(JSON.stringify({ error: "Rate limit exceeded. Please try again later." }), {
            status: 429,
            headers: { ...corsHeaders, "Content-Type": "application/json" },
          });
        }
        if (response.status === 402) {
          return new Response(JSON.stringify({ error: "AI usage limit reached. Please add credits." }), {
            status: 402,
            headers: { ...corsHeaders, "Content-Type": "application/json" },
          });
        }
        const errorText = await response.text();
        console.error("AI gateway error:", response.status, errorText);
        throw new Error(`AI gateway error: ${response.status}`);
      }

      return new Response(response.body, {
        headers: { ...corsHeaders, "Content-Type": "text/event-stream" },
      });
    } else {
      // Non-streaming response
      const response = await fetch("https://ai.gateway.lovable.dev/v1/chat/completions", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${LOVABLE_API_KEY}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          model: body.model || "google/gemini-2.5-flash",
          messages: aiMessages,
          max_tokens: body.max_tokens || 2000,
          temperature: body.temperature || 0.7
        }),
      });

      if (!response.ok) {
        if (response.status === 429) {
          return new Response(JSON.stringify({ error: "Rate limit exceeded. Please try again later." }), {
            status: 429,
            headers: { ...corsHeaders, "Content-Type": "application/json" },
          });
        }
        if (response.status === 402) {
          return new Response(JSON.stringify({ error: "AI usage limit reached. Please add credits." }), {
            status: 402,
            headers: { ...corsHeaders, "Content-Type": "application/json" },
          });
        }
        const errorText = await response.text();
        console.error("AI gateway error:", response.status, errorText);
        throw new Error(`AI gateway error: ${response.status}`);
      }

      const data = await response.json();
      const content = data.choices?.[0]?.message?.content || "";

      // Log AI interaction for analytics
      if (authHeader) {
        const token = authHeader.replace("Bearer ", "");
        const { data: { user } } = await supabase.auth.getUser(token);
        if (user) {
          await supabase.from("analytics_events").insert({
            user_id: user.id,
            event_type: "ai_chat",
            event_data: {
              type,
              message_count: messages.length,
              response_length: content.length
            }
          });
        }
      }

      return new Response(JSON.stringify({
        content,
        model: data.model,
        usage: data.usage
      }), {
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }
  } catch (error) {
    console.error("AI assistant error:", error);
    // Return generic error to client, log details server-side only
    return new Response(JSON.stringify({
      error: "An internal error occurred"
    }), {
      status: 500,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }
});
