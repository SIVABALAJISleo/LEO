// CostProtection - Per-IP/user rate limits, burst detection, cost ceilings
// Goal: Protect the platform from abuse while keeping legitimate users happy

interface RateLimitConfig {
  windowMs: number;
  maxRequests: number;
  burstLimit: number;
  burstWindowMs: number;
}

interface RateLimitState {
  key: string;
  requestCount: number;
  windowStart: Date;
  burstCount: number;
  burstWindowStart: Date;
  blocked: boolean;
  blockedUntil?: Date;
  violations: number;
}

interface CostCeiling {
  userId: string;
  dailyLimit: number;
  monthlyLimit: number;
  currentDailySpend: number;
  currentMonthlySpend: number;
  lastResetDaily: Date;
  lastResetMonthly: Date;
  enforced: boolean;
}

interface AbuseEvent {
  id: string;
  type: 'rate-limit' | 'burst' | 'cost-exceeded' | 'suspicious-pattern';
  key: string;
  details: string;
  timestamp: Date;
  action: 'throttle' | 'temp-ban' | 'alert' | 'none';
  duration?: number;
}

interface CostProtectionStats {
  totalRequests: number;
  blockedRequests: number;
  throttledRequests: number;
  burstDetections: number;
  costExceeded: number;
  tempBans: number;
  activeRateLimits: number;
}

const DEFAULT_LIMITS: Record<string, RateLimitConfig> = {
  api: { windowMs: 60000, maxRequests: 100, burstLimit: 20, burstWindowMs: 1000 },
  auth: { windowMs: 60000, maxRequests: 10, burstLimit: 3, burstWindowMs: 5000 },
  jobs: { windowMs: 60000, maxRequests: 30, burstLimit: 5, burstWindowMs: 1000 },
  uploads: { windowMs: 60000, maxRequests: 20, burstLimit: 3, burstWindowMs: 5000 },
  expensive: { windowMs: 60000, maxRequests: 5, burstLimit: 2, burstWindowMs: 10000 },
};

class CostProtection {
  private static instance: CostProtection;
  private rateLimits: Map<string, RateLimitState> = new Map();
  private costCeilings: Map<string, CostCeiling> = new Map();
  private abuseEvents: AbuseEvent[] = [];
  private customLimits: Map<string, RateLimitConfig> = new Map();
  
  private stats: CostProtectionStats = {
    totalRequests: 0,
    blockedRequests: 0,
    throttledRequests: 0,
    burstDetections: 0,
    costExceeded: 0,
    tempBans: 0,
    activeRateLimits: 0,
  };

  private readonly TEMP_BAN_DURATION_MS = 300000; // 5 minutes
  private readonly VIOLATION_THRESHOLD = 5;

  private constructor() {
    this.loadFromStorage();
    this.startCleanupInterval();
  }

  static getInstance(): CostProtection {
    if (!CostProtection.instance) {
      CostProtection.instance = new CostProtection();
    }
    return CostProtection.instance;
  }

  // ===== RATE LIMITING =====

  /**
   * Check if a request should be allowed
   * Returns { allowed: boolean, retryAfter?: number, reason?: string }
   */
  checkRateLimit(params: {
    key: string; // e.g., `user_${userId}` or `ip_${ipAddress}`
    action: string; // e.g., 'api', 'auth', 'jobs'
  }): { allowed: boolean; retryAfter?: number; reason?: string } {
    const { key, action } = params;
    const fullKey = `${action}:${key}`;
    const config = this.customLimits.get(action) || DEFAULT_LIMITS[action] || DEFAULT_LIMITS.api;
    const now = new Date();

    this.stats.totalRequests++;

    // Get or create state
    let state = this.rateLimits.get(fullKey);
    if (!state) {
      state = {
        key: fullKey,
        requestCount: 0,
        windowStart: now,
        burstCount: 0,
        burstWindowStart: now,
        blocked: false,
        violations: 0,
      };
      this.rateLimits.set(fullKey, state);
    }

    // Check if currently blocked
    if (state.blocked && state.blockedUntil && now < state.blockedUntil) {
      this.stats.blockedRequests++;
      return {
        allowed: false,
        retryAfter: Math.ceil((state.blockedUntil.getTime() - now.getTime()) / 1000),
        reason: 'Temporarily blocked due to excessive requests',
      };
    } else if (state.blocked) {
      // Unblock if time has passed
      state.blocked = false;
      state.blockedUntil = undefined;
    }

    // Reset window if expired
    if (now.getTime() - state.windowStart.getTime() > config.windowMs) {
      state.requestCount = 0;
      state.windowStart = now;
    }

    // Reset burst window if expired
    if (now.getTime() - state.burstWindowStart.getTime() > config.burstWindowMs) {
      state.burstCount = 0;
      state.burstWindowStart = now;
    }

    // Check burst limit
    state.burstCount++;
    if (state.burstCount > config.burstLimit) {
      this.stats.burstDetections++;
      this.recordAbuseEvent({
        type: 'burst',
        key: fullKey,
        details: `Burst limit exceeded: ${state.burstCount}/${config.burstLimit}`,
        action: 'throttle',
      });
      return {
        allowed: false,
        retryAfter: Math.ceil(config.burstWindowMs / 1000),
        reason: 'Too many requests in a short time',
      };
    }

    // Check rate limit
    state.requestCount++;
    if (state.requestCount > config.maxRequests) {
      state.violations++;
      this.stats.throttledRequests++;

      // Apply temp ban if too many violations
      if (state.violations >= this.VIOLATION_THRESHOLD) {
        state.blocked = true;
        state.blockedUntil = new Date(now.getTime() + this.TEMP_BAN_DURATION_MS);
        this.stats.tempBans++;
        this.recordAbuseEvent({
          type: 'rate-limit',
          key: fullKey,
          details: `Temp ban applied after ${state.violations} violations`,
          action: 'temp-ban',
          duration: this.TEMP_BAN_DURATION_MS,
        });
      } else {
        this.recordAbuseEvent({
          type: 'rate-limit',
          key: fullKey,
          details: `Rate limit exceeded: ${state.requestCount}/${config.maxRequests}`,
          action: 'throttle',
        });
      }

      const retryAfter = Math.ceil((state.windowStart.getTime() + config.windowMs - now.getTime()) / 1000);
      return {
        allowed: false,
        retryAfter: Math.max(1, retryAfter),
        reason: 'Rate limit exceeded',
      };
    }

    // Decay violations on successful request
    state.violations = Math.max(0, state.violations - 0.1);

    this.stats.activeRateLimits = this.rateLimits.size;
    return { allowed: true };
  }

