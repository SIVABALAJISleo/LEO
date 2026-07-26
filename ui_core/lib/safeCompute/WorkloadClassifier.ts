/**
 * WORKLOAD INTELLIGENCE CLASSIFIER
 *
 * Classifies every task BEFORE execution to determine optimal handling.
 * NO task may run before classification.
 */

export type WorkloadCategory =
  | "perceptual_tolerant" // Visual/audio where approximation is acceptable
  | "precision_critical" // Financial, medical, scientific - exact required
  | "latency_critical" // Real-time responses required
  | "throughput_critical" // Bulk processing, batch jobs
  | "cacheable" // Result can be stored and reused
  | "reusable" // Similar past results can apply
  | "batchable" // Can be grouped with similar workloads
  | "deferrable"; // Can wait for optimal execution window

export interface WorkloadClassification {
  id: string;
  categories: WorkloadCategory[];
  primaryCategory: WorkloadCategory;
  gpuRequired: boolean;
  canAvoid: boolean;
  avoidanceStrategies: AvoidanceStrategy[];
  qualityFloor: number; // Minimum acceptable quality 0-1
  latencyBudgetMs: number; // Max acceptable latency
  downscaleable: boolean; // Can reduce precision/resolution
  delegatable: boolean; // Can be sent to external GPU
  confidence: number; // Classification confidence 0-1
  classifiedAt: Date;
}

export type AvoidanceStrategy =
  | "cache_hit" // Use cached result
  | "similarity_collapse" // Merge with similar pending workload
  | "progressive_render" // Start low-res, refine if needed
  | "perception_equivalent" // Use perceptually equivalent shortcut
  | "early_exit" // Stop when confidence threshold met
  | "downscale" // Reduce precision/resolution
  | "temporal_batch" // Wait and batch with similar jobs
  | "defer" // Schedule for off-peak
  | "none"; // Must execute fully

export interface ClassificationStats {
  totalClassified: number;
  byCategory: Record<WorkloadCategory, number>;
  gpuRequiredCount: number;
  gpuAvoidedCount: number;
  avoidanceRate: number;
}

class WorkloadClassifierEngine {
  private static instance: WorkloadClassifierEngine;
  private classifications: Map<string, WorkloadClassification> = new Map();
  private stats: ClassificationStats = {
    totalClassified: 0,
    byCategory: {
      perceptual_tolerant: 0,
      precision_critical: 0,
      latency_critical: 0,
      throughput_critical: 0,
      cacheable: 0,
      reusable: 0,
      batchable: 0,
      deferrable: 0,
    },
    gpuRequiredCount: 0,
    gpuAvoidedCount: 0,
    avoidanceRate: 0,
  };

  private constructor() {}

  static getInstance(): WorkloadClassifierEngine {
    if (!WorkloadClassifierEngine.instance) {
      WorkloadClassifierEngine.instance = new WorkloadClassifierEngine();
    }
    return WorkloadClassifierEngine.instance;
  }

  /**
   * Classify a workload BEFORE execution
   * Returns classification with optimal handling strategy
   */
  classify(
    workloadId: string,
    workloadType: string,
    input: unknown,
    constraints: {
      maxLatencyMs?: number;
      requireExact?: boolean;
      allowDownscale?: boolean;
      userPriority?: "speed" | "quality" | "cost";
    } = {},
  ): WorkloadClassification {
    const categories = this.detectCategories(workloadType, input, constraints);
    const primaryCategory = categories[0] || "throughput_critical";
    const gpuRequired = this.isGpuRequired(workloadType, categories);
    const avoidanceStrategies = this.determineAvoidanceStrategies(categories, constraints);
    const canAvoid = avoidanceStrategies.length > 0 && avoidanceStrategies[0] !== "none";

    const classification: WorkloadClassification = {
      id: workloadId,
      categories,
      primaryCategory,
      gpuRequired,
      canAvoid,
      avoidanceStrategies,
      qualityFloor: this.determineQualityFloor(categories, constraints),
      latencyBudgetMs: constraints.maxLatencyMs || this.defaultLatencyBudget(primaryCategory),
      downscaleable:
        constraints.allowDownscale !== false && !categories.includes("precision_critical"),
      delegatable:
        !categories.includes("latency_critical") || (constraints.maxLatencyMs || 0) > 5000,
      confidence: 0.9, // Fixed confidence - no random values
      classifiedAt: new Date(),
    };

    this.classifications.set(workloadId, classification);
    this.updateStats(classification);

    return classification;
  }

  /**
   * Get classification for a workload
   */
  getClassification(workloadId: string): WorkloadClassification | null {
    return this.classifications.get(workloadId) || null;
  }

  /**
   * Check if workload was classified (required before execution)
   */
  isClassified(workloadId: string): boolean {
    return this.classifications.has(workloadId);
  }

  /**
   * Get current classification statistics
   */
  getStats(): ClassificationStats {
    return { ...this.stats };
  }

