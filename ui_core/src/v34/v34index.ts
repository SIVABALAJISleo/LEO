// LEO AI V34 — Compute Irrelevance Subsystem Barrel Index Exports
// Consolidates and exposes all 45 engine modules.

// === 1. BitNet Research Layer ===
export { BitNetResearchEngine } from "./bitnet/bitnetResearchEngine";
export type { BitNetEvaluation } from "./bitnet/bitnetResearchEngine";
export { TernaryWeightSimulator } from "./bitnet/ternaryWeightSimulator";
export type { TernarySimulationReport } from "./bitnet/ternaryWeightSimulator";
export { LowBitInferenceAnalyzer } from "./bitnet/lowBitInferenceAnalyzer";
export type { LowBitInferenceProfile } from "./bitnet/lowBitInferenceAnalyzer";
export { ComputeReductionCalculator } from "./bitnet/computeReductionCalculator";
export type { ComputeReductionStats } from "./bitnet/computeReductionCalculator";

// === 2. Intel Acceleration Layer ===
export { IntelCapabilityDetector } from "./intel/intelCapabilityDetector";
export type { IntelHardwareCapabilities } from "./intel/intelCapabilityDetector";
export { IpexOptimizationEngine } from "./intel/ipexOptimizationEngine";
export type { IpexSettings, IpexRuntimeStatus } from "./intel/ipexOptimizationEngine";
export { SyclAccelerationManager } from "./intel/syclAccelerationManager";
export type { SyclQueueStatus } from "./intel/syclAccelerationManager";
export { XpuExecutionPlanner } from "./intel/xpuExecutionPlanner";
export type { IntelExecutionReport } from "./intel/xpuExecutionPlanner";

// === 3. CPU-First RAG Core ===
export { ExternalMemoryEngine } from "./rag/externalMemoryEngine";
export type { RetrievalChunk } from "./rag/externalMemoryEngine";
export { RetrievalGovernor } from "./rag/retrievalGovernor";
export type { GovernorResolution } from "./rag/retrievalGovernor";
export { CrystalMemoryRouter } from "./rag/crystalMemoryRouter";
export type { RoutingDestination } from "./rag/crystalMemoryRouter";
export { KnowledgeExternalizationEngine } from "./rag/knowledgeExternalizationEngine";
export type { KnowledgeEfficiencyTelemetry } from "./rag/knowledgeExternalizationEngine";

// === 4. Crystal Memory Expansion ===
export { CrystalKnowledgeStore } from "./memory/crystalKnowledgeStore";
export type { CrystalConcept } from "./memory/crystalKnowledgeStore";
export { ReasoningCacheEngine } from "./memory/reasoningCacheEngine";
export type { ReasoningTrajectory } from "./memory/reasoningCacheEngine";
export { WorkflowMemoryEngine } from "./memory/workflowMemoryEngine";
export type { WorkflowMacro } from "./memory/workflowMemoryEngine";
export { SolutionReusabilityEngine } from "./memory/solutionReusabilityEngine";
export type { ReusabilityReport } from "./memory/solutionReusabilityEngine";

// === 5. Dynamic Expert Activation ===
export { ExpertRouter } from "./moe/expertRouter";
export type { RoutingDestination as MoeRoutingDestination } from "./moe/expertRouter";
export { ExpertPredictor } from "./moe/expertPredictor";
export type { RouterPrediction } from "./moe/expertPredictor";
export { SparseActivationEngine } from "./moe/sparseActivationEngine";
export type { ExpertActivationStatus } from "./moe/sparseActivationEngine";
export { InactiveExpertManager } from "./moe/inactiveExpertManager";
export type { ExpertSwapReport } from "./moe/inactiveExpertManager";

// === 6. Cache-First Computing ===
export { L1Optimizer } from "./cache/l1Optimizer";
export type { L1Allocation } from "./cache/l1Optimizer";
export { L2Optimizer } from "./cache/l2Optimizer";
export type { L2BufferReport } from "./cache/l2Optimizer";
export { L3Optimizer } from "./cache/l3Optimizer";
export type { L3PageStatus } from "./cache/l3Optimizer";
export { CacheResidencyAnalyzer } from "./cache/cacheResidencyAnalyzer";
export type { CacheResidencyTelemetry } from "./cache/cacheResidencyAnalyzer";

// === 7. AVX / SIMD Optimization ===
export { AvxPlanner } from "./simd/avxPlanner";
export type { AvxAllocationPlan } from "./simd/avxPlanner";
export { VnniPlanner } from "./simd/vnniPlanner";
export type { VnniPlan } from "./simd/vnniPlanner";
export { VectorKernelGenerator } from "./simd/vectorKernelGenerator";
export type { SimdInstructionPlan } from "./simd/vectorKernelGenerator";

