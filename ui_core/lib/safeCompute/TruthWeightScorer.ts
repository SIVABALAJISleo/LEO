// TRUTH-WEIGHT SCORER
// Deterministic criticality classification for all tasks
// Ensures honest path selection based on real impact assessment

export interface TaskMetadata {
  domain?: string;
  taskType: string;
  description?: string;

  // Safety factors
  affectsPhysicalWorld?: boolean;
  affectsHumanHealth?: boolean;
  affectsFinancialAssets?: boolean;
  affectsLegalStatus?: boolean;

  // Technical factors
  requiresSubMillisecondLatency?: boolean;
  requiresExactNumericalResult?: boolean;
  requiresCryptographicIntegrity?: boolean;

  // Context factors
  isNovelComputation?: boolean;
  hasPriorExamples?: boolean;
  toleratesApproximation?: boolean;
  userDefinedQualityThreshold?: number;
}

export interface TruthWeightResult {
  taskId: string;
  scores: {
    safetyImpact: number;
    legalFinality: number;
    userPerception: number;
    realtimeCausality: number;
    physicsNovelty: number;
  };
  compositeScore: number;
  criticality: "CRITICAL" | "NON_CRITICAL";
  reasoning: string[];
  allowedTechniques: AllowedTechnique[];
  forbiddenTechniques: ForbiddenTechnique[];
}

export type AllowedTechnique =
  | "knowledge_distillation"
  | "retrieval_augmented_inference"
  | "keyframe_delta_reconstruction"
  | "temporal_reuse"
  | "frame_interpolation"
  | "learned_prediction"
  | "caching_memoization";

export type ForbiddenTechnique =
  "claim_physical_exactness" | "hide_confidence_bounds" | "silent_correction" | "authority_bypass";

// Domain risk classifications
const HIGH_RISK_DOMAINS: Record<string, { weight: number; reason: string }> = {
  medical: { weight: 1.0, reason: "Affects human health and life" },
  nuclear: { weight: 1.0, reason: "Nuclear safety critical" },
  aviation: { weight: 1.0, reason: "Aviation safety critical" },
  financial_settlement: { weight: 0.9, reason: "Legally binding financial transaction" },
  legal_document: { weight: 0.9, reason: "Legally binding document" },
  autonomous_vehicle: { weight: 0.95, reason: "Real-time collision avoidance" },
  industrial_control: { weight: 0.85, reason: "Industrial process control" },
  pharmaceutical: { weight: 0.9, reason: "Drug safety and dosing" },
};

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const MEDIUM_RISK_DOMAINS: Record<string, { weight: number; reason: string }> = {
  e_commerce: { weight: 0.4, reason: "Financial transaction involved" },
  content_moderation: { weight: 0.5, reason: "Community safety impact" },
  identity_verification: { weight: 0.6, reason: "Identity security" },
  access_control: { weight: 0.55, reason: "Security access" },
};

class TruthWeightScorerCore {
  private static instance: TruthWeightScorerCore;
  private scoringHistory: Map<string, TruthWeightResult> = new Map();

  private constructor() {}

  static getInstance(): TruthWeightScorerCore {
    if (!TruthWeightScorerCore.instance) {
      TruthWeightScorerCore.instance = new TruthWeightScorerCore();
    }
    return TruthWeightScorerCore.instance;
  }

  /**
   * SCORE A TASK
   * Returns deterministic criticality classification with full reasoning
   */
  score(taskId: string, metadata: TaskMetadata): TruthWeightResult {
    const reasoning: string[] = [];

    // Calculate individual scores
    const safetyImpact = this.calculateSafetyImpact(metadata, reasoning);
    const legalFinality = this.calculateLegalFinality(metadata, reasoning);
    const userPerception = this.calculateUserPerception(metadata, reasoning);
    const realtimeCausality = this.calculateRealtimeCausality(metadata, reasoning);
    const physicsNovelty = this.calculatePhysicsNovelty(metadata, reasoning);

    // Weighted composite
    const compositeScore =
      safetyImpact * 0.35 +
      legalFinality * 0.25 +
      userPerception * 0.15 +
      realtimeCausality * 0.15 +
      physicsNovelty * 0.1;

    // Criticality determination
    const criticality = this.determineCriticality(
      { safetyImpact, legalFinality, physicsNovelty, compositeScore },
      reasoning,
    );

    // Determine allowed/forbidden techniques based on criticality
    const { allowedTechniques, forbiddenTechniques } = this.determineTechniques(
      criticality,
      metadata,
    );

    const result: TruthWeightResult = {
      taskId,
      scores: {
        safetyImpact,
        legalFinality,
        userPerception,
        realtimeCausality,
        physicsNovelty,
      },
      compositeScore,
      criticality,
      reasoning,
      allowedTechniques,
      forbiddenTechniques,
    };

    this.scoringHistory.set(taskId, result);
    return result;
  }

  private calculateSafetyImpact(metadata: TaskMetadata, reasoning: string[]): number {
    let score = 0;

    if (metadata.affectsPhysicalWorld) {
      score += 0.4;
      reasoning.push("Task affects physical world (+0.4 safety)");
    }

    if (metadata.affectsHumanHealth) {
      score += 0.5;
      reasoning.push("Task affects human health (+0.5 safety)");
    }

    // Domain-based safety
    if (metadata.domain) {
      const highRisk = HIGH_RISK_DOMAINS[metadata.domain];
      if (highRisk) {
        score = Math.max(score, highRisk.weight);
        reasoning.push(`Domain '${metadata.domain}': ${highRisk.reason}`);
      }
    }

    return Math.min(score, 1.0);
  }

