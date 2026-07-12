// Export V15 Core Substrate Modules
// Classes exported as values; interfaces/types exported with `export type` for Vite 8 (rolldown) compliance.
export { EvaluationUniverse } from "../evaluation/evaluationUniverse";
export type { DomainBenchmark, UniverseEvaluationReport } from "../evaluation/evaluationUniverse";

export { SelfCritiqueEngineV2 } from "../engines/selfCritiqueEngineV2";
export type { CritiqueFlaws, CritiqueCycleStep, SelfCritiqueV2Report } from "../engines/selfCritiqueEngineV2";

export { UniversalReasoningEngine } from "../engines/universalReasoningEngine";
export type { ReasoningParadigm, ReasoningPremise, ParadigmResult } from "../engines/universalReasoningEngine";

export { DebateFramework } from "../agents/debateFramework";
export type { AgentStatement, DebatePhase, DebateSessionReport } from "../agents/debateFramework";

export { ToolVerifier } from "../verification/toolVerifier";
export type { VerificationCheck, ToolVerifierReport } from "../verification/toolVerifier";

export { RealityFeedbackSystem } from "../learning/realityFeedback";
export type { FeedbackLog, CalibrationReport } from "../learning/realityFeedback";

export { KnowledgeImmuneSystem } from "../knowledge/knowledgeImmuneSystem";
export type { KnowledgeCrystal } from "../knowledge/knowledgeImmuneSystem";

export { MemoryImmuneSystem } from "../memory/memoryImmuneSystem";
export type { MemoryBlock, ImmuneAuditReport } from "../memory/memoryImmuneSystem";

export { MetaLearningGovernor } from "../meta/metaLearningGovernor";
export type { StrategyMetric } from "../meta/metaLearningGovernor";

export { WorldModelV3 } from "../world/worldModelV3";
export type { ScenarioProjection, SimulationResultV3 } from "../world/worldModelV3";

export { DiscoveryEngineV3 } from "../discovery/discoveryEngineV3";
export type { Hypothesis, DiscoveryReport } from "../discovery/discoveryEngineV3";

export { IntentReconstructionEngine } from "../language/intentReconstruction";
export type { IntentReconstructionReport } from "../language/intentReconstruction";

export { ConfidenceEngine } from "../verification/confidenceEngine";
export type { CalibrationResponse, CalibrationTelemetry } from "../verification/confidenceEngine";

export { DistributedMesh } from "../distributed/distributedMesh";
export type { MeshNode, ConflictResolutionReport } from "../distributed/distributedMesh";

export { HardeningTelemetry } from "../enterprise/hardening";
export type { TelemetryEvent, RollbackAction } from "../enterprise/hardening";

export { iGPUAccelerationEngine } from "../ucs/l16_iGPUAcceleration";
export type { iGPUMetrics } from "../ucs/l16_iGPUAcceleration";

export { SelfImprovementLoop } from "../meta/selfImprovementLoop";
export type { ImprovementStep, SelfImprovementReport } from "../meta/selfImprovementLoop";
