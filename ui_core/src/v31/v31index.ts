// LEO AI V31 — Subsystem Barrel index exports

export { SpeculativeDecodingEngine } from "./speculativeDecodingEngine";
export type { SpeculativeReport } from "./speculativeDecodingEngine";

export { QuantizationOptimizationEngine } from "./quantizationOptimizationEngine";
export type { QuantizationPrecision, QuantizationProfile } from "./quantizationOptimizationEngine";

export { AttentionOptimizationEngine } from "./attentionOptimizationEngine";
export type { AttentionStrategyType, AttentionMetrics } from "./attentionOptimizationEngine";

export { PagedMemoryEngine } from "./pagedMemoryEngine";
export type { MemoryBlock, PagedMemoryTelemetry } from "./pagedMemoryEngine";

export { KvCompressionEngine } from "./kvCompressionEngine";
export type { CompressionReport } from "./kvCompressionEngine";

export { HierarchicalCrystalMemory } from "./hierarchicalCrystalMemory";
export type { CrystalMemoryLevel, RetrievalStep, RetrievalAudit } from "./hierarchicalCrystalMemory";

export { ComputeAvoidanceGovernor } from "./computeAvoidanceGovernor";
export type { AvoidanceDecisionType, GovernorResolution } from "./computeAvoidanceGovernor";

export { TrainingEfficiencyEngine } from "./trainingEfficiencyEngine";
export type { FinetuningStrategy, RetrainingCostReport } from "./trainingEfficiencyEngine";

export { KnowledgeDistillationEngine } from "./knowledgeDistillationEngine";
export type { DistilledKnowledgeFragment } from "./knowledgeDistillationEngine";

export { SyntheticKnowledgeEngine } from "./syntheticKnowledgeEngine";
export type { SyntheticItem } from "./syntheticKnowledgeEngine";

export { AdaptiveCascadeV2 } from "./adaptiveCascadeV2";
export type { ModelTier, CascadeStepV2, CascadeResultV2 } from "./adaptiveCascadeV2";

export { ContinuousBatchEngine } from "./continuousBatchEngine";
export type { BatchRequest, ContinuousBatchTelemetry } from "./continuousBatchEngine";

export { PrefixReuseEngine } from "./prefixReuseEngine";
export type { PrefixCacheEntry, PrefixEvaluation } from "./prefixReuseEngine";

export { OpenvinoMaximumUtilization } from "./openvinoMaximumUtilization";
export type { OpenVINODevice, DeviceTelemetry } from "./openvinoMaximumUtilization";

export { DistributedIntelligenceMesh } from "./distributedIntelligenceMesh";
export type { ExecutionNode, MeshNodeStatus, WorkloadDistribution } from "./distributedIntelligenceMesh";

export { ComputeIrrelevanceScore } from "./computeIrrelevanceScore";
export type { ScoreBreakdown } from "./computeIrrelevanceScore";

export { IntelligencePerFlopEngine } from "./intelligencePerFlopEngine";
export type { FlopEfficiencyReport } from "./intelligencePerFlopEngine";

export { RealWorldValidationLab } from "./realWorldValidationLab";
export type { ValidationMetrics } from "./realWorldValidationLab";
