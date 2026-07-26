// SelfAwarenessLogger - Every request logs: path, reasoning, confidence, compute status
// Goal: Complete transparency into how every request is handled

interface RequestLog {
  id: string;
  timestamp: Date;
  requestType: string;

  // Decision path
  chosenPath: "cache" | "prediction" | "lookup" | "compute" | "delegate" | "reject";
  pathReason: string;
  confidence: number;

  // Compute tracking
  computeAvoided: boolean;
  computeAvoidanceMethod?:
    "cached" | "predicted" | "approximated" | "delegated" | "short-circuited";
  gpuSavingsMs?: number;

  // Authority tracking
  authorityRequired: boolean;
  authorityType?: "human" | "legal" | "hardware" | "none";
  authorityStatus?: "pending" | "approved" | "rejected" | "n/a";

  // Performance
  latencyMs: number;

  // Metadata
  userId?: string;
  moduleName?: string;
  metadata?: Record<string, unknown>;
}

interface AggregatedStats {
  totalRequests: number;

  // Path distribution
  pathDistribution: Record<string, number>;

  // Compute avoidance
  computeAvoided: number;
  computeAvoidanceRate: number;
  totalGpuSavingsMs: number;

  // Confidence
  avgConfidence: number;
  highConfidenceRequests: number;
  lowConfidenceRequests: number;

  // Authority
  authorityRequired: number;
  authorityApproved: number;
  authorityRejected: number;

  // Performance
  avgLatencyMs: number;
  p95LatencyMs: number;
  p99LatencyMs: number;
}

interface RealTimeMetrics {
  requestsPerMinute: number;
  computeAvoidanceRateLast5Min: number;
  avgLatencyLast5Min: number;
  activeAuthority: number;
}

const STORAGE_KEY = "hyper_self_awareness";
const MAX_LOGS = 10000;

class SelfAwarenessLogger {
  private static instance: SelfAwarenessLogger;
  private logs: RequestLog[] = [];
  private recentLogs: RequestLog[] = []; // Last 5 minutes for real-time metrics
  private listeners: Set<(stats: AggregatedStats) => void> = new Set();

  private constructor() {
    this.loadFromStorage();
    this.startCleanupInterval();
  }

  static getInstance(): SelfAwarenessLogger {
    if (!SelfAwarenessLogger.instance) {
      SelfAwarenessLogger.instance = new SelfAwarenessLogger();
    }
    return SelfAwarenessLogger.instance;
  }

  // ===== LOGGING =====

