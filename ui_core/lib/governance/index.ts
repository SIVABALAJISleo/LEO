/**
 * ═══════════════════════════════════════════════════════════════
 *  GOVERNED INTELLIGENCE SYSTEM — Public API
 * ═══════════════════════════════════════════════════════════════
 *
 *  Architecture: 11 modules, 1 type system, 1 pipeline.
 *  Zero existing modules modified.
 *
 *  ┌─────────────────────────────────────────────────────────┐
 *  │                  GovernedPipeline                       │
 *  │  Input → Domain → Novelty → Reasoning → Safety →      │
 *  │  Execute → Reliability → Authority → Memory            │
 *  ├─────────────────────────────────────────────────────────┤
 *  │  SchemaEnforcer      │  Policy #9: Maintainability     │
 *  │  SemanticLogger      │  Policy #8: Observability       │
 *  │  DomainRegistry      │  Policy #5/#10: Blast/Recovery  │
 *  │  DriftMonitor        │  Policy #2: Data Drift          │
 *  │  AdversarialShield   │  Policy #6: Adversarial Input   │
 *  │  ConfidenceGate      │  Policy #1: Confidence Risk     │
 *  │  AuthorityController │  Policy #7: Responsibility      │
 *  │  OutcomeFeedbackLoop │  Policy #3: Ground Truth        │
 *  │  MemoryGovernor      │  Memory Lifecycle               │
 *  │  InherentLimitHandler│  Inherent Limit Responses       │
 *  │  FailureTerminator   │  System Guarantee               │
 *  └─────────────────────────────────────────────────────────┘
 *
 *  SYSTEM GUARANTEE:
 *  Every failure → REFUSE | ESCALATE | VERIFY | LIMIT | LEARN
 *  Never silent failure. Never uncontrolled output.
 *
 * ═══════════════════════════════════════════════════════════════
 */

// ──── Core Types ────
export type {
    GovernedInput,
    GovernedOutput,
    ExplainabilityTrace,
    PipelineContext,
    DomainDefinition,
    DomainState,
    DistributionSnapshot,
    DriftReport,
    OutcomeFeedback,
    SemanticLogEntry,
    SchemaContract,
    GovernedMemoryEntry,
    ProbationRecord,
} from './types';

export {
    TerminalAction,
    AuthorityLevel,
    DecisionMode,
    DomainStatus,
    PipelineStage,
} from './types';

// ──── Pipeline ────
export { GovernedPipeline } from './GovernedPipeline';
export type { GovernedExecutor } from './GovernedPipeline';

// ──── Modules ────
export { SchemaEnforcer } from './SchemaEnforcer';
export { SemanticLogger } from './SemanticLogger';
export { DomainRegistry } from './DomainRegistry';
export { DriftMonitor } from './DriftMonitor';
export { AdversarialShield } from './AdversarialShield';
export { ConfidenceGate } from './ConfidenceGate';
export { AuthorityController } from './AuthorityController';
export { OutcomeFeedbackLoop } from './OutcomeFeedbackLoop';
export { MemoryGovernor } from './MemoryGovernor';
export { InherentLimitHandler, InherentLimit } from './InherentLimitHandler';
export { FailureTerminator } from './FailureTerminator';