  private calculateLegalFinality(metadata: TaskMetadata, reasoning: string[]): number {
    let score = 0;

    if (metadata.affectsLegalStatus) {
      score += 0.7;
      reasoning.push("Task has legal implications (+0.7 legal)");
    }

    if (metadata.affectsFinancialAssets) {
      score += 0.5;
      reasoning.push("Task affects financial assets (+0.5 legal)");
    }

    if (metadata.requiresCryptographicIntegrity) {
      score += 0.3;
      reasoning.push("Requires cryptographic integrity (+0.3 legal)");
    }

    return Math.min(score, 1.0);
  }

  private calculateUserPerception(metadata: TaskMetadata, reasoning: string[]): number {
    // User-defined quality threshold takes precedence
    if (metadata.userDefinedQualityThreshold !== undefined) {
      reasoning.push(`User quality threshold: ${metadata.userDefinedQualityThreshold}`);
      return metadata.userDefinedQualityThreshold;
    }

    // Default based on tolerance
    if (metadata.toleratesApproximation) {
      reasoning.push("Task tolerates approximation (0.3 perception)");
      return 0.3;
    }

    if (metadata.requiresExactNumericalResult) {
      reasoning.push("Requires exact numerical result (0.95 perception)");
      return 0.95;
    }

    return 0.5; // Default middle ground
  }

  private calculateRealtimeCausality(metadata: TaskMetadata, reasoning: string[]): number {
    if (metadata.requiresSubMillisecondLatency) {
      reasoning.push("Sub-millisecond latency required (1.0 realtime)");
      return 1.0;
    }

    if (metadata.affectsPhysicalWorld) {
      reasoning.push("Physical world causality (0.7 realtime)");
      return 0.7;
    }

    return 0.2;
  }

  private calculatePhysicsNovelty(metadata: TaskMetadata, reasoning: string[]): number {
    if (metadata.isNovelComputation && !metadata.hasPriorExamples) {
      reasoning.push("Novel computation with no prior examples (0.9 novelty)");
      return 0.9;
    }

    if (metadata.isNovelComputation) {
      reasoning.push("Novel computation with some prior examples (0.5 novelty)");
      return 0.5;
    }

    return 0.1;
  }

  private determineCriticality(
    scores: {
      safetyImpact: number;
      legalFinality: number;
      physicsNovelty: number;
      compositeScore: number;
    },
    reasoning: string[],
  ): "CRITICAL" | "NON_CRITICAL" {
    // Hard thresholds for criticality
    if (scores.safetyImpact >= 0.7) {
      reasoning.push("CRITICAL: High safety impact");
      return "CRITICAL";
    }

    if (scores.legalFinality >= 0.7) {
      reasoning.push("CRITICAL: High legal finality");
      return "CRITICAL";
    }

    if (scores.physicsNovelty >= 0.8) {
      reasoning.push("CRITICAL: High physics novelty");
      return "CRITICAL";
    }

    if (scores.compositeScore >= 0.6) {
      reasoning.push("CRITICAL: High composite score");
      return "CRITICAL";
    }

    reasoning.push("NON_CRITICAL: All thresholds within acceptable range");
    return "NON_CRITICAL";
  }

  private determineTechniques(
    criticality: "CRITICAL" | "NON_CRITICAL",
    metadata: TaskMetadata,
  ): { allowedTechniques: AllowedTechnique[]; forbiddenTechniques: ForbiddenTechnique[] } {
    // Always forbidden
    const forbiddenTechniques: ForbiddenTechnique[] = [
      "claim_physical_exactness",
      "hide_confidence_bounds",
      "silent_correction",
      "authority_bypass",
    ];

    if (criticality === "CRITICAL") {
      // Critical tasks: minimal techniques allowed
      return {
        allowedTechniques: metadata.hasPriorExamples ? ["caching_memoization"] : [],
        forbiddenTechniques,
      };
    }

    // Non-critical tasks: full technique palette
    const allowedTechniques: AllowedTechnique[] = [
      "knowledge_distillation",
      "retrieval_augmented_inference",
      "keyframe_delta_reconstruction",
      "temporal_reuse",
      "frame_interpolation",
      "learned_prediction",
      "caching_memoization",
    ];

    return { allowedTechniques, forbiddenTechniques };
  }

  getScore(taskId: string): TruthWeightResult | undefined {
    return this.scoringHistory.get(taskId);
  }

  getStats(): { totalScored: number; criticalCount: number; nonCriticalCount: number } {
    let criticalCount = 0;
    let nonCriticalCount = 0;

    this.scoringHistory.forEach((result) => {
      if (result.criticality === "CRITICAL") criticalCount++;
      else nonCriticalCount++;
    });

    return {
      totalScored: this.scoringHistory.size,
      criticalCount,
      nonCriticalCount,
    };
  }
}

export const truthWeightScorer = TruthWeightScorerCore.getInstance();
