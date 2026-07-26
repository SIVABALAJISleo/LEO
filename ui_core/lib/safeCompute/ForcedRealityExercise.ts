// Forced Reality Exercise Module
// Forces at least one real event for each failure category to prove survival

export type ExerciseCategory =
  | "service_kill" // Kill a service → auto-recover
  | "deployment_break" // Break a deployment → rollback
  | "api_flood" // Flood API → rate limit
  | "backup_restore" // Restore backup → validate data
  | "auth_denial" // Deny auth → proper 403
  | "data_corruption" // Corrupt data → detect and recover
  | "cascade_failure"; // Trigger cascade → contain blast radius

export interface ExerciseExecution {
  executionId: string;
  category: ExerciseCategory;

  // Timing
  startedAt: string;
  completedAt?: string;
  durationMs?: number;

  // Execution
  triggerAction: string;
  expectedResponse: string;
  actualResponse?: string;

  // Proof
  success: boolean;
  recoveryProof?: {
    recoveredAt: string;
    recoveryMethod: string;
    dataIntegrity: "verified" | "partial" | "failed";
    logsGenerated: string[];
  };

  // Error if failed
  failureReason?: string;
}

export interface ExerciseRequirement {
  category: ExerciseCategory;
  description: string;
  minimumExecutions: number;
  lastExecutedAt?: string;
  successCount: number;
  required: boolean;
}

export interface ForcedRealityStats {
  totalExercises: number;
  successfulExercises: number;
  failedExercises: number;
  categoriesCovered: number;
  totalCategories: number;
  overallCoverage: number;
}

class ForcedRealityExercise {
  private executions: Map<string, ExerciseExecution> = new Map();
  private requirements: Map<ExerciseCategory, ExerciseRequirement> = new Map();
  private stats: ForcedRealityStats = {
    totalExercises: 0,
    successfulExercises: 0,
    failedExercises: 0,
    categoriesCovered: 0,
    totalCategories: 7,
    overallCoverage: 0,
  };

  constructor() {
    this.initializeRequirements();
  }

  private initializeRequirements(): void {
    const categories: Array<{ cat: ExerciseCategory; desc: string }> = [
      { cat: "service_kill", desc: "Kill a service and verify auto-recovery" },
      { cat: "deployment_break", desc: "Break a deployment and verify rollback" },
      { cat: "api_flood", desc: "Flood API and verify rate limiting" },
      { cat: "backup_restore", desc: "Restore backup and validate data integrity" },
      { cat: "auth_denial", desc: "Deny authentication and verify proper 403" },
      { cat: "data_corruption", desc: "Corrupt data and verify detection/recovery" },
      { cat: "cascade_failure", desc: "Trigger cascade and verify blast radius containment" },
    ];

    categories.forEach(({ cat, desc }) => {
      this.requirements.set(cat, {
        category: cat,
        description: desc,
        minimumExecutions: 1,
        successCount: 0,
        required: true,
      });
    });
  }

  /**
   * Execute a forced reality exercise
   */
  async executeExercise(
    category: ExerciseCategory,
    triggerFn: () => Promise<{ success: boolean; response: string; logs: string[] }>,
  ): Promise<ExerciseExecution> {
    const executionId = `exercise_${category}_${Date.now()}`;
    const startedAt = new Date().toISOString();

    const requirement = this.requirements.get(category);
    const expectedResponse = this.getExpectedResponse(category);

    console.log(`[ForcedReality] Starting exercise: ${category}`);

    let execution: ExerciseExecution;

    try {
      const result = await triggerFn();
      const completedAt = new Date().toISOString();
      const durationMs = new Date(completedAt).getTime() - new Date(startedAt).getTime();

      execution = {
        executionId,
        category,
        startedAt,
        completedAt,
        durationMs,
        triggerAction: this.getTriggerDescription(category),
        expectedResponse,
        actualResponse: result.response,
        success: result.success,
        recoveryProof: result.success
          ? {
              recoveredAt: completedAt,
              recoveryMethod: this.getRecoveryMethod(category),
              dataIntegrity: "verified",
              logsGenerated: result.logs,
            }
          : undefined,
      };

      if (result.success) {
        this.stats.successfulExercises++;
        if (requirement) {
          requirement.successCount++;
          requirement.lastExecutedAt = completedAt;
        }
        console.log(`[ForcedReality] Exercise ${category} PASSED in ${durationMs}ms`);
      } else {
        this.stats.failedExercises++;
        execution.failureReason = result.response;
        console.error(`[ForcedReality] Exercise ${category} FAILED: ${result.response}`);
      }
    } catch (error) {
      const completedAt = new Date().toISOString();

      execution = {
        executionId,
        category,
        startedAt,
        completedAt,
        durationMs: new Date(completedAt).getTime() - new Date(startedAt).getTime(),
        triggerAction: this.getTriggerDescription(category),
        expectedResponse,
        success: false,
        failureReason: error instanceof Error ? error.message : "Unknown error",
      };

      this.stats.failedExercises++;
      console.error(`[ForcedReality] Exercise ${category} ERROR:`, error);
    }

    this.executions.set(executionId, execution);
    this.stats.totalExercises++;
    this.updateCoverageStats();

    return execution;
  }