  /**
   * Log a request with full decision context
   */
  logRequest(params: {
    requestType: string;
    chosenPath: RequestLog["chosenPath"];
    pathReason: string;
    confidence: number;
    computeAvoided: boolean;
    computeAvoidanceMethod?: RequestLog["computeAvoidanceMethod"];
    gpuSavingsMs?: number;
    authorityRequired?: boolean;
    authorityType?: RequestLog["authorityType"];
    authorityStatus?: RequestLog["authorityStatus"];
    latencyMs: number;
    userId?: string;
    moduleName?: string;
    metadata?: Record<string, unknown>;
  }): string {
    const id = `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    const log: RequestLog = {
      id,
      timestamp: new Date(),
      requestType: params.requestType,
      chosenPath: params.chosenPath,
      pathReason: params.pathReason,
      confidence: params.confidence,
      computeAvoided: params.computeAvoided,
      computeAvoidanceMethod: params.computeAvoidanceMethod,
      gpuSavingsMs: params.gpuSavingsMs,
      authorityRequired: params.authorityRequired || false,
      authorityType: params.authorityType,
      authorityStatus: params.authorityStatus,
      latencyMs: params.latencyMs,
      userId: params.userId,
      moduleName: params.moduleName,
      metadata: params.metadata,
    };

    this.logs.unshift(log);
    this.recentLogs.unshift(log);

    // Trim logs if too many
    if (this.logs.length > MAX_LOGS) {
      this.logs = this.logs.slice(0, MAX_LOGS);
    }

    // Keep only last 5 minutes in recent logs
    const fiveMinutesAgo = new Date(Date.now() - 5 * 60 * 1000);
    this.recentLogs = this.recentLogs.filter((l) => l.timestamp > fiveMinutesAgo);

    this.notifyListeners();
    this.saveToStorage();

    return id;
  }

  /**
   * Quick logging helper for common patterns
   */
  logCacheHit(
    requestType: string,
    latencyMs: number,
    gpuSavingsMs: number,
    userId?: string,
  ): string {
    return this.logRequest({
      requestType,
      chosenPath: "cache",
      pathReason: "Result found in cache",
      confidence: 1.0,
      computeAvoided: true,
      computeAvoidanceMethod: "cached",
      gpuSavingsMs,
      latencyMs,
      userId,
    });
  }

  logPrediction(
    requestType: string,
    confidence: number,
    latencyMs: number,
    userId?: string,
  ): string {
    return this.logRequest({
      requestType,
      chosenPath: "prediction",
      pathReason: "Result predicted based on patterns",
      confidence,
      computeAvoided: true,
      computeAvoidanceMethod: "predicted",
      latencyMs,
      userId,
    });
  }

  logCompute(requestType: string, latencyMs: number, userId?: string): string {
    return this.logRequest({
      requestType,
      chosenPath: "compute",
      pathReason: "Full compute required - no shortcuts available",
      confidence: 1.0,
      computeAvoided: false,
      latencyMs,
      userId,
    });
  }

  logDelegation(
    requestType: string,
    delegateTo: string,
    latencyMs: number,
    userId?: string,
  ): string {
    return this.logRequest({
      requestType,
      chosenPath: "delegate",
      pathReason: `Delegated to ${delegateTo}`,
      confidence: 0.95,
      computeAvoided: true,
      computeAvoidanceMethod: "delegated",
      latencyMs,
      userId,
    });
  }

  logAuthorityRequired(
    requestType: string,
    authorityType: RequestLog["authorityType"],
    userId?: string,
  ): string {
    return this.logRequest({
      requestType,
      chosenPath: "delegate",
      pathReason: `Authority required: ${authorityType}`,
      confidence: 1.0,
      computeAvoided: true,
      authorityRequired: true,
      authorityType,
      authorityStatus: "pending",
      latencyMs: 0,
      userId,
    });
  }

  // ===== AGGREGATED STATS =====

  getAggregatedStats(): AggregatedStats {
    if (this.logs.length === 0) {
      return this.emptyStats();
    }

    const pathDistribution: Record<string, number> = {};
    let computeAvoided = 0;
    let totalGpuSavings = 0;
    let totalConfidence = 0;
    let highConfidence = 0;
    let lowConfidence = 0;
    let authorityRequired = 0;
    let authorityApproved = 0;
    let authorityRejected = 0;
    const latencies: number[] = [];

    for (const log of this.logs) {
      // Path distribution
      pathDistribution[log.chosenPath] = (pathDistribution[log.chosenPath] || 0) + 1;

      // Compute avoidance
      if (log.computeAvoided) {
        computeAvoided++;
        totalGpuSavings += log.gpuSavingsMs || 0;
      }

      // Confidence
      totalConfidence += log.confidence;
      if (log.confidence >= 0.9) highConfidence++;
      if (log.confidence < 0.5) lowConfidence++;

      // Authority
      if (log.authorityRequired) {
        authorityRequired++;
        if (log.authorityStatus === "approved") authorityApproved++;
        if (log.authorityStatus === "rejected") authorityRejected++;
      }

      // Latency
      latencies.push(log.latencyMs);
    }

    // Sort latencies for percentiles
    latencies.sort((a, b) => a - b);

    return {
      totalRequests: this.logs.length,
      pathDistribution,
      computeAvoided,
      computeAvoidanceRate: computeAvoided / this.logs.length,
      totalGpuSavingsMs: totalGpuSavings,
      avgConfidence: totalConfidence / this.logs.length,
      highConfidenceRequests: highConfidence,
      lowConfidenceRequests: lowConfidence,
      authorityRequired,
      authorityApproved,
      authorityRejected,
      avgLatencyMs: latencies.reduce((a, b) => a + b, 0) / latencies.length,
      p95LatencyMs: latencies[Math.floor(latencies.length * 0.95)] || 0,
      p99LatencyMs: latencies[Math.floor(latencies.length * 0.99)] || 0,
    };
  }

  private emptyStats(): AggregatedStats {
    return {
      totalRequests: 0,
      pathDistribution: {},
      computeAvoided: 0,
      computeAvoidanceRate: 0,
      totalGpuSavingsMs: 0,
      avgConfidence: 0,
      highConfidenceRequests: 0,
      lowConfidenceRequests: 0,
      authorityRequired: 0,
      authorityApproved: 0,
      authorityRejected: 0,
      avgLatencyMs: 0,
      p95LatencyMs: 0,
      p99LatencyMs: 0,
    };
  }

  // ===== REAL-TIME METRICS =====

  getRealTimeMetrics(): RealTimeMetrics {
    const now = Date.now();
    const oneMinuteAgo = new Date(now - 60 * 1000);
    const fiveMinutesAgo = new Date(now - 5 * 60 * 1000);

    const lastMinute = this.recentLogs.filter((l) => l.timestamp > oneMinuteAgo);
    const lastFiveMinutes = this.recentLogs.filter((l) => l.timestamp > fiveMinutesAgo);

    const computeAvoidedLast5 = lastFiveMinutes.filter((l) => l.computeAvoided).length;
    const avgLatencyLast5 =
      lastFiveMinutes.length > 0
        ? lastFiveMinutes.reduce((sum, l) => sum + l.latencyMs, 0) / lastFiveMinutes.length
        : 0;
    const activeAuthority = lastFiveMinutes.filter(
      (l) => l.authorityRequired && l.authorityStatus === "pending",
    ).length;

    return {
      requestsPerMinute: lastMinute.length,
      computeAvoidanceRateLast5Min:
        lastFiveMinutes.length > 0 ? computeAvoidedLast5 / lastFiveMinutes.length : 0,
      avgLatencyLast5Min: avgLatencyLast5,
      activeAuthority,
    };
  }

  // ===== QUERY LOGS =====

  getLogs(params?: {
    limit?: number;
    offset?: number;
    chosenPath?: RequestLog["chosenPath"];
    userId?: string;
    since?: Date;
  }): RequestLog[] {
    let filtered = [...this.logs];

    if (params?.chosenPath) {
      filtered = filtered.filter((l) => l.chosenPath === params.chosenPath);
    }
    if (params?.userId) {
      filtered = filtered.filter((l) => l.userId === params.userId);
    }
    if (params?.since) {
      filtered = filtered.filter((l) => l.timestamp > params.since);
    }

    const offset = params?.offset || 0;
    const limit = params?.limit || 100;

    return filtered.slice(offset, offset + limit);
  }

  getLog(id: string): RequestLog | undefined {
    return this.logs.find((l) => l.id === id);
  }

  // ===== SUBSCRIPTIONS =====

  subscribe(listener: (stats: AggregatedStats) => void): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  private notifyListeners(): void {
    const stats = this.getAggregatedStats();
    this.listeners.forEach((l) => l(stats));
  }

  // ===== PERSISTENCE =====

  private saveToStorage(): void {
    try {
      // Only save last 1000 logs to storage
      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({
          logs: this.logs.slice(0, 1000),
        }),
      );
    } catch (e) {
      // Storage might be full
      console.warn("[SelfAwareness] Failed to save logs:", e);
    }
  }

  private loadFromStorage(): void {
    try {
      const data = localStorage.getItem(STORAGE_KEY);
      if (data) {
        const parsed = JSON.parse(data);
        if (parsed.logs) {
          this.logs = parsed.logs.map((l: RequestLog) => ({
            ...l,
            timestamp: new Date(l.timestamp),
          }));
        }
      }
    } catch (e) {
      console.warn("[SelfAwareness] Failed to load logs:", e);
    }
  }

  private startCleanupInterval(): void {
    setInterval(() => {
      // Keep only last 24 hours in memory
      const oneDayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000);
      this.logs = this.logs.filter((l) => l.timestamp > oneDayAgo);

      // Keep only last 5 minutes in recent logs
      const fiveMinutesAgo = new Date(Date.now() - 5 * 60 * 1000);
      this.recentLogs = this.recentLogs.filter((l) => l.timestamp > fiveMinutesAgo);
    }, 60000); // Every minute
  }

  // ===== EXPORT =====

  exportLogs(format: "json" | "csv" = "json"): string {
    if (format === "csv") {
      const headers = [
        "id",
        "timestamp",
        "requestType",
        "chosenPath",
        "pathReason",
        "confidence",
        "computeAvoided",
        "computeAvoidanceMethod",
        "gpuSavingsMs",
        "authorityRequired",
        "authorityType",
        "authorityStatus",
        "latencyMs",
        "userId",
        "moduleName",
      ];
      const rows = this.logs.map((l) =>
        [
          l.id,
          l.timestamp.toISOString(),
          l.requestType,
          l.chosenPath,
          l.pathReason,
          l.confidence,
          l.computeAvoided,
          l.computeAvoidanceMethod || "",
          l.gpuSavingsMs || "",
          l.authorityRequired,
          l.authorityType || "",
          l.authorityStatus || "",
          l.latencyMs,
          l.userId || "",
          l.moduleName || "",
        ].join(","),
      );
      return [headers.join(","), ...rows].join("\n");
    }
    return JSON.stringify(this.logs, null, 2);
  }

  clearLogs(): void {
    this.logs = [];
    this.recentLogs = [];
    this.saveToStorage();
  }
}

export const selfAwarenessLogger = SelfAwarenessLogger.getInstance();
export type { RequestLog, AggregatedStats, RealTimeMetrics };
