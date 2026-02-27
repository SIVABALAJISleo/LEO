import { serve } from 'https://deno.land/std@0.168.0/http/server.ts';
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

// Patterns for blocked private/internal IPs
const BLOCKED_IP_PATTERNS = [
  /^127\./, // Localhost
  /^10\./, // Private Class A
  /^172\.(1[6-9]|2[0-9]|3[0-1])\./, // Private Class B
  /^192\.168\./, // Private Class C
  /^169\.254\./, // Link-local
  /^0\./, // Invalid
  /^::1$/, // IPv6 localhost
  /^fe80::/i, // IPv6 link-local
  /^fc00::/i, // IPv6 unique local
  /^fd00::/i, // IPv6 unique local
];

// Check if hostname is a private/blocked IP
function isBlockedIP(ip: string): boolean {
  return BLOCKED_IP_PATTERNS.some(pattern => pattern.test(ip));
}

// Check if hostname looks like an IP address
function isIPAddress(hostname: string): boolean {
  return /^(\d{1,3}\.){3}\d{1,3}$/.test(hostname) || hostname.includes(':');
}

serve(async (req) => {
  // Handle CORS preflight requests
  if (req.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    // Create Supabase client
    const supabaseUrl = Deno.env.get('SUPABASE_URL')!;
    const supabaseServiceKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;
    const supabase = createClient(supabaseUrl, supabaseServiceKey);

    // Authenticate user
    const authHeader = req.headers.get('Authorization');
    if (!authHeader) {
      return new Response(JSON.stringify({ error: 'Authorization required' }), {
        status: 401,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      });
    }

    const token = authHeader.replace('Bearer ', '');
    const { data: { user }, error: authError } = await supabase.auth.getUser(token);

    if (authError || !user) {
      console.error('Auth error:', authError);
      return new Response(JSON.stringify({ error: 'Unauthorized' }), {
        status: 401,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      });
    }

    // Parse request body
    const { webhook_url } = await req.json();

    if (!webhook_url || typeof webhook_url !== 'string') {
      return new Response(JSON.stringify({ error: 'webhook_url is required' }), {
        status: 400,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      });
    }

    // Validate URL format
    let url: URL;
    try {
      url = new URL(webhook_url);
    } catch {
      return new Response(JSON.stringify({ error: 'Invalid URL format' }), {
        status: 400,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      });
    }

    // Only allow http/https protocols
    if (!['http:', 'https:'].includes(url.protocol)) {
      return new Response(JSON.stringify({ error: 'Only HTTP/HTTPS URLs are allowed' }), {
        status: 400,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      });
    }

    // Block direct IP addresses in URL
    if (isIPAddress(url.hostname)) {
      if (isBlockedIP(url.hostname)) {
        console.warn(`Blocked private IP access attempt: ${url.hostname} by user ${user.id}`);
        return new Response(JSON.stringify({ error: 'Private/internal IP addresses are not allowed' }), {
          status: 403,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        });
      }
    }

    // Block known internal hostnames
    const blockedHostnames = ['localhost', 'metadata', 'metadata.google.internal', '169.254.169.254'];
    if (blockedHostnames.some(h => url.hostname.toLowerCase().includes(h))) {
      console.warn(`Blocked internal hostname access attempt: ${url.hostname} by user ${user.id}`);
      return new Response(JSON.stringify({ error: 'Internal hostnames are not allowed' }), {
        status: 403,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      });
    }

    // Rate limiting: max 5 tests per hour per user
    const oneHourAgo = new Date(Date.now() - 3600000).toISOString();
    const { count, error: countError } = await supabase
      .from('webhook_test_log')
      .select('*', { count: 'exact', head: true })
      .eq('user_id', user.id)
      .gte('created_at', oneHourAgo);

    if (countError) {
      console.error('Rate limit check error:', countError);
    }

    if (count && count >= 5) {
      return new Response(JSON.stringify({ error: 'Rate limit exceeded: max 5 webhook tests per hour' }), {
        status: 429,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      });
    }

    // Make request with timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout

    let statusCode = 0;
    let success = false;
    let errorMessage = '';

    try {
      console.log(`User ${user.id} testing webhook: ${url.hostname}`);
      
      const response = await fetch(webhook_url, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'User-Agent': 'HYPER-Webhook-Test/1.0'
        },
        body: JSON.stringify({
          event: 'test',
          timestamp: new Date().toISOString(),
          data: { message: 'Webhook test from HYPER' }
        }),
        signal: controller.signal
      });

      clearTimeout(timeoutId);
      statusCode = response.status;
      success = response.ok;

    } catch (fetchError: any) {
      clearTimeout(timeoutId);
      
      if (fetchError.name === 'AbortError') {
        errorMessage = 'Request timed out after 10 seconds';
      } else {
        errorMessage = fetchError.message || 'Request failed';
      }
      console.error(`Webhook test failed for user ${user.id}:`, errorMessage);
    }

    // Log the test attempt (for audit and rate limiting)
    await supabase.from('webhook_test_log').insert({
      user_id: user.id,
      webhook_url: url.origin + url.pathname, // Don't log query params for privacy
      status_code: statusCode || null,
      success
    });

    if (success) {
      return new Response(JSON.stringify({ 
        success: true, 
        status: statusCode,
        message: 'Webhook test successful'
      }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      });
    } else {
      return new Response(JSON.stringify({ 
        success: false, 
        status: statusCode || null,
        error: errorMessage || `Webhook returned status ${statusCode}`
      }), {
        status: 200, // Return 200 so client can handle gracefully
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      });
    }

  } catch (error: unknown) {
    console.error('Webhook test error:', error);
    // Return generic error to client, log details server-side only
    return new Response(JSON.stringify({ error: 'An internal error occurred' }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });
  }
});