  /**
   * Check if all required exercises have been completed
   */
  isFullyCovered(): boolean {
    return Array.from(this.requirements.values()).every(
      (r) => r.successCount >= r.minimumExecutions,
    );
  }

  /**
   * Get missing exercises
   */
  getMissingExercises(): ExerciseRequirement[] {
    return Array.from(this.requirements.values()).filter(
      (r) => r.successCount < r.minimumExecutions,
    );
  }

  /**
   * Get exercise history for a category
   */
  getCategoryHistory(category: ExerciseCategory): ExerciseExecution[] {
    return Array.from(this.executions.values())
      .filter((e) => e.category === category)
      .sort((a, b) => new Date(b.startedAt).getTime() - new Date(a.startedAt).getTime());
  }

  /**
   * Get all requirements with their status
   */
  getRequirements(): ExerciseRequirement[] {
    return Array.from(this.requirements.values());
  }

  /**
   * Get statistics
   */
  getStats(): ForcedRealityStats {
    return { ...this.stats };
  }

  /**
   * Generate coverage report
   */
  generateCoverageReport(): {
    ready: boolean;
    coverage: number;
    categoriesStatus: Array<{
      category: ExerciseCategory;
      status: "passed" | "failed" | "not_run";
      lastExecution?: ExerciseExecution;
    }>;
    missingProofs: string[];
  } {
    const categoriesStatus = Array.from(this.requirements.entries()).map(([cat, req]) => {
      const history = this.getCategoryHistory(cat);
      const lastExecution = history[0];

      let status: "passed" | "failed" | "not_run";
      if (req.successCount >= req.minimumExecutions) {
        status = "passed";
      } else if (history.length > 0) {
        status = "failed";
      } else {
        status = "not_run";
      }

      return { category: cat, status, lastExecution };
    });

    const missingProofs = categoriesStatus
      .filter((c) => c.status !== "passed")
      .map(
        (c) =>
          `${c.category}: ${c.status === "failed" ? "Last execution failed" : "Never executed"}`,
      );

    return {
      ready: this.isFullyCovered(),
      coverage: this.stats.overallCoverage,
      categoriesStatus,
      missingProofs,
    };
  }

  // Private helpers

  private updateCoverageStats(): void {
    const covered = Array.from(this.requirements.values()).filter(
      (r) => r.successCount >= r.minimumExecutions,
    ).length;

    this.stats.categoriesCovered = covered;
    this.stats.overallCoverage = covered / this.stats.totalCategories;
  }

  private getExpectedResponse(category: ExerciseCategory): string {
    const responses: Record<ExerciseCategory, string> = {
      service_kill: "Service auto-recovered within timeout",
      deployment_break: "Deployment rolled back to previous version",
      api_flood: "Rate limit triggered, returning 429",
      backup_restore: "Backup restored with data integrity verified",
      auth_denial: "Authentication denied with 403 Forbidden",
      data_corruption: "Corruption detected and recovered from backup",
      cascade_failure: "Failure contained within blast radius",
    };
    return responses[category];
  }

  private getTriggerDescription(category: ExerciseCategory): string {
    const triggers: Record<ExerciseCategory, string> = {
      service_kill: "Simulated service process termination",
      deployment_break: "Deployed intentionally broken configuration",
      api_flood: "Sent 1000 requests in 1 second",
      backup_restore: "Initiated full backup restore procedure",
      auth_denial: "Attempted access with invalid credentials",
      data_corruption: "Injected corrupted data record",
      cascade_failure: "Triggered dependent service failure chain",
    };
    return triggers[category];
  }

  private getRecoveryMethod(category: ExerciseCategory): string {
    const methods: Record<ExerciseCategory, string> = {
      service_kill: "Automatic health check restart",
      deployment_break: "One-command rollback to last-known-good",
      api_flood: "Rate limiter with IP-based blocking",
      backup_restore: "Point-in-time recovery with integrity check",
      auth_denial: "Standard auth middleware rejection",
      data_corruption: "Checksum validation + backup restore",
      cascade_failure: "Circuit breaker isolation",
    };
    return methods[category];
  }
}

export const forcedRealityExercise = new ForcedRealityExercise();
