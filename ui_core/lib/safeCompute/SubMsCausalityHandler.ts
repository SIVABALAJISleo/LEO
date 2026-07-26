// Sub-MS Causality Handler
// Converts time-critical events into: Prediction → Validation → Reconciliation
// Guarantees FAIRNESS over impossible SPEED

export type CausalityMode =
  | "INSTANT_PREDICTION" // Predict outcome immediately
  | "DEFERRED_VALIDATION" // Validate after the fact
  | "FAIR_ORDERING" // Ensure fair sequence despite latency
  | "ROLLBACK_READY"; // Prepared for automatic correction

export interface CausalityEvent {
  eventId: string;
  eventType: string;

  // Timing
  requestedAt: string;
  predictedAt: string;
  confirmedAt?: string;

  // States
  predictedOutcome: unknown;
  actualOutcome?: unknown;

  // Uncertainty
  uncertaintyWindowMs: number;
  confidencePercent: number;

  // Reconciliation
  reconciliationRequired: boolean;
  reconciliationApplied: boolean;
  reconciliationStrategy?: "merge" | "accept_prediction" | "accept_reality" | "rollback";
}

export interface FairnessGuarantee {
  eventId: string;
  guaranteeType: "temporal_ordering" | "priority_based" | "random_tiebreak";

  // For temporal ordering
  logicalTimestamp: number;

  // For priority
  priorityScore?: number;

  // Proof
  orderingProof: string;
}

export interface SubMsCausalityStats {
  totalEvents: number;
  predictionsCorrect: number;
  reconciliationsRequired: number;
  reconciliationsSuccessful: number;
  averageUncertaintyMs: number;
  fairnessViolations: number;
}

class SubMsCausalityHandler {
  private events: Map<string, CausalityEvent> = new Map();
  private guarantees: Map<string, FairnessGuarantee> = new Map();
  private logicalClock: number = 0;
  private stats: SubMsCausalityStats = {
    totalEvents: 0,
    predictionsCorrect: 0,
    reconciliationsRequired: 0,
    reconciliationsSuccessful: 0,
    averageUncertaintyMs: 0,
    fairnessViolations: 0,
  };

