// Production hardening exports

export {
  incidentStateMachine,
  type IncidentState,
  type IncidentContext,
  type IncidentTransition,
} from "./IncidentStateMachine";
export {
  explainableErrors,
  createExplainableError,
  toExplainableError,
  type ExplainableError,
  type ErrorContext,
} from "./ExplainableErrors";
export {
  systemStatusService,
  type SystemStatusContract,
  type StabilityLevel,
  type KnownLimitation,
} from "./SystemStatusContract";
export {
  backupVerification,
  type BackupRecord,
  type BackupVerificationResult,
  type BackupPolicy,
} from "./BackupVerification";
export {
  releaseRollback,
  type Release,
  type HealthMetrics,
  type RolloutConfig,
} from "./ReleaseRollback";
export {
  incidentAutoHandler,
  type Incident,
  type IncidentType,
  type IncidentSeverity,
  type AutoAction,
} from "./IncidentAutoHandler";
export {
  launchVerification,
  type LaunchReadinessReport,
  type VerificationTest,
} from "./LaunchVerification";
export {
  productionReadinessChecker,
  type ProductionReadinessScore,
  type ReadinessCategory,
} from "./ProductionReadinessChecker";
export {
  productionHealthOrchestrator,
  type OrchestratorState,
  type HealthCheckResult,
  type AutoRecoveryAction,
} from "./ProductionHealthOrchestrator";
export {
  backupDrillAutomation,
  type BackupDrill,
  type DrillSchedule,
  type DrillReport,
} from "./BackupDrillAutomation";
export {
  abusePatternDetector,
  type AbusePattern,
  type AbuseEvent,
  type AbuseStats,
} from "./AbusePatternDetector";

// 99.9% Production Readiness Layer (NEW)
export {
  zeroLatencyEngine,
  type OptimisticUpdate,
  type SyncQueueItem,
  type PrefetchEntry,
  type ZeroLatencyStats,
} from "./ZeroLatencyEngine";
export {
  selfHealingOperations,
  type HealthCheck,
  type AutoRetryConfig,
  type FeatureFlagState,
  type IncidentLogEntry,
  type SelfHealingStats,
} from "./SelfHealingOperations";
export {
  costProtection,
  type RateLimitConfig,
  type RateLimitState,
  type CostCeiling,
  type AbuseEvent as CostAbuseEvent,
  type CostProtectionStats,
} from "./CostProtection";
export {
  selfAwarenessLogger,
  type RequestLog,
  type AggregatedStats,
  type RealTimeMetrics,
} from "./SelfAwarenessLogger";
