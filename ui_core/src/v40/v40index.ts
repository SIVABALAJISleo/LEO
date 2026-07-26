// LEO AI V40 — Consolidated Exporter barrel file
// Exposes all 15 upgraded subsystems.

// 1. Advanced Memory System
export { AdvancedMemorySystem } from "./engines/advancedMemorySystem";
export type { MemoryBlock, CacheLookupResult } from "./engines/advancedMemorySystem";

// 2. Graph Intelligence Engine
export { GraphIntelligenceEngine } from "./engines/graphIntelligenceEngine";
export type { NetworkNode, NetworkEdge, GraphTraceReport } from "./engines/graphIntelligenceEngine";

// 3. Multi-Agent System
export { MultiAgentSystem } from "./engines/multiAgentSystem";
export type { AgentAction, AgentDebateReport } from "./engines/multiAgentSystem";

// 4. Scientific Reasoning Engine
export { ScientificReasoningEngine } from "./engines/scientificReasoningEngine";
export type { ScientificHypothesis, ScienceEvaluation } from "./engines/scientificReasoningEngine";

// 5. World Model Engine
export { WorldModelEngine } from "./engines/worldModelEngine";
export type { SimulationStep, SimulationReport } from "./engines/worldModelEngine";

// 6. Mamba Hybrid Engine
export { MambaHybridEngine } from "./engines/mambaHybridEngine";
export type { MambaTelemetry } from "./engines/mambaHybridEngine";

// 7. Sparse Computation Engine
export { SparseComputationEngine } from "./engines/sparseComputationEngine";
export type { SparsityDirectives } from "./engines/sparseComputationEngine";

// 8. Mixture of Experts (MoE) Engine
export { MixtureOfExpertsEngine } from "./engines/mixtureOfExpertsEngine";
export type { ExpertGateReport } from "./engines/mixtureOfExpertsEngine";

// 9. Model Compression Engine
export { ModelCompressionEngine } from "./engines/modelCompressionEngine";
export type { CompressionDirectives } from "./engines/modelCompressionEngine";

// 10. Speculative Decoding Engine
export { SpeculativeDecodingEngine } from "./engines/speculativeDecodingEngine";
export type { SpeculativeDecodingReport } from "./engines/speculativeDecodingEngine";

// 11. Self-Improvement Engine
export { SelfImprovementEngine } from "./engines/selfImprovementEngine";
export type {
  ExceptionLog,
  OptimizationPatch,
  SelfImprovementReport,
} from "./engines/selfImprovementEngine";

// 12. Autonomous Research System
export { AutonomousResearchSystem } from "./engines/autonomousResearchSystem";
export type { LiteraturePaper, ResearchGapReport } from "./engines/autonomousResearchSystem";

// 13. Active Learning Engine
export { ActiveLearningEngine } from "./engines/activeLearningEngine";
export type { TrainingPriorityItem } from "./engines/activeLearningEngine";

// 14. Curriculum Learning Engine
export { CurriculumLearningEngine } from "./engines/curriculumLearningEngine";
export type { CurriculumStep, CurriculumReport } from "./engines/curriculumLearningEngine";

// 15. Intelligence Per Compute Optimizer
export { IntelligencePerComputeOptimizer } from "./engines/intelligencePerComputeOptimizer";
export type { OptimizationMetrics } from "./engines/intelligencePerComputeOptimizer";
