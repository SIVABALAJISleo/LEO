/**
 * ═══════════════════════════════════════════════════════════════
 *  GOVERNED INTELLIGENCE SYSTEM — Core Type Definitions
 * ═══════════════════════════════════════════════════════════════
 *  Every type used across the governance layer is defined here.
 *  No module may define ad-hoc types for cross-module communication.
 * ═══════════════════════════════════════════════════════════════
 */

// ──────────────────────────── Terminal States ────────────────────────────
// SYSTEM GUARANTEE: Every failure path ends in exactly one of these.
export enum TerminalAction {
    REFUSE = 'REFUSE',     // Hard rejection — input is invalid or forbidden
    ESCALATE = 'ESCALATE',   // Human required — system cannot safely decide
    VERIFY = 'VERIFY',     // Provisional output that must be confirmed
    LIMIT = 'LIMIT',      // Output capped to safe boundary
    LEARN = 'LEARN',      // Accept but tag for feedback collection
}

// ──────────────────────────── Authority Levels ───────────────────────────
// Policy #7: Responsibility Boundary
export enum AuthorityLevel {
    ADVISORY = 'ADVISORY',   // Output needs human review before action
    ASSISTED = 'ASSISTED',   // Suggested — human can override
    AUTOMATED = 'AUTOMATED',  // Allowed only in trusted domains with high reliability
}

// ──────────────────────────── Decision Modes ─────────────────────────────
export enum DecisionMode {
    CACHED = 'CACHED',        // Exact match from memory
    LIGHTWEIGHT = 'LIGHTWEIGHT',   // RAG-augmented fast path
    FULL = 'FULL',          // Complete reasoning pipeline
    DECOMPOSED = 'DECOMPOSED',    // Complex → broken into verified steps
    PROVISIONAL = 'PROVISIONAL',   // Slow verification → provisional + confirmed
}

// ──────────────────────────── Domain Health ──────────────────────────────
export enum DomainStatus {
    ACTIVE = 'ACTIVE',      // Normal operation
    DEGRADED = 'DEGRADED',    // Elevated error rate — tightened thresholds
    PROBATION = 'PROBATION',   // Recovering — no caching, strict verification
    DISABLED = 'DISABLED',    // Reliability below floor — domain is offline
}

// ──────────────────────────── Pipeline Stage ─────────────────────────────
export enum PipelineStage {
    INPUT = 'INPUT',
    DOMAIN_CHECK = 'DOMAIN_CHECK',
    NOVELTY_GATE = 'NOVELTY_GATE',
    REASONING_MODE = 'REASONING_MODE',
    SAFETY_CHECK = 'SAFETY_CHECK',
    RELIABILITY_UPDATE = 'RELIABILITY_UPDATE',
    AUTHORITY_CONTROL = 'AUTHORITY_CONTROL',
    MEMORY_LIFECYCLE = 'MEMORY_LIFECYCLE',
    COMPLETE = 'COMPLETE',
    TERMINATED = 'TERMINATED',
}

// ──────────────────────────── Input Validation ───────────────────────────
export interface GovernedInput {
    readonly id: string;
    readonly domain: string;
    readonly payload: string;
    readonly embedding?: number[];
    readonly timestamp: number;
    readonly sourceSystem: string;
    readonly metadata?: Record<string, unknown>;
}

// ──────────────────────────── Explainability Trace ───────────────────────
// Policy #4: Every answer includes trace metadata.
export interface ExplainabilityTrace {
    readonly sourceMemory: string | null;
    readonly reasoningPath: PipelineStage[];
    readonly decisionMode: DecisionMode;
    readonly confidenceScore: number;
    readonly domainReliability: number;
    readonly authorityLevel: AuthorityLevel;
    readonly terminalAction: TerminalAction | null;
    readonly driftDetected: boolean;
    readonly noveltyState: string;
    readonly latencyMs: number;
}

// ──────────────────────────── Pipeline Output ────────────────────────────
export interface GovernedOutput<T = unknown> {
    readonly id: string;
    readonly inputId: string;
    readonly result: T | null;
    readonly accepted: boolean;
    readonly terminalAction: TerminalAction | null;
    readonly authorityLevel: AuthorityLevel;
    readonly trace: ExplainabilityTrace;
    readonly timestamp: number;
}

