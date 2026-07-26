/**
 * ═══════════════════════════════════════════════════════════════
 *  AUTHORITY CONTROLLER — Policy #7: Responsibility Boundary
 * ═══════════════════════════════════════════════════════════════
 *  The model never directly decides.
 *  The system decides when the model is allowed to decide.
 *
 *  Outputs have levels:
 *    ADVISORY   → needs human
 *    ASSISTED   → suggested
 *    AUTOMATED  → allowed only in trusted domain
 * ═══════════════════════════════════════════════════════════════
 */

import { AuthorityLevel, DomainStatus, TerminalAction } from "./types";

export interface AuthorityDecision {
  readonly level: AuthorityLevel;
  readonly allowed: boolean;
  readonly requiresHuman: boolean;
  readonly terminalAction: TerminalAction | null;
  readonly reason: string;
}

export class AuthorityController {
  private static instance: AuthorityController;

  // Minimum reliability for AUTOMATED authority
  private readonly AUTOMATED_RELIABILITY_FLOOR = 0.85;
  // Minimum reliability for ASSISTED authority
  private readonly ASSISTED_RELIABILITY_FLOOR = 0.6;

  private constructor() {}

  static getInstance(): AuthorityController {
    if (!AuthorityController.instance) {
      AuthorityController.instance = new AuthorityController();
    }
    return AuthorityController.instance;
  }

  /**
   * Determine the authority level for an output.
   * CORE RULE: The system decides when the model is allowed to decide.
   */
  evaluate(
    requestedLevel: AuthorityLevel,
    domainMaxAuthority: AuthorityLevel,
    domainStatus: DomainStatus,
    domainReliability: number,
    confidence: number,
    driftActive: boolean,
  ): AuthorityDecision {
    // Step 1: Cap at domain maximum
    let effectiveLevel = this.capAuthority(requestedLevel, domainMaxAuthority);

    // Step 2: Domain status restrictions
    if (domainStatus === DomainStatus.DISABLED) {
      return {
        level: AuthorityLevel.ADVISORY,
        allowed: false,
        requiresHuman: true,
        terminalAction: TerminalAction.REFUSE,
        reason: "Domain is disabled — all outputs refused",
      };
    }

    if (domainStatus === DomainStatus.PROBATION) {
      effectiveLevel = AuthorityLevel.ADVISORY;
    }

    if (domainStatus === DomainStatus.DEGRADED) {
      effectiveLevel = this.capAuthority(effectiveLevel, AuthorityLevel.ASSISTED);
    }

    // Step 3: Drift override — never automate during drift
    if (driftActive && effectiveLevel === AuthorityLevel.AUTOMATED) {
      effectiveLevel = AuthorityLevel.ASSISTED;
    }

    // Step 4: Reliability checks
    if (
      effectiveLevel === AuthorityLevel.AUTOMATED &&
      domainReliability < this.AUTOMATED_RELIABILITY_FLOOR
    ) {
      effectiveLevel = AuthorityLevel.ASSISTED;
    }

    if (
      effectiveLevel === AuthorityLevel.ASSISTED &&
      domainReliability < this.ASSISTED_RELIABILITY_FLOOR
    ) {
      effectiveLevel = AuthorityLevel.ADVISORY;
    }

    // Step 5: Low confidence forces ADVISORY
    if (confidence < 0.5) {
      effectiveLevel = AuthorityLevel.ADVISORY;
    }

    // Determine terminal action
    const requiresHuman = effectiveLevel === AuthorityLevel.ADVISORY;
    let terminalAction: TerminalAction | null = null;

    if (requiresHuman) {
      terminalAction = TerminalAction.ESCALATE;
    } else if (effectiveLevel === AuthorityLevel.ASSISTED) {
      terminalAction = TerminalAction.VERIFY;
    }

    return {
      level: effectiveLevel,
      allowed: true,
      requiresHuman,
      terminalAction,
      reason: this.buildReason(
        effectiveLevel,
        domainStatus,
        domainReliability,
        confidence,
        driftActive,
      ),
    };
  }

  // ──────────────────── Private Helpers ────────────────────

  private capAuthority(requested: AuthorityLevel, max: AuthorityLevel): AuthorityLevel {
    const hierarchy = [AuthorityLevel.ADVISORY, AuthorityLevel.ASSISTED, AuthorityLevel.AUTOMATED];
    const requestedIdx = hierarchy.indexOf(requested);
    const maxIdx = hierarchy.indexOf(max);
    return hierarchy[Math.min(requestedIdx, maxIdx)];
  }

  private buildReason(
    level: AuthorityLevel,
    status: DomainStatus,
    reliability: number,
    confidence: number,
    drift: boolean,
  ): string {
    const parts: string[] = [`Authority: ${level}`];
    if (status !== DomainStatus.ACTIVE) parts.push(`domain_status=${status}`);
    if (drift) parts.push("drift_active");
    parts.push(`reliability=${reliability.toFixed(2)}`);
    parts.push(`confidence=${confidence.toFixed(2)}`);
    return parts.join(" | ");
  }
}
