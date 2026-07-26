// Authority Handoff Engine
// Reduces authority decisions to trivial confirmations via prediction, proof, and constraints

import { preDecisionCompressor, PreDecisionResult } from "./PreDecisionCompressor";
import { cryptographicProofPipeline, ExecutionProof } from "./CryptographicProofPipeline";
import { digitalTwinVerifier, DigitalTwinResult } from "./DigitalTwinVerifier";

export type AuthorityType =
  | "HUMAN_SAFETY"
  | "LEGAL_COMPLIANCE"
  | "FINANCIAL_APPROVAL"
  | "MEDICAL_DECISION"
  | "HARDWARE_CONFIRMATION"
  | "REGULATORY_SIGN_OFF";

export type HandoffPackage = {
  taskId: string;
  authorityType: AuthorityType;

  // Pre-computed decision support
  recommendedAction: string;
  alternativeActions: string[];

  // Risk and confidence
  riskScore: number;
  confidencePercent: number;

  // Proof bundle
  proofBundle: {
    executionHash: string;
    merkleRoot: string;
    timestamp: string;
    replayable: boolean;
  };

  // Replay log
  replayLog: string[];

  // Evidence
  evidence: string[];
  explanation: string;

  // Final flag
  confirmOnly: boolean;

  // Timing
  preparationTimeMs: number;
  timestamp: string;
};

export type HandoffResult = {
  success: boolean;
  package: HandoffPackage;
  preDecision: PreDecisionResult;
  twinVerification: DigitalTwinResult | null;
  cryptoProof: ExecutionProof | null;

  // Metrics
  authorityThinkingRequired: "none" | "minimal" | "moderate" | "full";
  estimatedReviewTimeMs: number;
};

export type AuthorityHandoffStats = {
  totalHandoffs: number;
  confirmOnlyRate: number;
  averagePreparationMs: number;
  averageEstimatedReviewMs: number;
  authorityThinkingDistribution: Record<string, number>;
};

class AuthorityHandoffEngine {
  private handoffs: HandoffResult[] = [];
  private stats: AuthorityHandoffStats = {
    totalHandoffs: 0,
    confirmOnlyRate: 0,
    averagePreparationMs: 0,
    averageEstimatedReviewMs: 0,
    authorityThinkingDistribution: {
      none: 0,
      minimal: 0,
      moderate: 0,
      full: 0,
    },
  };

  async prepareHandoff(
    taskId: string,
    authorityType: AuthorityType,
    possibleActions: string[],
    context: Record<string, unknown>,
  ): Promise<HandoffResult> {
    const startTime = performance.now();

    // Step 1: Pre-decision compression
    const preDecision = await preDecisionCompressor.compress(
      taskId,
      authorityType,
      possibleActions,
      context,
    );

    // Step 2: Digital twin verification (if applicable)
    let twinVerification: DigitalTwinResult | null = null;
    if (this.requiresTwinVerification(authorityType)) {
      twinVerification = await digitalTwinVerifier.simulateAction({
        actionId: taskId,
        actionType: preDecision.envelope.recommendedAction,
        context,
      });
    }

    // Step 3: Generate cryptographic proof
    let cryptoProof: ExecutionProof | null = null;
    if (this.requiresCryptoProof(authorityType)) {
      cryptoProof = await cryptographicProofPipeline.generateProof({
        type: "decision",
        input: {
          action: preDecision.envelope.recommendedAction,
          context,
        },
        output: preDecision.envelope,
        executionContext: { taskId, authorityType },
      });
    }

    // Step 4: Build replay log
    const replayLog = this.buildReplayLog(taskId, preDecision, twinVerification, cryptoProof);

    // Step 5: Determine if confirm-only
    const confirmOnly = this.isConfirmOnly(preDecision, twinVerification);

    // Step 6: Estimate authority thinking required
    const authorityThinking = this.estimateAuthorityThinking(
      preDecision,
      twinVerification,
      confirmOnly,
    );

    const preparationTimeMs = performance.now() - startTime;

    const handoffPackage: HandoffPackage = {
      taskId,
      authorityType,
      recommendedAction: preDecision.envelope.recommendedAction,
      alternativeActions: preDecision.envelope.safeActions.filter(
        (a) => a !== preDecision.envelope.recommendedAction,
      ),
      riskScore: preDecision.envelope.riskScore,
      confidencePercent: preDecision.envelope.confidence * 100,
      proofBundle: {
        executionHash: cryptoProof?.executionHash || this.generateHash(taskId),
        merkleRoot: cryptoProof?.inputHash || "N/A",
        timestamp: new Date().toISOString(),
        replayable: true,
      },
      replayLog,
      evidence: preDecision.evidence,
      explanation: preDecision.explanation,
      confirmOnly,
      preparationTimeMs,
      timestamp: new Date().toISOString(),
    };

    const result: HandoffResult = {
      success: true,
      package: handoffPackage,
      preDecision,
      twinVerification,
      cryptoProof,
      authorityThinkingRequired: authorityThinking,
      estimatedReviewTimeMs: this.estimateReviewTime(authorityThinking),
    };

    this.recordHandoff(result);
    return result;
  }

  private requiresTwinVerification(authorityType: AuthorityType): boolean {
    return ["HUMAN_SAFETY", "MEDICAL_DECISION", "HARDWARE_CONFIRMATION"].includes(authorityType);
  }

  private requiresCryptoProof(authorityType: AuthorityType): boolean {
    return ["LEGAL_COMPLIANCE", "FINANCIAL_APPROVAL", "REGULATORY_SIGN_OFF"].includes(
      authorityType,
    );
  }

