/**
 * ═══════════════════════════════════════════════════════════════════════
 *  GOVERNED PIPELINE — Master Orchestrator
 * ═══════════════════════════════════════════════════════════════════════
 *  GLOBAL PIPELINE (never bypassed):
 *
 *  Input → Domain Check → Novelty Gate → Reasoning Mode →
 *  Safety Check → Reliability Update → Authority Control → Memory Lifecycle
 *
 *  CORE RULE:
 *  The model never directly decides.
 *  The system decides when the model is allowed to decide.
 *
 *  SYSTEM GUARANTEE:
 *  Every possible failure path ends in:
 *    REFUSE | ESCALATE | VERIFY | LIMIT | LEARN
 * ═══════════════════════════════════════════════════════════════════════
 */

import { v4 as uuidv4 } from "uuid";

import {
  GovernedInput,
  GovernedOutput,
  PipelineContext,
  PipelineStage,
  DecisionMode,
  AuthorityLevel,
  TerminalAction,
  ExplainabilityTrace,
  DomainStatus,
  GovernedMemoryEntry,
} from "./types";

import { SchemaEnforcer } from "./SchemaEnforcer";
import { SemanticLogger } from "./SemanticLogger";
import { DomainRegistry } from "./DomainRegistry";
import { DriftMonitor } from "./DriftMonitor";
import { AdversarialShield } from "./AdversarialShield";
import { ConfidenceGate } from "./ConfidenceGate";
import { AuthorityController } from "./AuthorityController";
import { OutcomeFeedbackLoop } from "./OutcomeFeedbackLoop";
import { MemoryGovernor } from "./MemoryGovernor";
import { InherentLimitHandler } from "./InherentLimitHandler";
import { FailureTerminator } from "./FailureTerminator";

/**
 * Executor function type — the actual model/inference logic.
 * The pipeline controls WHEN and IF this is invoked.
 */
export type GovernedExecutor<T = unknown> = (
  input: string,
  context?: string,
  mode?: DecisionMode,
) => Promise<T>;

export class GovernedPipeline {
  private static instance: GovernedPipeline;

  // Sub-systems (all singletons — no external state)
  private readonly schema: SchemaEnforcer;
  private readonly logger: SemanticLogger;
  private readonly domains: DomainRegistry;
  private readonly drift: DriftMonitor;
  private readonly shield: AdversarialShield;
  private readonly confidence: ConfidenceGate;
  private readonly authority: AuthorityController;
  private readonly feedback: OutcomeFeedbackLoop;
  private readonly memory: MemoryGovernor;
  private readonly limits: InherentLimitHandler;
  private readonly terminator: FailureTerminator;

  private constructor() {
    this.schema = SchemaEnforcer.getInstance();
    this.logger = SemanticLogger.getInstance();
    this.domains = DomainRegistry.getInstance();
    this.drift = DriftMonitor.getInstance();
    this.shield = AdversarialShield.getInstance();
    this.confidence = ConfidenceGate.getInstance();
    this.authority = AuthorityController.getInstance();
    this.feedback = OutcomeFeedbackLoop.getInstance();
    this.memory = MemoryGovernor.getInstance();
    this.limits = InherentLimitHandler.getInstance();
    this.terminator = FailureTerminator.getInstance();
  }

  static getInstance(): GovernedPipeline {
    if (!GovernedPipeline.instance) {
      GovernedPipeline.instance = new GovernedPipeline();
    }
    return GovernedPipeline.instance;
  }