  private detectCategories(
    workloadType: string,
    input: unknown,
    constraints: { requireExact?: boolean; userPriority?: string },
  ): WorkloadCategory[] {
    const categories: WorkloadCategory[] = [];
    const type = workloadType.toLowerCase();
    const inputStr = JSON.stringify(input);

    // Precision-critical workloads
    if (
      constraints.requireExact ||
      type.includes("financial") ||
      type.includes("medical") ||
      type.includes("scientific") ||
      type.includes("crypto")
    ) {
      categories.push("precision_critical");
    }

    // Perceptual-tolerant workloads
    if (
      type.includes("image") ||
      type.includes("video") ||
      type.includes("audio") ||
      type.includes("render") ||
      type.includes("preview")
    ) {
      categories.push("perceptual_tolerant");
    }

    // Latency-critical workloads
    if (
      type.includes("realtime") ||
      type.includes("interactive") ||
      type.includes("chat") ||
      constraints.userPriority === "speed"
    ) {
      categories.push("latency_critical");
    }

    // Throughput-critical workloads
    if (
      type.includes("batch") ||
      type.includes("bulk") ||
      type.includes("training") ||
      inputStr.length > 10000
    ) {
      categories.push("throughput_critical");
    }

    // Cacheable workloads
    if (!type.includes("unique") && !type.includes("random")) {
      categories.push("cacheable");
    }

    // Batchable workloads
    if (type.includes("inference") || type.includes("embed") || type.includes("transform")) {
      categories.push("batchable");
    }

    // Deferrable workloads
    if (!categories.includes("latency_critical") && constraints.userPriority !== "speed") {
      categories.push("deferrable");
    }

    // Reusable
    if (categories.includes("cacheable") && !categories.includes("precision_critical")) {
      categories.push("reusable");
    }

    return categories.length > 0 ? categories : ["throughput_critical"];
  }

  private isGpuRequired(workloadType: string, categories: WorkloadCategory[]): boolean {
    const gpuWorkloads = [
      "training",
      "inference",
      "render",
      "image_generation",
      "video_encode",
      "video_decode",
      "llm",
      "diffusion",
      "3d_render",
      "ray_trace",
      "neural",
    ];

    const type = workloadType.toLowerCase();

    // Precision-critical GPU workloads always need real GPU
    if (categories.includes("precision_critical")) {
      return gpuWorkloads.some((w) => type.includes(w));
    }

    // Perceptual-tolerant can often avoid GPU
    if (categories.includes("perceptual_tolerant") && categories.includes("cacheable")) {
      return false; // Can use cached/approximated results
    }

    return gpuWorkloads.some((w) => type.includes(w));
  }

  private determineAvoidanceStrategies(
    categories: WorkloadCategory[],
    constraints: { requireExact?: boolean },
  ): AvoidanceStrategy[] {
    const strategies: AvoidanceStrategy[] = [];

    if (constraints.requireExact) {
      return ["none"];
    }

    if (categories.includes("cacheable")) {
      strategies.push("cache_hit");
    }

    if (categories.includes("reusable")) {
      strategies.push("similarity_collapse");
    }

    if (categories.includes("perceptual_tolerant")) {
      strategies.push("progressive_render");
      strategies.push("perception_equivalent");
      strategies.push("early_exit");
    }

    if (categories.includes("batchable")) {
      strategies.push("temporal_batch");
    }

    if (categories.includes("deferrable")) {
      strategies.push("defer");
    }

    if (!categories.includes("precision_critical")) {
      strategies.push("downscale");
    }

    return strategies.length > 0 ? strategies : ["none"];
  }

  private determineQualityFloor(
    categories: WorkloadCategory[],
    constraints: { userPriority?: string },
  ): number {
    if (categories.includes("precision_critical")) return 0.99;
    if (constraints.userPriority === "quality") return 0.95;
    if (categories.includes("perceptual_tolerant")) return 0.75;
    if (categories.includes("latency_critical")) return 0.85;
    return 0.9;
  }

  private defaultLatencyBudget(category: WorkloadCategory): number {
    const budgets: Record<WorkloadCategory, number> = {
      latency_critical: 500,
      perceptual_tolerant: 5000,
      precision_critical: 30000,
      throughput_critical: 60000,
      cacheable: 10000,
      reusable: 10000,
      batchable: 120000,
      deferrable: 300000,
    };
    return budgets[category];
  }

  private updateStats(classification: WorkloadClassification): void {
    this.stats.totalClassified++;

    classification.categories.forEach((cat) => {
      this.stats.byCategory[cat]++;
    });

    if (classification.gpuRequired) {
      this.stats.gpuRequiredCount++;
    }

    if (classification.canAvoid) {
      this.stats.gpuAvoidedCount++;
    }

    this.stats.avoidanceRate = this.stats.gpuAvoidedCount / this.stats.totalClassified;
  }

  /**
   * Clear old classifications
   */
  cleanup(maxAgeMs: number = 3600000): void {
    const cutoff = Date.now() - maxAgeMs;
    for (const [id, classification] of this.classifications) {
      if (classification.classifiedAt.getTime() < cutoff) {
        this.classifications.delete(id);
      }
    }
  }
}

export const workloadClassifier = WorkloadClassifierEngine.getInstance();
