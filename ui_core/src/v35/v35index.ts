// LEO AI V35 — Functional Parity & Compute Avoidance Barrel Index Exports
// Consolidates and exposes all V35 engine modules.

// === 1. Compute Avoidance Engine ===
export { ComputeAvoidanceEngine } from "./engines/computeAvoidanceEngine";
export type {
  AvoidanceLevel,
  AvoidanceResolution,
  AvoidanceTelemetry,
} from "./engines/computeAvoidanceEngine";

// === 2. Crystal Memory V2 ===
export { CrystalMemoryV2 } from "./engines/crystalMemoryV2";
export type { ConceptNode, CrystalMemoryReport } from "./engines/crystalMemoryV2";

// === 3. Retrieval-First Intelligence ===
export { RetrievalFirstIntelligence } from "./engines/retrievalFirstIntelligence";
export type {
  OutputCategory,
  RetrievedEvidence,
  RetrievalFirstOutput,
} from "./engines/retrievalFirstIntelligence";

// === 4. Dynamic Expert Routing ===
export { DynamicExpertRouting } from "./engines/dynamicExpertRouting";
export type { V35Expert, ExpertProfile, RoutingOutput } from "./engines/dynamicExpertRouting";

// === 5. Scientific Reasoning Layer ===
export { ScientificReasoningLayer } from "./engines/scientificReasoningLayer";
export type {
  ScientificHypothesis,
  ScienceEvaluationResult,
} from "./engines/scientificReasoningLayer";

// === 6. Continuous Knowledge Refresh ===
export { ContinuousKnowledgeRefresh } from "./engines/continuousKnowledgeRefresh";
export type {
  IngestionState,
  KnowledgeNode,
  RefreshReport,
} from "./engines/continuousKnowledgeRefresh";

// === 7. Real User Feedback Learning ===
export { RealUserFeedbackLearning } from "./engines/realUserFeedbackLearning";
export type {
  UserFeedbackRecord,
  FeedbackIntelligenceStats,
} from "./engines/realUserFeedbackLearning";

// === 8. Hardware-Aware Runtime ===
export { HardwareAwareRuntime } from "./engines/hardwareAwareRuntime";
export type {
  ExecutionDevice,
  HardwareSpecification,
  RuntimeOptimization,
} from "./engines/hardwareAwareRuntime";

// === 9. Unknown Knowledge Management ===
export { UnknownKnowledgeManagement } from "./engines/unknownKnowledgeManagement";
export type {
  VerificationTrigger,
  UncertaintyResolution,
} from "./engines/unknownKnowledgeManagement";