  /**
   * ═══════════════════════════════════════════════════════════
   *  EXECUTE — The one and only entry point.
   *  Every request flows through all 8 stages. No bypassing.
   * ═══════════════════════════════════════════════════════════
   */
  async execute<T = unknown>(
    input: GovernedInput,
    executor: GovernedExecutor<T>,
  ): Promise<GovernedOutput<T>> {
    const ctx = this.initContext(input);

    try {
      // ──── Stage 1: INPUT VALIDATION ────
      this.stageInput(ctx);
      if (ctx.terminated) return this.buildOutput<T>(ctx);

      // ──── Stage 2: DOMAIN CHECK ────
      this.stageDomainCheck(ctx);
      if (ctx.terminated) return this.buildOutput<T>(ctx);

      // ──── Stage 3: NOVELTY GATE ────
      this.stageNoveltyGate(ctx);
      if (ctx.terminated) return this.buildOutput<T>(ctx);

      // ──── Stage 4: REASONING MODE SELECTION ────
      this.stageReasoningMode(ctx);
      if (ctx.terminated) return this.buildOutput<T>(ctx);

      // ──── Stage 5: SAFETY CHECK ────
      this.stageSafetyCheck(ctx);
      if (ctx.terminated) return this.buildOutput<T>(ctx);

      // ──── EXECUTE THE MODEL (if allowed) ────
      await this.invokeExecutor(ctx, executor);
      if (ctx.terminated) return this.buildOutput<T>(ctx);

      // ──── Stage 6: RELIABILITY UPDATE ────
      this.stageReliabilityUpdate(ctx);

      // ──── Stage 7: AUTHORITY CONTROL ────
      this.stageAuthorityControl(ctx);
      if (ctx.terminated) return this.buildOutput<T>(ctx);

      // ──── Stage 8: MEMORY LIFECYCLE ────
      this.stageMemoryLifecycle(ctx);

      // ──── COMPLETE ────
      ctx.currentStage = PipelineStage.COMPLETE;
      ctx.stagesCompleted.push(PipelineStage.COMPLETE);

      // Ensure terminal action exists
      ctx.terminalAction = this.terminator.ensureTermination(ctx);
    } catch (error: unknown) {
      // SYSTEM GUARANTEE: No uncontrolled output
      const termination = this.terminator.terminate(error, ctx);
      ctx.terminated = true;
      ctx.terminalAction = termination.action;
      ctx.terminationReason = termination.reason;
      ctx.result = null;
    }

    return this.buildOutput<T>(ctx);
  }

  // ═══════════════════════════════════════════════════════════
  //  PIPELINE STAGES
  // ═══════════════════════════════════════════════════════════

  /**
   * Stage 1: INPUT — Schema validation and embedding generation.
   */
  private stageInput(ctx: PipelineContext): void {
    ctx.currentStage = PipelineStage.INPUT;

    // Policy #9: Validate input schema
    if (!this.schema.validateInput(ctx.input)) {
      this.terminateCtx(ctx, TerminalAction.REFUSE, "Invalid input schema");
      return;
    }

    // Generate embedding if not provided
    if (ctx.embedding.length === 0) {
      ctx.embedding = this.generateEmbedding(ctx.input.payload);
    }

    this.logger.record(
      "Input validated",
      1.0,
      1.0,
      "PROCEED",
      ctx.input.domain,
      PipelineStage.INPUT,
    );

    ctx.stagesCompleted.push(PipelineStage.INPUT);
  }

  /**
   * Stage 2: DOMAIN CHECK — Verify domain is operational.
   * Policy #5: Blast radius isolation.
   */
  private stageDomainCheck(ctx: PipelineContext): void {
    ctx.currentStage = PipelineStage.DOMAIN_CHECK;

    const domain = this.domains.getDomain(ctx.input.domain);
    if (!domain) {
      this.terminateCtx(ctx, TerminalAction.REFUSE, `Unknown domain: ${ctx.input.domain}`);
      return;
    }

    ctx.domain = domain;

    // Policy #5: Disabled domains refuse everything
    if (!this.domains.isOperational(ctx.input.domain)) {
      this.terminateCtx(ctx, TerminalAction.REFUSE, `Domain '${ctx.input.domain}' is DISABLED`);
      return;
    }

    // Policy #2: Check drift
    this.drift.recordInput(ctx.input.domain, ctx.embedding);
    const driftReport = this.drift.checkDrift(ctx.input.domain);
    ctx.driftReport = driftReport;

    if (driftReport.recommendation === "DISABLE") {
      this.terminateCtx(
        ctx,
        TerminalAction.REFUSE,
        `Severe drift detected in domain '${ctx.input.domain}'`,
      );
      return;
    }

    this.logger.record(
      `Domain check passed: ${ctx.input.domain} (${domain.status})`,
      1.0,
      domain.reliabilityScore,
      "PROCEED",
      ctx.input.domain,
      PipelineStage.DOMAIN_CHECK,
      { driftScore: driftReport.driftScore },
    );

    ctx.stagesCompleted.push(PipelineStage.DOMAIN_CHECK);
  }

