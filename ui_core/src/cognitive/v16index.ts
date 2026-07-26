// Export V16 Cognitive Substrate Modules
// Classes as values; interfaces/types with `export type` for Vite 8 (rolldown) compliance.
export { EvaluationUniverseV16 } from "../evaluation_universe/tasks";
export type { V16BenchmarkDomain, UniverseV16Report } from "../evaluation_universe/tasks";

export { UniversalReasoningCore } from "../engines/universalReasoningCore";

export { FormalProofEngine } from "../engines/formalProofEngine";
export type {
  TheoremSolver,
  ProofTelemetry,
  ProofEngineReport,
} from "../engines/formalProofEngine";

export { VerificationMesh } from "../verification/verificationMesh";
export type {
  VerificationCheckV16,
  VerificationMeshReport,
} from "../verification/verificationMesh";

export { RealityFeedbackEngineV3 } from "../learning/realityFeedbackEngineV3";

export { KnowledgeImmuneSystem } from "../knowledge/knowledgeImmuneSystem";
export type { KnowledgeCrystal } from "../knowledge/knowledgeImmuneSystem";

export { MemoryImmuneSystem } from "../memory/memoryImmuneSystem";
export type { MemoryBlock, ImmuneAuditReport } from "../memory/memoryImmuneSystem";

export { MetaLearningGovernor } from "../meta/metaLearningGovernor";
export type { StrategyMetric } from "../meta/metaLearningGovernor";

export { DiscoveryEngineV4 } from "../discovery/discoveryEngineV4";
export { WorldModelV4 } from "../world/worldModelV4";

export { DebateFrameworkV16 } from "../agents/debateFrameworkV16";
export type {
  AgentStatementV16,
  DebatePhaseV16,
  DebateV16Report,
} from "../agents/debateFrameworkV16";

export { IntentReconstructionEngine } from "../language/intentReconstruction";
export type { IntentReconstructionReport } from "../language/intentReconstruction";

export { ConfidenceEngine, ConfidenceEngineV16 } from "../verification/confidenceEngine";
export type { CalibrationResponse, CalibrationTelemetry } from "../verification/confidenceEngine";

export { HardeningTelemetry, HardeningTelemetryV16 } from "../enterprise/hardening";
export type { TelemetryEvent, RollbackAction, IncidentAlertV16 } from "../enterprise/hardening";

export { iGPUAccelerationEngine, iGPUAccelerationEngineV16 } from "../ucs/l16_iGPUAcceleration";
export type { iGPUMetrics, iGPUMetricsV16 } from "../ucs/l16_iGPUAcceleration";
