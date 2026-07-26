// ExecutionAuditLogger - Deterministic execution pipeline audit
// Every decision logged with reason, no silent fallbacks

export type ExecutionPath =
  | "SHORTCUT"
  | "LOOKUP"
  | "SURROGATE"
  | "DISTRIBUTED"
  | "RAW_COMPUTE"
  | "AUTHORITY_GOVERNED"
  | "EXPLAIN";

export type ExecutionOutcome =
  "completed" | "delegated" | "avoided" | "failed" | "authority_pending";

export interface ExecutionAuditEntry {
  id: string;
  timestamp: string;
  workloadId: string;
  workloadType: string;

  // Decision path
  selectedPath: ExecutionPath;
  pathReason: string;
  confidence: number;

  // Outcome
  outcome: ExecutionOutcome;
  outcomeReason: string;

  // Metrics
  latencyMs: number;
  gpuAvoided: boolean;
  surrogateUsed: boolean;

  // Authority
  authorityRequired: boolean;
  authorityStatus?: "pending" | "approved" | "denied";

  // Reproducibility
  inputHash: string;
  outputHash?: string;
}

class ExecutionAuditLogger {
  private static instance: ExecutionAuditLogger;
  private auditLog: ExecutionAuditEntry[] = [];
  private readonly MAX_LOG_SIZE = 10000;

  private constructor() {}

  static getInstance(): ExecutionAuditLogger {
    if (!ExecutionAuditLogger.instance) {
      ExecutionAuditLogger.instance = new ExecutionAuditLogger();
    }
    return ExecutionAuditLogger.instance;
  }

  // Generate deterministic hash for reproducibility
  private async generateHash(data: unknown): Promise<string> {
    const str = JSON.stringify(data);
    const encoder = new TextEncoder();
    const dataBuffer = encoder.encode(str);
    const hashBuffer = await crypto.subtle.digest("SHA-256", dataBuffer);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray
      .slice(0, 8)
      .map((b) => b.toString(16).padStart(2, "0"))
      .join("");
  }

  // Log execution decision
  async logExecution(params: {
    workloadId: string;
    workloadType: string;
    selectedPath: ExecutionPath;
    pathReason: string;
    confidence: number;
    outcome: ExecutionOutcome;
    outcomeReason: string;
    latencyMs: number;
    gpuAvoided: boolean;
    surrogateUsed: boolean;
    authorityRequired: boolean;
    authorityStatus?: "pending" | "approved" | "denied";
    input: unknown;
    output?: unknown;
  }): Promise<ExecutionAuditEntry> {
    const entry: ExecutionAuditEntry = {
      id: crypto.randomUUID(),
      timestamp: new Date().toISOString(),
      workloadId: params.workloadId,
      workloadType: params.workloadType,
      selectedPath: params.selectedPath,
      pathReason: params.pathReason,
      confidence: params.confidence,
      outcome: params.outcome,
      outcomeReason: params.outcomeReason,
      latencyMs: params.latencyMs,
      gpuAvoided: params.gpuAvoided,
      surrogateUsed: params.surrogateUsed,
      authorityRequired: params.authorityRequired,
      authorityStatus: params.authorityStatus,
      inputHash: await this.generateHash(params.input),
      outputHash: params.output ? await this.generateHash(params.output) : undefined,
    };

    this.auditLog.push(entry);

    // Trim log if too large
    if (this.auditLog.length > this.MAX_LOG_SIZE) {
      this.auditLog = this.auditLog.slice(-this.MAX_LOG_SIZE);
    }

    return entry;
  }

  // Get execution stats
  getStats(): {
    total: number;
    byPath: Record<ExecutionPath, number>;
    byOutcome: Record<ExecutionOutcome, number>;
    gpuAvoidedCount: number;
    surrogateUsedCount: number;
    authorityRequiredCount: number;
    avgLatencyMs: number;
    avgConfidence: number;
  } {
    const byPath: Record<ExecutionPath, number> = {
      SHORTCUT: 0,
      LOOKUP: 0,
      SURROGATE: 0,
      DISTRIBUTED: 0,
      RAW_COMPUTE: 0,
      AUTHORITY_GOVERNED: 0,
      EXPLAIN: 0,
    };

    const byOutcome: Record<ExecutionOutcome, number> = {
      completed: 0,
      delegated: 0,
      avoided: 0,
      failed: 0,
      authority_pending: 0,
    };

    let totalLatency = 0;
    let totalConfidence = 0;
    let gpuAvoidedCount = 0;
    let surrogateUsedCount = 0;
    let authorityRequiredCount = 0;

    for (const entry of this.auditLog) {
      byPath[entry.selectedPath]++;
      byOutcome[entry.outcome]++;
      totalLatency += entry.latencyMs;
      totalConfidence += entry.confidence;
      if (entry.gpuAvoided) gpuAvoidedCount++;
      if (entry.surrogateUsed) surrogateUsedCount++;
      if (entry.authorityRequired) authorityRequiredCount++;
    }

    return {
      total: this.auditLog.length,
      byPath,
      byOutcome,
      gpuAvoidedCount,
      surrogateUsedCount,
      authorityRequiredCount,
      avgLatencyMs: this.auditLog.length > 0 ? totalLatency / this.auditLog.length : 0,
      avgConfidence: this.auditLog.length > 0 ? totalConfidence / this.auditLog.length : 0,
    };
  }

  // Get recent entries for debugging
  getRecentEntries(count: number = 50): ExecutionAuditEntry[] {
    return this.auditLog.slice(-count);
  }

  // Find entries by workload ID
  findByWorkloadId(workloadId: string): ExecutionAuditEntry[] {
    return this.auditLog.filter((e) => e.workloadId === workloadId);
  }

  // Verify reproducibility - same input should produce same path
  async verifyReproducibility(
    input: unknown,
    expectedPath: ExecutionPath,
  ): Promise<{
    reproducible: boolean;
    inputHash: string;
    previousEntries: ExecutionAuditEntry[];
  }> {
    const inputHash = await this.generateHash(input);
    const previousEntries = this.auditLog.filter((e) => e.inputHash === inputHash);

    const reproducible =
      previousEntries.length === 0 || previousEntries.every((e) => e.selectedPath === expectedPath);

    return {
      reproducible,
      inputHash,
      previousEntries,
    };
  }

  // Export for external audit
  exportLog(): ExecutionAuditEntry[] {
    return [...this.auditLog];
  }

  // Clear log (admin only)
  clearLog(): void {
    this.auditLog = [];
  }
}

export const executionAuditLogger = ExecutionAuditLogger.getInstance();