  /**
   * Stage 3: NOVELTY GATE — Classify input novelty.
   * Policy #6: Adversarial input rejection (before any model processing).
   */
  private stageNoveltyGate(ctx: PipelineContext): void {
    ctx.currentStage = PipelineStage.NOVELTY_GATE;

    // Policy #6: Adversarial check BEFORE model processing
    const adversarial = this.shield.validate(ctx.input.domain, ctx.embedding);
    ctx.adversarialScore = adversarial.score;

    if (!adversarial.accepted) {
      this.terminateCtx(ctx, TerminalAction.REFUSE, adversarial.reason);
      return;
    }

    // Novelty detection via embedding similarity
    // (Uses simplified cosine similarity against memory)
    const { state, score, matchedId } = this.detectNovelty(ctx.embedding);
    ctx.noveltyState = state;
    ctx.noveltyScore = score;
    ctx.matchedMemoryId = matchedId;

    this.logger.record(
      `Novelty: ${state} (score=${score.toFixed(3)})`,
      score,
      ctx.domain?.reliabilityScore || 0,
      "PROCEED",
      ctx.input.domain,
      PipelineStage.NOVELTY_GATE,
    );

    ctx.stagesCompleted.push(PipelineStage.NOVELTY_GATE);
  }

  /**
   * Stage 4: REASONING MODE — Select execution strategy.
   * Handles inherent limits (decomposition, provisional responses).
   */
  private stageReasoningMode(ctx: PipelineContext): void {
    ctx.currentStage = PipelineStage.REASONING_MODE;

    // Check inherent limits
    const limitResponses = this.limits.evaluate(ctx);

    // Apply limit overrides
    for (const lr of limitResponses) {
      if (lr.decisionModeOverride) {
        ctx.decisionMode = lr.decisionModeOverride;
      }
      if (lr.terminalActionOverride) {
        // Inherent limits can terminate (e.g., ESCALATE for unknown knowledge)
        if (lr.terminalActionOverride === TerminalAction.ESCALATE) {
          this.terminateCtx(ctx, TerminalAction.ESCALATE, lr.instruction);
          return;
        }
        // Other terminal actions are noted but don't terminate the pipeline
        ctx.terminalAction = lr.terminalActionOverride;
      }
    }

    // Default reasoning mode based on novelty
    if (!ctx.decisionMode || ctx.decisionMode === DecisionMode.FULL) {
      switch (ctx.noveltyState) {
        case "SAME":
          ctx.decisionMode = DecisionMode.CACHED;
          break;
        case "SIMILAR":
          ctx.decisionMode = DecisionMode.LIGHTWEIGHT;
          break;
        default:
          ctx.decisionMode = DecisionMode.FULL;
      }
    }

    this.logger.record(
      `Reasoning mode: ${ctx.decisionMode}`,
      ctx.confidenceScore,
      ctx.domain?.reliabilityScore || 0,
      "PROCEED",
      ctx.input.domain,
      PipelineStage.REASONING_MODE,
    );

    ctx.stagesCompleted.push(PipelineStage.REASONING_MODE);
  }

  /**
   * Stage 5: SAFETY CHECK — Confidence gate + drift awareness.
   * Policy #1: If confidence < threshold → ABSTAIN.
   */
  private stageSafetyCheck(ctx: PipelineContext): void {
    ctx.currentStage = PipelineStage.SAFETY_CHECK;

    // Estimate confidence
    const domainReliability = ctx.domain?.reliabilityScore || 0;
    ctx.confidenceScore = this.confidence.estimateConfidence(
      ctx.noveltyScore,
      domainReliability,
      ctx.decisionMode === DecisionMode.DECOMPOSED,
    );

    // Get effective threshold (higher during drift/probation)
    const threshold = this.domains.getEffectiveConfidenceThreshold(ctx.input.domain);
    const driftActive = ctx.driftReport?.driftDetected || false;

    // Policy #1: Evaluate confidence
    const gateResult = this.confidence.evaluate(ctx.confidenceScore, threshold, driftActive);

    if (!gateResult.passed) {
      this.terminateCtx(ctx, gateResult.action || TerminalAction.REFUSE, gateResult.reason);
      return;
    }

    // If marginal confidence, note the VERIFY action but continue
    if (gateResult.action === TerminalAction.VERIFY) {
      ctx.terminalAction = TerminalAction.VERIFY;
    }

    this.logger.record(
      `Safety check: confidence=${ctx.confidenceScore.toFixed(3)} threshold=${threshold.toFixed(3)}`,
      ctx.confidenceScore,
      domainReliability,
      gateResult.action ? gateResult.action : "PROCEED",
      ctx.input.domain,
      PipelineStage.SAFETY_CHECK,
    );

    ctx.stagesCompleted.push(PipelineStage.SAFETY_CHECK);
  }

