// AbusePatternDetector - Real-time abuse pattern detection and auto-response
// Rule: Every endpoint assumes attackers exist

import { supabase } from '@/integrations/supabase/client';

export type AbusePattern = 
  | 'brute_force_auth'
  | 'credential_stuffing'
  | 'api_scraping'
  | 'rate_limit_evasion'
  | 'resource_exhaustion'
  | 'injection_attempt'
  | 'enumeration_attack'
  | 'bot_behavior';

export type AbuseResponse = 
  | 'log_only'
  | 'rate_limit'
  | 'slow_down'
  | 'temporary_block'
  | 'permanent_block'
  | 'captcha_challenge';

export interface AbuseEvent {
  id: string;
  pattern: AbusePattern;
  identifier: string; // IP or user ID
  identifierType: 'ip' | 'user' | 'api_key';
  detectedAt: string;
  confidence: number; // 0-1
  indicators: string[];
  response: AbuseResponse;
  blocked: boolean;
}

export interface PatternRule {
  pattern: AbusePattern;
  indicators: string[];
  threshold: number;
  windowMs: number;
  response: AbuseResponse;
  blockDurationMs: number;
}

export interface AbuseStats {
  totalEventsToday: number;
  blockedToday: number;
  topPatterns: Array<{ pattern: AbusePattern; count: number }>;
  topIdentifiers: Array<{ identifier: string; count: number }>;
  responseBreakdown: Record<AbuseResponse, number>;
}

class AbusePatternDetector {
  private static instance: AbusePatternDetector;
  private rules: PatternRule[];
  private recentEvents: AbuseEvent[] = [];
  private blockedIdentifiers: Map<string, { until: number; reason: AbusePattern }> = new Map();
  private requestHistory: Map<string, Array<{ timestamp: number; endpoint: string }>> = new Map();

  private constructor() {
    this.rules = [
      {
        pattern: 'brute_force_auth',
        indicators: ['repeated_auth_failures', 'password_guessing'],
        threshold: 5,
        windowMs: 60000, // 1 minute
        response: 'temporary_block',
        blockDurationMs: 300000, // 5 minutes
      },
      {
        pattern: 'credential_stuffing',
        indicators: ['multiple_accounts_same_ip', 'known_breach_passwords'],
        threshold: 3,
        windowMs: 300000, // 5 minutes
        response: 'temporary_block',
        blockDurationMs: 3600000, // 1 hour
      },
      {
        pattern: 'api_scraping',
        indicators: ['high_request_rate', 'sequential_ids', 'no_cache_headers'],
        threshold: 100,
        windowMs: 60000,
        response: 'rate_limit',
        blockDurationMs: 600000,
      },
      {
        pattern: 'rate_limit_evasion',
        indicators: ['ip_rotation', 'user_agent_rotation', 'timing_patterns'],
        threshold: 10,
        windowMs: 300000,
        response: 'slow_down',
        blockDurationMs: 1800000, // 30 minutes
      },
      {
        pattern: 'resource_exhaustion',
        indicators: ['large_payloads', 'expensive_queries', 'concurrent_connections'],
        threshold: 20,
        windowMs: 60000,
        response: 'temporary_block',
        blockDurationMs: 600000,
      },
      {
        pattern: 'injection_attempt',
        indicators: ['sql_patterns', 'xss_patterns', 'path_traversal'],
        threshold: 1,
        windowMs: 60000,
        response: 'permanent_block',
        blockDurationMs: 86400000, // 24 hours
      },
      {
        pattern: 'enumeration_attack',
        indicators: ['sequential_resource_access', 'error_pattern_analysis'],
        threshold: 15,
        windowMs: 60000,
        response: 'slow_down',
        blockDurationMs: 300000,
      },
      {
        pattern: 'bot_behavior',
        indicators: ['no_js_execution', 'headless_browser', 'timing_too_fast'],
        threshold: 5,
        windowMs: 60000,
        response: 'captcha_challenge',
        blockDurationMs: 0,
      },
    ];
  }

  static getInstance(): AbusePatternDetector {
    if (!AbusePatternDetector.instance) {
      AbusePatternDetector.instance = new AbusePatternDetector();
    }
    return AbusePatternDetector.instance;
  }

