// LEO AI V33 — Compute Irrelevance Subsystem Barrel Index Exports
// Consolidates and exposes all 38 engine modules.

// === 1. State Space Model Research ===
export { StateSpaceResearchEngine } from "./state_space/stateSpaceResearchEngine";
export type { ArchitectureMetrics } from "./state_space/stateSpaceResearchEngine";
export { MambaEvaluationEngine } from "./state_space/mambaEvaluationEngine";
export type { ScalingBenchmark } from "./state_space/mambaEvaluationEngine";
export { ArchitectureComparisonEngine } from "./state_space/architectureComparisonEngine";
export type { EfficiencyIndexReport } from "./state_space/architectureComparisonEngine";

// === 2. Extreme Quantization ===
export { TernaryQuantizationEngine } from "./quantization/ternaryQuantizationEngine";
export type { TernaryStats } from "./quantization/ternaryQuantizationEngine";
export { Int4OptimizationEngine } from "./quantization/int4OptimizationEngine";
export type { QuantizationProfile } from "./quantization/int4OptimizationEngine";
export { AdaptivePrecisionEngine } from "./quantization/adaptivePrecisionEngine";
export type { RoutingDecision, PrecisionTelemetry } from "./quantization/adaptivePrecisionEngine";

// === 3. Cache-First Intelligence ===
export { CacheResidentInferenceEngine } from "./cache/cacheResidentInferenceEngine";
export type { CacheResidencyRecord } from "./cache/cacheResidentInferenceEngine";
export { L3OptimizationEngine } from "./cache/l3OptimizationEngine";
export type { CacheLayerReport } from "./cache/l3OptimizationEngine";
export { MemoryResidencyAnalyzer } from "./cache/memoryResidencyAnalyzer";
export type { CacheAccessStats } from "./cache/memoryResidencyAnalyzer";

// === 4. Small Model Swarm ===
export { MicroModelCoordinator } from "./swarm/microModelCoordinator";
export type { SpecialistModel, SwarmAssignment } from "./swarm/microModelCoordinator";
export { SwarmConsensusEngine } from "./swarm/swarmConsensusEngine";
export type { AgentVote, SwarmConsensusReport } from "./swarm/swarmConsensusEngine";
export { DistributedReasoningEngine } from "./swarm/distributedReasoningEngine";
export type { ReasoningBranch, TreeOfThoughtReport } from "./swarm/distributedReasoningEngine";

// === 5. Heterogeneous Compute Orchestration ===
export { CpuReasoningEngine } from "./orchestration/cpuReasoningEngine";
export type { CpuExecutionStats } from "./orchestration/cpuReasoningEngine";
export { IgpuExecutionEngine } from "./orchestration/igpuExecutionEngine";
export type { IgpuMetrics } from "./orchestration/igpuExecutionEngine";
export { NpuExecutionEngine } from "./orchestration/npuExecutionEngine";
export type { NpuActivityReport } from "./orchestration/npuExecutionEngine";
export { TaskRoutingEngine } from "./orchestration/taskRoutingEngine";
export type { LoadRoutingReport } from "./orchestration/taskRoutingEngine";

// === 6. Dynamic Sparse Expert ===
export { ExpertPredictionEngine } from "./moe/expertPredictionEngine";
export type { ExpertWeight, PredictionTelemetry } from "./moe/expertPredictionEngine";
export { SparseActivationEngine } from "./moe/sparseActivationEngine";
export type { ExpertState, ActivationStats } from "./moe/sparseActivationEngine";
export { ExpertCacheManager } from "./moe/expertCacheManager";
export type { CacheSwapRecord } from "./moe/expertCacheManager";

// === 7. SIMD Acceleration ===
export { AvxOptimizationEngine } from "./simd/avxOptimizationEngine";
export type { VectorRegisterStats } from "./simd/avxOptimizationEngine";
export { VnniOptimizationEngine } from "./simd/vnniOptimizationEngine";
export type { VnniExecutionReport } from "./simd/vnniOptimizationEngine";
export { VectorInstructionPlanner } from "./simd/vectorInstructionPlanner";
export type { InstructionPlan } from "./simd/vectorInstructionPlanner";

// === 8. Algorithmic Math Optimization ===
export { WinogradEngine } from "./math/winogradEngine";
export type { WinogradStats } from "./math/winogradEngine";
export { FftOptimizationEngine } from "./math/fftOptimizationEngine";
export type { FftReport } from "./math/fftOptimizationEngine";
export { SparseMatrixEngine } from "./math/sparseMatrixEngine";
export type { SparsityReport } from "./math/sparseMatrixEngine";
export { MatrixPlanner } from "./math/matrixPlanner";
export type { MathSelectionReport } from "./math/matrixPlanner";

// === 9. Distributed Inference Swarm ===
export { FederatedInferenceEngine } from "./distributed/federatedInferenceEngine";
export type { EdgeNode, SplitInferenceJob } from "./distributed/federatedInferenceEngine";
export { PeerCoordinator } from "./distributed/peerCoordinator";
export type { ConnectionHeartbeat } from "./distributed/peerCoordinator";
export { GossipProtocolEngine } from "./distributed/gossipProtocolEngine";
export type { GossipMessage, DistributedSwarmReport } from "./distributed/gossipProtocolEngine";

// === 10. Self-Optimizing Runtime ===
export { RuntimeProfiler } from "./runtime/runtimeProfiler";
export type { RuntimeMetrics } from "./runtime/runtimeProfiler";
export { BottleneckDetector } from "./runtime/bottleneckDetector";
export type { SystemBottleneck } from "./runtime/bottleneckDetector";
export { ExecutionOptimizer } from "./runtime/executionOptimizer";
export type { OptimizationEvent, RuntimeOptimizationReport } from "./runtime/executionOptimizer";

// === 11. Intelligence-Per-Watt Governor ===
export { PowerMonitor } from "./efficiency/powerMonitor";
export type { ComponentPowerDraw, PowerTelemetryReport } from "./efficiency/powerMonitor";
export { EfficiencyGovernor } from "./efficiency/efficiencyGovernor";
export type { EfficiencyMetrics } from "./efficiency/efficiencyGovernor";
export { WorkloadBalancer } from "./efficiency/workloadBalancer";
export type { BalancerDirective } from "./efficiency/workloadBalancer";

// === 12. Compute Avoidance ===
export { AnswerReuseEngine } from "./avoidance/answerReuseEngine";
export type { CachedAnswer, ReuseReport } from "./avoidance/answerReuseEngine";
export { ReasoningCacheEngine } from "./avoidance/reasoningCacheEngine";
export type { LogicTrajectory } from "./avoidance/reasoningCacheEngine";
export { SolutionCrystallizationEngine } from "./avoidance/solutionCrystallizationEngine";
export type { CrystallizedEntity } from "./avoidance/solutionCrystallizationEngine";

// === 13. Functional Intelligence Scoring ===
export { FunctionalIntelligenceScore } from "./scoring/functionalIntelligenceScore";
export type { IntelligenceScoreBreakdown } from "./scoring/functionalIntelligenceScore";
