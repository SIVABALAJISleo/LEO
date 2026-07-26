/**
 * ═══════════════════════════════════════════════════════════════
 *  OUTCOME FEEDBACK LOOP — Policy #3: No Ground Truth Learning
 * ═══════════════════════════════════════════════════════════════
 *  Every decision must later receive outcome feedback.
 *  Update reliability score per memory and per domain.
 * ═══════════════════════════════════════════════════════════════
 */

// eslint-disable-next-line @typescript-eslint/no-unused-vars
import { v4 as uuidv4 } from "uuid";
import {
  OutcomeFeedback,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  TerminalAction,
} from "./types";
import { DomainRegistry } from "./DomainRegistry";

interface PendingOutcome {
  outputId: string;
  domain: string;
  memoryId: string | null;
  createdAt: number;
  deadline: number;
  resolved: boolean;
}

export class OutcomeFeedbackLoop {
  private static instance: OutcomeFeedbackLoop;
  private domainRegistry: DomainRegistry;
  private pendingOutcomes = new Map<string, PendingOutcome>();
  private feedbackHistory: OutcomeFeedback[] = [];
  private readonly FEEDBACK_DEADLINE_MS = 3600000; // 1 hour
  private readonly MAX_HISTORY = 2000;

  private constructor() {
    this.domainRegistry = DomainRegistry.getInstance();
    this.startExpirationMonitor();
  }

  static getInstance(): OutcomeFeedbackLoop {
    if (!OutcomeFeedbackLoop.instance) {
      OutcomeFeedbackLoop.instance = new OutcomeFeedbackLoop();
    }
    return OutcomeFeedbackLoop.instance;
  }

  /**
   * Register an output that needs future feedback.
   * Every non-refused output must call this.
   */
  registerPending(outputId: string, domain: string, memoryId: string | null): void {
    this.pendingOutcomes.set(outputId, {
      outputId,
      domain,
      memoryId,
      createdAt: Date.now(),
      deadline: Date.now() + this.FEEDBACK_DEADLINE_MS,
      resolved: false,
    });
  }

  /**
   * Submit feedback for a previous output.
   * Updates domain reliability based on weighted reviewer trust.
   */
  submitFeedback(feedback: OutcomeFeedback): {
    accepted: boolean;
    reliabilityDelta: number;
  } {
    const pending = this.pendingOutcomes.get(feedback.outputId);

    // Accept feedback even for non-pending outputs (late feedback is still valuable)
    if (pending) {
      pending.resolved = true;
    }

    // Weight the feedback by reviewer trust
    const weight = Math.max(0.1, Math.min(1.0, feedback.reviewerTrust));

    // Update domain reliability
    if (feedback.correct) {
      this.domainRegistry.recordSuccess(feedback.domain);
    } else {
      // Weighted failure — untrusted reviewers have less impact
      if (weight > 0.5) {
        this.domainRegistry.recordFailure(feedback.domain);
      }
      // Low-trust negative feedback → reduced impact, treated as partial
    }

    // Calculate reliability delta
    const reliabilityDelta = feedback.correct ? weight * 0.01 : -(weight * 0.02);

    // Store feedback
    this.feedbackHistory.push(feedback);
    if (this.feedbackHistory.length > this.MAX_HISTORY) {
      this.feedbackHistory = this.feedbackHistory.slice(-Math.floor(this.MAX_HISTORY * 0.8));
    }

    return { accepted: true, reliabilityDelta };
  }

  /**
   * Get all pending (unresolved) outcomes.
   */
  getPendingOutcomes(): PendingOutcome[] {
    return Array.from(this.pendingOutcomes.values()).filter((p) => !p.resolved);
  }

  /**
   * Get feedback statistics for a domain.
   */
  getDomainFeedbackStats(domain: string): {
    total: number;
    correct: number;
    incorrect: number;
    avgReviewerTrust: number;
    pendingCount: number;
  } {
    const domainFeedback = this.feedbackHistory.filter((f) => f.domain === domain);
    const correct = domainFeedback.filter((f) => f.correct).length;
    const avgTrust =
      domainFeedback.length > 0
        ? domainFeedback.reduce((s, f) => s + f.reviewerTrust, 0) / domainFeedback.length
        : 0;

    const pending = Array.from(this.pendingOutcomes.values()).filter(
      (p) => p.domain === domain && !p.resolved,
    ).length;

    return {
      total: domainFeedback.length,
      correct,
      incorrect: domainFeedback.length - correct,
      avgReviewerTrust: avgTrust,
      pendingCount: pending,
    };
  }

  // ──────────────────── Private Helpers ────────────────────

  private startExpirationMonitor(): void {
    // Check for expired outcomes every 5 minutes
    setInterval(() => {
      const now = Date.now();
      this.pendingOutcomes.forEach((pending, id) => {
        if (!pending.resolved && now > pending.deadline) {
          // Expired without feedback — log but don't punish
          console.warn(
            `[OutcomeFeedback] Output ${id} expired without feedback (domain: ${pending.domain})`,
          );
          pending.resolved = true; // Mark as resolved to stop checking
        }
      });

      // Clean up old resolved entries
      const cutoff = now - this.FEEDBACK_DEADLINE_MS * 2;
      this.pendingOutcomes.forEach((pending, id) => {
        if (pending.resolved && pending.createdAt < cutoff) {
          this.pendingOutcomes.delete(id);
        }
      });
    }, 300000);
  }
}
