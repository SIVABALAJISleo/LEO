// LEO AI V38 — Consolidated Subsystems Exporter Barrel Index
// Exposes all 13 core engines.

// 1. Intelligence Per Compute Engine
export { IntelligencePerComputeEngine } from "./engines/intelligencePerComputeEngine";
export type { MoERoutingReport } from "./engines/intelligencePerComputeEngine";

// 2. GraphRAG Engine
export { GraphRagEngine } from "./engines/graphRagEngine";
export type { GraphEntity, GraphRelation, GraphRagReport } from "./engines/graphRagEngine";

// 3. Long Term Memory Engine
export { LongTermMemoryEngine } from "./engines/longTermMemoryEngine";
export type { MemoryCell } from "./engines/longTermMemoryEngine";

// 4. Scientific Reasoning Engine
export { ScientificReasoningEngine } from "./engines/scientificReasoningEngine";
export type {
  DebateParticipant,
  VerificationStep,
  ScientificReport,
} from "./engines/scientificReasoningEngine";

// 5. Causal Reasoning Engine
export { CausalReasoningEngine } from "./engines/causalReasoningEngine";
export type {
  CausalVariable,
  CausalIntervention,
  CausalReport,
} from "./engines/causalReasoningEngine";

// 6. Self Improvement Engine
export { SelfImprovementEngine } from "./engines/selfImprovementEngine";
export type {
  FailureLog,
  ImprovementPlan,
  SelfImprovementReport,
} from "./engines/selfImprovementEngine";

// 7. Reality Adaptation Engine
export { RealityAdaptationEngine } from "./engines/realityAdaptationEngine";
export type { SensorSignal, AdaptationReport } from "./engines/realityAdaptationEngine";

// 8. Discovery Engine
export { DiscoveryEngine } from "./engines/discoveryEngine";
export type { ResearchHypothesis, DiscoveryReport } from "./engines/discoveryEngine";

// 9. Hardware Efficiency Engine
export { HardwareEfficiencyEngine } from "./engines/hardwareEfficiencyEngine";
export type { EfficiencyDirectives } from "./engines/hardwareEfficiencyEngine";

// 10. World Model Engine
export { WorldModelEngine } from "./engines/worldModelEngine";
export type { StateForecast, ScenarioReport } from "./engines/worldModelEngine";

// 11. Frontier Training Efficiency
export { FrontierTrainingEfficiency } from "./engines/frontierTrainingEfficiency";
export type { TrainingDirectives } from "./engines/frontierTrainingEfficiency";

// 12. Autonomous Intelligence
export { AutonomousIntelligence } from "./engines/autonomousIntelligence";
export type { SubTask, AutonomousPlanReport } from "./engines/autonomousIntelligence";

// 13. Safety and Verification
export { SafetyVerificationEngine } from "./engines/safetyVerificationEngine";
export type { SourceCitationRating, VerificationAudit } from "./engines/safetyVerificationEngine";