  // ===== COST CEILING ENFORCEMENT =====

  setCostCeiling(userId: string, dailyLimit: number, monthlyLimit: number): void {
    const existing = this.costCeilings.get(userId);
    const now = new Date();
    
    this.costCeilings.set(userId, {
      userId,
      dailyLimit,
      monthlyLimit,
      currentDailySpend: existing?.currentDailySpend || 0,
      currentMonthlySpend: existing?.currentMonthlySpend || 0,
      lastResetDaily: existing?.lastResetDaily || now,
      lastResetMonthly: existing?.lastResetMonthly || now,
      enforced: true,
    });
  }

  checkCostCeiling(userId: string, amount: number): { allowed: boolean; reason?: string } {
    const ceiling = this.costCeilings.get(userId);
    if (!ceiling || !ceiling.enforced) {
      return { allowed: true };
    }

    const now = new Date();

    // Reset daily if new day
    if (this.isDifferentDay(ceiling.lastResetDaily, now)) {
      ceiling.currentDailySpend = 0;
      ceiling.lastResetDaily = now;
    }

    // Reset monthly if new month
    if (this.isDifferentMonth(ceiling.lastResetMonthly, now)) {
      ceiling.currentMonthlySpend = 0;
      ceiling.lastResetMonthly = now;
    }

    // Check daily limit
    if (ceiling.currentDailySpend + amount > ceiling.dailyLimit) {
      this.stats.costExceeded++;
      this.recordAbuseEvent({
        type: 'cost-exceeded',
        key: userId,
        details: `Daily cost ceiling exceeded: ${ceiling.currentDailySpend + amount} > ${ceiling.dailyLimit}`,
        action: 'alert',
      });
      return { allowed: false, reason: 'Daily spending limit reached' };
    }

    // Check monthly limit
    if (ceiling.currentMonthlySpend + amount > ceiling.monthlyLimit) {
      this.stats.costExceeded++;
      this.recordAbuseEvent({
        type: 'cost-exceeded',
        key: userId,
        details: `Monthly cost ceiling exceeded: ${ceiling.currentMonthlySpend + amount} > ${ceiling.monthlyLimit}`,
        action: 'alert',
      });
      return { allowed: false, reason: 'Monthly spending limit reached' };
    }

    return { allowed: true };
  }

  recordCost(userId: string, amount: number): void {
    const ceiling = this.costCeilings.get(userId);
    if (ceiling) {
      ceiling.currentDailySpend += amount;
      ceiling.currentMonthlySpend += amount;
      this.saveToStorage();
    }
  }

  private isDifferentDay(date1: Date, date2: Date): boolean {
    return date1.toDateString() !== date2.toDateString();
  }

  private isDifferentMonth(date1: Date, date2: Date): boolean {
    return date1.getMonth() !== date2.getMonth() || date1.getFullYear() !== date2.getFullYear();
  }

  // ===== BURST DETECTION =====