  /**
   * Execute the actual model/inference logic.
   * This is the ONLY place where the executor is invoked.
   */
  private async invokeExecutor<T>(
    ctx: PipelineContext,
    executor: GovernedExecutor<T>,
  ): Promise<void> {
    // For CACHED mode, retrieve from memory instead of executing
    if (ctx.decisionMode === DecisionMode.CACHED && ctx.matchedMemoryId) {
      const cached = this.memory.retrieve(ctx.matchedMemoryId);
      if (cached && this.memory.isUsable(ctx.matchedMemoryId)) {
        ctx.result = cached.output;
        return;
      }
      // Cache miss — fall through to full execution
      ctx.decisionMode = DecisionMode.FULL;
    }

    try {
      const startMs = performance.now();
      const result = await executor(ctx.input.payload, undefined, ctx.decisionMode);
      const elapsedMs = performance.now() - startMs;

      // Check for slow verification
      const slowCheck = this.limits.checkSlowVerification(elapsedMs);
      if (slowCheck) {
        ctx.terminalAction = TerminalAction.VERIFY;
      }

      ctx.result = result;
    } catch (error: unknown) {
      const termination = this.terminator.terminate(error, ctx);
      ctx.terminated = true;
      ctx.terminalAction = termination.action;
      ctx.terminationReason = termination.reason;
    }
  }

  /**
   * Stage 6: RELIABILITY UPDATE — Update domain scores.
   * Policy #3: Register for future outcome feedback.
   */
  private stageReliabilityUpdate(ctx: PipelineContext): void {
    ctx.currentStage = PipelineStage.RELIABILITY_UPDATE;

    if (ctx.result !== null) {
      this.domains.recordSuccess(ctx.input.domain);
    } else {
      this.domains.recordFailure(ctx.input.domain);
    }

    ctx.stagesCompleted.push(PipelineStage.RELIABILITY_UPDATE);
  }

  /**
   * Stage 7: AUTHORITY CONTROL — Determine output authority level.
   * Policy #7: The system decides when the model is allowed to decide.
   */
  private stageAuthorityControl(ctx: PipelineContext): void {
    ctx.currentStage = PipelineStage.AUTHORITY_CONTROL;

    const domainMaxAuth = this.domains.getMaxAuthority(ctx.input.domain);
    const domainStatus = ctx.domain?.status || DomainStatus.DISABLED;
    const domainReliability = ctx.domain?.reliabilityScore || 0;
    const driftActive = ctx.driftReport?.driftDetected || false;

    const authDecision = this.authority.evaluate(
      AuthorityLevel.AUTOMATED, // Request highest — let controller decide
      domainMaxAuth,
      domainStatus,
      domainReliability,
      ctx.confidenceScore,
      driftActive,
    );

    ctx.authorityLevel = authDecision.level;

    if (!authDecision.allowed) {
      this.terminateCtx(
        ctx,
        authDecision.terminalAction || TerminalAction.REFUSE,
        authDecision.reason,
      );
      return;
    }

    // Override terminal action if authority requires it
    if (authDecision.terminalAction) {
      ctx.terminalAction = authDecision.terminalAction;
    }

    this.logger.record(
      `Authority: ${authDecision.level}`,
      ctx.confidenceScore,
      domainReliability,
      authDecision.terminalAction || "PROCEED",
      ctx.input.domain,
      PipelineStage.AUTHORITY_CONTROL,
      { requiresHuman: authDecision.requiresHuman },
    );

    ctx.stagesCompleted.push(PipelineStage.AUTHORITY_CONTROL);
  }

  /**
   * Stage 8: MEMORY LIFECYCLE — Store results, manage memory.
   */
  private stageMemoryLifecycle(ctx: PipelineContext): void {
    ctx.currentStage = PipelineStage.MEMORY_LIFECYCLE;

    // Only store if caching is allowed and we have a result
    if (ctx.result !== null && this.domains.isCachingAllowed(ctx.input.domain)) {
      const entry: GovernedMemoryEntry = {
        id: uuidv4(),
        domain: ctx.input.domain,
        input: ctx.input.payload,
        embedding: ctx.embedding,
        output: ctx.result,
        reliability: ctx.domain?.reliabilityScore || 0,
        usageCount: 0,
        createdAt: Date.now(),
        lastAccessedAt: Date.now(),
        feedbackScore: null,
      };

      this.memory.store(entry);
    }

    // Register for outcome feedback (Policy #3)
    const outputId = uuidv4();
    this.feedback.registerPending(outputId, ctx.input.domain, ctx.matchedMemoryId);

    ctx.stagesCompleted.push(PipelineStage.MEMORY_LIFECYCLE);
  }