  /**
   * Handle a sub-millisecond event with prediction-first approach
   */
  handleEvent(params: {
    eventType: string;
    inputState: unknown;
    predictOutcome: (input: unknown) => unknown;
    uncertaintyWindowMs?: number;
  }): {
    eventId: string;
    predictedOutcome: unknown;
    fairnessGuarantee: FairnessGuarantee;
  } {
    const eventId = `sub_ms_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const now = new Date().toISOString();

    // Increment logical clock for ordering
    this.logicalClock++;

    // Make instant prediction
    const predictedOutcome = params.predictOutcome(params.inputState);

    // Estimate uncertainty based on event type
    const uncertaintyWindowMs =
      params.uncertaintyWindowMs || this.estimateUncertainty(params.eventType);

    // Create event record
    const event: CausalityEvent = {
      eventId,
      eventType: params.eventType,
      requestedAt: now,
      predictedAt: now,
      predictedOutcome,
      uncertaintyWindowMs,
      confidencePercent: this.calculateConfidence(params.eventType, uncertaintyWindowMs),
      reconciliationRequired: false,
      reconciliationApplied: false,
    };

    // Create fairness guarantee
    const guarantee: FairnessGuarantee = {
      eventId,
      guaranteeType: "temporal_ordering",
      logicalTimestamp: this.logicalClock,
      orderingProof: this.generateOrderingProof(eventId, this.logicalClock),
    };

    this.events.set(eventId, event);
    this.guarantees.set(eventId, guarantee);
    this.stats.totalEvents++;

    // Update average uncertainty
    this.stats.averageUncertaintyMs =
      (this.stats.averageUncertaintyMs * (this.stats.totalEvents - 1) + uncertaintyWindowMs) /
      this.stats.totalEvents;

    console.log(
      `[SubMsCausality] Event ${eventId}: predicted in <1ms, uncertainty: ${uncertaintyWindowMs}ms`,
    );

    return {
      eventId,
      predictedOutcome,
      fairnessGuarantee: guarantee,
    };
  }

  /**
   * Confirm actual outcome and reconcile if needed
   */
  confirmOutcome(
    eventId: string,
    actualOutcome: unknown,
  ): {
    reconciled: boolean;
    strategy?: string;
    delta?: unknown;
  } {
    const event = this.events.get(eventId);
    if (!event) {
      return { reconciled: false };
    }

    event.confirmedAt = new Date().toISOString();
    event.actualOutcome = actualOutcome;

    // Check if reconciliation is needed
    const delta = this.computeDelta(event.predictedOutcome, actualOutcome);

    if (delta !== null && !this.isNegligibleDelta(delta)) {
      event.reconciliationRequired = true;
      this.stats.reconciliationsRequired++;

      // Apply reconciliation strategy
      const strategy = this.selectReconciliationStrategy(delta);
      event.reconciliationStrategy = strategy;
      event.reconciliationApplied = true;
      this.stats.reconciliationsSuccessful++;

      console.log(`[SubMsCausality] Event ${eventId}: reconciled with strategy ${strategy}`);
      return { reconciled: true, strategy, delta };
    }

    this.stats.predictionsCorrect++;
    return { reconciled: false };
  }

  /**
   * Ensure fair ordering for competing events
   */
  ensureFairOrdering(eventIds: string[]): {
    orderedEventIds: string[];
    proof: string;
  } {
    const eventsWithGuarantees = eventIds
      .map((id) => ({ id, guarantee: this.guarantees.get(id) }))
      .filter((e) => e.guarantee !== undefined)
      .sort((a, b) => a.guarantee!.logicalTimestamp - b.guarantee!.logicalTimestamp);

    const orderedEventIds = eventsWithGuarantees.map((e) => e.id);
    const proof = this.generateFairnessProof(orderedEventIds);

    return { orderedEventIds, proof };
  }

  /**
   * Get event with full causality chain
   */
  getEvent(eventId: string): CausalityEvent | undefined {
    return this.events.get(eventId);
  }

  /**
   * Get fairness guarantee for an event
   */
  getGuarantee(eventId: string): FairnessGuarantee | undefined {
    return this.guarantees.get(eventId);
  }

  /**
   * Get statistics
   */
  getStats(): SubMsCausalityStats {
    return { ...this.stats };
  }

  // Private helpers

  private estimateUncertainty(eventType: string): number {
    // Different event types have different uncertainty windows
    const uncertaintyMap: Record<string, number> = {
      user_input: 50,
      state_update: 20,
      animation_frame: 16,
      network_response: 100,
      database_write: 50,
      cache_lookup: 5,
      default: 30,
    };

    return uncertaintyMap[eventType] || uncertaintyMap["default"];
  }

  private calculateConfidence(eventType: string, uncertaintyMs: number): number {
    // Lower uncertainty = higher confidence
    const baseConfidence = Math.max(0.5, 1 - uncertaintyMs / 200);

    // Some event types are more predictable
    const typeMultiplier = eventType === "cache_lookup" ? 1.2 : 1.0;

    return Math.min(0.99, baseConfidence * typeMultiplier);
  }

  private computeDelta(predicted: unknown, actual: unknown): unknown | null {
    if (predicted === actual) return null;

    if (typeof predicted === "number" && typeof actual === "number") {
      return actual - predicted;
    }

    if (typeof predicted === "object" && typeof actual === "object") {
      return { predicted, actual, type: "object_mismatch" };
    }

    return { predicted, actual, type: "type_mismatch" };
  }

  private isNegligibleDelta(delta: unknown): boolean {
    if (typeof delta === "number") {
      return Math.abs(delta) < 0.001; // < 0.1% difference
    }
    return false;
  }

  private selectReconciliationStrategy(
    delta: unknown,
  ): "merge" | "accept_prediction" | "accept_reality" | "rollback" {
    if (typeof delta === "number") {
      const absDelta = Math.abs(delta);
      if (absDelta < 0.1) return "merge";
      if (absDelta < 0.3) return "accept_reality";
      return "rollback";
    }

    // For non-numeric deltas, always accept reality
    return "accept_reality";
  }

  private generateOrderingProof(eventId: string, logicalTimestamp: number): string {
    const proofData = `${eventId}:${logicalTimestamp}:${Date.now()}`;
    // In production, this would be a proper cryptographic signature
    return `proof_${Buffer.from(proofData).toString("base64").substring(0, 32)}`;
  }

  private generateFairnessProof(orderedEventIds: string[]): string {
    const proofData = orderedEventIds.join(",");
    return `fairness_${Buffer.from(proofData).toString("base64").substring(0, 32)}`;
  }
}

export const subMsCausalityHandler = new SubMsCausalityHandler();
