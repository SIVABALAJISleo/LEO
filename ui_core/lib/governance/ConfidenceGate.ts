/**
 * ═══════════════════════════════════════════════════════════════
 *  CONFIDENCE GATE — Policy #1: Confidence Risk
 * ═══════════════════════════════════════════════════════════════
 *  If output confidence < threshold → ABSTAIN.
 *  Never guess. Never auto-complete uncertain outputs.
 * ═══════════════════════════════════════════════════════════════
 */

import { TerminalAction } from "./types";

export interface ConfidenceResult {
  readonly passed: boolean;
  readonly confidence: number;
  readonly threshold: number;
  readonly action: TerminalAction | null;
  readonly reason: string;
}

export class ConfidenceGate {
  private static instance: ConfidenceGate;

  // Absolute minimum — even trusted domains cannot go below this
  private readonly ABSOLUTE_FLOOR = 0.3;

  private constructor() {}

  static getInstance(): ConfidenceGate {
    if (!ConfidenceGate.instance) {
      ConfidenceGate.instance = new ConfidenceGate();
    }
    return ConfidenceGate.instance;
  }

  /**
   * Evaluate whether a confidence score passes the gate.
   * @param confidence - Output confidence (0.0–1.0)
   * @param threshold - Domain-specific threshold (from DomainRegistry)
   * @param driftActive - Whether drift is currently detected (tightens gate)
   */
  evaluate(confidence: number, threshold: number, driftActive: boolean = false): ConfidenceResult {
    // Apply drift penalty
    const effectiveThreshold = driftActive ? Math.min(1.0, threshold * 1.3) : threshold;

    // Absolute floor check
    if (confidence < this.ABSOLUTE_FLOOR) {
      return {
        passed: false,
        confidence,
        threshold: effectiveThreshold,
        action: TerminalAction.REFUSE,
        reason: `Confidence ${confidence.toFixed(3)} below absolute floor ${this.ABSOLUTE_FLOOR}`,
      };
    }

    // Threshold check
    if (confidence < effectiveThreshold) {
      // Between floor and threshold → escalate rather than refuse
      return {
        passed: false,
        confidence,
        threshold: effectiveThreshold,
        action: TerminalAction.ESCALATE,
        reason: `Confidence ${confidence.toFixed(3)} below effective threshold ${effectiveThreshold.toFixed(3)}`,
      };
    }

    // Marginal confidence → output with VERIFY flag
    if (confidence < effectiveThreshold + 0.1) {
      return {
        passed: true,
        confidence,
        threshold: effectiveThreshold,
        action: TerminalAction.VERIFY,
        reason: `Marginal confidence ${confidence.toFixed(3)} — output requires verification`,
      };
    }

    // Solid confidence → proceed
    return {
      passed: true,
      confidence,
      threshold: effectiveThreshold,
      action: null,
      reason: "Confidence acceptable",
    };
  }

  /**
   * Estimate confidence from novelty similarity and domain reliability.
   * Used when no explicit model confidence is available.
   */
  estimateConfidence(
    noveltySimilarity: number,
    domainReliability: number,
    isDecomposed: boolean = false,
  ): number {
    // Base confidence from novelty (higher similarity = higher confidence)
    let confidence = noveltySimilarity * 0.6 + domainReliability * 0.4;

    // Decomposed reasoning gets a small bonus (verified steps)
    if (isDecomposed) {
      confidence = Math.min(1.0, confidence * 1.1);
    }

    return Math.max(0, Math.min(1.0, confidence));
  }
}
