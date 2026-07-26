import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers":
    "authorization, x-client-info, apikey, content-type, stripe-signature, x-razorpay-signature",
};

// Crypto utilities for signature verification
async function verifyStripeSignature(
  payload: string,
  signature: string,
  secret: string,
): Promise<boolean> {
  if (!secret) return false;

  try {
    const parts = signature.split(",");
    const timestamp = parts.find((p) => p.startsWith("t="))?.slice(2);
    const v1Signature = parts.find((p) => p.startsWith("v1="))?.slice(3);

    if (!timestamp || !v1Signature) return false;

    // Check timestamp is within 5 minutes
    const timestampNum = parseInt(timestamp, 10);
    const now = Math.floor(Date.now() / 1000);
    if (Math.abs(now - timestampNum) > 300) return false;

    const signedPayload = `${timestamp}.${payload}`;
    const encoder = new TextEncoder();
    const key = await crypto.subtle.importKey(
      "raw",
      encoder.encode(secret),
      { name: "HMAC", hash: "SHA-256" },
      false,
      ["sign"],
    );
    const signatureBytes = await crypto.subtle.sign("HMAC", key, encoder.encode(signedPayload));
    const expectedSignature = Array.from(new Uint8Array(signatureBytes))
      .map((b) => b.toString(16).padStart(2, "0"))
      .join("");

    return expectedSignature === v1Signature;
  } catch {
    return false;
  }
}

async function verifyRazorpaySignature(
  payload: string,
  signature: string,
  secret: string,
): Promise<boolean> {
  if (!secret) return false;

  try {
    const encoder = new TextEncoder();
    const key = await crypto.subtle.importKey(
      "raw",
      encoder.encode(secret),
      { name: "HMAC", hash: "SHA-256" },
      false,
      ["sign"],
    );
    const signatureBytes = await crypto.subtle.sign("HMAC", key, encoder.encode(payload));
    const expectedSignature = Array.from(new Uint8Array(signatureBytes))
      .map((b) => b.toString(16).padStart(2, "0"))
      .join("");

    return expectedSignature === signature;
  } catch {
    return false;
  }
}

// Idempotency check

async function isEventProcessed(
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  supabase: any,
  eventId: string,
): Promise<boolean> {
  const { data } = await supabase
    .from("payment_webhook_events")
    .select("id")
    .eq("event_id", eventId)
    .eq("processed", true)
    .single();
  return !!data;
}

serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: corsHeaders });
  }

  const supabaseClient = createClient(
    Deno.env.get("SUPABASE_URL") ?? "",
    Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? "",
  );

  try {
    const url = new URL(req.url);
    const provider = url.pathname.split("/").pop();
    const body = await req.text();

    // Get signature headers
    const stripeSignature = req.headers.get("stripe-signature") || "";
    const razorpaySignature = req.headers.get("x-razorpay-signature") || "";

    // Get secrets (will be empty if not configured)
    const stripeWebhookSecret = Deno.env.get("STRIPE_WEBHOOK_SECRET") || "";
    const razorpayWebhookSecret = Deno.env.get("RAZORPAY_WEBHOOK_SECRET") || "";

    // CRITICAL: Verify signatures when secrets are configured
    let signatureVerified = false;
    let signatureRequired = false;

    if (provider === "stripe") {
      signatureRequired = !!stripeWebhookSecret;
      if (signatureRequired) {
        signatureVerified = await verifyStripeSignature(body, stripeSignature, stripeWebhookSecret);
        if (!signatureVerified) {
          console.error("Stripe signature verification failed");
          // Log security violation
          await supabaseClient.from("security_audit_log").insert({
            event_type: "webhook_signature_failure",
            actor_id: null,
            resource_type: "payment_webhook",
            resource_id: null,
            action: "stripe_webhook_rejected",
            outcome: "denied",
            metadata: { reason: "invalid_signature", provider: "stripe" },
          });
          return new Response(JSON.stringify({ error: "Invalid signature" }), {
            status: 401,
            headers: { ...corsHeaders, "Content-Type": "application/json" },
          });
        }
      }
    } else if (provider === "razorpay") {
      signatureRequired = !!razorpayWebhookSecret;
      if (signatureRequired) {
        signatureVerified = await verifyRazorpaySignature(
          body,
          razorpaySignature,
          razorpayWebhookSecret,
        );
        if (!signatureVerified) {
          console.error("Razorpay signature verification failed");
          await supabaseClient.from("security_audit_log").insert({
            event_type: "webhook_signature_failure",
            actor_id: null,
            resource_type: "payment_webhook",
            resource_id: null,
            action: "razorpay_webhook_rejected",
            outcome: "denied",
            metadata: { reason: "invalid_signature", provider: "razorpay" },
          });
          return new Response(JSON.stringify({ error: "Invalid signature" }), {
            status: 401,
            headers: { ...corsHeaders, "Content-Type": "application/json" },
          });
        }
      }
    }

    // Parse payload after signature verification
    let payload: Record<string, unknown>;
    try {
      payload = JSON.parse(body);
    } catch {
      return new Response(JSON.stringify({ error: "Invalid JSON" }), {
        status: 400,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    const eventType = (payload.type as string) || (payload.event as string) || "";
    if (!eventType) {
      return new Response(JSON.stringify({ error: "Missing event type" }), {
        status: 400,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    const eventId = (payload.id as string) || crypto.randomUUID();

    // IDEMPOTENCY: Check if already processed
    if (await isEventProcessed(supabaseClient, eventId)) {
      console.log(`Event ${eventId} already processed, skipping`);
      return new Response(JSON.stringify({ received: true, duplicate: true }), {
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    // Log webhook event (append-only)
    const { error: logError } = await supabaseClient.from("payment_webhook_events").insert({
      provider: provider === "stripe" ? "stripe" : "razorpay",
      event_type: eventType,
      event_id: eventId,
      payload,
      signature_verified: signatureVerified,
      processed: false,
    });

    if (logError) {
      console.error("Failed to log webhook event:", logError);
    }

    // Process webhooks with deterministic state machine
    let paymentId: string | null = null;
    let newStatus: string | null = null;
    let userId: string | null = null;
    let plan: string | null = null;

    if (provider === "stripe") {
      const data = payload.data as Record<string, unknown> | undefined;
      const object = data?.object as Record<string, unknown> | undefined;
      const metadata = object?.metadata as Record<string, string> | undefined;
      paymentId = metadata?.payment_id || null;

      if (eventType === "payment_intent.succeeded" && paymentId) {
        newStatus = "succeeded";
        await supabaseClient
          .from("payments")
          .update({
            status: newStatus,
            provider_payment_id: object?.id as string,
            webhook_received_at: new Date().toISOString(),
          })
          .eq("id", paymentId);

        const { data: payment } = await supabaseClient
          .from("payments")
          .select("user_id, plan")
          .eq("id", paymentId)
          .single();

        if (payment) {
          userId = payment.user_id;
          plan = payment.plan;
          await supabaseClient.from("billing_subscriptions").upsert({
            user_id: payment.user_id,
            plan: payment.plan,
            status: "active",
            renewed_at: new Date().toISOString(),
          });
        }
      } else if (eventType === "payment_intent.payment_failed" && paymentId) {
        newStatus = "failed";
        await supabaseClient
          .from("payments")
          .update({
            status: newStatus,
            webhook_received_at: new Date().toISOString(),
          })
          .eq("id", paymentId);
      } else if (eventType === "charge.refunded" && paymentId) {
        newStatus = "refunded";
        await supabaseClient
          .from("payments")
          .update({
            status: newStatus,
            webhook_received_at: new Date().toISOString(),
          })
          .eq("id", paymentId);
      }
    } else if (provider === "razorpay") {
      const payloadData = payload.payload as Record<string, unknown> | undefined;
      const payment = payloadData?.payment as Record<string, unknown> | undefined;
      const entity = payment?.entity as Record<string, unknown> | undefined;
      const notes = entity?.notes as Record<string, string> | undefined;
      paymentId = notes?.payment_id || null;

      if (eventType === "payment.captured" && paymentId) {
        newStatus = "succeeded";
        await supabaseClient
          .from("payments")
          .update({
            status: newStatus,
            provider_payment_id: entity?.id as string,
            webhook_received_at: new Date().toISOString(),
          })
          .eq("id", paymentId);

        const { data: paymentRecord } = await supabaseClient
          .from("payments")
          .select("user_id, plan")
          .eq("id", paymentId)
          .single();

        if (paymentRecord) {
          userId = paymentRecord.user_id;
          plan = paymentRecord.plan;
          await supabaseClient.from("billing_subscriptions").upsert({
            user_id: paymentRecord.user_id,
            plan: paymentRecord.plan,
            status: "active",
            renewed_at: new Date().toISOString(),
          });
        }
      } else if (eventType === "payment.failed" && paymentId) {
        newStatus = "failed";
        await supabaseClient
          .from("payments")
          .update({
            status: newStatus,
            webhook_received_at: new Date().toISOString(),
          })
          .eq("id", paymentId);
      } else if (eventType === "refund.processed" && paymentId) {
        newStatus = "refunded";
        await supabaseClient
          .from("payments")
          .update({
            status: newStatus,
            webhook_received_at: new Date().toISOString(),
          })
          .eq("id", paymentId);
      }
    }

    // Mark event as processed (idempotency)
    await supabaseClient
      .from("payment_webhook_events")
      .update({
        processed: true,
        processed_at: new Date().toISOString(),
      })
      .eq("event_id", eventId);

    // Log successful processing to audit log
    if (paymentId && newStatus) {
      await supabaseClient.from("security_audit_log").insert({
        event_type: "payment_state_change",
        actor_id: userId,
        resource_type: "payment",
        resource_id: paymentId,
        action: `${provider}_${eventType}`,
        outcome: "success",
        metadata: {
          new_status: newStatus,
          plan,
          signature_verified: signatureVerified,
          signature_required: signatureRequired,
        },
      });
    }

    return new Response(JSON.stringify({ received: true }), {
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  } catch (error) {
    console.error("Webhook error:", error);
    // Log error but return generic message
    return new Response(JSON.stringify({ error: "An internal error occurred" }), {
      status: 500,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }
});