  // Check if an identifier is blocked
  isBlocked(identifier: string): { blocked: boolean; reason?: AbusePattern; unblockAt?: number } {
    this.cleanupExpiredBlocks();
    
    const block = this.blockedIdentifiers.get(identifier);
    if (block && block.until > Date.now()) {
      return { blocked: true, reason: block.reason, unblockAt: block.until };
    }
    return { blocked: false };
  }

  // Record a request for pattern analysis
  recordRequest(identifier: string, endpoint: string): void {
    const history = this.requestHistory.get(identifier) || [];
    history.push({ timestamp: Date.now(), endpoint });
    
    // Keep only last 5 minutes of history
    const fiveMinutesAgo = Date.now() - 300000;
    const filteredHistory = history.filter(h => h.timestamp > fiveMinutesAgo);
    
    this.requestHistory.set(identifier, filteredHistory);
  }

  // Analyze for abuse patterns
  async analyzeRequest(params: {
    identifier: string;
    identifierType: 'ip' | 'user' | 'api_key';
    endpoint: string;
    method: string;
    statusCode: number;
    responseTimeMs: number;
    payload?: Record<string, unknown>;
  }): Promise<AbuseEvent | null> {
    const { identifier, identifierType, endpoint, statusCode, payload } = params;
    
    // Record request
    this.recordRequest(identifier, endpoint);
    
    // Check for blocked status first
    const blockStatus = this.isBlocked(identifier);
    if (blockStatus.blocked) {
      return null; // Already blocked, let middleware handle
    }
    
    // Detect patterns
    const detectedPatterns: Array<{ pattern: AbusePattern; confidence: number; indicators: string[] }> = [];
    
    // Check for brute force auth
    if (endpoint.includes('auth') && statusCode === 401) {
      const authFailures = this.countRecentFailures(identifier, 'auth', 60000);
      if (authFailures >= 5) {
        detectedPatterns.push({
          pattern: 'brute_force_auth',
          confidence: Math.min(authFailures / 10, 1),
          indicators: ['repeated_auth_failures'],
        });
      }
    }
    
    // Check for API scraping
    const requestRate = this.getRequestRate(identifier, 60000);
    if (requestRate > 100) {
      detectedPatterns.push({
        pattern: 'api_scraping',
        confidence: Math.min(requestRate / 200, 1),
        indicators: ['high_request_rate'],
      });
    }
    
    // Check for injection attempts
    if (payload) {
      const payloadStr = JSON.stringify(payload).toLowerCase();
      const injectionPatterns = [
        /select\s+.*\s+from/i,
        /union\s+select/i,
        /<script/i,
        /javascript:/i,
        /\.\.\//,
      ];
      
      const hasInjection = injectionPatterns.some(p => p.test(payloadStr));
      if (hasInjection) {
        detectedPatterns.push({
          pattern: 'injection_attempt',
          confidence: 1,
          indicators: ['sql_patterns', 'xss_patterns'],
        });
      }
    }
    
    // Check for resource exhaustion
    if (params.responseTimeMs > 5000) {
      detectedPatterns.push({
        pattern: 'resource_exhaustion',
        confidence: Math.min(params.responseTimeMs / 10000, 1),
        indicators: ['expensive_queries'],
      });
    }
    
    // No patterns detected
    if (detectedPatterns.length === 0) {
      return null;
    }
    
    // Get the most severe pattern
    const mostSevere = detectedPatterns.sort((a, b) => b.confidence - a.confidence)[0];
    const rule = this.rules.find(r => r.pattern === mostSevere.pattern);
    
    if (!rule) return null;
    
    // Create abuse event
    const event: AbuseEvent = {
      id: `abuse_${Date.now()}`,
      pattern: mostSevere.pattern,
      identifier,
      identifierType,
      detectedAt: new Date().toISOString(),
      confidence: mostSevere.confidence,
      indicators: mostSevere.indicators,
      response: rule.response,
      blocked: false,
    };
    
    // Apply response
    await this.applyResponse(event, rule);
    
    // Log event
    this.recentEvents.unshift(event);
    this.recentEvents = this.recentEvents.slice(0, 1000);
    
    // Log to database
    await this.logAbuseEvent(event);
    
    return event;
  }