  /**
   * Detect suspicious patterns (beyond simple rate limiting)
   */
  detectSuspiciousPattern(params: {
    key: string;
    action: string;
    metadata?: Record<string, unknown>;
  }): boolean {
    // This would integrate with more sophisticated pattern detection
    // For now, we check for anomalous request patterns
    const { key, action } = params;
    const fullKey = `${action}:${key}`;
    const state = this.rateLimits.get(fullKey);
    
    if (!state) return false;

    // Check for suspicious patterns:
    // 1. Very high request rate with consistent timing (bot behavior)
    // 2. Requests during unusual hours
    // 3. Repeated access to expensive endpoints

    if (state.violations > 3 && state.requestCount > 50) {
      this.recordAbuseEvent({
        type: 'suspicious-pattern',
        key: fullKey,
        details: 'Suspicious request pattern detected',
        action: 'alert',
      });
      return true;
    }

    return false;
  }

  // ===== CUSTOM LIMITS =====

  setCustomLimit(action: string, config: RateLimitConfig): void {
    this.customLimits.set(action, config);
  }

  removeCustomLimit(action: string): void {
    this.customLimits.delete(action);
  }

  // ===== ABUSE EVENTS =====

  private recordAbuseEvent(params: Omit<AbuseEvent, 'id' | 'timestamp'>): void {
    const event: AbuseEvent = {
      id: `abuse_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      ...params,
      timestamp: new Date(),
    };

    this.abuseEvents.unshift(event);
    if (this.abuseEvents.length > 1000) {
      this.abuseEvents = this.abuseEvents.slice(0, 1000);
    }

    console.log(`[CostProtection] Abuse event: ${event.type} - ${event.key} - ${event.details}`);
    this.saveToStorage();
  }

  getAbuseEvents(limit = 50): AbuseEvent[] {
    return this.abuseEvents.slice(0, limit);
  }

  // ===== CLEANUP =====

  private startCleanupInterval(): void {
    setInterval(() => {
      const now = new Date();
      const oneHourAgo = new Date(now.getTime() - 3600000);

      // Clean up old rate limit states
      for (const [key, state] of this.rateLimits.entries()) {
        if (state.windowStart < oneHourAgo && !state.blocked) {
          this.rateLimits.delete(key);
        }
      }

      this.stats.activeRateLimits = this.rateLimits.size;
    }, 60000); // Every minute
  }

  // ===== MANUAL CONTROLS =====

  unblockKey(key: string): void {
    for (const [fullKey, state] of this.rateLimits.entries()) {
      if (fullKey.includes(key)) {
        state.blocked = false;
        state.blockedUntil = undefined;
        state.violations = 0;
      }
    }
    this.saveToStorage();
  }

  blockKey(key: string, durationMs: number = this.TEMP_BAN_DURATION_MS): void {
    for (const [fullKey, state] of this.rateLimits.entries()) {
      if (fullKey.includes(key)) {
        state.blocked = true;
        state.blockedUntil = new Date(Date.now() + durationMs);
        this.stats.tempBans++;
      }
    }
    this.saveToStorage();
  }

  // ===== PERSISTENCE =====

  private saveToStorage(): void {
    try {
      localStorage.setItem('hyper_cost_protection', JSON.stringify({
        rateLimits: Array.from(this.rateLimits.entries()),
        costCeilings: Array.from(this.costCeilings.entries()),
        abuseEvents: this.abuseEvents.slice(0, 100),
        stats: this.stats,
      }));
    } catch (e) {
      console.warn('[CostProtection] Failed to save state:', e);
    }
  }

  private loadFromStorage(): void {
    try {
      const data = localStorage.getItem('hyper_cost_protection');
      if (data) {
        const parsed = JSON.parse(data);
        if (parsed.rateLimits) {
          this.rateLimits = new Map(parsed.rateLimits.map(([k, v]: [string, RateLimitState]) => [
            k,
            { ...v, windowStart: new Date(v.windowStart), burstWindowStart: new Date(v.burstWindowStart), blockedUntil: v.blockedUntil ? new Date(v.blockedUntil) : undefined }
          ]));
        }
        if (parsed.costCeilings) {
          this.costCeilings = new Map(parsed.costCeilings.map(([k, v]: [string, CostCeiling]) => [
            k,
            { ...v, lastResetDaily: new Date(v.lastResetDaily), lastResetMonthly: new Date(v.lastResetMonthly) }
          ]));
        }
        if (parsed.abuseEvents) {
          this.abuseEvents = parsed.abuseEvents.map((e: AbuseEvent) => ({
            ...e,
            timestamp: new Date(e.timestamp),
          }));
        }
        if (parsed.stats) {
          this.stats = { ...this.stats, ...parsed.stats };
        }
      }
    } catch (e) {
      console.warn('[CostProtection] Failed to load state:', e);
    }
  }

  // ===== STATS =====

  getStats(): CostProtectionStats {
    return { ...this.stats };
  }

  getCostCeiling(userId: string): CostCeiling | undefined {
    return this.costCeilings.get(userId);
  }
}

export const costProtection = CostProtection.getInstance();
export type { RateLimitConfig, RateLimitState, CostCeiling, AbuseEvent, CostProtectionStats };
