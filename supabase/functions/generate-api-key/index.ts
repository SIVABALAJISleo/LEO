import { serve } from 'https://deno.land/std@0.168.0/http/server.ts';
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';
import { hash, genSalt } from 'https://deno.land/x/bcrypt@v0.4.1/mod.ts';

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

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
    const { key_name } = await req.json();

    if (!key_name || typeof key_name !== 'string' || key_name.trim().length === 0) {
      return new Response(JSON.stringify({ error: 'key_name is required' }), {
        status: 400,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      });
    }

    // Sanitize key name
    const sanitizedKeyName = key_name.trim().slice(0, 100);

    // Rate limiting: max 5 keys per hour per user
    const oneHourAgo = new Date(Date.now() - 3600000).toISOString();
    const { count, error: countError } = await supabase
      .from('api_keys')
      .select('*', { count: 'exact', head: true })
      .eq('user_id', user.id)
      .gte('created_at', oneHourAgo);

    if (countError) {
      console.error('Rate limit check error:', countError);
    }

    if (count && count >= 5) {
      return new Response(JSON.stringify({ error: 'Rate limit exceeded: max 5 API keys per hour' }), {
        status: 429,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      });
    }

    // Check total key count (max 20 active keys per user)
    const { count: totalCount } = await supabase
      .from('api_keys')
      .select('*', { count: 'exact', head: true })
      .eq('user_id', user.id)
      .eq('is_active', true);

    if (totalCount && totalCount >= 20) {
      return new Response(JSON.stringify({ error: 'Maximum of 20 active API keys allowed. Please revoke unused keys.' }), {
        status: 400,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      });
    }

    // Generate key server-side (secure)
    const newKey = `hyper_${crypto.randomUUID().replace(/-/g, '')}`;
    const keyPrefix = newKey.slice(0, 8) + '...' + newKey.slice(-4);

    // Use bcrypt for secure hashing with generated salt
    console.log(`Generating API key for user ${user.id}`);
    const salt = await genSalt(10); // Cost factor of 10
    const keyHash = await hash(newKey, salt);

    // Insert to database
    const { error: insertError } = await supabase
      .from('api_keys')
      .insert({
        user_id: user.id,
        key_name: sanitizedKeyName,
        key_hash: keyHash,
        key_prefix: keyPrefix,
        is_active: true
      });

    if (insertError) {
      console.error('Insert error:', insertError);
      return new Response(JSON.stringify({ error: 'Failed to create API key' }), {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      });
    }

    console.log(`API key created successfully for user ${user.id}`);

    // Return the plaintext key only once for the user to copy
    return new Response(JSON.stringify({ 
      success: true,
      key: newKey,
      message: 'API key created. Copy it now - it will not be shown again!'
    }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });

  } catch (error: unknown) {
    console.error('Generate API key error:', error);
    // Return generic error to client, log details server-side only
    return new Response(JSON.stringify({ error: 'An internal error occurred' }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });
  }
});