  private async applyResponse(event: AbuseEvent, rule: PatternRule): Promise<void> {
    switch (rule.response) {
      case 'temporary_block':
      case 'permanent_block':
        this.blockedIdentifiers.set(event.identifier, {
          until: Date.now() + rule.blockDurationMs,
          reason: event.pattern,
        });
        event.blocked = true;
        console.log(`[AbusePatternDetector] Blocked ${event.identifier} for ${event.pattern}`);
        break;
        
      case 'slow_down':
        // In production, this would set a slow-down flag for the rate limiter
        console.log(`[AbusePatternDetector] Slowing down ${event.identifier}`);
        break;
        
      case 'rate_limit':
        // In production, this would reduce rate limits for the identifier
        console.log(`[AbusePatternDetector] Rate limiting ${event.identifier}`);
        break;
        
      case 'captcha_challenge':
        // In production, this would flag for captcha challenge
        console.log(`[AbusePatternDetector] Captcha required for ${event.identifier}`);
        break;
    }
  }

  private async logAbuseEvent(event: AbuseEvent): Promise<void> {
    try {
      await supabase.from('security_audit_log').insert({
        action: 'abuse_detected',
        resource_type: 'abuse_detection',
        resource_id: event.id,
        result: event.blocked ? 'blocked' : 'flagged',
        reason: event.pattern,
        metadata: {
          identifier: event.identifier,
          identifierType: event.identifierType,
          confidence: event.confidence,
          indicators: event.indicators,
          response: event.response,
        },
      });
    } catch (error) {
      console.error('[AbusePatternDetector] Failed to log abuse event:', error);
    }
  }

  private countRecentFailures(identifier: string, endpointPattern: string, windowMs: number): number {
    const history = this.requestHistory.get(identifier) || [];
    const cutoff = Date.now() - windowMs;
    return history.filter(h => h.timestamp > cutoff && h.endpoint.includes(endpointPattern)).length;
  }

  private getRequestRate(identifier: string, windowMs: number): number {
    const history = this.requestHistory.get(identifier) || [];
    const cutoff = Date.now() - windowMs;
    return history.filter(h => h.timestamp > cutoff).length;
  }

  private cleanupExpiredBlocks(): void {
    const now = Date.now();
    for (const [identifier, block] of this.blockedIdentifiers.entries()) {
      if (block.until <= now) {
        this.blockedIdentifiers.delete(identifier);
      }
    }
  }

  // Get abuse statistics
  getStats(): AbuseStats {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const todayEvents = this.recentEvents.filter(e => new Date(e.detectedAt) >= today);
    
    // Count by pattern
    const patternCounts: Record<string, number> = {};
    const identifierCounts: Record<string, number> = {};
    const responseCounts: Record<string, number> = {};
    
    todayEvents.forEach(e => {
      patternCounts[e.pattern] = (patternCounts[e.pattern] || 0) + 1;
      identifierCounts[e.identifier] = (identifierCounts[e.identifier] || 0) + 1;
      responseCounts[e.response] = (responseCounts[e.response] || 0) + 1;
    });
    
    return {
      totalEventsToday: todayEvents.length,
      blockedToday: todayEvents.filter(e => e.blocked).length,
      topPatterns: Object.entries(patternCounts)
        .map(([pattern, count]) => ({ pattern: pattern as AbusePattern, count }))
        .sort((a, b) => b.count - a.count)
        .slice(0, 5),
      topIdentifiers: Object.entries(identifierCounts)
        .map(([identifier, count]) => ({ identifier, count }))
        .sort((a, b) => b.count - a.count)
        .slice(0, 5),
      responseBreakdown: responseCounts as Record<AbuseResponse, number>,
    };
  }

  // Get blocked identifiers
  getBlockedIdentifiers(): Array<{ identifier: string; reason: AbusePattern; until: number }> {
    this.cleanupExpiredBlocks();
    return Array.from(this.blockedIdentifiers.entries()).map(([identifier, block]) => ({
      identifier,
      reason: block.reason,
      until: block.until,
    }));
  }

  // Manually unblock an identifier
  unblock(identifier: string): boolean {
    return this.blockedIdentifiers.delete(identifier);
  }

  // Get rules
  getRules(): PatternRule[] {
    return [...this.rules];
  }

  // Update a rule
  updateRule(pattern: AbusePattern, updates: Partial<PatternRule>): void {
    const rule = this.rules.find(r => r.pattern === pattern);
    if (rule) {
      Object.assign(rule, updates);
    }
  }
}

export const abusePatternDetector = AbusePatternDetector.getInstance();
