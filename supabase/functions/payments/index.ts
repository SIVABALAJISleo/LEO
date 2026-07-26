import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

// Validation constants
const MAX_AMOUNT = 10000000; // 10 million max
const VALID_PROVIDERS = ["stripe", "razorpay"];
const VALID_PLANS = ["free", "pro", "heavy", "enterprise"];
const VALID_CYCLES = ["monthly", "yearly"];

serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const supabaseClient = createClient(
      Deno.env.get("SUPABASE_URL") ?? "",
      Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? "",
    );

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
    } = await supabaseClient.auth.getUser(token);

    if (authError || !user) {
      return new Response(JSON.stringify({ error: "Invalid token" }), {
        status: 401,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    const url = new URL(req.url);
    const path = url.pathname.split("/").pop();

    // POST /payments/create-checkout
    if (req.method === "POST" && path === "create-checkout") {
      const body = await req.json();
      const { provider, plan, billing_cycle, amount } = body;

      // Validate inputs
      if (!VALID_PROVIDERS.includes(provider)) {
        return new Response(JSON.stringify({ error: "Invalid provider" }), {
          status: 400,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        });
      }
      if (!VALID_PLANS.includes(plan)) {
        return new Response(JSON.stringify({ error: "Invalid plan" }), {
          status: 400,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        });
      }
      if (!VALID_CYCLES.includes(billing_cycle)) {
        return new Response(JSON.stringify({ error: "Invalid billing cycle" }), {
          status: 400,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        });
      }
      if (typeof amount !== "number" || amount <= 0 || amount > MAX_AMOUNT) {
        return new Response(JSON.stringify({ error: "Invalid amount" }), {
          status: 400,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        });
      }

      // Create pending payment record
      const { data: payment, error: paymentError } = await supabaseClient
        .from("payments")
        .insert({
          user_id: user.id,
          provider,
          plan,
          billing_cycle,
          amount,
          currency: "INR",
          status: "pending",
        })
        .select()
        .single();

      if (paymentError) {
        console.error("Payment creation error:", paymentError);
        return new Response(JSON.stringify({ error: "Failed to create payment" }), {
          status: 500,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        });
      }

      // Return checkout session info (provider integration would go here)
      return new Response(
        JSON.stringify({
          payment_id: payment.id,
          checkout_url: `/billing/checkout/${payment.id}`,
          provider,
          amount,
          currency: "INR",
        }),
        {
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        },
      );
    }

    // GET /payments/history
    if (req.method === "GET" && path === "history") {
      const { data: payments, error } = await supabaseClient
        .from("payments")
        .select("*")
        .eq("user_id", user.id)
        .order("created_at", { ascending: false });

      if (error) {
        return new Response(JSON.stringify({ error: "Failed to fetch payments" }), {
          status: 500,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        });
      }

      return new Response(JSON.stringify({ payments }), {
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    // POST /payments/verify
    if (req.method === "POST" && path === "verify") {
      const body = await req.json();
      const { payment_id, transaction_id } = body;

      if (!payment_id || typeof payment_id !== "string") {
        return new Response(JSON.stringify({ error: "Invalid payment_id" }), {
          status: 400,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        });
      }

      // Update payment status
      const { data: payment, error } = await supabaseClient
        .from("payments")
        .update({
          status: "succeeded",
          transaction_id,
          webhook_received_at: new Date().toISOString(),
        })
        .eq("id", payment_id)
        .eq("user_id", user.id)
        .select()
        .single();

      if (error || !payment) {
        return new Response(JSON.stringify({ error: "Payment not found" }), {
          status: 404,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        });
      }

      // Update subscription
      await supabaseClient.from("billing_subscriptions").upsert(
        {
          user_id: user.id,
          plan: payment.plan,
          status: "active",
          renewed_at: new Date().toISOString(),
        },
        { onConflict: "user_id" },
      );

      return new Response(JSON.stringify({ success: true, payment }), {
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    return new Response(JSON.stringify({ error: "Not found" }), {
      status: 404,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  } catch (error) {
    console.error("Payments error:", error);
    return new Response(JSON.stringify({ error: "Internal server error" }), {
      status: 500,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }
});
