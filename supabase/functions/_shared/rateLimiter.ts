// Shared Rate Limiter for Edge Functions
// Server-side rate limiting - frontend limits are ignored

import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

export interface RateLimitConfig {
  windowMs: number;          // Time window in milliseconds
  maxRequests: number;       // Max requests per window
  keyPrefix: string;         // Prefix for rate limit key
  blockDurationMs?: number;  // How long to block after limit exceeded
}

export interface RateLimitResult {
  allowed: boolean;
  remaining: number;
  resetAt: number;
  retryAfter?: number;
}

// In-memory store for edge function instances (reset on cold start)
const rateLimitStore = new Map<string, { count: number; resetAt: number; blocked?: number }>();

export function getRateLimitKey(config: RateLimitConfig, identifier: string): string {
  return `${config.keyPrefix}:${identifier}`;
}

export async function checkRateLimit(
  config: RateLimitConfig,
  identifier: string,
  supabase?: ReturnType<typeof createClient>
): Promise<RateLimitResult> {
  const key = getRateLimitKey(config, identifier);
  const now = Date.now();
  
  // Get current state
  let state = rateLimitStore.get(key);
  
  // Check if blocked
  if (state?.blocked && state.blocked > now) {
    return {
      allowed: false,
      remaining: 0,
      resetAt: state.blocked,
      retryAfter: Math.ceil((state.blocked - now) / 1000),
    };
  }
  
  // Reset window if expired
  if (!state || state.resetAt <= now) {
    state = {
      count: 0,
      resetAt: now + config.windowMs,
    };
  }
  
  // Increment count
  state.count++;
  
  // Check if limit exceeded
  if (state.count > config.maxRequests) {
    // Block if configured
    if (config.blockDurationMs) {
      state.blocked = now + config.blockDurationMs;
    }
    
    rateLimitStore.set(key, state);
    
    // Log rate limit breach to console (table insert handled by main function)
    console.warn(`[RateLimiter] Rate limit exceeded for ${identifier}: ${config.keyPrefix} (${state.count} requests)`);
    
    return {
      allowed: false,
      remaining: 0,
      resetAt: state.resetAt,
      retryAfter: Math.ceil((state.resetAt - now) / 1000),
    };
  }
  
  rateLimitStore.set(key, state);
  
  return {
    allowed: true,
    remaining: config.maxRequests - state.count,
    resetAt: state.resetAt,
  };
}

// Add rate limit headers to response
export function addRateLimitHeaders(
  headers: Headers,
  result: RateLimitResult,
  config: RateLimitConfig
): Headers {
  headers.set('X-RateLimit-Limit', config.maxRequests.toString());
  headers.set('X-RateLimit-Remaining', result.remaining.toString());
  headers.set('X-RateLimit-Reset', Math.ceil(result.resetAt / 1000).toString());
  
  if (!result.allowed && result.retryAfter) {
    headers.set('Retry-After', result.retryAfter.toString());
  }
  
  return headers;
}

// Preset configurations
export const RATE_LIMITS = {
  // Standard API - 100 requests per minute
  STANDARD: {
    windowMs: 60 * 1000,
    maxRequests: 100,
    keyPrefix: 'api_standard',
  } as RateLimitConfig,
  
  // Auth endpoints - 10 attempts per minute
  AUTH: {
    windowMs: 60 * 1000,
    maxRequests: 10,
    keyPrefix: 'api_auth',
    blockDurationMs: 5 * 60 * 1000, // 5 minute block
  } as RateLimitConfig,
  
  // Job creation - 20 per minute
  JOBS: {
    windowMs: 60 * 1000,
    maxRequests: 20,
    keyPrefix: 'api_jobs',
  } as RateLimitConfig,
  
  // Admin endpoints - 50 per minute
  ADMIN: {
    windowMs: 60 * 1000,
    maxRequests: 50,
    keyPrefix: 'api_admin',
  } as RateLimitConfig,
  
  // Webhooks - 100 per minute (higher for payment providers)
  WEBHOOKS: {
    windowMs: 60 * 1000,
    maxRequests: 100,
    keyPrefix: 'api_webhooks',
  } as RateLimitConfig,
  
  // Health checks - 10 per minute
  HEALTH: {
    windowMs: 60 * 1000,
    maxRequests: 10,
    keyPrefix: 'api_health',
  } as RateLimitConfig,
};

// Middleware helper for edge functions
export async function withRateLimit(
  req: Request,
  config: RateLimitConfig,
  handler: () => Promise<Response>,
  supabase?: ReturnType<typeof createClient>
): Promise<Response> {
  // Get identifier - prefer user ID, fall back to IP
  const authHeader = req.headers.get('Authorization');
  let identifier = req.headers.get('x-forwarded-for')?.split(',')[0] || 
                   req.headers.get('x-real-ip') || 
                   'unknown';
  
  // If we have auth, use user ID (more accurate)
  if (authHeader && supabase) {
    try {
      const token = authHeader.replace('Bearer ', '');
      const { data: { user } } = await supabase.auth.getUser(token);
      if (user) {
        identifier = user.id;
      }
    } catch {
      // Fall back to IP
    }
  }
  
  const result = await checkRateLimit(config, identifier, supabase);
  
  if (!result.allowed) {
    const headers = new Headers({
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*',
    });
    addRateLimitHeaders(headers, result, config);
    
    return new Response(
      JSON.stringify({
        error: 'Rate limit exceeded',
        retryAfter: result.retryAfter,
        message: `Too many requests. Please try again in ${result.retryAfter} seconds.`,
      }),
      { status: 429, headers }
    );
  }
  
  // Call the actual handler
  const response = await handler();
  
  // Add rate limit headers to successful response
  const headers = new Headers(response.headers);
  addRateLimitHeaders(headers, result, config);
  
  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers,
  });
}
