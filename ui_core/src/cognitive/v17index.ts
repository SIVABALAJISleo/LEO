// Export V17 Domain Dominance Substrate Modules
// Classes as values; interfaces/types with `export type` for Vite 8 (rolldown) compliance.
export { EnterpriseCommandCenter } from "../enterprise/enterpriseCommandCenter";
export type { KnowledgeGraphNode, KnowledgeGraphEdge, EnterpriseSearchQueryReport } from "../enterprise/enterpriseCommandCenter";

export { EvaluationUniverseV17 } from "../evaluation_universe/tasks";
export type { V17DomainBenchmark, UniverseV17Report } from "../evaluation_universe/tasks";

export { RagGovernorV3 } from "../rag/ragGovernorV3";
export type { RagChunk, RagPipelineReport } from "../rag/ragGovernorV3";

export { SearchGovernorV3 } from "../search/searchGovernorV3";
export type { SearchResult, UniversalSearchReport } from "../search/searchGovernorV3";

export { CodeGovernor } from "../code/codeGovernor";
export type { VulnerabilityReport, CodePipelineResult } from "../code/codeGovernor";

export { WorkflowGovernor } from "../workflow/workflowGovernor";
export type { WorkflowActionStep, WorkflowExecutionReport } from "../workflow/workflowGovernor";

export { EdgeGovernor } from "../edge/edgeGovernor";
export type { EdgeCompilationMetrics, EdgeInferenceReport } from "../edge/edgeGovernor";

export { InspectionGovernor } from "../inspection/inspectionGovernor";
export type { DefectItem, InspectionPipelineReport } from "../inspection/inspectionGovernor";

export { CameraGovernor } from "../camera/cameraGovernor";
export type { CameraEvent, CameraAnalyticsReport } from "../camera/cameraGovernor";

export { RoboticsGovernor } from "../robotics/roboticsGovernor";
export type { RobotState, RouteNavigationReport } from "../robotics/roboticsGovernor";

export { AutonomyGovernor } from "../autonomy/autonomyGovernor";
export type { AutonomyScenarioProjection, AutonomousDecisionReport } from "../autonomy/autonomyGovernor";

export { RealityFeedbackNetwork } from "../learning/realityNetwork";
export type { RealityDecisionLog, RealityCalibrationSummary } from "../learning/realityNetwork";

export { IntelligenceGovernor } from "../intelligence/intelligenceGovernor";
export type { CritiqueRound, IntelligenceQualityReport } from "../intelligence/intelligenceGovernor";

// Backward compatible utilities
export { KnowledgeImmuneSystem } from "../knowledge/knowledgeImmuneSystem";
export type { KnowledgeCrystal } from "../knowledge/knowledgeImmuneSystem";

export { MemoryImmuneSystem } from "../memory/memoryImmuneSystem";
export type { MemoryBlock, ImmuneAuditReport } from "../memory/memoryImmuneSystem";