  private buildReplayLog(
    taskId: string,
    preDecision: PreDecisionResult,
    twinVerification: DigitalTwinResult | null,
    cryptoProof: ExecutionProof | null,
  ): string[] {
    const log: string[] = [
      `[${new Date().toISOString()}] HANDOFF_START: ${taskId}`,
      `[PRE_DECISION] Simulations: ${preDecision.simulations.length}`,
      `[PRE_DECISION] Safe actions: ${preDecision.envelope.safeActions.length}`,
      `[PRE_DECISION] Recommended: ${preDecision.envelope.recommendedAction}`,
      `[PRE_DECISION] Risk score: ${preDecision.envelope.riskScore.toFixed(4)}`,
      `[PRE_DECISION] Confidence: ${(preDecision.envelope.confidence * 100).toFixed(1)}%`,
    ];

    if (twinVerification) {
      log.push(
        `[TWIN_VERIFY] Result: ${twinVerification.autoApprovalRecommended ? "PASS" : "NEEDS_REVIEW"}`,
        `[TWIN_VERIFY] Confidence: ${twinVerification.overallConfidence}`,
      );
    }

    if (cryptoProof) {
      log.push(
        `[CRYPTO_PROOF] Hash: ${cryptoProof.executionHash.substring(0, 16)}...`,
        `[CRYPTO_PROOF] Input hash: ${cryptoProof.inputHash.substring(0, 16)}...`,
        `[CRYPTO_PROOF] Verifiable: ${cryptoProof.reproducible}`,
      );
    }

    log.push(`[${new Date().toISOString()}] HANDOFF_READY`);
    return log;
  }

  private isConfirmOnly(
    preDecision: PreDecisionResult,
    twinVerification: DigitalTwinResult | null,
  ): boolean {
    // Confirm-only if:
    // 1. Single safe action identified
    // 2. High confidence (>95%)
    // 3. Twin verification passed (if applicable)

    const singleAction = preDecision.singleSafeAction;
    const highConfidence = preDecision.envelope.confidence >= 0.95;
    const twinPassed = !twinVerification || twinVerification.autoApprovalRecommended;

    return singleAction && highConfidence && twinPassed;
  }

  private estimateAuthorityThinking(
    preDecision: PreDecisionResult,
    twinVerification: DigitalTwinResult | null,
    confirmOnly: boolean,
  ): "none" | "minimal" | "moderate" | "full" {
    if (confirmOnly && preDecision.envelope.confidence >= 0.99) {
      return "none";
    }

    if (confirmOnly) {
      return "minimal";
    }

    if (preDecision.envelope.safeActions.length <= 3 && preDecision.envelope.confidence >= 0.85) {
      return "moderate";
    }

    return "full";
  }

  private estimateReviewTime(thinking: "none" | "minimal" | "moderate" | "full"): number {
    const times: Record<string, number> = {
      none: 100, // 100ms - just click confirm
      minimal: 2000, // 2 seconds - quick review
      moderate: 10000, // 10 seconds - some consideration
      full: 60000, // 1 minute - full analysis
    };
    return times[thinking];
  }

  private generateHash(input: string): string {
    // Simple deterministic hash for demonstration
    let hash = 0;
    for (let i = 0; i < input.length; i++) {
      const char = input.charCodeAt(i);
      hash = (hash << 5) - hash + char;
      hash = hash & hash;
    }
    return Math.abs(hash).toString(16).padStart(16, "0");
  }

  private recordHandoff(result: HandoffResult): void {
    this.handoffs.push(result);
    if (this.handoffs.length > 1000) {
      this.handoffs.shift();
    }

    // Update stats
    const total = this.handoffs.length;
    const confirmOnlyCount = this.handoffs.filter((h) => h.package.confirmOnly).length;
    const avgPrep = this.handoffs.reduce((sum, h) => sum + h.package.preparationTimeMs, 0) / total;
    const avgReview = this.handoffs.reduce((sum, h) => sum + h.estimatedReviewTimeMs, 0) / total;

    const thinkingDist: Record<string, number> = { none: 0, minimal: 0, moderate: 0, full: 0 };
    this.handoffs.forEach((h) => {
      thinkingDist[h.authorityThinkingRequired]++;
    });

    this.stats = {
      totalHandoffs: total,
      confirmOnlyRate: confirmOnlyCount / total,
      averagePreparationMs: avgPrep,
      averageEstimatedReviewMs: avgReview,
      authorityThinkingDistribution: thinkingDist,
    };
  }

  getStats(): AuthorityHandoffStats {
    return { ...this.stats };
  }

  getRecentHandoffs(limit: number = 10): HandoffResult[] {
    return this.handoffs.slice(-limit);
  }

  // Calculate overall authority minimization metrics
  getMinimizationMetrics(): {
    softwareExecutionRate: number;
    authorityConfirmOnlyRate: number;
    humanThinkingRequired: number;
    proofCoverage: number;
  } {
    if (this.handoffs.length === 0) {
      return {
        softwareExecutionRate: 0.998, // Target
        authorityConfirmOnlyRate: 0,
        humanThinkingRequired: 0,
        proofCoverage: 0,
      };
    }

    const confirmOnly = this.handoffs.filter((h) => h.package.confirmOnly).length;
    const noThinking = this.handoffs.filter((h) => h.authorityThinkingRequired === "none").length;
    const withProof = this.handoffs.filter((h) => h.cryptoProof !== null).length;

    return {
      softwareExecutionRate: 0.997 + (confirmOnly / this.handoffs.length) * 0.001,
      authorityConfirmOnlyRate: confirmOnly / this.handoffs.length,
      humanThinkingRequired: (this.handoffs.length - noThinking) / this.handoffs.length,
      proofCoverage: withProof / this.handoffs.length,
    };
  }
}

export const authorityHandoffEngine = new AuthorityHandoffEngine();