// ──────────────────────────── Domain Definition ──────────────────────────
export interface DomainDefinition {
    readonly name: string;
    readonly confidenceThreshold: number;
    readonly reliabilityFloor: number;
    readonly maxAuthorityLevel: AuthorityLevel;
    readonly allowCaching: boolean;
    readonly driftSensitivity: number; // 0.0–1.0
}

// ──────────────────────────── Domain State ────────────────────────────────
export interface DomainState {
    definition: DomainDefinition;
    status: DomainStatus;
    reliabilityScore: number;           // 0.0–1.0 rolling score
    totalDecisions: number;
    successfulDecisions: number;
    failedDecisions: number;
    consecutiveFailures: number;
    lastActivityTimestamp: number;
    probationStartTimestamp: number | null;
    probationVerifications: number;
    inputDistribution: DistributionSnapshot;
}

// ──────────────────────────── Drift Detection ────────────────────────────
// Policy #2: Continuous distribution comparison.
export interface DistributionSnapshot {
    mean: number[];
    variance: number[];
    sampleCount: number;
    windowStart: number;
    windowEnd: number;
}

export interface DriftReport {
    readonly domain: string;
    readonly driftScore: number;      // 0.0 = no drift, 1.0 = total drift
    readonly driftDetected: boolean;
    readonly recommendation: 'NONE' | 'TIGHTEN' | 'DISABLE';
    readonly timestamp: number;
}

// ──────────────────────────── Outcome Feedback ───────────────────────────
// Policy #3: No Ground Truth Learning
export interface OutcomeFeedback {
    readonly outputId: string;
    readonly domain: string;
    readonly correct: boolean;
    readonly reviewerTrust: number;     // 0.0–1.0 weighted trust
    readonly feedbackTimestamp: number;
    readonly correctedResult?: unknown;
}

// ──────────────────────────── Semantic Log ────────────────────────────────
// Policy #8: Log meaning, not events.
export interface SemanticLogEntry {
    readonly id: string;
    readonly intent: string;
    readonly confidence: number;
    readonly reliability: number;
    readonly decisionState: TerminalAction | 'PROCEED';
    readonly domain: string;
    readonly pipelineStage: PipelineStage;
    readonly timestamp: number;
    readonly metadata?: Record<string, unknown>;
}

// ──────────────────────────── Schema Contract ────────────────────────────
// Policy #9: All module communication follows strict schemas.
export interface SchemaContract<T> {
    readonly name: string;
    readonly version: number;
    validate(data: unknown): data is T;
}

// ──────────────────────────── Memory Entry ────────────────────────────────
export interface GovernedMemoryEntry {
    readonly id: string;
    readonly domain: string;
    readonly input: string;
    readonly embedding: number[];
    readonly output: unknown;
    readonly reliability: number;
    readonly usageCount: number;
    readonly createdAt: number;
    readonly lastAccessedAt: number;
    readonly feedbackScore: number | null;
}

// ──────────────────────────── Probation Record ───────────────────────────
// Policy #10: Recovery protocol.
export interface ProbationRecord {
    readonly domain: string;
    readonly enteredAt: number;
    readonly requiredVerifications: number;
    readonly completedVerifications: number;
    readonly successfulVerifications: number;
    readonly strictThresholdMultiplier: number;
}

// ──────────────────────────── Pipeline Context ───────────────────────────
// Mutable state that flows through the pipeline stages.
export interface PipelineContext {
    input: GovernedInput;
    currentStage: PipelineStage;
    domain: DomainState | null;
    embedding: number[];
    noveltyState: string;
    noveltyScore: number;
    matchedMemoryId: string | null;
    decisionMode: DecisionMode;
    confidenceScore: number;
    adversarialScore: number;
    driftReport: DriftReport | null;
    authorityLevel: AuthorityLevel;
    terminalAction: TerminalAction | null;
    terminated: boolean;
    terminationReason: string | null;
    result: unknown | null;
    stagesCompleted: PipelineStage[];
    startTimestamp: number;
    errors: string[];
}
