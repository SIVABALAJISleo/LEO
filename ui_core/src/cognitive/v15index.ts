// Export V15 Core Substrate Modules
export { EvaluationUniverse, DomainBenchmark, UniverseEvaluationReport } from "../evaluation/evaluationUniverse";
export { SelfCritiqueEngineV2, CritiqueFlaws, CritiqueCycleStep, SelfCritiqueV2Report } from "../engines/selfCritiqueEngineV2";
export { UniversalReasoningEngine, ReasoningParadigm, ReasoningPremise, ParadigmResult } from "../engines/universalReasoningEngine";
export { DebateFramework, AgentStatement, DebatePhase, DebateSessionReport } from "../agents/debateFramework";
export { ToolVerifier, VerificationCheck, ToolVerifierReport } from "../verification/toolVerifier";
export { RealityFeedbackSystem, FeedbackLog, CalibrationReport } from "../learning/realityFeedback";
export { KnowledgeImmuneSystem, KnowledgeCrystal } from "../knowledge/knowledgeImmuneSystem";
export { MemoryImmuneSystem, MemoryBlock, ImmuneAuditReport } from "../memory/memoryImmuneSystem";
export { MetaLearningGovernor, StrategyMetric } from "../meta/metaLearningGovernor";
export { WorldModelV3, ScenarioProjection, SimulationResultV3 } from "../world/worldModelV3";
export { DiscoveryEngineV3, Hypothesis, DiscoveryReport } from "../discovery/discoveryEngineV3";
export { IntentReconstructionEngine, IntentReconstructionReport } from "../language/intentReconstruction";
export { ConfidenceEngine, CalibrationResponse, CalibrationTelemetry } from "../verification/confidenceEngine";
export { DistributedMesh, MeshNode, ConflictResolutionReport } from "../distributed/distributedMesh";
export { HardeningTelemetry, TelemetryEvent, RollbackAction } from "../enterprise/hardening";
export { iGPUAccelerationEngine, iGPUMetrics } from "../ucs/l16_iGPUAcceleration";
export { SelfImprovementLoop, ImprovementStep, SelfImprovementReport } from "../meta/selfImprovementLoop";