// === 8. Self-Optimizing Execution Engine ===
export { RuntimeProfiler } from "./runtime/runtimeProfiler";
export type { RuntimeMetrics } from "./runtime/runtimeProfiler";
export { BottleneckFinder } from "./runtime/bottleneckFinder";
export type { SystemBottleneck } from "./runtime/bottleneckFinder";
export { ExecutionRewriter } from "./runtime/executionRewriter";
export type { RewriteEvent, RuntimeOptimizationReport } from "./runtime/executionRewriter";

// === 9. Real User Feedback Learning ===
export { FeedbackCollector } from "./feedback/feedbackCollector";
export type { UserRating } from "./feedback/feedbackCollector";
export { CorrectionAnalyzer } from "./feedback/correctionAnalyzer";
export type { CorrectionAnalysis } from "./feedback/correctionAnalyzer";
export { ImprovementPlanner } from "./feedback/improvementPlanner";
export type { ImprovementTask } from "./feedback/improvementPlanner";
export { DeploymentLearner } from "./feedback/deploymentLearner";
export type { LearningReport } from "./feedback/deploymentLearner";

// === 10. Knowledge Freshness System ===
export { SourceRanker } from "./freshness/sourceRanker";
export type { SourceRank } from "./freshness/sourceRanker";
export { ContradictionDetector } from "./freshness/contradictionDetector";
export type { ContradictionReport } from "./freshness/contradictionDetector";
export { FreshnessMonitor } from "./freshness/freshnessMonitor";
export type { FreshnessMetrics } from "./freshness/freshnessMonitor";
export { UpdateScheduler } from "./freshness/updateScheduler";
export type { UpdateJob } from "./freshness/updateScheduler";

// === 11. Long-Tail Failure Discovery ===
export { RareBugFinder } from "./failures/rareBugFinder";
export type { AnomalyReport } from "./failures/rareBugFinder";
export { AnomalyCatalog } from "./failures/anomalyCatalog";
export type { AnomalyRecord } from "./failures/anomalyCatalog";
export { EdgeCaseRegistry } from "./failures/edgeCaseRegistry";
export type { EdgeCaseRecord } from "./failures/edgeCaseRegistry";
export { FailureReplayEngine } from "./failures/failureReplayEngine";
export type { ReplayResult, RobustnessTelemetry } from "./failures/failureReplayEngine";

// === 12. Functional Intelligence Certification ===
export { FunctionalScoreEngine } from "./certification/functionalScoreEngine";
export type { V34ScoreBreakdown } from "./certification/functionalScoreEngine";
export { OutcomeQualityEvaluator } from "./certification/outcomeQualityEvaluator";
export type { QualityEvaluation } from "./certification/outcomeQualityEvaluator";
export type { EfficiencyMetricsReport } from "./certification/efficiencyEvaluator";
export { EfficiencyEvaluator } from "./certification/efficiencyEvaluator";

// === 13. V34 Frontier Compute Irrelevance Engines ===
export { TernaryReasoningEngine } from "./engines/ternaryReasoningEngine";
export type { TernaryTelemetry, TernaryInferenceResult } from "./engines/ternaryReasoningEngine";
export { HeterogeneousComputeOrchestrator } from "./engines/heterogeneousComputeOrchestrator";
export type {
  DeviceType,
  TaskProfile,
  DeviceTelemetry,
} from "./engines/heterogeneousComputeOrchestrator";
export { ExternalizedMemoryEngine } from "./engines/externalizedMemoryEngine";
export type { FactDetails, RetrievalSummary } from "./engines/externalizedMemoryEngine";
export { MoeRouterEngine } from "./engines/moeRouterEngine";
export type { ExpertType, ExpertPerformance, MoeRoutingReport } from "./engines/moeRouterEngine";
export { CacheIntelligenceEngine } from "./engines/cacheIntelligenceEngine";
export type { CacheEntry, CacheReport } from "./engines/cacheIntelligenceEngine";
export { WorldModelEngineV2 } from "./engines/worldModelEngineV2";
export type { EntityState, CausalLink, WorldState } from "./engines/worldModelEngineV2";
export { ScientificReasoningEngineV2 } from "./engines/scientificReasoningEngineV2";
export type { ScientificHypothesis, ScienceReport } from "./engines/scientificReasoningEngineV2";
export { PhysicsSurrogateEngine } from "./engines/physicsSurrogateEngine";
export type { SurrogateEstimation } from "./engines/physicsSurrogateEngine";
export { ActiveInferenceEngine } from "./engines/activeInferenceEngine";
export type { ConfidenceState, ActiveInferenceResult } from "./engines/activeInferenceEngine";
export { SelfOptimizationRuntime } from "./engines/selfOptimizationRuntime";
export type { RuntimeProfiling, OptimizationDirectives } from "./engines/selfOptimizationRuntime";
export { RealityAlignmentEngineV3 } from "./engines/realityAlignmentEngineV3";
export type { AlignmentStats, AlignmentResolution } from "./engines/realityAlignmentEngineV3";