  // ═══════════════════════════════════════════════════════════
  //  HELPERS
  // ═══════════════════════════════════════════════════════════

  private initContext(input: GovernedInput): PipelineContext {
    return {
      input,
      currentStage: PipelineStage.INPUT,
      domain: null,
      embedding: input.embedding ? [...input.embedding] : [],
      noveltyState: "NEW",
      noveltyScore: 0,
      matchedMemoryId: null,
      decisionMode: DecisionMode.FULL,
      confidenceScore: 0,
      adversarialScore: 0,
      driftReport: null,
      authorityLevel: AuthorityLevel.ADVISORY,
      terminalAction: null,
      terminated: false,
      terminationReason: null,
      result: null,
      stagesCompleted: [],
      startTimestamp: performance.now(),
      errors: [],
    };
  }

  private terminateCtx(ctx: PipelineContext, action: TerminalAction, reason: string): void {
    ctx.terminated = true;
    ctx.terminalAction = action;
    ctx.terminationReason = reason;
    ctx.currentStage = PipelineStage.TERMINATED;
    ctx.stagesCompleted.push(PipelineStage.TERMINATED);

    this.logger.record(
      reason,
      ctx.confidenceScore,
      ctx.domain?.reliabilityScore || 0,
      action,
      ctx.input.domain,
      ctx.currentStage,
    );
  }

  private buildOutput<T>(ctx: PipelineContext): GovernedOutput<T> {
    const latencyMs = performance.now() - ctx.startTimestamp;

    const trace: ExplainabilityTrace = {
      sourceMemory: ctx.matchedMemoryId,
      reasoningPath: ctx.stagesCompleted,
      decisionMode: ctx.decisionMode,
      confidenceScore: ctx.confidenceScore,
      domainReliability: ctx.domain?.reliabilityScore || 0,
      authorityLevel: ctx.authorityLevel,
      terminalAction: ctx.terminalAction,
      driftDetected: ctx.driftReport?.driftDetected || false,
      noveltyState: ctx.noveltyState,
      latencyMs,
    };

    return {
      id: uuidv4(),
      inputId: ctx.input.id,
      result: (ctx.result as T) || null,
      accepted:
        !ctx.terminated ||
        ctx.terminalAction === TerminalAction.LEARN ||
        ctx.terminalAction === TerminalAction.VERIFY,
      terminalAction: ctx.terminalAction,
      authorityLevel: ctx.authorityLevel,
      trace,
      timestamp: Date.now(),
    };
  }

  private generateEmbedding(text: string): number[] {
    // Mock embedding — real implementation would use ONNX model
    const embedding = new Array(384).fill(0);
    for (let i = 0; i < text.length && i < 384; i++) {
      embedding[i] = text.charCodeAt(i) / 255;
    }
    // Normalize
    const norm = Math.sqrt(embedding.reduce((s: number, v: number) => s + v * v, 0));
    return norm > 0 ? embedding.map((v: number) => v / norm) : embedding;
  }

  private detectNovelty(embedding: number[]): {
    state: string;
    score: number;
    matchedId: string | null;
  } {
    // Simplified novelty detection
    // In production, this delegates to the existing NoveltyDetector
    const norm = Math.sqrt(embedding.reduce((s, v) => s + v * v, 0));
    const score = Math.min(1.0, norm); // Higher norm → more "known"

    if (score > 0.95) return { state: "SAME", score, matchedId: null };
    if (score > 0.7) return { state: "SIMILAR", score, matchedId: null };
    return { state: "NEW", score, matchedId: null };
  }

  // ═══════════════════════════════════════════════════════════
  //  PUBLIC ACCESSORS (for dashboard/admin integration)
  // ═══════════════════════════════════════════════════════════

  getDomainHealth() {
    return this.domains.getHealthReport();
  }
  getSemanticLog(limit?: number) {
    return this.logger.query({ limit });
  }
  getTerminationStats() {
    return this.terminator.getStats();
  }
  getMemoryStats() {
    return this.memory.getStats();
  }
  getDriftReport(domain: string) {
    return this.drift.checkDrift(domain);
  }
  getFeedbackStats(domain: string) {
    return this.feedback.getDomainFeedbackStats(domain);
  }
}
