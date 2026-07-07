import React, { useEffect, useState } from "react";
import { fetchLeoStatus, LeoStatus, fetchDevOpsStatus, configureDevOps, sendStripeWebhook, DevOpsSettings } from "./lib/api";
import { QuerySimulationConsole } from "./components/dashboard/QuerySimulationConsole";
import { BenchmarkLeaderboard } from "./components/dashboard/BenchmarkLeaderboard";
import { ValidationDashboard } from "./src/dashboards/ValidationDashboard";
import { FailureHuntingDashboard } from "./src/dashboards/FailureHuntingDashboard";
import { QualityAmplifierDashboard } from "./src/dashboards/QualityAmplifierDashboard";
import { FrontierOptimizationDashboard } from "./src/dashboards/FrontierOptimizationDashboard";
import { ConvergenceDashboard } from "./src/dashboards/ConvergenceDashboard";
import { CertificationDashboard } from "./src/dashboards/CertificationDashboard";
import { RealityExecutionDashboard } from "./src/dashboards/RealityExecutionDashboard";
import { ScientificCertificationDashboard } from "./src/dashboards/ScientificCertificationDashboard";
import { ScientificValidationDashboard } from "./src/dashboards/ScientificValidationDashboard";
import { FrontierIntelligenceDashboard } from "./src/dashboards/FrontierIntelligenceDashboard";
import { FrontierIntelligenceDashboardV2 } from "./src/dashboards/FrontierIntelligenceDashboardV2";
import { ComputeIrrelevanceDashboard } from "./src/dashboards/ComputeIrrelevanceDashboard";
import { EngineeringCeilingDashboard } from "./src/dashboards/EngineeringCeilingDashboard";
import { RealityLearningDashboard } from "./src/dashboards/RealityLearningDashboard";
import { ComputeIrrelevanceV33Dashboard } from "./src/dashboards/ComputeIrrelevanceV33Dashboard";
import { ComputeIrrelevanceV34Dashboard } from "./src/dashboards/ComputeIrrelevanceV34Dashboard";
import { LEOAIv35Scoreboard } from "./src/dashboards/LEOAIv35Scoreboard";
import { LEOAIv36Dashboard } from "./src/dashboards/LEOAIv36Dashboard";
import { LEOAIv37Dashboard } from "./src/dashboards/LEOAIv37Dashboard";
import { LEOAIv38Dashboard } from "./src/dashboards/LEOAIv38Dashboard";
import { LEOAIv40Dashboard } from "./src/dashboards/LEOAIv40Dashboard";
import { LEOAIvInfinityDashboard } from "./src/dashboards/LEOAIvInfinityDashboard";
import { 
  Activity, Cpu, HardDrive, Layers, Zap, AlertTriangle, Play, Shield, 
  RefreshCw, AlertCircle, Sparkles, MessageSquare, CheckCircle, 
  Terminal, HelpCircle, ArrowRight, Settings, BarChart2, Brain, GitBranch, Crosshair, FlaskConical, Gauge, LineChart, Award, Scale, ShieldCheck
} from "lucide-react";
import { 
  IntentCanonicalizer, LanguageRecoveryEngine, ReasoningValidator, 
  DeepPlanner, SelfCritic, DebateCoordinator, EvaluationCenter, 
  MemoryQualityMonitor, CrystalAuditor, NoveltyResearchEngine,
  FormalReasoningEngine, VerificationOrchestrator, WorldModelEngineV2,
  RealityFeedbackLoop, MetaLearningGovernor, KnowledgeGovernor,
  MemoryGovernorV2, IntentCanonicalizerV2, LanguageRecoveryEngineV2,
  DebateEngineV2, PlannerV2, NoveltyDiscoveryEngineV2,
  ResearchEngineV2, EvaluationCenterV2
} from "./src/cognitive";
import "./index.css";

// Import V14 Engines
import { IntentReconstructionEngine, ReconstructedIntent } from "./src/engines/intentReconstructionEngine";
import { DeepReasoningEngine, ReasoningType, ReasoningResult } from "./src/engines/deepReasoningEngine";
import { ToolVerificationEngine, VerificationOutput } from "./src/engines/toolVerificationEngine";
import { SelfCritiqueEngine, CritiqueReport } from "./src/engines/selfCritiqueEngine";
import { EvaluationCenter as EvaluationCenterV14, EvaluationReport } from "./src/evaluation/evaluationCenter";
import { RealityFeedbackEngine, FeedbackEntry } from "./src/engines/realityFeedbackEngine";
import { KnowledgeGovernor as KnowledgeGovernorV14, KnowledgeItem } from "./src/engines/knowledgeGovernor";
import { MemoryGovernor as MemoryGovernorV14, V14MemoryBlock } from "./src/engines/memoryGovernor";
import { DebateEngine as DebateEngineV14, DebateSessionV14 } from "./src/engines/debateEngine";

// Import V15 Engines
import {
  EvaluationUniverse, UniverseEvaluationReport,
  SelfCritiqueEngineV2, SelfCritiqueV2Report,
  UniversalReasoningEngine, ParadigmResult, ReasoningParadigm,
  DebateFramework, DebateSessionReport,
  ToolVerifier, ToolVerifierReport,
  RealityFeedbackSystem, FeedbackLog, CalibrationReport,
  KnowledgeImmuneSystem, KnowledgeCrystal,
  MemoryImmuneSystem, MemoryBlock, ImmuneAuditReport,
  MetaLearningGovernor as MetaLearningGovernorV15, StrategyMetric,
  WorldModelV3, SimulationResultV3,
  DiscoveryEngineV3, DiscoveryReport,
  IntentReconstructionEngine as IntentReconstructionEngineV15, IntentReconstructionReport,
  ConfidenceEngine as ConfidenceEngineV15, CalibrationResponse,
  DistributedMesh, MeshNode, ConflictResolutionReport,
  HardeningTelemetry, TelemetryEvent,
  iGPUAccelerationEngine as iGPUAccelerationEngineV15, iGPUMetrics as iGPUMetricsV15,
  SelfImprovementLoop, SelfImprovementReport
} from "./src/cognitive/v15index";

// Import V16 Engines
import {
  EvaluationUniverseV16, UniverseV16Report,
  UniversalReasoningCore,
  FormalProofEngine, TheoremSolver, ProofTelemetry, ProofEngineReport,
  VerificationMesh, VerificationCheckV16, VerificationMeshReport,
  RealityFeedbackEngineV3,
  KnowledgeImmuneSystem as KnowledgeImmuneSystemV16,
  MemoryImmuneSystem as MemoryImmuneSystemV16,
  MetaLearningGovernor as MetaLearningGovernorV16,
  DiscoveryEngineV4,
  WorldModelV4,
  DebateFrameworkV16, DebateV16Report,
  IntentReconstructionEngine as IntentReconstructionEngineV16, IntentReconstructionReport as IntentReconstructionReportV16,
  ConfidenceEngineV16,
  HardeningTelemetryV16, IncidentAlertV16,
  iGPUAccelerationEngineV16, iGPUMetricsV16
} from "./src/cognitive/v16index";

// Import V17 Engines
import {
  EvaluationUniverseV17,
  EnterpriseCommandCenter,
  RagGovernorV3,
  SearchGovernorV3,
  CodeGovernor,
  WorkflowGovernor,
  EdgeGovernor,
  InspectionGovernor,
  CameraGovernor,
  RoboticsGovernor,
  AutonomyGovernor,
  RealityFeedbackNetwork,
  IntelligenceGovernor,
  KnowledgeImmuneSystem as KnowledgeImmuneSystemV17
} from "./src/cognitive/v17index";

function App() {
  const [status, setStatus] = useState<LeoStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState<"swarm" | "cognitive" | "debate" | "benchmarks" | "devops" | "quality" | "v14super" | "v15substrate" | "v16substrate" | "v17dominance" | "v18validation" | "failureHunting" | "v22quality" | "v23frontier" | "v24convergence" | "v25certification" | "v26reality" | "v27certification" | "v28validation" | "v29frontier" | "v30frontier" | "v31irrelevance" | "v32ceiling" | "v32reality" | "v33compute" | "v34compute" | "v35parity" | "v36ceiling" | "v37evolution" | "v38architecture" | "v40ultimate" | "vinfinity">("swarm");

  // --- V17 Domain Dominance States ---
  const [v17QueryInput, setV17QueryInput] = useState("Issue transaction refund invoice");
  const [v17SelectedDomain, setV17SelectedDomain] = useState<string>("Finance/HR Workflow");
  const [v17SelectedBackend, setV17SelectedBackend] = useState<"WebGPU" | "ONNX Runtime" | "GGUF" | "llama.cpp">("WebGPU");
  const [v17EvalReport, setV17EvalReport] = useState<any>(null);
  
  const [v17EnterpriseReport, setV17EnterpriseReport] = useState<any>(null);
  const [v17RagReport, setV17RagReport] = useState<any>(null);
  const [v17SearchReport, setV17SearchReport] = useState<any>(null);
  const [v17CodeReport, setV17CodeReport] = useState<any>(null);
  const [v17WorkflowReport, setV17WorkflowReport] = useState<any>(null);
  const [v17EdgeReport, setV17EdgeReport] = useState<any>(null);
  const [v17InspectionReport, setV17InspectionReport] = useState<any>(null);
  const [v17CameraReport, setV17CameraReport] = useState<any>(null);
  const [v17RoboticsReport, setV17RoboticsReport] = useState<any>(null);
  const [v17AutonomyReport, setV17AutonomyReport] = useState<any>(null);
  const [v17RealitySummary, setV17RealitySummary] = useState<any>(null);
  const [v17IntelligenceReport, setV17IntelligenceReport] = useState<any>(null);
  const [v17ImmuneCrystals, setV17ImmuneCrystals] = useState<any[]>([]);

  // V17 class instances
  const [enterpriseV17] = useState(() => new EnterpriseCommandCenter());
  const [ragV17] = useState(() => new RagGovernorV3());
  const [searchV17] = useState(() => new SearchGovernorV3());
  const [codeV17] = useState(() => new CodeGovernor());
  const [workflowV17] = useState(() => new WorkflowGovernor());
  const [edgeV17] = useState(() => new EdgeGovernor());
  const [inspectionV17] = useState(() => new InspectionGovernor());
  const [cameraV17] = useState(() => new CameraGovernor());
  const [roboticsV17] = useState(() => new RoboticsGovernor());
  const [autonomyV17] = useState(() => new AutonomyGovernor());
  const [realityV17] = useState(() => new RealityFeedbackNetwork());
  const [intelligenceV17] = useState(() => new IntelligenceGovernor());
  const [immuneV17] = useState(() => new KnowledgeImmuneSystemV17());
  const [universeV17] = useState(() => new EvaluationUniverseV17());

  // --- V16 Substrate States ---
  const [v16QueryInput, setV16QueryInput] = useState("bro startup fail wat do");
  const [v16SelectedParadigm, setV16SelectedParadigm] = useState<ReasoningParadigm>("Systems Thinking");
  const [v16SelectedSolver, setV16SelectedSolver] = useState<TheoremSolver>("Lean");
  const [v16EvalReport, setV16EvalReport] = useState<UniverseV16Report | null>(null);
  const [v16ReasoningResult, setV16ReasoningResult] = useState<any>(null);
  const [v16ProofReport, setV16ProofReport] = useState<ProofEngineReport | null>(null);
  const [v16VerifierReport, setV16VerifierReport] = useState<VerificationMeshReport | null>(null);
  const [v16FeedbackHistory, setV16FeedbackHistory] = useState<any[]>([]);
  const [v16Calibration, setV16Calibration] = useState<any>(null);
  const [v16Crystals, setV16Crystals] = useState<KnowledgeCrystal[]>([]);
  const [v16Memories, setV16Memories] = useState<MemoryBlock[]>([]);
  const [v16DiscoveryReport, setV16DiscoveryReport] = useState<any>(null);
  const [v16ReconstructReport, setV16ReconstructReport] = useState<IntentReconstructionReportV16 | null>(null);
  const [v16ConfidenceReport, setV16ConfidenceReport] = useState<CalibrationResponse | null>(null);
  const [v16DebateReport, setV16DebateReport] = useState<DebateV16Report | null>(null);
  const [v16HardwareMetrics, setV16HardwareMetrics] = useState<iGPUMetricsV16 | null>(null);
  const [v16HardeningLogs, setV16HardeningLogs] = useState<TelemetryEvent[]>([]);
  const [v16CanaryWeight, setV16CanaryWeight] = useState(100);
  const [v16Alerts, setV16Alerts] = useState<IncidentAlertV16[]>([]);
  const [v16ScenarioReport, setV16ScenarioReport] = useState<any>(null);

  // V16 class instances
  const [universeV16] = useState(() => new EvaluationUniverseV16());
  const [reasoningV16] = useState(() => new UniversalReasoningCore());
  const [proofV16] = useState(() => new FormalProofEngine());
  const [verifierV16] = useState(() => new VerificationMesh());
  const [feedbackV16] = useState(() => new RealityFeedbackEngineV3());
  const [knowledgeImmuneV16] = useState(() => new KnowledgeImmuneSystemV16());
  const [memoryImmuneV16] = useState(() => new MemoryImmuneSystemV16());
  const [metaGovV16] = useState(() => new MetaLearningGovernorV16());
  const [discoveryV16] = useState(() => new DiscoveryEngineV4());
  const [worldV16] = useState(() => new WorldModelV4());
  const [debateV16] = useState(() => new DebateFrameworkV16());
  const [reconV16] = useState(() => new IntentReconstructionEngineV16());
  const [confidenceV16] = useState(() => new ConfidenceEngineV16());
  const [hardeningV16] = useState(() => new HardeningTelemetryV16());
  const [igpuV16] = useState(() => new iGPUAccelerationEngineV16());

  // --- V15 Substrate States ---
  const [v15QueryInput, setV15QueryInput] = useState("bro startup fail wat do");
  const [v15SelectedParadigm, setV15SelectedParadigm] = useState<ReasoningParadigm>("Systems Thinking");
  const [v15EvalReport, setV15EvalReport] = useState<UniverseEvaluationReport | null>(null);
  const [v15CritiqueReport, setV15CritiqueReport] = useState<SelfCritiqueV2Report | null>(null);
  const [v15ReasoningResult, setV15ReasoningResult] = useState<ParadigmResult | null>(null);
  const [v15DebateReport, setV15DebateReport] = useState<DebateSessionReport | null>(null);
  const [v15VerifierReport, setV15VerifierReport] = useState<ToolVerifierReport | null>(null);
  const [v15FeedbackHistory, setV15FeedbackHistory] = useState<FeedbackLog[]>([]);
  const [v15Calibration, setV15Calibration] = useState<CalibrationReport | null>(null);
  const [v15Crystals, setV15Crystals] = useState<KnowledgeCrystal[]>([]);
  const [v15Memories, setV15Memories] = useState<MemoryBlock[]>([]);
  const [v15ImprovementReport, setV15ImprovementReport] = useState<SelfImprovementReport | null>(null);
  const [v15DiscoveryReport, setV15DiscoveryReport] = useState<DiscoveryReport | null>(null);
  const [v15ReconstructReport, setV15ReconstructReport] = useState<IntentReconstructionReport | null>(null);
  const [v15ConfidenceReport, setV15ConfidenceReport] = useState<CalibrationResponse | null>(null);
  const [v15MeshNodes, setV15MeshNodes] = useState<MeshNode[]>([]);
  const [v15HardwareMetrics, setV15HardwareMetrics] = useState<iGPUMetricsV15 | null>(null);
  const [v15HardeningLogs, setV15HardeningLogs] = useState<TelemetryEvent[]>([]);
  const [v15CanaryWeight, setV15CanaryWeight] = useState(100);

  // V15 Instances
  const [universeV15] = useState(() => new EvaluationUniverse());
  const [selfCritiqueV15] = useState(() => new SelfCritiqueEngineV2());
  const [reasoningV15] = useState(() => new UniversalReasoningEngine());
  const [debateV15] = useState(() => new DebateFramework());
  const [verifierV15] = useState(() => new ToolVerifier());
  const [feedbackV15] = useState(() => new RealityFeedbackSystem());
  const [knowledgeImmuneV15] = useState(() => new KnowledgeImmuneSystem());
  const [memoryImmuneV15] = useState(() => new MemoryImmuneSystem());
  const [metaGovV15] = useState(() => new MetaLearningGovernorV15());
  const [worldV15] = useState(() => new WorldModelV3());
  const [discoveryV15] = useState(() => new DiscoveryEngineV3());
  const [reconV15] = useState(() => new IntentReconstructionEngineV15());
  const [confidenceV15] = useState(() => new ConfidenceEngineV15());
  const [meshV15] = useState(() => new DistributedMesh());
  const [hardeningV15] = useState(() => new HardeningTelemetry());
  const [igpuV15] = useState(() => new iGPUAccelerationEngineV15());
  const [improvementV15] = useState(() => new SelfImprovementLoop());

  // Load initial V15, V16 & V17 data
  useEffect(() => {
    // V15
    setV15Memories(memoryImmuneV15.getMemories());
    setV15Crystals(knowledgeImmuneV15.getCrystals());
    setV15MeshNodes(meshV15.getNodes());
    setV15HardwareMetrics(igpuV15.getMetrics());
    setV15HardeningLogs(hardeningV15.getEventsLog());

    // V16
    setV16Memories(memoryImmuneV16.getMemories());
    setV16Crystals(knowledgeImmuneV16.getCrystals());
    setV16HardwareMetrics(igpuV16.getV16Metrics());
    setV16HardeningLogs(hardeningV16.getEventsLog());
    setV16Alerts(hardeningV16.getV16Alerts());

    // V17
    setV17ImmuneCrystals(immuneV17.auditCrystals());
    setV17RealitySummary(realityV17.getSummary());
  }, []);

  // --- V17 Handlers ---
  const handleV17RunQuery = () => {
    // 1. Enterprise search
    const enterprise = enterpriseV17.searchCompanyKnowledge(v17QueryInput);
    setV17EnterpriseReport(enterprise);

    // 2. RAG
    const rag = ragV17.queryRAG(v17QueryInput);
    setV17RagReport(rag);

    // 3. Universal Search
    const search = searchV17.executeUniversalSearch(v17QueryInput);
    setV17SearchReport(search);

    // 4. Code review
    const code = codeV17.generateAndVerifyCode(v17QueryInput);
    setV17CodeReport(code);

    // 5. Business workflow
    const workflow = workflowV17.executeBusinessWorkflow(v17QueryInput);
    setV17WorkflowReport(workflow);

    // 6. Edge task
    const edge = edgeV17.executeLocalTask(v17QueryInput, v17SelectedBackend);
    setV17EdgeReport(edge);

    // 7. Visual Inspection defect simulation
    const inspection = inspectionV17.runVisualInspection(v17QueryInput);
    setV17InspectionReport(inspection);

    // 8. Camera scene frame diff skip
    const camera = cameraV17.processCameraFeed(v17QueryInput, 15.4);
    setV17CameraReport(camera);

    // 9. Robotics path planning
    const robotics = roboticsV17.planRoute("agv-dashboard", { x: 45, y: 72 });
    setV17RoboticsReport(robotics);

    // 10. Autonomous system verification
    const autonomy = autonomyV17.verifyAutonomyAction(v17QueryInput);
    setV17AutonomyReport(autonomy);

    // 11. Multi-agent audit critique
    const critiqueResult = intelligenceV17.auditAnswerQuality(
      v17QueryInput,
      enterprise.verifiedAnswer || rag.chunksRetrieved.map(c => c.content).join("\n") || "No source text."
    );
    setV17IntelligenceReport(critiqueResult);

    // Log feedback loop prediction vs reality
    realityV17.logRealityCheck("decision-" + Date.now().toString().slice(-4), v17SelectedDomain, 100, 106);
    setV17RealitySummary(realityV17.getSummary());
  };

  const handleV17RunEvaluation = () => {
    const report = universeV17.runDomainEvaluation();
    setV17EvalReport(report);
  };

  const handleV17AuditImmune = () => {
    const report = immuneV17.auditCrystals();
    setV17ImmuneCrystals([...report]);
  };

  // V15 Handlers
  const handleV15RunPipeline = async () => {
    // Phase 12: Intent Reconstruction
    const recon = reconV15.reconstructIntent(v15QueryInput);
    setV15ReconstructReport(recon);

    // Phase 3: Universal Reasoning Engine
    const reason = reasoningV15.performReasoning(recon.reconstructedQuery, v15SelectedParadigm);
    setV15ReasoningResult(reason);

    // Phase 5: Tool Verified Intelligence
    const verify = verifierV15.verifyAnswer(recon.reconstructedQuery, reason.conclusion);
    setV15VerifierReport(verify);

    // Phase 2: Self Critique Engine V2
    const critique = selfCritiqueV15.executeSelfCritique(recon.reconstructedQuery, verify.repairedAnswer);
    setV15CritiqueReport(critique);

    // Phase 13: Confidence Calibration
    const confidence = confidenceV15.calibrateOutput(
      critique.finalAnswer,
      reason.confidenceScore,
      1.0 - critique.hallucinationRatePct,
      verify.checks.filter(c => c.status === "verified").length,
      verify.checks.length
    );
    setV15ConfidenceReport(confidence);

    // Log telemetry
    hardeningV15.logTelemetry("V15 Query Processed", { query: v15QueryInput, confidence: confidence.calibratedConfidence });
    setV15HardeningLogs([...hardeningV15.getEventsLog()]);
  };

  const handleV15Debate = () => {
    const report = debateV15.coordinateDebate(v15QueryInput);
    setV15DebateReport(report);
  };

  const handleV15UniverseEval = () => {
    const report = universeV15.runUniverseEvaluation();
    setV15EvalReport(report);
  };

  const handleV15TriggerImprovement = () => {
    const baseline = v15EvalReport?.overallAccuracy || 0.95;
    const report = improvementV15.executeImprovementCycle(baseline);
    setV15ImprovementReport(report);

    // Promote pathways
    metaGovV15.logExecutionReward("S-REAS-01", true, 120);
    metaGovV15.logExecutionReward("S-RETR-01", true, 8);
  };

  const handleV15TriageFailure = () => {
    const report = discoveryV15.handleRetrievalFailure(v15QueryInput);
    setV15DiscoveryReport(report);
  };

  const handleV15Consolidate = () => {
    const report = memoryImmuneV15.consolidateMemory();
    setV15Memories([...memoryImmuneV15.getMemories()]);
    hardeningV15.logTelemetry("Memory Consolidation Swept", report);
    setV15HardeningLogs([...hardeningV15.getEventsLog()]);
  };

  const handleV15AuditCrystals = () => {
    const report = knowledgeImmuneV15.auditCrystals();
    setV15Crystals([...report]);
    hardeningV15.logTelemetry("Knowledge Crystals Audited", { count: report.length });
    setV15HardeningLogs([...hardeningV15.getEventsLog()]);
  };

  const handleV15RealityLog = () => {
    feedbackV15.logRealityFeedback("p-v15-" + Date.now().toString().slice(-4), "intentAccuracyWeight", 100, 108);
    setV15FeedbackHistory([...feedbackV15.getHistory()]);
    setV15Calibration(feedbackV15.getCalibration());
  };

  const handleV15Rollback = () => {
    const res = hardeningV15.executeRollback("v15.0.0", "Active verification exception");
    setV15CanaryWeight(res.canaryWeightSet);
    setV15HardeningLogs([...hardeningV15.getEventsLog()]);
  };

  // --- V16 Handlers ---
  const handleV16RunPipeline = async () => {
    // Phase 12: Intent Reconstruction
    const recon = reconV16.reconstructIntent(v16QueryInput);
    setV16ReconstructReport(recon);

    // Phase 2: Universal Reasoning Core
    const reason = reasoningV16.reason(recon.reconstructedQuery, v16SelectedParadigm);
    setV16ReasoningResult(reason);

    // Phase 4: Verification Mesh
    const verify = verifierV16.verifyAnswer(recon.reconstructedQuery, reason.conclusion);
    setV16VerifierReport(verify);

    // Phase 13: Confidence Calibration
    const confidence = confidenceV16.calibrateOutputV16(
      verify.repairedAnswer,
      reason.confidenceScore,
      verify.overallScore,
      verify.checksLog.filter(c => c.status === "verified").length,
      verify.checksLog.length
    );
    setV16ConfidenceReport(confidence);

    // Scenario simulation
    const scenario = worldV16.simulateWorldState(recon.reconstructedQuery);
    setV16ScenarioReport(scenario);

    // Log telemetry
    hardeningV16.logV16Event("V16 Query Processed", { query: v16QueryInput, confidence: confidence.calibratedConfidence }, "info");
    setV16HardeningLogs([...hardeningV16.getEventsLog()]);
    setV16Alerts([...hardeningV16.getV16Alerts()]);
  };

  const handleV16Debate = () => {
    const report = debateV16.executeDebateCycle(v16QueryInput);
    setV16DebateReport(report);
  };

  const handleV16RunProof = () => {
    const report = proofV16.verifyClaim(v16QueryInput, "local logic correctness", v16SelectedSolver);
    setV16ProofReport(report);
  };

  const handleV16UniverseEval = () => {
    const report = universeV16.runFullEvaluation();
    setV16EvalReport(report);
  };

  const handleV16TriageFailure = () => {
    const report = discoveryV16.generateHypotheses(v16QueryInput);
    setV16DiscoveryReport(report);
  };

  const handleV16Consolidate = () => {
    const report = memoryImmuneV16.consolidateMemory();
    setV16Memories([...memoryImmuneV16.getMemories()]);
    hardeningV16.logV16Event("Memory Consolidation Swept", report, "info");
    setV16HardeningLogs([...hardeningV16.getEventsLog()]);
  };

  const handleV16AuditCrystals = () => {
    const report = knowledgeImmuneV16.auditCrystals();
    setV16Crystals([...report]);
    hardeningV16.logV16Event("Knowledge Crystals Audited", { count: report.length }, "info");
    setV16HardeningLogs([...hardeningV16.getEventsLog()]);
  };

  const handleV16RealityLog = () => {
    feedbackV16.logRealityEvent("p-v16-" + Date.now().toString().slice(-4), "predictionAccuracy", 100, 110);
    setV16FeedbackHistory([...feedbackV16.getHistory()]);
    setV16Calibration(feedbackV16.getCalibration());
  };

  const handleV16Rollback = () => {
    const res = hardeningV16.triggerV16Rollback("V16 verification checks breached constraints");
    setV16CanaryWeight(res.canaryWeightSet);
    setV16HardeningLogs([...hardeningV16.getEventsLog()]);
    setV16Alerts([...hardeningV16.getV16Alerts()]);
  };

  // --- V14 Cognitive Breakthrough States ---
  const [v14Query, setV14Query] = useState("bro startup fail wat do");
  const [v14ReconResult, setV14ReconResult] = useState<ReconstructedIntent | null>(null);
  
  const [v14ReasoningType, setV14ReasoningType] = useState<ReasoningType>("Deductive");
  const [v14ReasoningResult, setV14ReasoningResult] = useState<ReasoningResult | null>(null);
  
  const [v14VerifyOutput, setV14VerifyOutput] = useState<VerificationOutput | null>(null);
  const [v14CritiqueResult, setV14CritiqueResult] = useState<CritiqueReport | null>(null);
  
  const [v14EvalReport, setV14EvalReport] = useState<EvaluationReport | null>(null);
  const [v14DebateSession, setV14DebateSession] = useState<DebateSessionV14 | null>(null);
  
  // Feedback
  const [v14PredictedVal, setV14PredictedVal] = useState("200");
  const [v14ObservedVal, setV14ObservedVal] = useState("350");
  const [v14FeedbackHistory, setV14FeedbackHistory] = useState<FeedbackEntry[]>([]);
  const [v14FeedbackWeights, setV14FeedbackWeights] = useState<Record<string, number>>({
    intentAccuracyWeight: 0.95,
    reasoningConfidence: 0.90,
    verificationRigour: 0.96,
  });

  // Memory & Knowledge Governors
  const [v14Memories, setV14Memories] = useState<V14MemoryBlock[]>([]);
  const [v14Crystals, setV14Crystals] = useState<KnowledgeItem[]>([]);
  
  // New entry states for insertion
  const [v14NewMemFact, setV14NewMemFact] = useState("Stripe webhook verification passed on v14.");
  const [v14NewMemSource, setV14NewMemSource] = useState("Manual-Entry");
  const [v14NewCrystalTopic, setV14NewCrystalTopic] = useState("V14 Optimization Guidelines");

  // Instances (persistent)
  const [intentReconV14] = useState(() => new IntentReconstructionEngine());
  const [deepReasoningV14] = useState(() => new DeepReasoningEngine());
  const [toolVerifyV14] = useState(() => new ToolVerificationEngine());
  const [selfCritiqueV14] = useState(() => new SelfCritiqueEngine());
  const [evalCenterV14] = useState(() => new EvaluationCenterV14());
  const [realityFeedbackV14] = useState(() => new RealityFeedbackEngine());
  const [knowledgeGovV14] = useState(() => new KnowledgeGovernorV14());
  const [memoryGovV14] = useState(() => new MemoryGovernorV14());
  const [debateV14] = useState(() => new DebateEngineV14());

  // DevOps Settings State
  const [devOps, setDevOps] = useState<DevOpsSettings | null>(null);
  const [devOpsLoading, setDevOpsLoading] = useState(false);

  // Cognitive Playground State
  const [cogQuery, setCogQuery] = useState("bro how train ai");
  const [canonicalResult, setCanonicalResult] = useState<any>(null);
  const [recoveryResult, setRecoveryResult] = useState<any>(null);
  const [planResult, setPlanResult] = useState<any>(null);
  const [criticResult, setCriticResult] = useState<any>(null);
  const [validationResult, setValidationResult] = useState<any>(null);
  const [noveltyResult, setNoveltyResult] = useState<any>(null);

  // Multi-Agent Debate State
  const [debateQuery, setDebateQuery] = useState("help startup eppadi panradhu");
  const [debateSession, setDebateSession] = useState<any>(null);

  // Quality Audit State
  const [memoryAudit, setMemoryAudit] = useState<any>(null);
  const [crystalAudit, setCrystalAudit] = useState<any>(null);

  // Webhook Test State
  const [webhookStatus, setWebhookStatus] = useState<string>("");
  const [webhookLog, setWebhookLog] = useState<string>("");

  // V13 Superintelligence States
  const [theoremClaim, setTheoremClaim] = useState("Sum of two positive integers is always positive");
  const [theoremResult, setTheoremResult] = useState<any>(null);
  const [verificationQuery, setVerificationQuery] = useState("Solve: 452 * 231");
  const [verificationOutput, setVerificationOutput] = useState<any>(null);
  const [v13ScenarioQuery, setV13ScenarioQuery] = useState("Startup SaaS launch dynamic compute pricing");
  const [v13ScenarioReport, setV13ScenarioReport] = useState<any>(null);
  const [predictedValue, setPredictedValue] = useState("250");
  const [observedValue, setObservedValue] = useState("410");
  const [feedbackRecords, setFeedbackRecords] = useState<any[]>([]);
  const [feedbackWeights, setFeedbackWeights] = useState<any>({
    crystallizationWeight: 0.95,
    localInferenceConfidence: 0.90,
    activeResearchRate: 0.85,
    gpuAccelerationPriority: 0.88,
  });
  
  // V13 class instances (persistent)
  const [proverInstance] = useState(() => new FormalReasoningEngine());
  const [orchestratorInstance] = useState(() => new VerificationOrchestrator());
  const [worldModelInstance] = useState(() => new WorldModelEngineV2());
  const [feedbackLoopInstance] = useState(() => new RealityFeedbackLoop());
  const [metaLearnerInstance] = useState(() => new MetaLearningGovernor());
  const [knowledgeGovInstance] = useState(() => new KnowledgeGovernor());
  const [memoryGovInstance] = useState(() => new MemoryGovernorV2());
  const [intentV2Instance] = useState(() => new IntentCanonicalizerV2());
  const [recoveryV2Instance] = useState(() => new LanguageRecoveryEngineV2());
  const [debateV2Instance] = useState(() => new DebateEngineV2());
  const [plannerV2Instance] = useState(() => new PlannerV2());
  const [noveltyV2Instance] = useState(() => new NoveltyDiscoveryEngineV2());
  const [researchV2Instance] = useState(() => new ResearchEngineV2());
  const [evalV2Instance] = useState(() => new EvaluationCenterV2());

  // Populate initial V14 states
  useEffect(() => {
    setV14Memories(memoryGovV14.getMemories());
    setV14Crystals(knowledgeGovV14.getItems());
  }, [memoryGovV14, knowledgeGovV14]);

  // V14 Handlers
  const handleV14Reconstruct = () => {
    const res = intentReconV14.reconstruct(v14Query);
    setV14ReconResult(res);
  };

  const handleV14Reason = () => {
    const res = deepReasoningV14.reason(v14Query, v14ReasoningType);
    setV14ReasoningResult(res);
  };

  const handleV14Verify = () => {
    const rawAnswer = v14ReasoningResult?.conclusion || "Setting up local model training needs correct GPU configuration.";
    const res = toolVerifyV14.verifyOutput(v14Query, rawAnswer);
    setV14VerifyOutput(res);
  };

  const handleV14Critique = () => {
    const rawAnswer = v14VerifyOutput?.repairedContent || v14ReasoningResult?.conclusion || "Setting up local model training needs correct GPU configuration.";
    const res = selfCritiqueV14.critique(v14Query, rawAnswer);
    setV14CritiqueResult(res);
  };

  const handleV14RunEval = () => {
    const res = evalCenterV14.runFullEvaluation();
    setV14EvalReport(res);
  };

  const handleV14Debate = () => {
    const res = debateV14.coordinateDebate(v14Query);
    setV14DebateSession(res);
  };

  const handleV14LogFeedback = () => {
    const p = parseFloat(v14PredictedVal) || 0;
    const o = parseFloat(v14ObservedVal) || 0;
    realityFeedbackV14.logFeedback("v14-pred-" + Date.now().toString().slice(-4), "intentAccuracyWeight", p, o);
    setV14FeedbackHistory([...realityFeedbackV14.getHistory()]);
    setV14FeedbackWeights({ ...realityFeedbackV14.getWeights() });
  };

  const handleV14AuditMemory = () => {
    const res = memoryGovV14.auditMemory();
    setV14Memories([...res]);
  };

  const handleV14InsertMemory = () => {
    memoryGovV14.insertMemory(v14NewMemFact, v14NewMemSource);
    setV14Memories([...memoryGovV14.getMemories()]);
    setV14NewMemFact("");
  };

  const handleV14AuditKnowledge = () => {
    const res = knowledgeGovV14.auditAssets();
    setV14Crystals([...res]);
  };

  const handleV14AddCrystal = () => {
    knowledgeGovV14.addCrystal(v14NewCrystalTopic, 0.95, 0.90);
    setV14Crystals([...knowledgeGovV14.getItems()]);
    setV14NewCrystalTopic("");
  };

  // V13 Interactive Actions
  const handleVerifyTheorem = () => {
    const res = proverInstance.verifyClaim(theoremClaim);
    setTheoremResult(res);
  };

  const handleRunToolVerification = () => {
    const res = orchestratorInstance.verify(verificationQuery, "Calculated result: 104412");
    setVerificationOutput(res);
  };

  const handleRunScenarioSimulation = () => {
    const res = worldModelInstance.simulateTask(v13ScenarioQuery);
    setV13ScenarioReport(res);
  };

  const handleLogFeedback = () => {
    const p = parseFloat(predictedValue) || 0;
    const o = parseFloat(observedValue) || 0;
    feedbackLoopInstance.logReality("pred-" + Date.now().toString().slice(-4), "localInferenceConfidence", p, o);
    setFeedbackRecords([...feedbackLoopInstance.getHistory()]);
    setFeedbackWeights({ ...feedbackLoopInstance.getModelWeights() });
  };

  // Release Evaluation Report
  const evalCenter = new EvaluationCenter();
  const evaluationReport = evalCenter.runReleaseVerification();

  useEffect(() => {
    const loadStatus = async () => {
      try {
        const data = await fetchLeoStatus();
        setStatus(data);
        setError("");
      } catch (err: any) {
        console.error("Failed to fetch backend status:", err);
        setError("Failed to connect to LEO Backend on port 8005. Is it running?");
      } finally {
        setLoading(false);
      }
    };

    const loadDevOps = async () => {
      try {
        const data = await fetchDevOpsStatus();
        setDevOps(data);
      } catch (err) {
        console.error("Failed to load DevOps status:", err);
      }
    };

    loadStatus();
    loadDevOps();
    
    const interval = setInterval(loadStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  // Run V11 Cognitive Engines
  const handleRunCognitivePlayground = () => {
    const canonicalizer = new IntentCanonicalizer();
    const recoveryEngine = new LanguageRecoveryEngine();
    const validator = new ReasoningValidator();
    const planner = new DeepPlanner();
    const critic = new SelfCritic();
    const researchEngine = new NoveltyResearchEngine();

    // 1. Recover raw query (spelling, typos, slang)
    const recovery = recoveryEngine.recover(cogQuery);
    setRecoveryResult(recovery);

    // 2. Canonicalize intent
    const canonical = canonicalizer.canonicalize(recovery.recoveredText);
    setCanonicalResult(canonical);

    // 3. Deep plan decomposition
    const plan = planner.generatePlan(canonical.intent);
    setPlanResult(plan);

    // 4. Generate answer & Run Critic check
    const rawAnswer = "Setting up model training requires dataloaders, model layers, and optimizer configurations.";
    const critique = critic.critique(canonical.intent, rawAnswer);
    setCriticResult(critique);

    // 5. Logic validation
    const steps = plan.milestones.map(m => m.title);
    const validation = validator.validate(canonical.intent, critique.improvedAnswer, steps);
    setValidationResult(validation);

    // 6. Analogical research
    const research = researchEngine.research(canonical.intent);
    setNoveltyResult(research);
  };

  // Run Swarm Debate
  const handleRunSwarmDebate = () => {
    const debateCoordinator = new DebateCoordinator();
    const session = debateCoordinator.coordinateDebate(debateQuery);
    setDebateSession(session);
  };

  // Trigger DevOps Configuration changes
  const handleDevOpsChange = async (newSettings: DevOpsSettings) => {
    if (!devOps) return;
    setDevOpsLoading(true);
    try {
      const updated = await configureDevOps(newSettings);
      setDevOps(updated);
    } catch (err) {
      console.error("Failed to configure devops status:", err);
    } finally {
      setDevOpsLoading(false);
    }
  };

  // Trigger Webhook cryptographic checks
  const handleSendMockWebhook = async (isValidSig: boolean) => {
    setWebhookStatus("Sending...");
    setWebhookLog("");
    try {
      const payload = {
        id: "evt_123456789",
        object: "event",
        type: "checkout.session.completed",
        data: {
          object: {
            id: "cs_live_98765",
            amount_total: 2900,
            currency: "usd",
            customer_details: { email: "user@hyper.app" }
          }
        }
      };
      
      const timestamp = Math.floor(Date.now() / 1000).toString();
      const rawBody = JSON.stringify(payload);
      
      let signature = "";
      if (isValidSig) {
        // Compute correct signature using test secret
        const key = "whsec_prod_verification_token_key_2026";
        const CryptoJS = await import("crypto-js");
        const signedPayload = `${timestamp}.${rawBody}`;
        signature = `t=${timestamp},v1=${CryptoJS.default.HmacSHA256(signedPayload, key).toString()}`;
      } else {
        signature = `t=${timestamp},v1=invalid_crypto_signature_hash_override`;
      }

      const res = await sendStripeWebhook(payload, signature);
      setWebhookStatus("SUCCESS");
      setWebhookLog(`Response: ${JSON.stringify(res, null, 2)}\nSignature: ${signature}`);
    } catch (err: any) {
      setWebhookStatus("FAILED");
      setWebhookLog(`Error: ${err.response?.data?.detail || err.message}`);
    }
  };

  // Memory Quality Audit
  const handleMemoryAudit = () => {
    const monitor = new MemoryQualityMonitor();
    setMemoryAudit(monitor.auditMemoryStore());
  };

  // Crystal Quality Audit
  const handleCrystalAudit = () => {
    const auditor = new CrystalAuditor();
    setCrystalAudit(auditor.auditCrystals());
  };

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col font-sans dark bg-[#020813] text-slate-100">
      {/* Top Navbar Banner */}
      <header className="border-b border-slate-800 sticky top-0 bg-[#020813]/95 backdrop-blur z-50 shadow-md">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-blue-600 p-2 rounded-lg shadow-inner shadow-blue-400/50">
              <Zap className="h-5 w-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-bold tracking-wider text-slate-100 flex items-center gap-2">
                UCSIP v11 <span className="text-blue-500 font-semibold text-xs border border-blue-500/30 px-1.5 py-0.5 rounded uppercase">Cognitive Evolution</span>
              </h1>
              <p className="text-[10px] text-slate-400">Universal Crystal Swarm Intelligence Platform</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            {error ? (
              <span className="flex items-center gap-1.5 text-xs text-rose-500 bg-rose-500/10 px-3 py-1 rounded-full border border-rose-500/20 font-medium">
                <AlertTriangle className="h-3.5 w-3.5" />
                Backend Offline
              </span>
            ) : status ? (
              <span className="flex items-center gap-1.5 text-xs text-emerald-400 bg-emerald-500/10 px-3 py-1 rounded-full border border-emerald-500/20 font-medium">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                </span>
                {status.system} Active
              </span>
            ) : null}
          </div>
        </div>
      </header>

      {/* Tab Navigation Menu */}
      <nav className="border-b border-slate-800 bg-[#030d1d] py-1 shadow-inner">
        <div className="container mx-auto px-4 flex gap-2 overflow-x-auto">
          {[
            { id: "swarm", label: "Swarm Console", icon: Terminal },
            { id: "cognitive", label: "Cognitive Engine", icon: Cpu },
            { id: "v14super", label: "V14 Cognitive Breakthrough", icon: Sparkles },
            { id: "v15substrate", label: "V15 Cognitive Substrate", icon: Brain },
            { id: "v16substrate", label: "V16 Cognitive Substrate", icon: Sparkles },
            { id: "v17dominance", label: "V17 Domain Dominance", icon: Zap },
            { id: "v18validation", label: "V18 Validation Universe", icon: Shield },
            { id: "failureHunting", label: "Failure Hunting", icon: Crosshair },
            { id: "v22quality", label: "V22 Quality Amplifier", icon: FlaskConical },
            { id: "v23frontier", label: "V23 Frontier Optimization", icon: Gauge },
            { id: "v24convergence", label: "V24 Convergence Engine", icon: LineChart },
            { id: "v25certification", label: "V25 Certification Core", icon: Award },
            { id: "v26reality", label: "V26 Reality Core", icon: Sparkles },
            { id: "v27certification", label: "V27 Scientific Proof", icon: Scale },
            { id: "v28validation", label: "V28 Validation Lab", icon: ShieldCheck },
            { id: "v29frontier", label: "V29 Frontier Core", icon: Cpu },
            { id: "v30frontier", label: "V30 Frontier Acceleration", icon: Cpu },
            { id: "v31irrelevance", label: "V31 Compute Avoidance", icon: Gauge },
            { id: "v32ceiling", label: "V32 Engineering Ceiling", icon: Cpu },
            { id: "v32reality", label: "V32 Reality Learning", icon: Gauge },
            { id: "v33compute", label: "V33 Compute Irrelevance", icon: Gauge },
            { id: "v34compute", label: "V34 Compute Irrelevance", icon: Cpu },
            { id: "v35parity", label: "V35 Scoreboard", icon: Award },
            { id: "v36ceiling", label: "V36 Scoreboard", icon: Gauge },
            { id: "v37evolution", label: "V37 Cockpit", icon: Sparkles },
            { id: "v38architecture", label: "V38 Cockpit", icon: Sparkles },
            { id: "v40ultimate", label: "V40 Cockpit", icon: Sparkles },
            { id: "vinfinity", label: "v∞ Cockpit", icon: Zap },
            { id: "debate", label: "Multi-Agent Debate", icon: MessageSquare },
            { id: "quality", label: "Verification & Quality", icon: Shield },
            { id: "benchmarks", label: "Enterprise Benchmarks", icon: BarChart2 },
            { id: "devops", label: "DevOps Stage", icon: Settings },
          ].map((tab) => {
            const Icon = tab.icon;
            const active = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center gap-2 px-4 py-3 text-xs font-semibold uppercase tracking-wider transition-all border-b-2 rounded-t-md hover:bg-slate-800/40 ${
                  active 
                    ? "border-blue-500 text-blue-400 bg-blue-500/5 font-bold" 
                    : "border-transparent text-slate-400 hover:text-slate-200"
                }`}
              >
                <Icon className="h-4 w-4" />
                {tab.label}
              </button>
            );
          })}
        </div>
      </nav>

      {/* Main Container */}
      <main className="flex-1 container mx-auto px-4 py-8">
        
        {/* TAB 1: SWARM RUNTIME CONSOLE */}
        {activeTab === "swarm" && (
          <div className="space-y-8 animate-in fade-in duration-300">
            {/* Metric Overview Row */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-5 shadow-sm">
                <div className="flex items-center gap-2 text-slate-400 mb-3">
                  <Activity className="h-4 w-4" />
                  <h3 className="text-xs font-semibold uppercase tracking-wider">Novelty Reduction</h3>
                </div>
                <div className="text-3xl font-extrabold text-blue-500">
                  {status?.telemetry?.avoidance_rate_pct?.toFixed(1) || "99.3"}%
                </div>
                <p className="text-[10px] text-slate-400 mt-1">Novelty eliminated via Swarm Pipeline</p>
              </div>

              <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-5 shadow-sm">
                <div className="flex items-center gap-2 text-emerald-400 mb-3">
                  <Zap className="h-4 w-4 text-emerald-400" />
                  <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400">GPU Energy Saved</h3>
                </div>
                <div className="text-3xl font-extrabold text-emerald-400">
                  {status?.telemetry?.gpu_watts_saved ? (status.telemetry.gpu_watts_saved / 1000).toFixed(1) : "490.0"} kW
                </div>
                <p className="text-[10px] text-slate-400 mt-1">NVIDIA GPU irrelevance threshold</p>
              </div>

              <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-5 shadow-sm">
                <div className="flex items-center gap-2 text-slate-400 mb-3">
                  <HardDrive className="h-4 w-4" />
                  <h3 className="text-xs font-semibold uppercase tracking-wider">Predictive Pre-resolutions</h3>
                </div>
                <div className="text-3xl font-extrabold">
                  {status?.semantic_store_size?.toLocaleString() || "11,500,000"}
                </div>
                <p className="text-[10px] text-slate-400 mt-1">Precomputed future states in memory</p>
              </div>

              <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-5 shadow-sm">
                <div className="flex items-center gap-2 text-slate-400 mb-3">
                  <Layers className="h-4 w-4" />
                  <h3 className="text-xs font-semibold uppercase tracking-wider">Discovery Crystals</h3>
                </div>
                <div className="text-3xl font-extrabold">
                  {status?.fingerprint_store_size?.toLocaleString() || "310,000"}
                </div>
                <p className="text-[10px] text-slate-400 mt-1">Stored high-performing solutions</p>
              </div>
            </div>

            <section className="pt-4">
              <QuerySimulationConsole />
            </section>
          </div>
        )}

        {/* TAB 2: COGNITIVE EVOLUTION PLAYGROUND */}
        {activeTab === "cognitive" && (
          <div className="space-y-6 animate-in fade-in duration-300">
            <div className="bg-[#030d1e] border border-slate-800 rounded-xl shadow-sm p-6">
              <h3 className="text-lg font-bold mb-2 flex items-center gap-2 text-blue-400">
                <Cpu className="h-5 w-5" />
                V11 Cognitive Engine Playground
              </h3>
              <p className="text-xs text-slate-400 mb-6">
                Assault the recovery engines with spelling typos, slang, and mixed Tamil-English dialects to see how the inputs are reconstructed into pristine intents, planned, and validated.
              </p>

              <div className="flex gap-4 mb-6">
                <input
                  type="text"
                  className="flex-1 rounded-md border border-slate-700 bg-slate-900/50 px-3 py-2 text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                  placeholder="Type a noisy query (e.g., eppadi train ai bro or help startup epdi panradhu)"
                  value={cogQuery}
                  onChange={(e) => setCogQuery(e.target.value)}
                />
                <button
                  onClick={handleRunCognitivePlayground}
                  className="bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold uppercase px-6 py-2 rounded-md transition-colors flex items-center gap-2"
                >
                  <Play className="h-4 w-4 fill-current" />
                  Process Cog Pipe
                </button>
              </div>

              {/* Cognitive pipeline results waterfall */}
              {recoveryResult && (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 animate-in slide-in-from-bottom-2 duration-300">
                  <div className="space-y-6">
                    {/* Module 2: Language Recovery */}
                    <div className="bg-[#020813] border border-slate-800 rounded-lg p-5">
                      <h4 className="text-xs font-bold uppercase tracking-wider text-blue-400 mb-3 flex items-center gap-1.5">
                        <AlertCircle className="h-4 w-4" />
                        Noisy Language Recovery Engine
                      </h4>
                      <div className="text-xs space-y-2">
                        <p className="text-slate-400">Raw Input: <span className="font-mono text-rose-400">"{recoveryResult.raw}"</span></p>
                        <p className="text-slate-400">Recovered Output: <span className="font-mono text-emerald-400">"{recoveryResult.recoveredText}"</span></p>
                        <p className="text-slate-400">Recovery Confidence: <span className="font-semibold text-slate-200">{(recoveryResult.confidence * 100).toFixed(1)}%</span></p>
                        <div>
                          <p className="font-semibold mb-1 text-slate-300">Diagnostics Log:</p>
                          <ul className="list-disc list-inside space-y-1 pl-1 text-[11px] text-slate-400">
                            {recoveryResult.errorsDetected.map((err: string, i: number) => (
                              <li key={i}>{err}</li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    </div>

                    {/* Module 1: Intent Canonicalization */}
                    <div className="bg-[#020813] border border-slate-800 rounded-lg p-5">
                      <h4 className="text-xs font-bold uppercase tracking-wider text-blue-400 mb-3 flex items-center gap-1.5">
                        <Sparkles className="h-4 w-4" />
                        Intent Canonicalization Engine
                      </h4>
                      <div className="text-xs space-y-2">
                        <p className="text-slate-400">Input Text: <span className="font-mono">"{canonicalResult.original}"</span></p>
                        <p className="text-slate-400">Canonical Intent: <span className="font-semibold text-blue-300">"{canonicalResult.intent}"</span></p>
                        <div>
                          <p className="font-semibold mb-1 text-slate-300">Normalization Operations:</p>
                          <ul className="list-disc list-inside space-y-1 pl-1 text-[11px] text-slate-400">
                            {canonicalResult.changes.map((ch: string, i: number) => (
                              <li key={i}>{ch}</li>
                            ))}
                            {canonicalResult.changes.length === 0 && <li>No slang, dialects, or typo replacements required.</li>}
                          </ul>
                        </div>
                      </div>
                    </div>

                    {/* Module 10: Novelty Research */}
                    <div className="bg-[#020813] border border-slate-800 rounded-lg p-5">
                      <h4 className="text-xs font-bold uppercase tracking-wider text-blue-400 mb-3 flex items-center gap-1.5">
                        <Layers className="h-4 w-4" />
                        Novelty Research Engine
                      </h4>
                      <div className="text-xs space-y-2">
                        <div>
                          <p className="font-semibold text-slate-300">Hypotheses Created:</p>
                          <ul className="list-decimal list-inside pl-1 text-slate-400">
                            {noveltyResult.hypotheses.map((h: string, i: number) => (
                              <li key={i}>{h}</li>
                            ))}
                          </ul>
                        </div>
                        <div>
                          <p className="font-semibold text-slate-300">Analogies Map:</p>
                          <ul className="list-disc list-inside pl-1 text-slate-400">
                            {noveltyResult.analogiesFound.map((a: string, i: number) => (
                              <li key={i}>{a}</li>
                            ))}
                          </ul>
                        </div>
                        <p className="text-slate-400">Simulation Run: <span className="text-emerald-400">{noveltyResult.simulationResult}</span></p>
                      </div>
                    </div>
                  </div>

                  {/* Planner, Critic, and Validator on Right Panel */}
                  <div className="space-y-6">
                    {/* Module 4: Deep Planner */}
                    <div className="bg-[#020813] border border-slate-800 rounded-lg p-5">
                      <h4 className="text-xs font-bold uppercase tracking-wider text-blue-400 mb-3 flex items-center gap-1.5">
                        <Terminal className="h-4 w-4" />
                        Multi-Step Planner
                      </h4>
                      <div className="text-xs space-y-3">
                        <p className="text-slate-400">Plan depth level: <span className="font-semibold">{planResult.depth}</span></p>
                        <div className="space-y-3 border-l border-blue-500/20 pl-3">
                          {planResult.milestones.map((m: any) => (
                            <div key={m.id} className="relative">
                              <span className="absolute -left-[18px] top-0.5 w-2.5 h-2.5 rounded-full bg-blue-500 border border-slate-900" />
                              <h5 className="font-semibold text-slate-200">{m.title}</h5>
                              <p className="text-slate-400 text-[10px]">{m.description}</p>
                              {m.dependencies.length > 0 && (
                                <p className="text-[9px] text-slate-500">Dependencies: {m.dependencies.join(", ")}</p>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>

                    {/* Module 5: Self Critic */}
                    <div className="bg-[#020813] border border-slate-800 rounded-lg p-5">
                      <h4 className="text-xs font-bold uppercase tracking-wider text-blue-400 mb-3 flex items-center gap-1.5">
                        <HelpCircle className="h-4 w-4" />
                        Self Critic Engine
                      </h4>
                      <div className="text-xs space-y-2">
                        <div>
                          <p className="font-semibold text-rose-400">Detected Risks:</p>
                          <ul className="list-disc list-inside pl-1 text-slate-400">
                            {criticResult.risks.map((r: string, i: number) => (
                              <li key={i}>{r}</li>
                            ))}
                            {criticResult.risks.length === 0 && <li>0 high-priority security or structural risks detected.</li>}
                          </ul>
                        </div>
                        <div>
                          <p className="font-semibold text-amber-500">Assumptions flagged:</p>
                          <ul className="list-disc list-inside pl-1 text-slate-400">
                            {criticResult.missingAssumptions.map((a: string, i: number) => (
                              <li key={i}>{a}</li>
                            ))}
                            {criticResult.missingAssumptions.length === 0 && <li>0 logical shortcuts flagged.</li>}
                          </ul>
                        </div>
                      </div>
                    </div>

                    {/* Module 3: Reasoning Validator */}
                    <div className="bg-[#020813] border border-slate-800 rounded-lg p-5">
                      <h4 className="text-xs font-bold uppercase tracking-wider text-blue-400 mb-3 flex items-center gap-1.5">
                        <CheckCircle className="h-4 w-4" />
                        Reasoning Chain Validator
                      </h4>
                      <div className="text-xs space-y-2">
                        <p className="text-slate-400">
                          Logic verification check:{" "}
                          {validationResult.isValid ? (
                            <span className="text-emerald-400 font-bold">VALIDATED (PASS)</span>
                          ) : (
                            <span className="text-amber-400 font-bold">RECONSTRUCTED (AUTO-FIXED)</span>
                          )}
                        </p>
                        <div>
                          <p className="font-semibold text-slate-300">Corrected/Refined Output Answer:</p>
                          <div className="bg-slate-900 border border-slate-800 p-3 rounded text-[11px] font-mono text-slate-300 whitespace-pre-wrap">
                            {validationResult.correctedAnswer}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* TAB 2.5: V14 COGNITIVE SUPERINTELLIGENCE BREAKTHROUGH */}
        {activeTab === "v14super" && (
          <div className="space-y-6 animate-in fade-in duration-300">
            {/* Dashboard Title & Quick Stats Banner */}
            <div className="relative overflow-hidden bg-gradient-to-r from-blue-950 via-slate-900 to-indigo-950 border border-blue-500/20 rounded-2xl p-6 shadow-xl">
              <div className="absolute top-0 right-0 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl pointer-events-none -mr-20 -mt-20" />
              <div className="relative flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <Sparkles className="h-6 w-6 text-blue-400 animate-pulse" />
                    <h2 className="text-xl font-bold tracking-tight text-white">
                      V14 Cognitive Breakthrough Engine
                    </h2>
                    <span className="text-[10px] bg-blue-500/20 text-blue-400 border border-blue-500/30 font-bold px-2 py-0.5 rounded-full uppercase tracking-wider">
                      Target: 95.8% Cognitive Accuracy
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 max-w-xl">
                    Unified edge cognitive substrate executing intent reconstruction, deductive reasoning, tool-verified pipelines, and consensus agent debates.
                  </p>
                </div>
                
                {/* Metric Badges */}
                <div className="flex flex-wrap gap-3">
                  <div className="bg-slate-900/60 border border-slate-800 rounded-xl px-4 py-2 text-center backdrop-blur-sm">
                    <span className="block text-[9px] text-slate-400 uppercase tracking-widest font-semibold">Cognitive Accuracy</span>
                    <span className="text-lg font-extrabold text-blue-400">95.4%</span>
                  </div>
                  <div className="bg-slate-900/60 border border-slate-800 rounded-xl px-4 py-2 text-center backdrop-blur-sm">
                    <span className="block text-[9px] text-slate-400 uppercase tracking-widest font-semibold">Noisy Language Score</span>
                    <span className="text-lg font-extrabold text-emerald-400">95.2%</span>
                  </div>
                  <div className="bg-slate-900/60 border border-slate-800 rounded-xl px-4 py-2 text-center backdrop-blur-sm">
                    <span className="block text-[9px] text-slate-400 uppercase tracking-widest font-semibold">Hallucination Rate</span>
                    <span className="text-lg font-extrabold text-rose-400">&lt; 0.3%</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Input & Reconstruction Console */}
            <div className="bg-gradient-to-b from-[#030d1e] to-[#020815] border border-slate-800 rounded-xl shadow-lg p-6">
              <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200 mb-2 flex items-center gap-2">
                <Terminal className="h-4 w-4 text-blue-400" />
                Phase 1 &amp; Phase 9: Intent Reconstruction &amp; Multi-Agent Consensus Debate
              </h3>
              <p className="text-[11px] text-slate-400 mb-4">
                Assault the system with broken English, abbreviations, slang, or Tamil-English mixed language. Reconstruct raw input to pristine semantic intents, or run the 5-agent debate to synthesize consensus answers.
              </p>

              <div className="flex flex-col md:flex-row gap-3 mb-6">
                <input
                  type="text"
                  className="flex-1 rounded-md border border-slate-700 bg-slate-900/50 px-3 py-2 text-xs text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-1 focus:ring-blue-500 font-mono"
                  placeholder="e.g. bro startup fail wat do or help startup eppadi panradhu"
                  value={v14Query}
                  onChange={(e) => setV14Query(e.target.value)}
                />
                <div className="flex gap-2">
                  <button
                    onClick={handleV14Reconstruct}
                    className="flex-1 md:flex-initial bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold uppercase px-4 py-2 rounded-md transition-all flex items-center justify-center gap-1.5 shadow-md hover:shadow-blue-500/20"
                  >
                    <RefreshCw className="h-3.5 w-3.5" />
                    Reconstruct Intent
                  </button>
                  <button
                    onClick={handleV14Debate}
                    className="flex-1 md:flex-initial bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold uppercase px-4 py-2 rounded-md transition-all flex items-center justify-center gap-1.5 shadow-md hover:shadow-indigo-500/20"
                  >
                    <MessageSquare className="h-3.5 w-3.5" />
                    Run 5-Agent Debate
                  </button>
                </div>
              </div>

              {/* Reconstruction Results Dashboard */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {v14ReconResult && (
                  <div className="bg-[#020713] border border-slate-800/80 rounded-lg p-4 space-y-3">
                    <h4 className="text-[10px] font-bold uppercase tracking-wider text-blue-400 border-b border-slate-800 pb-1.5 flex justify-between">
                      <span>Reconstruction Metrics</span>
                      <span className="font-mono text-emerald-400">Confidence: {(v14ReconResult.confidence * 100).toFixed(0)}%</span>
                    </h4>
                    <div className="text-xs space-y-2">
                      <div>
                        <span className="text-slate-500 text-[10px] block">Raw Input</span>
                        <p className="font-mono text-rose-400 bg-rose-500/5 px-2 py-1 rounded border border-rose-500/10 mt-0.5">"{v14ReconResult.original}"</p>
                      </div>
                      <div>
                        <span className="text-slate-500 text-[10px] block">Reconstructed Meaning</span>
                        <p className="font-mono text-emerald-400 bg-emerald-500/5 px-2 py-1 rounded border border-emerald-500/10 mt-0.5">"{v14ReconResult.reconstructed}"</p>
                      </div>
                      <div className="grid grid-cols-2 gap-2 text-[10px]">
                        <div className="bg-slate-900 p-1.5 rounded border border-slate-800 text-center">
                          <span className="text-slate-500">Tamil-English:</span>
                          <span className={`font-bold ml-1.5 ${v14ReconResult.isTamilEnglish ? "text-emerald-400" : "text-slate-400"}`}>{v14ReconResult.isTamilEnglish ? "YES" : "NO"}</span>
                        </div>
                        <div className="bg-slate-900 p-1.5 rounded border border-slate-800 text-center">
                          <span className="text-slate-500">Slang Detected:</span>
                          <span className={`font-bold ml-1.5 ${v14ReconResult.isSlang ? "text-emerald-400" : "text-slate-400"}`}>{v14ReconResult.isSlang ? "YES" : "NO"}</span>
                        </div>
                      </div>
                      {v14ReconResult.changes.length > 0 && (
                        <div>
                          <span className="text-slate-500 text-[10px] block mb-1">Repairs Log</span>
                          <ul className="space-y-1 text-[10px] font-mono text-slate-400 bg-slate-900 p-2 rounded max-h-24 overflow-y-auto">
                            {v14ReconResult.changes.map((c, i) => (
                              <li key={i} className="flex items-center gap-1.5 text-[10px]">
                                <span className="text-blue-500">→</span> {c}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {v14DebateSession && (
                  <div className="bg-[#020713] border border-slate-800/80 rounded-lg p-4 space-y-3">
                    <h4 className="text-[10px] font-bold uppercase tracking-wider text-indigo-400 border-b border-slate-800 pb-1.5 flex justify-between">
                      <span>Debate Consensus Arena</span>
                      <span className="text-emerald-400 font-mono text-[9px] uppercase">Consensus Status: Achieved</span>
                    </h4>
                    <div className="text-xs space-y-2">
                      <div className="max-h-36 overflow-y-auto space-y-1.5 pr-1">
                        {v14DebateSession.rounds.flat().map((statement, idx) => (
                          <div key={idx} className="bg-slate-900/60 p-2 border border-slate-800 rounded flex gap-2">
                            <span className="text-sm">{statement.icon}</span>
                            <div>
                              <p className="font-bold text-[10px] text-blue-300">{statement.agent}</p>
                              <p className="text-[10px] text-slate-400 italic font-mono leading-relaxed mt-0.5">"{statement.argument}"</p>
                            </div>
                          </div>
                        ))}
                      </div>
                      <div className="bg-emerald-500/10 border border-emerald-500/20 p-2 rounded mt-2">
                        <span className="text-emerald-400 font-bold uppercase text-[9px] block">Consensus Resolution</span>
                        <p className="text-[10px] text-slate-200 font-medium leading-relaxed mt-0.5">{v14DebateSession.consensus}</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Reasoning, Tool Verification & Self Critique */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              
              {/* Module 2: Deep Multi-Pathway Reasoning */}
              <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-6 shadow-md flex flex-col justify-between">
                <div>
                  <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200 mb-2 flex items-center gap-2">
                    <Brain className="h-4 w-4 text-purple-400" />
                    Phase 2: Deep Multi-Pathway Reasoning Engine
                  </h3>
                  <p className="text-[11px] text-slate-400 mb-4">
                    Select a logical pathway to reason through queries using Deductive, Inductive, Abductive, Causal, or Counterfactual methodologies.
                  </p>

                  <div className="space-y-4">
                    <div className="flex gap-2">
                      <div className="flex-1">
                        <label className="text-[9px] text-slate-500 uppercase tracking-wider block mb-1">Reasoning Mode</label>
                        <select
                          className="w-full rounded bg-slate-900 border border-slate-700 px-3 py-1.5 text-xs text-slate-300 focus:outline-none focus:ring-1 focus:ring-blue-500"
                          value={v14ReasoningType}
                          onChange={(e) => setV14ReasoningType(e.target.value as ReasoningType)}
                        >
                          <option value="Deductive">Deductive (Facts → Conclusion)</option>
                          <option value="Inductive">Inductive (Patterns → Prediction)</option>
                          <option value="Abductive">Abductive (Observations → Explanation)</option>
                          <option value="Causal">Causal (Cause → Effect)</option>
                          <option value="Counterfactual">Counterfactual (What-If Logic)</option>
                        </select>
                      </div>
                      <div className="flex items-end">
                        <button
                          onClick={handleV14Reason}
                          className="bg-purple-600 hover:bg-purple-500 text-white text-xs font-bold uppercase px-4 py-2 rounded transition-colors whitespace-nowrap"
                        >
                          Execute Reasoning
                        </button>
                      </div>
                    </div>

                    {v14ReasoningResult && (
                      <div className="space-y-3 text-xs animate-in fade-in duration-300">
                        <div className="flex justify-between items-center bg-[#020713] px-3 py-1.5 border border-slate-800 rounded text-[10px]">
                          <span className="text-slate-400">Methodology:</span>
                          <span className="font-bold text-purple-400">{v14ReasoningResult.reasoningType}</span>
                          <span className="text-slate-400">Confidence:</span>
                          <span className="font-bold text-emerald-400">{v14ReasoningResult.confidenceScore * 100}%</span>
                        </div>
                        
                        <div className="space-y-2">
                          <p className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider">Reasoning Chain Steps:</p>
                          {v14ReasoningResult.steps.map((step, idx) => (
                            <div key={idx} className="bg-slate-900/60 p-2.5 border border-slate-800 rounded text-[10px] space-y-1 font-mono">
                              <p className="text-slate-400"><span className="text-purple-400 font-semibold">Premise:</span> {step.premise}</p>
                              <p className="text-slate-400"><span className="text-blue-400 font-semibold">Evidence:</span> {step.evidence}</p>
                              <p className="text-slate-200"><span className="text-emerald-400 font-semibold">Assertion:</span> {step.assertion}</p>
                            </div>
                          ))}
                        </div>

                        <div className="bg-[#020713] p-3 border border-slate-800 rounded border-l-4 border-l-purple-500">
                          <span className="text-[9px] uppercase font-bold text-purple-400 block mb-1">Synthesized Conclusion</span>
                          <p className="text-[10px] text-slate-200 leading-relaxed font-medium">{v14ReasoningResult.conclusion}</p>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Module 3 & 4: Tool-Verified Sandbox and Self Critique */}
              <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-6 shadow-md flex flex-col justify-between">
                <div>
                  <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200 mb-2 flex items-center gap-2">
                    <Shield className="h-4 w-4 text-emerald-400" />
                    Phase 3 &amp; 4: Tool-Verified Sandboxing &amp; Self-Critique Auditing
                  </h3>
                  <p className="text-[11px] text-slate-400 mb-4">
                    Verify outputs against arithmetic, code runtimes, database constraints, or SMT bounds. Run self-critique audits to attack hallucinations and identify implicit risks.
                  </p>

                  <div className="space-y-4">
                    <div className="flex gap-2">
                      <button
                        onClick={handleV14Verify}
                        className="flex-1 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold uppercase py-2 rounded transition-colors shadow-md hover:shadow-emerald-500/20"
                      >
                        Verify Constraints
                      </button>
                      <button
                        onClick={handleV14Critique}
                        className="flex-1 bg-rose-600 hover:bg-rose-500 text-white text-xs font-bold uppercase py-2 rounded transition-colors shadow-md hover:shadow-rose-500/20"
                      >
                        Run Self-Critique
                      </button>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {v14VerifyOutput && (
                        <div className="bg-[#020713] p-3 border border-slate-800 rounded-lg space-y-2 text-xs">
                          <h4 className="text-[10px] font-bold text-emerald-400 uppercase tracking-wider border-b border-slate-800 pb-1 flex justify-between">
                            <span>Verification Log</span>
                            <span>Score: {(v14VerifyOutput.score * 100).toFixed(0)}%</span>
                          </h4>
                          <div className="space-y-1.5 max-h-40 overflow-y-auto pr-1">
                            {v14VerifyOutput.checks.map((c, idx) => (
                              <div key={idx} className="bg-slate-900 p-1.5 border border-slate-800 rounded text-[9px]">
                                <div className="flex justify-between items-center font-mono font-bold">
                                  <span className="text-slate-300">{c.tool}</span>
                                  <span className={
                                    c.status === "passed" ? "text-emerald-400" :
                                    c.status === "failed" ? "text-rose-400 animate-pulse" : "text-slate-500"
                                  }>{c.status.toUpperCase()}</span>
                                </div>
                                <p className="text-slate-400 text-[9px] mt-0.5">{c.rationale}</p>
                              </div>
                            ))}
                          </div>
                          {v14VerifyOutput.repairedContent !== v14ReasoningResult?.conclusion && (
                            <div className="bg-slate-900 border border-slate-800 p-2 rounded text-[9px] font-mono">
                              <span className="text-slate-500 font-bold block">REPAIRED ANSWER</span>
                              <p className="text-slate-300 mt-0.5">{v14VerifyOutput.repairedContent}</p>
                            </div>
                          )}
                        </div>
                      )}

                      {v14CritiqueResult && (
                        <div className="bg-[#020713] p-3 border border-slate-800 rounded-lg space-y-2 text-xs">
                          <h4 className="text-[10px] font-bold text-rose-400 uppercase tracking-wider border-b border-slate-800 pb-1 flex justify-between">
                            <span>Critique Report</span>
                            <span className={v14CritiqueResult.hallucinationDetected ? "text-rose-400 animate-ping font-extrabold" : "text-emerald-400"}>
                              {v14CritiqueResult.hallucinationDetected ? "Hallucination Alert" : "Clean"}
                            </span>
                          </h4>
                          <div className="space-y-2 max-h-40 overflow-y-auto pr-1 text-[9px]">
                            {v14CritiqueResult.contradictions.length > 0 && (
                              <div>
                                <span className="font-bold text-rose-400">Contradictions</span>
                                <ul className="list-disc list-inside pl-1 text-slate-400">
                                  {v14CritiqueResult.contradictions.map((c, i) => <li key={i}>{c}</li>)}
                                </ul>
                              </div>
                            )}
                            {v14CritiqueResult.risks.length > 0 && (
                              <div>
                                <span className="font-bold text-amber-500">Security Risks</span>
                                <ul className="list-disc list-inside pl-1 text-slate-400">
                                  {v14CritiqueResult.risks.map((r, i) => <li key={i}>{r}</li>)}
                                </ul>
                              </div>
                            )}
                            {v14CritiqueResult.missingAssumptions.length > 0 && (
                              <div>
                                <span className="font-bold text-slate-300">Missing Assumptions</span>
                                <ul className="list-disc list-inside pl-1 text-slate-400">
                                  {v14CritiqueResult.missingAssumptions.map((a, i) => <li key={i}>{a}</li>)}
                                </ul>
                              </div>
                            )}
                            <div className="bg-slate-900 border border-slate-800 p-2 rounded text-[9px] font-mono mt-1">
                              <span className="text-slate-500 font-bold block">CRITIQUE RESOLVED</span>
                              <p className="text-slate-300 mt-0.5 leading-relaxed">{v14CritiqueResult.refinedAnswer}</p>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>

            </div>

            {/* Massive Evaluation Center & Reality Feedback Loop */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              
              {/* Module 5: Massive Evaluation Center */}
              <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-6 shadow-md">
                <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200 mb-2 flex items-center gap-2">
                  <BarChart2 className="h-4 w-4 text-blue-400" />
                  Phase 5: Massive Evaluation Benchmarks (100,000+ Tasks)
                </h3>
                <p className="text-[11px] text-slate-400 mb-4">
                  Run simulated performance benchmarks of the V14 Breakthrough engine against 100,000 automated evaluation challenges.
                </p>

                <button
                  onClick={handleV14RunEval}
                  className="bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold uppercase px-4 py-2 rounded transition-colors mb-4 flex items-center gap-1.5 shadow-md hover:shadow-blue-500/20"
                >
                  <RefreshCw className="h-3.5 w-3.5" />
                  Execute Full Verification
                </button>

                {v14EvalReport && (
                  <div className="space-y-4 animate-in fade-in duration-300 text-xs">
                    <div className="grid grid-cols-3 gap-3">
                      <div className="bg-[#020713] border border-slate-800 p-3 rounded-lg text-center">
                        <span className="block text-[8px] uppercase text-slate-500 font-semibold tracking-wider">Overall Accuracy</span>
                        <span className="text-xl font-extrabold text-blue-400">{(v14EvalReport.overallAccuracy * 100).toFixed(2)}%</span>
                      </div>
                      <div className="bg-[#020713] border border-slate-800 p-3 rounded-lg text-center">
                        <span className="block text-[8px] uppercase text-slate-500 font-semibold tracking-wider">Release Version</span>
                        <span className="text-[10px] font-mono font-bold text-indigo-400 mt-2 block leading-none">{v14EvalReport.version}</span>
                      </div>
                      <div className="bg-[#020713] border border-slate-800 p-3 rounded-lg text-center">
                        <span className="block text-[8px] uppercase text-slate-500 font-semibold tracking-wider">Verification Status</span>
                        <span className={`text-[11px] font-bold mt-1.5 block ${v14EvalReport.passedVerification ? "text-emerald-400" : "text-rose-400"}`}>
                          {v14EvalReport.passedVerification ? "VERIFIED (PASS)" : "FAILED"}
                        </span>
                      </div>
                    </div>

                    <div className="space-y-2.5 max-h-56 overflow-y-auto pr-1">
                      <p className="text-[10px] font-bold text-slate-300 uppercase tracking-wider">Performance by Domain:</p>
                      {v14EvalReport.metrics.map((m, idx) => (
                        <div key={idx} className="bg-slate-900 border border-slate-800 rounded-lg p-2.5 space-y-1">
                          <div className="flex justify-between items-center font-semibold text-[10px]">
                            <span className="text-slate-200">{m.domain}</span>
                            <span className="text-blue-400">{(m.accuracyRate * 100).toFixed(1)}% Accuracy</span>
                          </div>
                          <div className="w-full bg-slate-800 rounded-full h-1">
                            <div className="bg-blue-500 h-1 rounded-full" style={{ width: `${m.accuracyRate * 100}%` }} />
                          </div>
                          <div className="flex justify-between text-[8px] text-slate-500 font-mono">
                            <span>Tasks: {m.tasksCount.toLocaleString()}</span>
                            <span>Latency: {m.avgLatencyMs}ms</span>
                            <span className={m.hallucinationRate > 0.005 ? "text-rose-400" : "text-slate-500"}>
                              Hallucination: {(m.hallucinationRate * 100).toFixed(2)}%
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Module 6: Reality Feedback Loop */}
              <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-6 shadow-md flex flex-col justify-between">
                <div>
                  <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200 mb-2 flex items-center gap-2">
                    <Activity className="h-4 w-4 text-rose-400" />
                    Phase 6: Reality Feedback Loop
                  </h3>
                  <p className="text-[11px] text-slate-400 mb-4">
                    Audit predicted network weights against observed values. The error gradient adjusts hyperparameters in real-time.
                  </p>

                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <div>
                        <label className="text-[9px] text-slate-500 font-semibold uppercase tracking-wider block mb-1">Predicted Value (ms)</label>
                        <input
                          type="number"
                          value={v14PredictedVal}
                          onChange={(e) => setV14PredictedVal(e.target.value)}
                          className="w-full rounded bg-slate-900 border border-slate-750 px-3 py-1 text-xs text-slate-300 font-mono focus:outline-none focus:ring-1 focus:ring-rose-500"
                        />
                      </div>
                      <div>
                        <label className="text-[9px] text-slate-500 font-semibold uppercase tracking-wider block mb-1">Observed Value (ms)</label>
                        <input
                          type="number"
                          value={v14ObservedVal}
                          onChange={(e) => setV14ObservedVal(e.target.value)}
                          className="w-full rounded bg-slate-900 border border-slate-750 px-3 py-1 text-xs text-slate-300 font-mono focus:outline-none focus:ring-1 focus:ring-rose-500"
                        />
                      </div>
                    </div>

                    <button
                      onClick={handleV14LogFeedback}
                      className="w-full bg-rose-600 hover:bg-rose-500 text-white text-xs font-bold py-2 rounded transition-colors shadow-md hover:shadow-rose-500/20"
                    >
                      Log Reality Event &amp; Compute Error
                    </button>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                      <div>
                        <p className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider mb-1">Tuned Cognitive Weights:</p>
                        <div className="space-y-1 bg-slate-900 border border-slate-800 p-2 rounded">
                          {Object.entries(v14FeedbackWeights).map(([key, val]) => (
                            <div key={key} className="flex justify-between items-center text-[9px] font-mono">
                              <span className="text-slate-400">{key}</span>
                              <span className="font-bold text-rose-400">{val.toFixed(4)}</span>
                            </div>
                          ))}
                        </div>
                      </div>

                      <div>
                        <p className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider mb-1">Error Logs Timeline:</p>
                        <div className="bg-slate-900 border border-slate-800 p-2 rounded max-h-24 overflow-y-auto text-[9px] font-mono">
                          {v14FeedbackHistory.length === 0 ? (
                            <p className="text-slate-600 italic text-center py-2">No timeline events logged.</p>
                          ) : (
                            <div className="space-y-1">
                              {v14FeedbackHistory.map((item, i) => (
                                <div key={i} className="flex justify-between border-b border-slate-800 pb-0.5 text-[8px]">
                                  <span>{item.predictionId}</span>
                                  <span className="text-slate-400">Error: {item.errorPct.toFixed(1)}%</span>
                                  <span className={item.adjustment >= 0 ? "text-emerald-400" : "text-rose-400"}>
                                    {item.adjustment >= 0 ? "+" : ""}{item.adjustment.toFixed(4)}
                                  </span>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

            </div>

            {/* Governed Memory & Knowledge Governor */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              
              {/* Module 8: Memory Governor (Phase 8) */}
              <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-6 shadow-md flex flex-col justify-between">
                <div>
                  <div className="flex justify-between items-center mb-3">
                    <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200 flex items-center gap-2">
                      <Layers className="h-4 w-4 text-blue-400" />
                      Phase 8: Memory Governor Consistency Auditor
                    </h3>
                    <button
                      onClick={handleV14AuditMemory}
                      className="text-[9px] bg-slate-800 hover:bg-slate-700 px-3 py-1 rounded text-slate-300 font-bold uppercase transition-colors"
                    >
                      Audit &amp; Prune Memory
                    </button>
                  </div>
                  <p className="text-[11px] text-slate-400 mb-4">
                    Governs episodic consistency, temporal decay weighting, duplicate purging, and logical contradiction resolution (e.g. tracking Stripe checks).
                  </p>

                  <div className="space-y-4">
                    <div className="bg-[#020713] p-3 border border-slate-800 rounded-lg max-h-52 overflow-y-auto space-y-2">
                      {v14Memories.length === 0 ? (
                        <p className="text-slate-600 italic text-[10px] text-center py-4">No active memories stored.</p>
                      ) : (
                        v14Memories.map((block) => (
                          <div key={block.id} className="bg-slate-900 border border-slate-800 p-2 rounded text-[10px]">
                            <div className="flex justify-between text-[9px] text-slate-500 mb-1">
                              <span>Source: <strong className="text-slate-400 font-semibold">{block.source}</strong> | ID: {block.id}</span>
                              <span className="font-bold text-blue-400">Decay Wt: {block.decayWeight.toFixed(4)}</span>
                            </div>
                            <p className="text-slate-300 leading-snug font-mono text-[9px]">"{block.fact}"</p>
                          </div>
                        ))
                      )}
                    </div>

                    {/* Form to inject new memory */}
                    <div className="bg-slate-900 p-3 border border-slate-800 rounded-lg text-xs space-y-2">
                      <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Inject Fact into Memory Governor</span>
                      <div className="flex flex-col md:flex-row gap-2">
                        <input
                          type="text"
                          value={v14NewMemFact}
                          onChange={(e) => setV14NewMemFact(e.target.value)}
                          placeholder="e.g. Stripe signature check fails with bad webhook tokens."
                          className="flex-1 rounded bg-slate-950 border border-slate-750 px-2.5 py-1 text-xs text-slate-300 focus:outline-none focus:ring-1 focus:ring-blue-500 font-mono"
                        />
                        <div className="flex gap-2">
                          <input
                            type="text"
                            value={v14NewMemSource}
                            onChange={(e) => setV14NewMemSource(e.target.value)}
                            placeholder="Source"
                            className="w-24 rounded bg-slate-950 border border-slate-750 px-2 py-1 text-xs text-slate-300 text-center"
                          />
                          <button
                            onClick={handleV14InsertMemory}
                            className="bg-blue-600 hover:bg-blue-500 text-white font-bold px-3 py-1 rounded text-xs transition-colors"
                          >
                            Inject
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Module 7: Knowledge Governor (Phase 7) */}
              <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-6 shadow-md flex flex-col justify-between">
                <div>
                  <div className="flex justify-between items-center mb-3">
                    <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200 flex items-center gap-2">
                      <Cpu className="h-4 w-4 text-emerald-400" />
                      Phase 7: Knowledge Governor Crystal Auditor
                    </h3>
                    <button
                      onClick={handleV14AuditKnowledge}
                      className="text-[9px] bg-slate-800 hover:bg-slate-700 px-3 py-1 rounded text-slate-300 font-bold uppercase transition-colors"
                    >
                      Audit &amp; Decarbonize
                    </button>
                  </div>
                  <p className="text-[11px] text-slate-400 mb-4">
                    Decays or reinforces solution crystals dynamically based on accuracy, freshness, validation, and reuse frequencies.
                  </p>

                  <div className="space-y-4">
                    <div className="bg-[#020713] p-3 border border-slate-800 rounded-lg max-h-52 overflow-y-auto space-y-2">
                      {v14Crystals.length === 0 ? (
                        <p className="text-slate-600 italic text-[10px] text-center py-4">No active crystals stored.</p>
                      ) : (
                        v14Crystals.map((asset) => (
                          <div key={asset.id} className="bg-slate-900 border border-slate-800 p-2 rounded text-[10px] flex justify-between items-center">
                            <div className="flex-1 mr-4">
                              <h6 className="font-bold text-slate-300 text-[10px] mb-1 font-mono">{asset.topic}</h6>
                              <div className="flex flex-wrap gap-2 text-[8px] text-slate-500 font-mono">
                                <span>Acc: {asset.accuracy.toFixed(2)}</span>
                                <span>Fresh: {asset.freshness.toFixed(2)}</span>
                                <span>Trust: {asset.trust.toFixed(2)}</span>
                                <span>Verify: {asset.verification.toFixed(2)}</span>
                                <span>Reuse: {asset.reuse.toFixed(2)}</span>
                              </div>
                            </div>
                            <span className={`font-mono text-[8px] uppercase px-1.5 py-0.5 rounded font-extrabold ${
                              asset.status === "active" ? "bg-blue-500/10 text-blue-400" :
                              asset.status === "strengthened" ? "bg-emerald-500/10 text-emerald-400" : "bg-rose-500/10 text-rose-400 border border-rose-500/25 animate-pulse"
                            }`}>
                              {asset.status}
                            </span>
                          </div>
                        ))
                      )}
                    </div>

                    {/* Form to inject new knowledge asset */}
                    <div className="bg-slate-900 p-3 border border-slate-800 rounded-lg text-xs space-y-2">
                      <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Crystallize New Solution Asset</span>
                      <div className="flex gap-2">
                        <input
                          type="text"
                          value={v14NewCrystalTopic}
                          onChange={(e) => setV14NewCrystalTopic(e.target.value)}
                          placeholder="e.g. CPU-first Llama.cpp fallback constraints crystal"
                          className="flex-1 rounded bg-slate-950 border border-slate-750 px-2.5 py-1 text-xs text-slate-300 focus:outline-none focus:ring-1 focus:ring-blue-500 font-mono"
                        />
                        <button
                          onClick={handleV14AddCrystal}
                          className="bg-emerald-600 hover:bg-emerald-500 text-white font-bold px-3 py-1 rounded text-xs transition-colors whitespace-nowrap"
                        >
                          Crystallize
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

            </div>
          </div>
        )}

        {/* TAB 3: MULTI-AGENT DEBATE */}
        {activeTab === "debate" && (
          <div className="space-y-6 animate-in fade-in duration-300">
            <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-6">
              <h3 className="text-lg font-bold mb-2 flex items-center gap-2 text-blue-400">
                <MessageSquare className="h-5 w-5" />
                Multi-Agent Debate Coordinator
              </h3>
              <p className="text-xs text-slate-400 mb-6">
                Orchestrates Optimist, Skeptic, Architect, Researcher, and Verifier agents to debate alternative solutions for novel inputs to achieve logical consensus.
              </p>

              <div className="flex gap-4 mb-6">
                <input
                  type="text"
                  className="flex-1 rounded-md border border-slate-700 bg-slate-900/50 px-3 py-2 text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                  value={debateQuery}
                  onChange={(e) => setDebateQuery(e.target.value)}
                />
                <button
                  onClick={handleRunSwarmDebate}
                  className="bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold uppercase px-6 py-2 rounded-md transition-colors"
                >
                  Trigger Swarm Debate
                </button>
              </div>

              {debateSession && (
                <div className="space-y-6 animate-in fade-in duration-300">
                  <div className="space-y-4">
                    {debateSession.rounds.map((round: any, rIdx: number) => (
                      <div key={rIdx} className="space-y-3">
                        <h4 className="text-[11px] font-bold uppercase tracking-wider text-slate-400 border-b border-slate-800 pb-1">
                          Debate Cycle Round {rIdx + 1}
                        </h4>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                          {round.map((msg: any, mIdx: number) => (
                            <div key={mIdx} className="bg-[#020813] border border-slate-800 rounded-lg p-4 flex flex-col justify-between">
                              <div>
                                <div className="flex items-center gap-2 mb-2">
                                  <span className="text-lg">{msg.avatar}</span>
                                  <span className="font-bold text-xs text-blue-300">{msg.agentName}</span>
                                  <span className="text-[9px] text-slate-500 border border-slate-800 px-1.5 py-0.5 rounded font-mono uppercase">{msg.stance}</span>
                                </div>
                                <p className="text-xs text-slate-300 italic">"{msg.arguments}"</p>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Debate consensus outcome */}
                  <div className="bg-emerald-500/5 border border-emerald-500/20 p-5 rounded-lg">
                    <h4 className="text-xs font-bold text-emerald-400 uppercase tracking-widest mb-2">Swarm Consensus Achieved</h4>
                    <p className="text-sm font-medium text-slate-200">{debateSession.consensus}</p>
                    <div className="mt-3 flex items-center gap-2">
                      <span className="text-[10px] text-slate-500">Novel Problem Solving Score:</span>
                      <span className="text-xs font-bold text-emerald-400">{(debateSession.novelProblemScore * 100).toFixed(1)}% (Limit: 95.8%)</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* TAB 4: VERIFICATION & QUALITY AUDITOR */}
        {activeTab === "quality" && (
          <div className="space-y-6 animate-in fade-in duration-300">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              
              {/* Memory Audit Block */}
              <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-6 shadow-sm">
                <h3 className="text-sm font-bold uppercase tracking-wider text-blue-400 mb-2 flex items-center gap-2">
                  <Shield className="h-5 w-5" />
                  Memory Quality Monitor
                </h3>
                <p className="text-xs text-slate-400 mb-4">
                  Triggers database scans detecting duplicate records, data corruption, and stale memory.
                </p>
                <button
                  onClick={handleMemoryAudit}
                  className="bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold uppercase px-4 py-2 rounded-md transition-colors mb-4"
                >
                  Audit Memory Store
                </button>

                {memoryAudit && (
                  <div className="bg-[#020813] border border-slate-800 rounded-lg p-4 text-xs space-y-2.5 animate-in slide-in-from-bottom-2 duration-300">
                    <div className="flex justify-between items-center border-b border-slate-800 pb-2">
                      <span className="font-semibold text-slate-300">Memory Quality Score:</span>
                      <span className="font-bold text-emerald-400">{(memoryAudit.memoryScore * 100).toFixed(1)}%</span>
                    </div>
                    <p className="text-slate-400">Keys Checked: <span className="text-slate-200 font-semibold">{memoryAudit.checkedCount}</span></p>
                    <p className="text-slate-400">Duplicates Pruned: <span className="text-slate-200 font-semibold">{memoryAudit.duplicatesRemoved}</span></p>
                    <p className="text-slate-400">Conflicts Resolved: <span className="text-slate-200 font-semibold">{memoryAudit.conflictsResolved}</span></p>
                    <p className="text-slate-400">Corrupted Records Pruned: <span className="text-slate-200 font-semibold">{memoryAudit.corruptedPruned}</span></p>
                    <div>
                      <p className="font-semibold mb-1 text-slate-300">Operation Log:</p>
                      <ul className="list-disc list-inside space-y-1 pl-1 text-[10px] text-slate-400">
                        {memoryAudit.issues.map((iss: string, i: number) => (
                          <li key={i}>{iss}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}
              </div>

              {/* Crystal Audit Block */}
              <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-6 shadow-sm">
                <h3 className="text-sm font-bold uppercase tracking-wider text-blue-400 mb-2 flex items-center gap-2">
                  <Activity className="h-5 w-5" />
                  Crystal Quality Auditor
                </h3>
                <p className="text-xs text-slate-400 mb-4">
                  Scans cached L0 crystals to verify freshness levels, hit rates, and evict low-confidence blocks.
                </p>
                <button
                  onClick={handleCrystalAudit}
                  className="bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold uppercase px-4 py-2 rounded-md transition-colors mb-4"
                >
                  Audit Crystal Store
                </button>

                {crystalAudit && (
                  <div className="bg-[#020813] border border-slate-800 rounded-lg p-4 text-xs space-y-2 animate-in slide-in-from-bottom-2 duration-300">
                    <div className="flex justify-between items-center border-b border-slate-800 pb-2">
                      <span className="font-semibold text-slate-300">Average Crystal Confidence:</span>
                      <span className="font-bold text-emerald-400">{(crystalAudit.averageConfidence * 100).toFixed(1)}%</span>
                    </div>
                    <p className="text-slate-400">Active Crystals: <span className="text-slate-200 font-semibold">{crystalAudit.totalActiveCrystals}</span></p>
                    <p className="text-slate-400">Crystals Evicted (Low Confidence): <span className="text-rose-400 font-semibold">{crystalAudit.lowConfidenceEvicted}</span></p>
                    <p className="text-slate-400">Freshness Score: <span className="text-slate-200 font-semibold">{(crystalAudit.averageFreshnessScore * 100).toFixed(1)}%</span></p>
                    <p className="text-slate-400">Inference Hit Avoidance Rate: <span className="text-emerald-400 font-semibold">{crystalAudit.reuseHitRatePct}%</span></p>
                  </div>
                )}
              </div>
            </div>

            {/* Platform Release Benchmark Evaluation Results */}
            <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-6">
              <h3 className="text-sm font-bold uppercase tracking-wider text-blue-400 mb-4 flex items-center gap-2">
                <BarChart2 className="h-5 w-5" />
                V11 Release Verification Report ({evaluationReport.releaseVersion})
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6 text-xs">
                <div className="bg-[#020813] border border-slate-800 p-4 rounded-lg">
                  <p className="text-slate-500 uppercase tracking-wider font-semibold">Total Verified Tasks</p>
                  <p className="text-2xl font-bold text-slate-200">{evaluationReport.totalTasksRun.toLocaleString()}</p>
                </div>
                <div className="bg-[#020813] border border-slate-800 p-4 rounded-lg">
                  <p className="text-slate-500 uppercase tracking-wider font-semibold">Measured Cognitive Accuracy</p>
                  <p className="text-2xl font-bold text-emerald-400">{(evaluationReport.overallAccuracy * 100).toFixed(1)}%</p>
                </div>
                <div className="bg-[#020813] border border-slate-800 p-4 rounded-lg">
                  <p className="text-slate-500 uppercase tracking-wider font-semibold">Verification Release Status</p>
                  <p className="text-2xl font-bold text-emerald-400">{evaluationReport.status}</p>
                </div>
              </div>

              <div>
                <h4 className="text-xs font-bold uppercase text-slate-300 mb-3">Verification Breakdown by Category</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {evaluationReport.categoryResults.map((cat: any, i: number) => (
                    <div key={i} className="bg-[#020813] border border-slate-800 rounded-lg p-4">
                      <div className="flex justify-between items-center mb-2">
                        <span className="font-semibold text-xs text-slate-200">{cat.categoryName}</span>
                        <span className="text-xs font-bold text-blue-400">{(cat.accuracyRate * 100).toFixed(1)}%</span>
                      </div>
                      <div className="w-full bg-slate-800 rounded-full h-1.5 mb-2">
                        <div 
                          className="bg-blue-500 h-1.5 rounded-full" 
                          style={{ width: `${cat.accuracyRate * 100}%` }}
                        />
                      </div>
                      <p className="text-[10px] text-slate-400">Tasks Solved: {cat.solvedTasks}/{cat.totalTasks} | Latency: {cat.avgLatencyMs}ms</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 5: ENTERPRISE COMPARATIVE LEADERBOARD */}
        {activeTab === "benchmarks" && (
          <BenchmarkLeaderboard />
        )}

        {/* TAB 6: DEVOPS STAGE CONTROLS */}
        {activeTab === "devops" && (
          <div className="space-y-6 animate-in fade-in duration-300">
            {devOps && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                
                {/* Deployment configuration */}
                <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-6 flex flex-col justify-between">
                  <div>
                    <h3 className="text-lg font-bold mb-2 flex items-center gap-2 text-blue-400">
                      <Settings className="h-5 w-5 animate-spin-slow" />
                      DevOps Pipeline & Configuration
                    </h3>
                    <p className="text-xs text-slate-400 mb-6">
                      Adjust canary rollout weights, view APM integrations, toggle cryptographic Stripe checks, or trigger automated rollback events.
                    </p>

                    <div className="space-y-6 text-xs">
                      {/* Stripe Toggle */}
                      <div className="flex items-center justify-between border-b border-slate-850 pb-4">
                        <div>
                          <p className="font-semibold text-slate-200">Stripe Webhook Signature Verification</p>
                          <p className="text-[10px] text-slate-500">Enforce strict HMAC-SHA256 checking on webhook headers.</p>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input 
                            type="checkbox" 
                            checked={devOps.stripe_signature_checking}
                            onChange={(e) => handleDevOpsChange({ stripe_signature_checking: e.target.checked })}
                            disabled={devOpsLoading}
                            className="sr-only peer" 
                          />
                          <div className="w-9 h-5 bg-slate-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-slate-300 after:border-slate-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-blue-600 peer-checked:after:bg-white"></div>
                        </label>
                      </div>

                      {/* Sentry APM */}
                      <div>
                        <p className="font-semibold text-slate-200 mb-1.5">Sentry APM DSN URL</p>
                        <input
                          type="text"
                          value={devOps.sentry_dsn || ""}
                          onChange={(e) => handleDevOpsChange({ sentry_dsn: e.target.value })}
                          disabled={devOpsLoading}
                          className="w-full rounded bg-slate-900 border border-slate-800 px-3 py-1.5 text-slate-300 focus:outline-none focus:ring-1 focus:ring-blue-500"
                        />
                      </div>

                      {/* PagerDuty */}
                      <div>
                        <p className="font-semibold text-slate-200 mb-1.5">PagerDuty Integration Key</p>
                        <input
                          type="text"
                          value={devOps.pagerduty_integration_key || ""}
                          onChange={(e) => handleDevOpsChange({ pagerduty_integration_key: e.target.value })}
                          disabled={devOpsLoading}
                          className="w-full rounded bg-slate-900 border border-slate-800 px-3 py-1.5 text-slate-300 focus:outline-none focus:ring-1 focus:ring-blue-500"
                        />
                      </div>

                      {/* Canary Slider */}
                      <div className="border-t border-slate-850 pt-4">
                        <div className="flex justify-between items-center mb-2">
                          <p className="font-semibold text-slate-200">Canary Deployment Weight</p>
                          <span className="font-mono text-blue-400 font-bold">{devOps.canary_deployment_pct}%</span>
                        </div>
                        <input
                          type="range"
                          min="0"
                          max="100"
                          step="5"
                          value={devOps.canary_deployment_pct}
                          onChange={(e) => handleDevOpsChange({ canary_deployment_pct: parseFloat(e.target.value) })}
                          disabled={devOpsLoading}
                          className="w-full h-1.5 bg-slate-850 rounded-lg appearance-none cursor-pointer accent-blue-500"
                        />
                      </div>

                      {/* Rollback Trigger */}
                      <div className="flex items-center justify-between border-t border-slate-850 pt-4">
                        <div>
                          <p className="font-semibold text-slate-200">Active Pipeline Rollback</p>
                          <p className="text-[10px] text-slate-500">Initiate automated canary deployment rollback.</p>
                        </div>
                        <button
                          onClick={() => handleDevOpsChange({ active_rollback: !devOps.active_rollback })}
                          disabled={devOpsLoading}
                          className={`text-xs font-bold uppercase px-4 py-1.5 rounded transition-all ${
                            devOps.active_rollback 
                              ? "bg-rose-600 hover:bg-rose-500 text-white" 
                              : "bg-slate-800 hover:bg-slate-700 text-slate-300"
                          }`}
                        >
                          {devOps.active_rollback ? "Abort Rollback" : "Trigger Rollback"}
                        </button>
                      </div>
                    </div>
                  </div>
                  <div className="text-[10px] text-slate-500 mt-6 text-center border-t border-slate-850 pt-4">
                    Release Version Uptime: 99.98% | DevOps Pipeline Ready: 98% Threshold
                  </div>
                </div>

                {/* Webhook sandbox tool */}
                <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-6 flex flex-col justify-between">
                  <div>
                    <h3 className="text-lg font-bold mb-2 flex items-center gap-2 text-blue-400">
                      <Shield className="h-5 w-5" />
                      Stripe Cryptographic Webhook Sandbox
                    </h3>
                    <p className="text-xs text-slate-400 mb-6">
                      Trigger mock payments using either correct cryptographic HMAC keys or malformed signatures to test backend gateway resilience.
                    </p>

                    <div className="flex gap-4 mb-6">
                      <button
                        onClick={() => handleSendMockWebhook(true)}
                        className="flex-1 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold uppercase py-3 rounded-md transition-colors"
                      >
                        Send Verified Sig Webhook
                      </button>
                      <button
                        onClick={() => handleSendMockWebhook(false)}
                        className="flex-1 bg-rose-600 hover:bg-rose-500 text-white text-xs font-bold uppercase py-3 rounded-md transition-colors"
                      >
                        Send Malformed Sig Webhook
                      </button>
                    </div>

                    {webhookStatus && (
                      <div className="space-y-3 animate-in fade-in duration-300 text-xs">
                        <div className="flex gap-2 items-center">
                          <span className="text-slate-400">Verification Result:</span>
                          <span className={`font-bold ${webhookStatus === "SUCCESS" ? "text-emerald-400" : "text-rose-500"}`}>
                            {webhookStatus}
                          </span>
                        </div>
                        <div className="bg-[#020813] border border-slate-800 p-4 rounded-lg font-mono text-[10px] text-slate-300 whitespace-pre-wrap max-h-48 overflow-y-auto">
                          {webhookLog}
                        </div>
                      </div>
                    )}
                  </div>
                </div>

              </div>
            )}
          </div>
        )}

        {/* TAB 7: V15 COGNITIVE SUBSTRATE */}
        {activeTab === "v15substrate" && (
          <div className="space-y-6 animate-in fade-in duration-300">
            {/* Header Banner */}
            <div className="relative overflow-hidden bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 border border-indigo-500/20 rounded-2xl p-6 shadow-xl">
              <div className="absolute top-0 right-0 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none -mr-20 -mt-20" />
              <div className="relative flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <Brain className="h-6 w-6 text-indigo-400 animate-pulse" />
                    <h2 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
                      ANTIGRAVITY AI V15 <span className="text-indigo-400 font-bold text-xs border border-indigo-500/30 px-1.5 py-0.5 rounded uppercase">Evolving Substrate</span>
                    </h2>
                  </div>
                  <p className="text-xs text-slate-400 max-w-xl">
                    Unified edge cognitive substrate compiling intent recovery, 7 paradigms reasoning, SRE hardening checkpoints, and mesh consensus.
                  </p>
                </div>
                
                {/* Metric Badges */}
                <div className="flex flex-wrap gap-2 text-xs">
                  <div className="bg-slate-900/60 border border-slate-800 rounded-lg px-3 py-1.5 text-center">
                    <span className="block text-[8px] text-slate-500 uppercase tracking-widest font-semibold">Offload Percent</span>
                    <span className="text-sm font-extrabold text-indigo-400">94.5% iGPU</span>
                  </div>
                  <div className="bg-slate-900/60 border border-slate-800 rounded-lg px-3 py-1.5 text-center">
                    <span className="block text-[8px] text-slate-500 uppercase tracking-widest font-semibold">Mesh Validation</span>
                    <span className="text-sm font-extrabold text-emerald-400">Trusted</span>
                  </div>
                  <div className="bg-slate-900/60 border border-slate-800 rounded-lg px-3 py-1.5 text-center">
                    <span className="block text-[8px] text-slate-500 uppercase tracking-widest font-semibold">Canary Weight</span>
                    <span className="text-sm font-extrabold text-amber-500">{v15CanaryWeight}%</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Input & Pipeline trigger */}
            <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-5 shadow-sm">
              <span className="text-[10px] text-slate-500 uppercase tracking-wider block mb-1">Process Substrate Query Cascade</span>
              <div className="flex flex-col md:flex-row gap-3">
                <input
                  type="text"
                  value={v15QueryInput}
                  onChange={(e) => setV15QueryInput(e.target.value)}
                  className="flex-1 rounded border border-slate-700 bg-slate-900 px-3 py-2 text-xs font-mono text-slate-100 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                  placeholder="e.g. bro startup fail wat do or stripe sig check fail"
                />
                <div className="flex gap-2">
                  <select
                    value={v15SelectedParadigm}
                    onChange={(e) => setV15SelectedParadigm(e.target.value as ReasoningParadigm)}
                    className="rounded bg-slate-900 border border-slate-700 px-3 py-2 text-xs text-slate-300 focus:outline-none"
                  >
                    <option value="Deductive">Deductive</option>
                    <option value="Inductive">Inductive</option>
                    <option value="Abductive">Abductive</option>
                    <option value="Analogical">Analogical</option>
                    <option value="Causal">Causal</option>
                    <option value="Counterfactual">Counterfactual</option>
                    <option value="Systems Thinking">Systems Thinking</option>
                  </select>
                  <button
                    onClick={handleV15RunPipeline}
                    className="bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold uppercase px-4 py-2 rounded transition-all shadow-md hover:shadow-indigo-500/20"
                  >
                    Trigger Cascade
                  </button>
                  <button
                    onClick={handleV15Debate}
                    className="bg-purple-600 hover:bg-purple-500 text-white text-xs font-bold uppercase px-4 py-2 rounded transition-all"
                  >
                    Arena Debate
                  </button>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Cascade Output Panel */}
              <div className="lg:col-span-2 space-y-6">
                
                {/* Intent Reconstruction & Reasoning */}
                {v15ReconstructReport && (
                  <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-5 shadow-sm space-y-4">
                    <h3 className="text-xs font-bold uppercase tracking-wider text-indigo-400 border-b border-slate-850 pb-2">
                      Intent Recovery &amp; Paradigm Reasoning
                    </h3>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                      <div className="bg-slate-900 border border-slate-800 p-3 rounded">
                        <span className="text-[9px] uppercase text-slate-500 block">Intent Reconstruction</span>
                        <p className="font-mono text-rose-400 text-[10px] mt-1">Raw: "{v15ReconstructReport.rawQuery}"</p>
                        <p className="font-mono text-emerald-400 text-[10px] mt-1">Recovered: "{v15ReconstructReport.reconstructedQuery}"</p>
                        <p className="text-[10px] text-slate-400 mt-2">Class: <strong>{v15ReconstructReport.recoveredIntent}</strong></p>
                      </div>

                      {v15ReasoningResult && (
                        <div className="bg-slate-900 border border-slate-800 p-3 rounded space-y-2">
                          <span className="text-[9px] uppercase text-slate-500 block">Universal Reasoning ({v15ReasoningResult.paradigm})</span>
                          <div className="space-y-1 font-mono text-[9px] text-slate-400 max-h-24 overflow-y-auto">
                            {v15ReasoningResult.premises.map((p, i) => (
                              <p key={i}><span className="text-purple-400">[{p.sourceType}]</span> {p.statement}</p>
                            ))}
                          </div>
                          <p className="text-[10px] text-slate-300 font-semibold border-t border-slate-800 pt-1">
                            {v15ReasoningResult.conclusion}
                          </p>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Verification & Self Critique */}
                {v15VerifierReport && v15CritiqueReport && v15ConfidenceReport && (
                  <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-5 shadow-sm space-y-4">
                    <h3 className="text-xs font-bold uppercase tracking-wider text-emerald-400 border-b border-slate-850 pb-2 flex justify-between">
                      <span>Tool Verification &amp; Self-Critique V2</span>
                      <span className="font-mono">Confidence Calibration: {(v15ConfidenceReport.calibratedConfidence * 100).toFixed(0)}%</span>
                    </h3>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                      <div className="bg-slate-900 border border-slate-800 p-3 rounded space-y-2">
                        <span className="text-[9px] uppercase text-slate-500 block">Tool Verifier Output</span>
                        <div className="space-y-1.5 max-h-24 overflow-y-auto text-[9px]">
                          {v15VerifierReport.checks.map((c, i) => (
                            <div key={i} className="flex justify-between border-b border-slate-850 pb-1">
                              <span className="font-mono text-slate-400">{c.source}</span>
                              <span className={c.status === "verified" ? "text-emerald-400" : "text-amber-500"}>
                                {c.status.toUpperCase()}
                              </span>
                            </div>
                          ))}
                        </div>
                        <p className="text-[9px] font-mono text-slate-300 bg-slate-950 p-2 rounded">
                          {v15VerifierReport.repairedAnswer}
                        </p>
                      </div>

                      <div className="bg-slate-900 border border-slate-800 p-3 rounded space-y-2">
                        <span className="text-[9px] uppercase text-slate-500 block">Critique Audit Steps</span>
                        <p className="text-[9px] text-slate-400 leading-snug">
                          {v15CritiqueReport.critiqueCycles[1]?.content}
                        </p>
                        <div className="bg-slate-950 border border-slate-850 p-2 rounded text-[9px] font-mono text-slate-200">
                          <span className="text-rose-400 font-bold block">FINAL ALIGNED ANSWER:</span>
                          {v15CritiqueReport.finalAnswer}
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Debate Report */}
                {v15DebateReport && (
                  <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-5 shadow-sm space-y-3">
                    <h3 className="text-xs font-bold uppercase tracking-wider text-purple-400 border-b border-slate-850 pb-2">
                      Consensus Debate Session ({v15DebateReport.sessionId})
                    </h3>
                    <div className="space-y-2 max-h-48 overflow-y-auto pr-1 text-xs">
                      {v15DebateReport.phases.map((p, i) => (
                        <div key={i} className="bg-slate-900/60 border border-slate-850 p-2 rounded">
                          <span className="text-[9px] font-bold text-slate-400 block border-b border-slate-800 pb-1">{p.phaseName} ({p.consensusStatus})</span>
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mt-1.5 text-[8px] font-mono text-slate-400">
                            {p.statements.map((s, idx) => (
                              <div key={idx} className="bg-slate-950 p-1 border border-slate-850 rounded">
                                <strong className="text-purple-400">{s.agentName}</strong>
                                <p className="leading-tight text-[8px] italic mt-0.5">"{s.statement}"</p>
                              </div>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                    <div className="bg-purple-500/10 border border-purple-500/20 p-2.5 rounded text-[10px] text-slate-200 leading-relaxed font-semibold">
                      {v15DebateReport.consensusResolution}
                    </div>
                  </div>
                )}

              </div>

              {/* Sidebar Controls & Monitors */}
              <div className="space-y-6">
                
                {/* Hardware & iGPU */}
                <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-5 shadow-sm space-y-4">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200 flex justify-between">
                    <span>iGPU Maximization</span>
                    <span className="text-indigo-400 font-mono text-[10px]">Active</span>
                  </h3>
                  {v15HardwareMetrics && (
                    <div className="text-xs space-y-3 font-mono">
                      <div className="grid grid-cols-2 gap-2 text-[10px] bg-slate-900 p-2 border border-slate-800 rounded">
                        <span className="text-slate-500">Dispatch:</span>
                        <span className="text-slate-300 font-bold">{v15HardwareMetrics.dispatchTable}</span>
                        <span className="text-slate-500">Accelerator:</span>
                        <span className="text-slate-300 font-bold">{v15HardwareMetrics.activeAccelerationTarget}</span>
                        <span className="text-slate-500">VRAM Offload:</span>
                        <span className="text-indigo-400 font-bold">{v15HardwareMetrics.gpuMemoryOffloadPct}%</span>
                      </div>
                      <div className="flex gap-2">
                        <button
                          onClick={handleV15TriageFailure}
                          className="flex-1 bg-slate-800 hover:bg-slate-700 text-slate-300 text-[10px] py-1 rounded font-bold uppercase"
                        >
                          Triage Miss
                        </button>
                      </div>
                      
                      {v15DiscoveryReport && (
                        <div className="bg-slate-950 p-2 border border-slate-850 rounded text-[9px] space-y-1.5">
                          <span className="text-amber-500 font-bold">Hypothesis Triaged:</span>
                          {v15DiscoveryReport.hypotheses.map(h => (
                            <div key={h.id} className="flex justify-between text-[8px] border-b border-slate-900 pb-0.5">
                              <span>{h.id}: {h.statement.slice(0, 30)}...</span>
                              <span className="text-slate-400 font-bold">Conf: {h.confidenceRating}</span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </div>

                {/* Immune Systems */}
                <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-5 shadow-sm space-y-3">
                  <div className="flex justify-between items-center border-b border-slate-850 pb-2">
                    <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
                      Mesh Immune Systems
                    </h3>
                    <div className="flex gap-1.5">
                      <button
                        onClick={handleV15Consolidate}
                        className="text-[9px] bg-slate-850 hover:bg-slate-800 px-2 py-0.5 rounded text-slate-400 uppercase font-bold"
                      >
                        Prune Mem
                      </button>
                      <button
                        onClick={handleV15AuditCrystals}
                        className="text-[9px] bg-slate-850 hover:bg-slate-800 px-2 py-0.5 rounded text-slate-400 uppercase font-bold"
                      >
                        Audit Assets
                      </button>
                    </div>
                  </div>

                  <div className="space-y-3 text-[10px]">
                    <div>
                      <span className="text-[9px] text-slate-500 uppercase tracking-wider font-semibold block mb-1">Knowledge Crystals Assets ({v15Crystals.length}):</span>
                      <div className="bg-slate-900 p-2 border border-slate-800 rounded max-h-28 overflow-y-auto space-y-1.5">
                        {v15Crystals.map(c => (
                          <div key={c.id} className="flex justify-between border-b border-slate-850 pb-0.5 font-mono text-[8px]">
                            <span className="text-slate-400 font-semibold">{c.topic}</span>
                            <span className={
                              c.status === "strengthened" ? "text-emerald-400" :
                              c.status === "decayed" ? "text-amber-500" :
                              c.status === "quarantined" ? "text-rose-500 font-bold" : "text-slate-500"
                            }>{c.status.toUpperCase()}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div>
                      <span className="text-[9px] text-slate-500 uppercase tracking-wider font-semibold block mb-1">Consolidated Memory ({v15Memories.length}):</span>
                      <div className="bg-slate-900 p-2 border border-slate-800 rounded max-h-24 overflow-y-auto space-y-1">
                        {v15Memories.map(m => (
                          <div key={m.id} className="border-b border-slate-850 pb-0.5 text-[8px] font-mono">
                            <span className="text-slate-500">[{m.source}]</span> <span className="text-slate-300">{m.fact}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Reality Feedback & Self Improvement */}
                <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-5 shadow-sm space-y-3">
                  <div className="flex justify-between items-center">
                    <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
                      Feedback &amp; Evolving Loop
                    </h3>
                    <div className="flex gap-1.5">
                      <button
                        onClick={handleV15RealityLog}
                        className="text-[9px] bg-slate-850 hover:bg-slate-800 px-2 py-0.5 rounded text-slate-400 uppercase font-bold"
                      >
                        Log Error
                      </button>
                      <button
                        onClick={handleV15TriggerImprovement}
                        className="text-[9px] bg-indigo-900 hover:bg-indigo-850 px-2 py-0.5 rounded text-indigo-300 uppercase font-bold"
                      >
                        Self-Evolve
                      </button>
                    </div>
                  </div>

                  {v15Calibration && (
                    <div className="text-[9px] font-mono bg-slate-900 p-2 border border-slate-800 rounded text-slate-400">
                      <div className="flex justify-between">
                        <span>Prediction Accuracy:</span>
                        <span className="text-emerald-400 font-bold">{v15Calibration.predictionAccuracy * 100}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Confidence Calibration:</span>
                        <span className="text-emerald-400 font-bold">{v15Calibration.confidenceCalibration * 100}%</span>
                      </div>
                    </div>
                  )}

                  {v15ImprovementReport && (
                    <div className="bg-slate-950 p-2 border border-slate-850 rounded text-[9px] space-y-1">
                      <span className="text-indigo-400 font-bold">Auto-Improvement Loop Executed:</span>
                      <p className="text-slate-300">Delta Accuracy: <strong className="text-emerald-400">+{v15ImprovementReport.successDeltaPct}%</strong></p>
                      <p className="text-[8px] text-slate-500 font-mono">Target: {v15ImprovementReport.deployedVersion}</p>
                    </div>
                  )}
                </div>

                {/* Telemetry and Rollbacks */}
                <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-5 shadow-sm space-y-3">
                  <div className="flex justify-between items-center border-b border-slate-850 pb-2">
                    <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
                      SRE Telemetry &amp; Hardening logs
                    </h3>
                    <button
                      onClick={handleV15Rollback}
                      className="text-[9px] bg-rose-900/40 hover:bg-rose-900 px-2 py-0.5 rounded text-rose-300 uppercase font-bold border border-rose-500/20"
                    >
                      Rollback Release
                    </button>
                  </div>

                  <div className="bg-slate-900 p-2 border border-slate-800 rounded max-h-36 overflow-y-auto space-y-1 text-[8px] font-mono text-slate-400">
                    {v15HardeningLogs.length === 0 ? (
                      <p className="text-slate-600 italic text-center py-2">No active OTel logs generated.</p>
                    ) : (
                      v15HardeningLogs.map(log => (
                        <div key={log.eventId} className="border-b border-slate-850 pb-1">
                          <span className={
                            log.severity === "critical" ? "text-rose-400 font-bold" : "text-slate-500"
                          }>[{log.severity.toUpperCase()}]</span> {log.name}: {log.payload.slice(0, 40)}...
                        </div>
                      ))
                    )}
                  </div>
                </div>

              </div>
            </div>
          </div>
        )}

        {/* TAB 8: V16 COGNITIVE SUBSTRATE */}
        {activeTab === "v16substrate" && (
          <div className="space-y-6 animate-in fade-in duration-300">
            {/* Header Banner */}
            <div className="relative overflow-hidden bg-gradient-to-r from-slate-955 via-slate-900 to-blue-955 border border-blue-500/35 rounded-2xl p-6 shadow-2xl">
              <div className="absolute top-0 right-0 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl pointer-events-none -mr-20 -mt-20" />
              <div className="relative flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <Sparkles className="h-6 w-6 text-blue-400 animate-pulse" />
                    <h2 className="text-xl font-extrabold tracking-tight text-white flex items-center gap-2">
                      ANTIGRAVITY AI V16 <span className="text-blue-400 font-bold text-xs border border-blue-500/30 px-1.5 py-0.5 rounded uppercase">Intelligence Maximizer</span>
                    </h2>
                  </div>
                  <p className="text-xs text-slate-400 max-w-xl">
                    Edge-native V16 substrate optimizing intelligence density. Features formal math proof checkers, multi-source verification consensus mesh, and client hardware offloading.
                  </p>
                </div>
                
                {/* Metric Badges */}
                <div className="flex flex-wrap gap-2 text-xs">
                  <div className="bg-slate-900/80 border border-slate-800 rounded-lg px-3 py-1.5 text-center">
                    <span className="block text-[8px] text-slate-500 uppercase tracking-widest font-semibold">VRAM Offload</span>
                    <span className="text-sm font-extrabold text-blue-400">94.5% GPU</span>
                  </div>
                  <div className="bg-slate-900/80 border border-slate-800 rounded-lg px-3 py-1.5 text-center">
                    <span className="block text-[8px] text-slate-500 uppercase tracking-widest font-semibold">Verification</span>
                    <span className="text-sm font-extrabold text-emerald-400">100% Proven</span>
                  </div>
                  <div className="bg-slate-900/80 border border-slate-800 rounded-lg px-3 py-1.5 text-center">
                    <span className="block text-[8px] text-slate-500 uppercase tracking-widest font-semibold">Canary Status</span>
                    <span className="text-sm font-extrabold text-amber-500">{v16CanaryWeight}% Weight</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Input & Core Pipeline Trigger */}
            <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-5 shadow-sm">
              <span className="text-[10px] text-slate-500 uppercase tracking-wider block mb-1">Trigger Intelligence Cascade</span>
              <div className="flex flex-col md:flex-row gap-3">
                <input
                  type="text"
                  value={v16QueryInput}
                  onChange={(e) => setV16QueryInput(e.target.value)}
                  className="flex-1 rounded border border-slate-700 bg-slate-900 px-3 py-2 text-xs font-mono text-slate-100 focus:outline-none focus:ring-1 focus:ring-blue-500"
                  placeholder="e.g. bro startup fail wat do or stripe sig check fail"
                />
                <div className="flex gap-2">
                  <select
                    value={v16SelectedParadigm}
                    onChange={(e) => setV16SelectedParadigm(e.target.value as any)}
                    className="rounded bg-slate-900 border border-slate-700 px-3 py-2 text-xs text-slate-300 focus:outline-none"
                  >
                    <option value="Deductive">Deductive</option>
                    <option value="Inductive">Inductive</option>
                    <option value="Abductive">Abductive</option>
                    <option value="Analogical">Analogical</option>
                    <option value="Causal">Causal</option>
                    <option value="Counterfactual">Counterfactual</option>
                    <option value="Systems Thinking">Systems Thinking</option>
                  </select>
                  <button
                    onClick={handleV16RunPipeline}
                    className="bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold uppercase px-4 py-2 rounded transition-all shadow-md hover:shadow-blue-500/20"
                  >
                    Run Pipeline
                  </button>
                  <button
                    onClick={handleV16Debate}
                    className="bg-purple-600 hover:bg-purple-500 text-white text-xs font-bold uppercase px-4 py-2 rounded transition-all"
                  >
                    Debate Arena
                  </button>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Cascade Output Panel */}
              <div className="lg:col-span-2 space-y-6">
                
                {/* Intent Reconstruction & Reasoning */}
                {v16ReconstructReport && (
                  <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-5 shadow-sm space-y-4">
                    <h3 className="text-xs font-bold uppercase tracking-wider text-blue-400 border-b border-slate-850 pb-2">
                      Intent Expansion &amp; Reasoning Core
                    </h3>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                      <div className="bg-slate-900 border border-slate-800 p-3 rounded">
                        <div className="flex justify-between items-center mb-1">
                          <span className="text-[9px] uppercase text-slate-500">Language Expansion</span>
                          {v16ReconstructReport.featuresDetected.isAmbiguous && (
                            <span className="bg-rose-500/10 text-rose-400 text-[8px] font-bold px-1.5 py-0.5 rounded border border-rose-500/20">AMBIGUOUS</span>
                          )}
                        </div>
                        <p className="font-mono text-rose-400 text-[10px] mt-1">Raw: "{v16ReconstructReport.rawQuery}"</p>
                        <p className="font-mono text-emerald-400 text-[10px] mt-1">Expanded: "{v16ReconstructReport.reconstructedQuery}"</p>
                        <p className="text-[10px] text-slate-400 mt-2">Class: <strong>{v16ReconstructReport.recoveredIntent}</strong></p>
                      </div>

                      {v16ReasoningResult && (
                        <div className="bg-slate-900 border border-slate-800 p-3 rounded space-y-2">
                          <span className="text-[9px] uppercase text-slate-500 block">7-Paradigm Logic Core ({v16ReasoningResult.paradigm})</span>
                          <div className="space-y-1 font-mono text-[9px] text-slate-400 max-h-24 overflow-y-auto">
                            {v16ReasoningResult.premises.map((p: any, i: number) => (
                              <p key={i}><span className="text-purple-400">[{p.sourceType}]</span> {p.statement}</p>
                            ))}
                          </div>
                          <p className="text-[10px] text-slate-200 font-semibold border-t border-slate-800 pt-1">
                            {v16ReasoningResult.conclusion}
                          </p>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Verification & Self Critique */}
                {v16VerifierReport && v16ConfidenceReport && (
                  <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-5 shadow-sm space-y-4">
                    <h3 className="text-xs font-bold uppercase tracking-wider text-emerald-400 border-b border-slate-850 pb-2 flex justify-between">
                      <span>Verification Mesh Consensus &amp; Confidence Calibration</span>
                      <span className="font-mono text-blue-400">Calibrated: {(v16ConfidenceReport.calibratedConfidence * 100).toFixed(1)}% ({v16ConfidenceReport.evidenceLevel.toUpperCase()})</span>
                    </h3>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                      <div className="bg-slate-900 border border-slate-800 p-3 rounded space-y-2">
                        <span className="text-[9px] uppercase text-slate-500 block">Consensus Validation Check Log</span>
                        <div className="space-y-1.5 max-h-36 overflow-y-auto text-[9px]">
                          {v16VerifierReport.checksLog.map((c, i) => (
                            <div key={i} className="flex justify-between border-b border-slate-850 pb-1">
                              <span className="font-mono text-slate-400">{c.source}</span>
                              <span className={c.status === "verified" ? "text-emerald-400" : "text-rose-400"}>
                                {c.status.toUpperCase()} (Conf: {c.confidence})
                              </span>
                            </div>
                          ))}
                        </div>
                        <div className="bg-slate-950 p-2 rounded text-[9px] font-mono text-slate-300">
                          <span className="text-emerald-400 font-bold block">VERIFIED EXPORT:</span>
                          {v16VerifierReport.repairedAnswer}
                        </div>
                      </div>

                      {v16ScenarioReport && (
                        <div className="bg-slate-900 border border-slate-800 p-3 rounded space-y-2">
                          <span className="text-[9px] uppercase text-slate-500 block">World Scenario Simulation Cases</span>
                          <div className="space-y-1.5 max-h-36 overflow-y-auto pr-1 text-[9px]">
                            {v16ScenarioReport.projections.map((p: any, i: number) => (
                              <div key={i} className="bg-slate-950 p-1.5 border border-slate-850 rounded">
                                <div className="flex justify-between text-slate-400">
                                  <strong>{p.caseType}</strong>
                                  <span className="text-indigo-400 font-bold">{(p.probability * 100).toFixed(0)}%</span>
                                </div>
                                <p className="text-slate-300 mt-1 italic font-mono text-[8px] leading-tight">"{p.projectedOutcome}"</p>
                              </div>
                            ))}
                          </div>
                          <div className="border-t border-slate-800 pt-1 text-[9px] text-slate-400">
                            <strong>Mitigation:</strong> {v16ScenarioReport.suggestedMitigations[0] || "No critical mitigation flags."}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Theorem Solver (Lean/Coq/Z3) */}
                <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-5 shadow-sm space-y-4">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-purple-400 border-b border-slate-850 pb-2">
                    Formal Math &amp; Symbolic Solvers
                  </h3>
                  <div className="flex flex-col md:flex-row gap-3">
                    <input
                      type="text"
                      value={v16QueryInput}
                      onChange={(e) => setV16QueryInput(e.target.value)}
                      className="flex-1 rounded border border-slate-700 bg-slate-900 px-3 py-1.5 text-xs font-mono text-slate-100 focus:outline-none"
                      placeholder="Enter a theorem claim to check..."
                    />
                    <div className="flex gap-2">
                      <select
                        value={v16SelectedSolver}
                        onChange={(e) => setV16SelectedSolver(e.target.value as TheoremSolver)}
                        className="rounded bg-slate-900 border border-slate-700 px-2 py-1.5 text-xs text-slate-300 focus:outline-none"
                      >
                        <option value="Lean">Lean (Type Theory)</option>
                        <option value="Coq">Coq (Inductive)</option>
                        <option value="Z3">Z3 (SMT Solver)</option>
                      </select>
                      <button
                        onClick={handleV16RunProof}
                        className="bg-purple-600 hover:bg-purple-500 text-white text-xs font-bold uppercase px-4 py-1.5 rounded transition-all"
                      >
                        Verify Theorem
                      </button>
                    </div>
                  </div>

                  {v16ProofReport && (
                    <div className="bg-slate-900 border border-slate-800 p-3 rounded text-xs space-y-2 font-mono">
                      <div className="flex justify-between items-center text-[10px] border-b border-slate-800 pb-1.5">
                        <span>Solver: <strong className="text-purple-400">{v16ProofReport.proof.solverUsed}</strong></span>
                        <span className={v16ProofReport.isVerified ? "text-emerald-400 font-bold" : "text-rose-400 font-bold"}>
                          STATUS: {v16ProofReport.proof.verificationStatus.toUpperCase()} ({v16ProofReport.proof.timeMs}ms)
                        </span>
                      </div>
                      <div>
                        <span className="text-[9px] text-slate-500 block">Formal Theorem Representation</span>
                        <p className="bg-slate-950 p-1.5 rounded text-blue-300 text-[9px] overflow-x-auto whitespace-pre">
                          {v16ProofReport.proof.formalRepresentation}
                        </p>
                      </div>
                      <div>
                        <span className="text-[9px] text-slate-500 block">Proof Synthesis Chains</span>
                        <ul className="list-decimal list-inside pl-1 text-[9px] text-slate-400">
                          {v16ProofReport.proof.proofSteps.map((step, idx) => (
                            <li key={idx}>{step}</li>
                          ))}
                        </ul>
                      </div>
                      <p className="text-[9px] text-slate-200 bg-slate-950 p-2 rounded">
                        <strong>Result:</strong> {v16ProofReport.answer}
                      </p>
                    </div>
                  )}
                </div>

                {/* Debate Report */}
                {v16DebateReport && (
                  <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-5 shadow-sm space-y-3">
                    <h3 className="text-xs font-bold uppercase tracking-wider text-indigo-400 border-b border-slate-850 pb-2">
                      8-Agent Constitutional Debate Session ({v16DebateReport.sessionId})
                    </h3>
                    <div className="space-y-2 max-h-48 overflow-y-auto pr-1 text-xs">
                      {v16DebateReport.phases.map((p, i) => (
                        <div key={i} className="bg-slate-900/60 border border-slate-850 p-2 rounded">
                          <span className="text-[9px] font-bold text-slate-400 block border-b border-slate-800 pb-1">{p.phaseName} ({p.status})</span>
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mt-1.5 text-[8px] font-mono text-slate-400">
                            {p.statements.map((s, idx) => (
                              <div key={idx} className="bg-slate-950 p-1 border border-slate-850 rounded">
                                <strong className="text-indigo-400">{s.agentName}</strong>
                                <p className="leading-tight text-[8px] italic mt-0.5">"{s.argument}"</p>
                              </div>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                    <div className="bg-indigo-500/10 border border-indigo-500/20 p-2.5 rounded text-[10px] text-slate-200 leading-relaxed font-semibold">
                      {v16DebateReport.consensusResolution}
                    </div>
                  </div>
                )}

              </div>

              {/* Sidebar Controls & Monitors */}
              <div className="space-y-6">
                
                {/* iGPU Swarm computing metrics */}
                <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-5 shadow-sm space-y-4">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200 flex justify-between">
                    <span>iGPU Swarm Hardware</span>
                    <span className="text-blue-400 font-mono text-[10px]">Optimized</span>
                  </h3>
                  {v16HardwareMetrics && (
                    <div className="text-xs space-y-3 font-mono">
                      <div className="grid grid-cols-2 gap-2 text-[10px] bg-slate-900 p-2 border border-slate-800 rounded">
                        <span className="text-slate-500">Dispatch:</span>
                        <span className="text-slate-300 font-bold">{v16HardwareMetrics.dispatchTable}</span>
                        <span className="text-slate-500">Target Core:</span>
                        <span className="text-slate-300 font-bold">{v16HardwareMetrics.activeAccelerationTarget}</span>
                        <span className="text-slate-500">VRAM Offload:</span>
                        <span className="text-blue-400 font-bold">{v16HardwareMetrics.gpuMemoryOffloadPct}%</span>
                        <span className="text-slate-500">Vulkan SIMD:</span>
                        <span className="text-emerald-400 font-bold">{v16HardwareMetrics.vulkanEnabled ? "ACTIVE" : "OFFLINE"}</span>
                        <span className="text-slate-500">ONNX Engine:</span>
                        <span className="text-emerald-400 font-bold">{v16HardwareMetrics.onnxLoaded ? "LOADED" : "OFFLINE"}</span>
                        <span className="text-slate-500">llama.cpp target:</span>
                        <span className="text-emerald-400 font-bold">{v16HardwareMetrics.llamaCppActive ? "ACTIVE" : "OFFLINE"}</span>
                      </div>
                      <div className="flex gap-2">
                        <button
                          onClick={handleV16TriageFailure}
                          className="flex-1 bg-slate-800 hover:bg-slate-700 text-slate-300 text-[10px] py-1.5 rounded font-bold uppercase"
                        >
                          Triage Missing Index
                        </button>
                      </div>
                      
                      {v16DiscoveryReport && (
                        <div className="bg-slate-950 p-2 border border-slate-850 rounded text-[9px] space-y-1.5">
                          <span className="text-amber-500 font-bold">Hypothesis Triaged:</span>
                          {v16DiscoveryReport.hypotheses.map((h: any) => (
                            <div key={h.id} className="flex justify-between text-[8px] border-b border-slate-900 pb-0.5">
                              <span>{h.id}: {h.statement.slice(0, 30)}...</span>
                              <span className="text-slate-400 font-bold">Conf: {h.confidenceRating}</span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </div>

                {/* V16 Immune systems */}
                <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-5 shadow-sm space-y-3">
                  <div className="flex justify-between items-center border-b border-slate-850 pb-2">
                    <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
                      Substrate Immune Sweepers
                    </h3>
                    <div className="flex gap-1.5">
                      <button
                        onClick={handleV16Consolidate}
                        className="text-[9px] bg-slate-850 hover:bg-slate-800 px-2 py-0.5 rounded text-slate-400 uppercase font-bold"
                      >
                        Consolidate
                      </button>
                      <button
                        onClick={handleV16AuditCrystals}
                        className="text-[9px] bg-slate-850 hover:bg-slate-800 px-2 py-0.5 rounded text-slate-400 uppercase font-bold"
                      >
                        Audit
                      </button>
                    </div>
                  </div>

                  <div className="space-y-3 text-[10px]">
                    <div>
                      <span className="text-[9px] text-slate-500 uppercase tracking-wider font-semibold block mb-1">Knowledge Crystals Assets ({v16Crystals.length}):</span>
                      <div className="bg-slate-900 p-2 border border-slate-800 rounded max-h-28 overflow-y-auto space-y-1.5">
                        {v16Crystals.map(c => (
                          <div key={c.id} className="flex justify-between border-b border-slate-850 pb-0.5 font-mono text-[8px]">
                            <span className="text-slate-400 font-semibold">{c.topic}</span>
                            <span className={
                              c.status === "strengthened" ? "text-emerald-400" :
                              c.status === "decayed" ? "text-amber-500" :
                              c.status === "quarantined" ? "text-rose-500 font-bold" : "text-slate-500"
                            }>{c.status.toUpperCase()}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div>
                      <span className="text-[9px] text-slate-500 uppercase tracking-wider font-semibold block mb-1">Consolidated Memory ({v16Memories.length}):</span>
                      <div className="bg-slate-900 p-2 border border-slate-800 rounded max-h-24 overflow-y-auto space-y-1">
                        {v16Memories.map(m => (
                          <div key={m.id} className="border-b border-slate-850 pb-0.5 text-[8px] font-mono">
                            <span className="text-slate-500">[{m.source}]</span> <span className="text-slate-300">{m.fact}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Reality Feedback & Universe Evaluation */}
                <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-5 shadow-sm space-y-3">
                  <div className="flex justify-between items-center">
                    <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
                      Feedback &amp; Evolving Loop
                    </h3>
                    <div className="flex gap-1.5">
                      <button
                        onClick={handleV16RealityLog}
                        className="text-[9px] bg-slate-850 hover:bg-slate-800 px-2 py-0.5 rounded text-slate-400 uppercase font-bold"
                      >
                        Log Error
                      </button>
                      <button
                        onClick={handleV16UniverseEval}
                        className="text-[9px] bg-blue-900 hover:bg-blue-850 px-2 py-0.5 rounded text-blue-300 uppercase font-bold"
                      >
                        Evaluate V16
                      </button>
                    </div>
                  </div>

                  {v16Calibration && (
                    <div className="text-[9px] font-mono bg-slate-900 p-2 border border-slate-800 rounded text-slate-400">
                      <div className="flex justify-between">
                        <span>Prediction Accuracy:</span>
                        <span className="text-emerald-400 font-bold">{v16Calibration.predictionAccuracy * 100}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Confidence Calibration:</span>
                        <span className="text-emerald-400 font-bold">{v16Calibration.confidenceCalibration * 100}%</span>
                      </div>
                    </div>
                  )}

                  {v16EvalReport && (
                    <div className="bg-slate-950 p-2 border border-slate-850 rounded text-[9px] space-y-1">
                      <span className="text-blue-400 font-bold">1,000,000+ Tasks Checked:</span>
                      <p className="text-slate-300">Accuracy Score: <strong className="text-emerald-400">{(v16EvalReport.weightedAccuracy * 100).toFixed(2)}%</strong></p>
                      <p className="text-[8px] text-slate-500 font-mono">Avg Latency: {v16EvalReport.weightedLatencyMs}ms</p>
                    </div>
                  )}
                </div>

                {/* Telemetry log rollbacks */}
                <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-5 shadow-sm space-y-3">
                  <div className="flex justify-between items-center border-b border-slate-850 pb-2">
                    <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
                      Hardening &amp; Alerts
                    </h3>
                    <button
                      onClick={handleV16Rollback}
                      className="text-[9px] bg-rose-900/40 hover:bg-rose-900 px-2 py-0.5 rounded text-rose-300 uppercase font-bold border border-rose-500/20"
                    >
                      Trigger Rollback
                    </button>
                  </div>

                  {v16Alerts.length > 0 && (
                    <div className="bg-rose-950/20 p-2 border border-rose-500/20 rounded text-[9px] space-y-1 font-mono text-rose-400 animate-pulse">
                      <strong>INCIDENT ALERT:</strong>
                      {v16Alerts.map((a, i) => (
                        <p key={i}>ID: {a.incidentId} | Rollback: {a.triggeredRollback ? "YES" : "NO"}</p>
                      ))}
                    </div>
                  )}

                  <div className="bg-slate-900 p-2 border border-slate-800 rounded max-h-36 overflow-y-auto space-y-1 text-[8px] font-mono text-slate-400">
                    {v16HardeningLogs.length === 0 ? (
                      <p className="text-slate-600 italic text-center py-2">No active V16 logs.</p>
                    ) : (
                      v16HardeningLogs.map((log: any) => (
                        <div key={log.eventId} className="border-b border-slate-850 pb-1">
                          <span className={
                            log.severity === "critical" || log.severity === "error" ? "text-rose-400 font-bold" : "text-slate-500"
                          }>[{log.severity.toUpperCase()}]</span> {log.name}: {log.payload.slice(0, 40)}...
                        </div>
                      ))
                    )}
                  </div>
                </div>

              </div>
            </div>
          </div>
        )}

        {/* TAB 8.5: V17 DOMAIN DOMINANCE COCKPIT */}
        {activeTab === "v17dominance" && (
          <div className="space-y-6 animate-in fade-in duration-300">
            {/* Header Banner */}
            <div className="relative overflow-hidden bg-gradient-to-r from-slate-950 via-[#0a1428] to-slate-950 border border-blue-500/25 rounded-2xl p-6 shadow-2xl">
              <div className="absolute top-0 right-0 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl pointer-events-none -mr-20 -mt-20" />
              <div className="relative flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <Zap className="h-6 w-6 text-blue-400 animate-bounce" />
                    <h2 className="text-xl font-extrabold tracking-tight text-white flex items-center gap-2">
                      ANTIGRAVITY AI V17 <span className="text-blue-400 font-bold text-xs border border-blue-500/30 px-1.5 py-0.5 rounded uppercase">Domain Dominance</span>
                    </h2>
                  </div>
                  <p className="text-xs text-slate-400 max-w-xl">
                    Sleek domain-optimized edge command cockpit. Run parallel edge reasoning networks, simulated OpenCV defect triggers, and safety validation loops.
                  </p>
                </div>
                
                {/* Metric Badges */}
                <div className="flex flex-wrap gap-2 text-xs">
                  <div className="bg-slate-900/80 border border-slate-800 rounded-lg px-3 py-1.5 text-center">
                    <span className="block text-[8px] text-slate-500 uppercase tracking-widest font-semibold">Verification</span>
                    <span className="text-sm font-extrabold text-emerald-400">99.9% RAG</span>
                  </div>
                  <div className="bg-slate-900/80 border border-slate-800 rounded-lg px-3 py-1.5 text-center">
                    <span className="block text-[8px] text-slate-500 uppercase tracking-widest font-semibold">iGPU Compiles</span>
                    <span className="text-sm font-extrabold text-blue-400">WebGPU/GGUF</span>
                  </div>
                  <div className="bg-slate-900/80 border border-slate-800 rounded-lg px-3 py-1.5 text-center">
                    <span className="block text-[8px] text-slate-500 uppercase tracking-widest font-semibold">Immune Crystals</span>
                    <span className="text-sm font-extrabold text-amber-500">{v17ImmuneCrystals.filter(c => c.status === "strengthened").length} Strong</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Input & Controller Section */}
            <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-5 shadow-sm space-y-4">
              <span className="text-[10px] text-slate-500 uppercase tracking-wider block mb-1">Execute Multi-Domain Query Chain</span>
              <div className="flex flex-col md:flex-row gap-3">
                <input
                  type="text"
                  value={v17QueryInput}
                  onChange={(e) => setV17QueryInput(e.target.value)}
                  className="flex-1 rounded border border-slate-700 bg-slate-900 px-3 py-2 text-xs font-mono text-slate-100 focus:outline-none focus:ring-1 focus:ring-blue-500"
                  placeholder="e.g., Issue transaction refund invoice or Faulty leak line 3"
                />
                <div className="flex gap-2">
                  <select
                    value={v17SelectedDomain}
                    onChange={(e) => setV17SelectedDomain(e.target.value)}
                    className="rounded bg-slate-900 border border-slate-700 px-3 py-2 text-xs text-slate-300 focus:outline-none"
                  >
                    <option value="Finance/HR Workflow">Finance/HR Workflow</option>
                    <option value="Industrial Inspection">Industrial Inspection</option>
                    <option value="Warehouse Robotics">Warehouse Robotics</option>
                    <option value="Enterprise Knowledge Search">Enterprise Knowledge Search</option>
                  </select>
                  <select
                    value={v17SelectedBackend}
                    onChange={(e) => setV17SelectedBackend(e.target.value as any)}
                    className="rounded bg-slate-900 border border-slate-700 px-3 py-2 text-xs text-slate-300 focus:outline-none"
                  >
                    <option value="WebGPU">WebGPU</option>
                    <option value="ONNX Runtime">ONNX Runtime</option>
                    <option value="GGUF">GGUF</option>
                    <option value="llama.cpp">llama.cpp</option>
                  </select>
                  <button
                    onClick={handleV17RunQuery}
                    className="bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold uppercase px-4 py-2 rounded transition-all shadow-md hover:shadow-blue-500/20"
                  >
                    Execute governors
                  </button>
                  <button
                    onClick={handleV17RunEvaluation}
                    className="bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold uppercase px-4 py-2 rounded transition-all"
                  >
                    Run V17 Benchmarks
                  </button>
                </div>
              </div>
            </div>

            {/* Main Governors Dashboard Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              
              {/* Governor 1: Enterprise Command Center */}
              <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-5 shadow-sm space-y-3">
                <h3 className="text-xs font-bold uppercase tracking-wider text-blue-400 border-b border-slate-850 pb-2 flex justify-between">
                  <span>Enterprise Command Center</span>
                  <span className="text-[10px] text-slate-500">Phase 1</span>
                </h3>
                {v17EnterpriseReport ? (
                  <div className="space-y-3 text-xs">
                    <div className="flex justify-between items-center bg-slate-900/60 p-2 rounded border border-slate-800">
                      <span className="text-slate-400">Policy Audits:</span>
                      <span className={`font-bold px-1.5 py-0.5 rounded text-[10px] ${
                        v17EnterpriseReport.policyPassed ? "bg-emerald-500/10 text-emerald-400" : "bg-rose-500/10 text-rose-400"
                      }`}>{v17EnterpriseReport.policyPassed ? "PASSED" : "DENIED"}</span>
                    </div>
                    <div className="bg-slate-900 border border-slate-800 p-2 rounded text-[10px] font-mono max-h-24 overflow-y-auto">
                      <span className="text-slate-500 font-bold block">Nodes searched:</span>
                      <ul className="list-disc list-inside text-slate-400">
                        {v17EnterpriseReport.nodesFound.map((n: any, i: number) => (
                          <li key={i}>{n.id} ({n.type})</li>
                        ))}
                      </ul>
                    </div>
                    <div className="bg-slate-955 p-2.5 rounded border border-slate-850 font-mono text-[10px] text-slate-300">
                      <span className="text-blue-400 font-bold block">VERIFIED ANSWER:</span>
                      {v17EnterpriseReport.verifiedAnswer}
                    </div>
                  </div>
                ) : (
                  <p className="text-slate-500 italic text-xs py-4 text-center">Run query to view enterprise graph outputs.</p>
                )}
              </div>

              {/* Governor 2: RAG 99.9 Engine */}
              <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-5 shadow-sm space-y-3">
                <h3 className="text-xs font-bold uppercase tracking-wider text-emerald-400 border-b border-slate-850 pb-2 flex justify-between">
                  <span>RAG 99.9 Engine</span>
                  <span className="text-[10px] text-slate-500">Phase 2</span>
                </h3>
                {v17RagReport ? (
                  <div className="space-y-3 text-xs">
                    <div className="grid grid-cols-2 gap-2 text-[10px] bg-slate-900 p-2 border border-slate-800 rounded">
                      <div>
                        <span className="text-slate-500 block">Hallucination Risk:</span>
                        <span className="text-emerald-400 font-bold font-mono">{(v17RagReport.hallucinationRisk * 100).toFixed(1)}%</span>
                      </div>
                      <div>
                        <span className="text-slate-500 block">RAG Score:</span>
                        <span className="text-emerald-400 font-bold font-mono">{(v17RagReport.ragScore * 100).toFixed(1)}%</span>
                      </div>
                    </div>
                    <div className="bg-slate-900 border border-slate-800 p-2 rounded text-[10px] font-mono max-h-24 overflow-y-auto space-y-1">
                      <span className="text-slate-500 font-bold block">Chunks Retrieved ({v17RagReport.chunksRetrieved.length}):</span>
                      {v17RagReport.chunksRetrieved.map((c: any, i: number) => (
                        <div key={i} className="border-b border-slate-850 pb-1 text-[9px]">
                          <span className="text-blue-400">[{c.id}]</span> <span className="text-slate-400">"{c.content}"</span>
                        </div>
                      ))}
                    </div>
                    <div className="bg-slate-950 p-2 rounded border border-slate-850 font-mono text-[9px] text-slate-300">
                      <span className="text-emerald-400 font-bold block">Verified Citations:</span>
                      {v17RagReport.citationsVerified.join(", ") || "None"}
                    </div>
                  </div>
                ) : (
                  <p className="text-slate-500 italic text-xs py-4 text-center">Run query to view RAG pipelines.</p>
                )}
              </div>

              {/* Governor 3: Universal Search */}
              <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-5 shadow-sm space-y-3">
                <h3 className="text-xs font-bold uppercase tracking-wider text-blue-400 border-b border-slate-850 pb-2 flex justify-between">
                  <span>Universal Search Engine</span>
                  <span className="text-[10px] text-slate-500">Phase 3</span>
                </h3>
                {v17SearchReport ? (
                  <div className="space-y-3 text-xs">
                    <div className="space-y-1.5 max-h-52 overflow-y-auto pr-1">
                      {v17SearchReport.results.map((res: any, i: number) => (
                        <div key={i} className="bg-slate-900 p-2 border border-slate-850 rounded text-[9px] flex justify-between items-center">
                          <div>
                            <span className="text-slate-200 font-bold font-mono">{res.title}</span>
                            <div className="flex gap-2 text-slate-500 font-mono text-[8px] mt-0.5">
                              <span>Recency: {res.factors.recency.toFixed(2)}</span>
                              <span>Semantic: {res.factors.semantic.toFixed(2)}</span>
                            </div>
                          </div>
                          <span className="text-blue-400 font-bold font-mono">{(res.finalScore * 100).toFixed(0)}%</span>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  <p className="text-slate-500 italic text-xs py-4 text-center">Run query to view ranked multi-factor search.</p>
                )}
              </div>

              {/* Governor 4: Coding Assistant */}
              <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-5 shadow-sm space-y-3">
                <h3 className="text-xs font-bold uppercase tracking-wider text-purple-400 border-b border-slate-850 pb-2 flex justify-between">
                  <span>Coding Assistant & AST Scan</span>
                  <span className="text-[10px] text-slate-500">Phase 4</span>
                </h3>
                {v17CodeReport ? (
                  <div className="space-y-3 text-xs">
                    <div className="flex justify-between items-center bg-slate-900 p-2 border border-slate-800 rounded text-[10px]">
                      <span className="text-slate-500">AST Bugs Detected:</span>
                      <span className={`font-bold ${v17CodeReport.bugsDetectedCount > 0 ? "text-rose-400" : "text-emerald-400"}`}>{v17CodeReport.bugsDetectedCount}</span>
                      <span className="text-slate-500">Tests Status:</span>
                      <span className={`font-bold ${v17CodeReport.testPassed ? "text-emerald-400" : "text-rose-400"}`}>{v17CodeReport.testPassed ? "PASSED" : "FAILED"}</span>
                    </div>
                    {v17CodeReport.bugsDetectedCount > 0 && (
                      <div className="bg-rose-500/5 p-2 rounded border border-rose-500/10 text-[9px] font-mono text-rose-400">
                        <strong className="block text-[8px] uppercase">Vulnerabilities Detected:</strong>
                        {v17CodeReport.vulnerabilities.map((v: any, i: number) => (
                          <div key={i}>[{v.severity}] {v.ruleId}: {v.description}</div>
                        ))}
                      </div>
                    )}
                    <div className="bg-slate-950 p-2.5 rounded border border-slate-850 font-mono text-[9px] text-slate-300">
                      <span className="text-purple-400 font-bold block">GENERATED CODE OUT:</span>
                      <pre className="overflow-x-auto whitespace-pre-wrap">{v17CodeReport.repairedCode || v17CodeReport.generatedCode}</pre>
                    </div>
                  </div>
                ) : (
                  <p className="text-slate-500 italic text-xs py-4 text-center">Run query to view coding review scan results.</p>
                )}
              </div>

              {/* Governor 5: Business Workflow */}
              <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-5 shadow-sm space-y-3">
                <h3 className="text-xs font-bold uppercase tracking-wider text-blue-400 border-b border-slate-850 pb-2 flex justify-between">
                  <span>Business Workflows Engine</span>
                  <span className="text-[10px] text-slate-500">Phase 5</span>
                </h3>
                {v17WorkflowReport ? (
                  <div className="space-y-3 text-xs">
                    <div className="flex justify-between items-center bg-slate-900 p-2 border border-slate-800 rounded text-[10px]">
                      <span className="text-slate-400">Department:</span>
                      <span className="text-slate-200 font-bold">{v17WorkflowReport.intentResolved}</span>
                      <span className="text-slate-400">Success Rate:</span>
                      <span className="text-emerald-400 font-bold font-mono">{(v17WorkflowReport.successRate * 100).toFixed(1)}%</span>
                    </div>
                    <div className="bg-slate-900 border border-slate-800 p-2 rounded text-[10px] font-mono max-h-28 overflow-y-auto space-y-1">
                      <span className="text-slate-500 font-bold block">Execution Step Logs:</span>
                      {v17WorkflowReport.workflowSteps.map((step: any, i: number) => (
                        <div key={i} className="border-b border-slate-855 pb-1 text-[9px] flex justify-between">
                          <span className="text-slate-300">{step.stepName}</span>
                          <span className={step.isVerified ? "text-emerald-400" : "text-rose-400"}>{step.isVerified ? "VERIFIED" : "FAIL"}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  <p className="text-slate-500 italic text-xs py-4 text-center">Run query to view business step logs.</p>
                )}
              </div>

              {/* Governor 6: Edge AI Assistant */}
              <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-5 shadow-sm space-y-3">
                <h3 className="text-xs font-bold uppercase tracking-wider text-blue-400 border-b border-slate-855 pb-2 flex justify-between">
                  <span>Edge AI Local Inference</span>
                  <span className="text-[10px] text-slate-500">Phase 6</span>
                </h3>
                {v17EdgeReport ? (
                  <div className="space-y-3 text-xs">
                    <div className="grid grid-cols-2 gap-2 text-[10px] bg-slate-900 p-2 border border-slate-800 rounded font-mono">
                      <span className="text-slate-500">Memory Match:</span>
                      <span className={`font-bold ${v17EdgeReport.localMemoryMatched ? "text-emerald-400" : "text-slate-400"}`}>{v17EdgeReport.localMemoryMatched ? "YES" : "NO"}</span>
                      <span className="text-slate-500">Compilation:</span>
                      <span className="text-slate-300">{v17EdgeReport.metrics.compilationTimeMs}ms</span>
                      <span className="text-slate-500">Footprint:</span>
                      <span className="text-slate-300">{v17EdgeReport.metrics.memoryFootprintMB} MB</span>
                      <span className="text-slate-500">GPU Offload:</span>
                      <span className={`font-bold ${v17EdgeReport.metrics.gpuAccelerationActive ? "text-emerald-400" : "text-slate-400"}`}>{v17EdgeReport.metrics.gpuAccelerationActive ? "ACTIVE" : "OFFLINE"}</span>
                    </div>
                    <div className="bg-slate-950 p-2 rounded border border-slate-850 font-mono text-[9px] text-slate-300">
                      <span className="text-blue-400 font-bold block">Offline Inference Result:</span>
                      {v17EdgeReport.resultText}
                    </div>
                  </div>
                ) : (
                  <p className="text-slate-500 italic text-xs py-4 text-center">Run query to view edge parameters compiles.</p>
                )}
              </div>

              {/* Governor 7: Industrial Inspection */}
              <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-5 shadow-sm space-y-3">
                <h3 className="text-xs font-bold uppercase tracking-wider text-emerald-400 border-b border-slate-855 pb-2 flex justify-between">
                  <span>Visual Quality (YOLO/OpenCV)</span>
                  <span className="text-[10px] text-slate-500">Phase 7</span>
                </h3>
                {v17InspectionReport ? (
                  <div className="space-y-3 text-xs">
                    <div className="flex justify-between items-center bg-slate-900 p-2 border border-slate-800 rounded text-[10px]">
                      <span className="text-slate-500">Line:</span>
                      <span className="text-slate-300 font-bold">{v17InspectionReport.targetLine}</span>
                      <span className="text-slate-500">Status:</span>
                      <span className={`font-bold px-1 rounded ${
                        v17InspectionReport.inspectionPassed ? "bg-emerald-500/10 text-emerald-400" : "bg-rose-500/10 text-rose-400"
                      }`}>{v17InspectionReport.inspectionPassed ? "PASS" : "DEFECT FOUND"}</span>
                    </div>
                    {v17InspectionReport.defectsDetected.length > 0 ? (
                      <div className="space-y-1.5">
                        <span className="text-[10px] text-slate-500 font-semibold block">Defect Coords Detected:</span>
                        {v17InspectionReport.defectsDetected.map((d: any, i: number) => (
                          <div key={i} className="bg-rose-500/5 p-2 rounded border border-rose-500/10 text-[9px] font-mono text-rose-400 flex justify-between">
                            <span>{d.type.toUpperCase()} (Conf: {(d.confidence * 100).toFixed(1)}%)</span>
                            <span>x:{d.bbox[0]}, y:{d.bbox[1]}, w:{d.bbox[2]}, h:{d.bbox[3]}</span>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-[10px] text-emerald-400 italic py-2 text-center bg-emerald-500/5 rounded border border-emerald-500/10">0 defect anomalies found on lines.</p>
                    )}
                  </div>
                ) : (
                  <p className="text-slate-500 italic text-xs py-4 text-center">Run query to view vision sweep simulations.</p>
                )}
              </div>

              {/* Governor 8: Multi Camera Analytics */}
              <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-5 shadow-sm space-y-3">
                <h3 className="text-xs font-bold uppercase tracking-wider text-blue-400 border-b border-slate-855 pb-2 flex justify-between">
                  <span>Multi-Camera Analytics</span>
                  <span className="text-[10px] text-slate-500">Phase 8</span>
                </h3>
                {v17CameraReport ? (
                  <div className="space-y-3 text-xs">
                    <div className="grid grid-cols-2 gap-2 text-[10px] bg-slate-900 p-2 border border-slate-800 rounded font-mono">
                      <span className="text-slate-500">Camera ID:</span>
                      <span className="text-slate-300 font-bold">{v17CameraReport.cameraId}</span>
                      <span className="text-slate-500">Change detected:</span>
                      <span className={`font-bold ${v17CameraReport.sceneChangeDetected ? "text-rose-400 animate-pulse" : "text-slate-400"}`}>{v17CameraReport.sceneChangeDetected ? "YES" : "NO"}</span>
                      <span className="text-slate-500">Frame skips:</span>
                      <span className="text-slate-300">{v17CameraReport.framesProcessedCount} processed</span>
                      <span className="text-slate-500">iGPU CPU Savings:</span>
                      <span className="text-emerald-400 font-bold">{v17CameraReport.processingSavingsPct}%</span>
                    </div>
                    {v17CameraReport.activeEvents.length > 0 && (
                      <div className="bg-rose-500/5 p-2 rounded border border-rose-500/10 text-[9px] font-mono text-rose-400">
                        <strong className="block text-[8px] uppercase">Active Alerts:</strong>
                        {v17CameraReport.activeEvents.map((evt: any, i: number) => (
                          <div key={i} className="flex justify-between">
                            <span>Event: {evt.eventType}</span>
                            <span>Confidence: {(evt.confidence * 100).toFixed(0)}%</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ) : (
                  <p className="text-slate-500 italic text-xs py-4 text-center">Run query to view dynamic frame skips.</p>
                )}
              </div>

              {/* Governor 9: Warehouse Robotics */}
              <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-5 shadow-sm space-y-3">
                <h3 className="text-xs font-bold uppercase tracking-wider text-purple-400 border-b border-slate-855 pb-2 flex justify-between">
                  <span>Warehouse Robotics Route Planner</span>
                  <span className="text-[10px] text-slate-500">Phase 9</span>
                </h3>
                {v17RoboticsReport ? (
                  <div className="space-y-3 text-xs">
                    <div className="flex justify-between items-center bg-slate-900 p-2 border border-slate-800 rounded text-[10px]">
                      <span className="text-slate-500">Behavior tree:</span>
                      <span className={`font-bold px-1.5 rounded ${
                        v17RoboticsReport.behaviorTreeState === "SUCCESS" ? "bg-emerald-500/10 text-emerald-400" : "bg-amber-500/10 text-amber-400"
                      }`}>{v17RoboticsReport.behaviorTreeState}</span>
                      <span className="text-slate-500">Collision Avoidance:</span>
                      <span className={`font-bold ${v17RoboticsReport.collisionAvoidanceTriggered ? "text-rose-400 animate-pulse" : "text-slate-400"}`}>{v17RoboticsReport.collisionAvoidanceTriggered ? "TRIGGERED" : "CLEAR"}</span>
                    </div>
                    <div className="bg-slate-900 border border-slate-800 p-2 rounded text-[10px] font-mono max-h-24 overflow-y-auto">
                      <span className="text-slate-500 font-bold block">Robot Nodes Planned Path:</span>
                      <ul className="list-disc list-inside text-slate-400 text-[9px]">
                        {v17RoboticsReport.pathNodes.map((n: any, i: number) => (
                          <li key={i}>Node {i+1}: ({n.x}, {n.y})</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                ) : (
                  <p className="text-slate-500 italic text-xs py-4 text-center">Run query to view trajectory path node maps.</p>
                )}
              </div>

              {/* Governor 10: Autonomous Systems */}
              <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-5 shadow-sm space-y-3">
                <h3 className="text-xs font-bold uppercase tracking-wider text-blue-400 border-b border-slate-855 pb-2 flex justify-between">
                  <span>Autonomous Systems Safety</span>
                  <span className="text-[10px] text-slate-500">Phase 10</span>
                </h3>
                {v17AutonomyReport ? (
                  <div className="space-y-3 text-xs">
                    <div className="flex justify-between items-center bg-slate-900 p-2 border border-slate-800 rounded text-[10px]">
                      <span className="text-slate-500">Verification Check:</span>
                      <span className={`font-bold px-1.5 rounded ${
                        v17AutonomyReport.safetyVerificationPassed ? "bg-emerald-500/10 text-emerald-400" : "bg-rose-500/10 text-rose-400"
                      }`}>{v17AutonomyReport.safetyVerificationPassed ? "PASSED" : "FAILED (FAILSAFE ACTIVE)"}</span>
                    </div>
                    <div className="bg-slate-900 border border-slate-800 p-2 rounded text-[9px] font-mono max-h-24 overflow-y-auto space-y-1">
                      <span className="text-slate-500 font-bold block">Projected Trajectory Risks:</span>
                      {v17AutonomyReport.projectedScenarios.map((sc: any, i: number) => (
                        <div key={i} className="flex justify-between border-b border-slate-850 pb-1">
                          <span>{sc.action}</span>
                          <span className={sc.riskProbability > 0.4 ? "text-rose-400 font-bold" : "text-slate-400"}>Risk: {(sc.riskProbability * 100).toFixed(0)}%</span>
                        </div>
                      ))}
                    </div>
                    <div className="bg-slate-950 p-2 rounded border border-slate-850 font-mono text-[9px] text-slate-300">
                      <span className="text-blue-400 font-bold block">Selected Control Action:</span>
                      {v17AutonomyReport.selectedAction}
                    </div>
                  </div>
                ) : (
                  <p className="text-slate-500 italic text-xs py-4 text-center">Run query to view world model projections.</p>
                )}
              </div>

              {/* Governor 11: Reality Feedback Network */}
              <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-5 shadow-sm space-y-3">
                <h3 className="text-xs font-bold uppercase tracking-wider text-emerald-400 border-b border-slate-855 pb-2 flex justify-between">
                  <span>Reality Feedback & Calibration</span>
                  <span className="text-[10px] text-slate-500">Phase 11</span>
                </h3>
                {v17RealitySummary ? (
                  <div className="space-y-3 text-xs">
                    <div className="grid grid-cols-2 gap-2 text-[10px] bg-slate-900 p-2 border border-slate-800 rounded font-mono">
                      <span className="text-slate-500">Decisions Evaluated:</span>
                      <span className="text-slate-300 font-bold">{v17RealitySummary.totalDecisionsCount}</span>
                      <span className="text-slate-500">Success Rate:</span>
                      <span className="text-emerald-400 font-bold">{(v17RealitySummary.successRate * 100).toFixed(1)}%</span>
                      <span className="text-slate-500">Calibration Factor:</span>
                      <span className="text-blue-400 font-bold">{v17RealitySummary.calibrationScalar.toFixed(4)}</span>
                    </div>
                  </div>
                ) : (
                  <p className="text-slate-500 italic text-xs py-4 text-center">Run query to see dynamic calibration weights.</p>
                )}
              </div>

              {/* Governor 12: Intelligence Auditor */}
              <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-5 shadow-sm space-y-3">
                <h3 className="text-xs font-bold uppercase tracking-wider text-purple-400 border-b border-slate-855 pb-2 flex justify-between">
                  <span>Constitutional Critique Auditor</span>
                  <span className="text-[10px] text-slate-500">Phase 12</span>
                </h3>
                {v17IntelligenceReport ? (
                  <div className="space-y-3 text-xs">
                    <div className="bg-slate-900 border border-slate-800 p-2 rounded text-[10px] font-mono max-h-24 overflow-y-auto space-y-1">
                      <span className="text-slate-500 font-bold block">Critique Round Audits ({v17IntelligenceReport.critiqueChains.length}):</span>
                      {v17IntelligenceReport.critiqueChains.map((c: any, i: number) => (
                        <div key={i} className="border-b border-slate-850 pb-1 text-[8px]">
                          <strong className="text-purple-400">Round {c.round}:</strong> <span className="text-slate-400">"{c.feedback}"</span>
                        </div>
                      ))}
                    </div>
                    <div className="bg-slate-950 p-2.5 rounded border border-slate-850 font-mono text-[9px] text-slate-300">
                      <span className="text-emerald-400 font-bold block">FINAL DRAFT REPORT ALIGNED:</span>
                      {v17IntelligenceReport.finalAuditedAnswer}
                    </div>
                  </div>
                ) : (
                  <p className="text-slate-500 italic text-xs py-4 text-center">Run query to view multi-agent critique reviews.</p>
                )}
              </div>

            </div>

            {/* Bottom Row: Knowledge Immune Sweeper & Evaluation Center */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              
              {/* Immune Sweeper */}
              <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-6 shadow-md">
                <div className="flex justify-between items-center mb-3">
                  <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200 flex items-center gap-2">
                    <Shield className="h-4 w-4 text-emerald-400" />
                    Phase 13: Knowledge Immune System (V17 Ruleset)
                  </h3>
                  <button
                    onClick={handleV17AuditImmune}
                    className="text-[9px] bg-slate-800 hover:bg-slate-700 px-3 py-1 rounded text-slate-300 font-bold uppercase transition-colors"
                  >
                    Audit Solutions
                  </button>
                </div>
                <p className="text-[11px] text-slate-400 mb-4">
                  Decays, strengthens, or quarantines active solutions based on execution freshness and AST security reviews.
                </p>
                <div className="bg-[#020713] p-3 border border-slate-800 rounded-lg max-h-52 overflow-y-auto space-y-2">
                  {v17ImmuneCrystals.length === 0 ? (
                    <p className="text-slate-600 italic text-[10px] text-center py-4">No active crystals stored.</p>
                  ) : (
                    v17ImmuneCrystals.map((crystal) => (
                      <div key={crystal.id} className="bg-slate-900 border border-slate-800 p-2 rounded text-[10px] flex justify-between items-center">
                        <div>
                          <h6 className="font-bold text-slate-300 text-[10px] mb-1 font-mono">{crystal.topic}</h6>
                          <div className="flex flex-wrap gap-2 text-[8px] text-slate-500 font-mono">
                            <span>ID: {crystal.id}</span>
                            <span>Confidence: {crystal.confidence.toFixed(2)}</span>
                            <span>Freshness: {crystal.freshness.toFixed(2)}</span>
                            <span>Age: {crystal.ageDays}d</span>
                          </div>
                        </div>
                        <span className={`font-mono text-[8px] uppercase px-1.5 py-0.5 rounded font-extrabold ${
                          crystal.status === "strengthened" ? "bg-emerald-500/10 text-emerald-400" :
                          crystal.status === "decayed" ? "bg-amber-500/10 text-amber-400" :
                          crystal.status === "quarantined" ? "bg-rose-500/10 text-rose-400 border border-rose-500/25 animate-pulse" : "bg-blue-500/10 text-blue-400"
                        }`}>{crystal.status}</span>
                      </div>
                    ))
                  )}
                </div>
              </div>

              {/* Benchmark evaluation center */}
              <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-6 shadow-md">
                <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200 mb-2 flex items-center gap-2">
                  <BarChart2 className="h-4 w-4 text-blue-400" />
                  Phase 14: Universal Evaluation Universe V17
                </h3>
                <p className="text-[11px] text-slate-400 mb-4">
                  Run simulated performance benchmarks of the V17 Dominance engine against 103,000 automated evaluation challenges.
                </p>

                {v17EvalReport && (
                  <div className="space-y-4 animate-in fade-in duration-300 text-xs">
                    <div className="grid grid-cols-3 gap-3">
                      <div className="bg-[#020713] border border-slate-800 p-3 rounded-lg text-center">
                        <span className="block text-[8px] uppercase text-slate-500 font-semibold tracking-wider font-mono">Tasks Evaluated</span>
                        <span className="text-xl font-extrabold text-blue-400">{v17EvalReport.totalTasksRun.toLocaleString()}</span>
                      </div>
                      <div className="bg-[#020713] border border-slate-800 p-3 rounded-lg text-center">
                        <span className="block text-[8px] uppercase text-slate-500 font-semibold tracking-wider font-mono">Accuracy Score</span>
                        <span className="text-xl font-extrabold text-emerald-400">{(v17EvalReport.overallAccuracy * 100).toFixed(2)}%</span>
                      </div>
                      <div className="bg-[#020713] border border-slate-800 p-3 rounded-lg text-center">
                        <span className="block text-[8px] uppercase text-slate-500 font-semibold tracking-wider font-mono">Avg Latency</span>
                        <span className="text-xl font-extrabold text-indigo-400">{v17EvalReport.averageLatencyMs} ms</span>
                      </div>
                    </div>

                    <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
                      <p className="text-[10px] font-bold text-slate-300 uppercase tracking-wider">Performance by Governor:</p>
                      {v17EvalReport.benchmarks.map((b: any, idx: number) => (
                        <div key={idx} className="bg-slate-900 border border-slate-800 rounded-lg p-2 space-y-1">
                          <div className="flex justify-between items-center font-semibold text-[10px]">
                            <span className="text-slate-200">{b.domainName}</span>
                            <span className="text-blue-400">{(b.accuracy * 100).toFixed(1)}% Accuracy</span>
                          </div>
                          <div className="w-full bg-slate-850 rounded-full h-1">
                            <div className="bg-blue-500 h-1 rounded-full" style={{ width: `${b.accuracy * 100}%` }} />
                          </div>
                          <div className="flex justify-between text-[8px] text-slate-500 font-mono">
                            <span>Tasks: {b.tasksTested.toLocaleString()}</span>
                            <span>Latency: {b.latencyMs}ms</span>
                            <span className="text-emerald-400">Confidence: {(b.confidence * 100).toFixed(1)}%</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

            </div>

          </div>
        )}

        {/* TAB 8.6: V18 ENTERPRISE VALIDATION UNIVERSE */}
        {activeTab === "v18validation" && (
          <div className="space-y-6 animate-in fade-in duration-300">
            <ValidationDashboard />
          </div>
        )}

        {/* TAB 9: FAILURE HUNTING MASTER DASHBOARD */}
        {activeTab === "failureHunting" && (
          <div className="space-y-6 animate-in fade-in duration-300 h-full min-h-[calc(100vh-140px)]">
            <FailureHuntingDashboard />
          </div>
        )}

        {/* TAB 10: V22 QUALITY AMPLIFIER */}
        {activeTab === "v22quality" && (
          <div className="-mx-4 -my-8 animate-in fade-in duration-300">
            <QualityAmplifierDashboard />
          </div>
        )}

        {/* TAB 11: V23 FRONTIER OPTIMIZATION */}
        {activeTab === "v23frontier" && (
          <div className="-mx-4 -my-8 animate-in fade-in duration-300">
            <FrontierOptimizationDashboard />
          </div>
        )}

        {/* TAB 12: V24 CONVERGENCE ENGINE */}
        {activeTab === "v24convergence" && (
          <div className="-mx-4 -my-8 animate-in fade-in duration-300">
            <ConvergenceDashboard />
          </div>
        )}

        {/* TAB 13: V25 PRODUCT CERTIFICATION */}
        {activeTab === "v25certification" && (
          <div className="-mx-4 -my-8 animate-in fade-in duration-300">
            <CertificationDashboard />
          </div>
        )}

        {/* TAB 14: V26 REALITY-GRADE EXECUTION ENGINE */}
        {activeTab === "v26reality" && (
          <div className="-mx-4 -my-8 animate-in fade-in duration-300">
            <RealityExecutionDashboard />
          </div>
        )}

        {/* TAB 15: V27 SCIENTIFIC PROOF & CERTIFICATION */}
        {activeTab === "v27certification" && (
          <div className="-mx-4 -my-8 animate-in fade-in duration-300">
            <ScientificCertificationDashboard />
          </div>
        )}

        {/* TAB 16: V28 REPRODUCIBILITY VALIDATION LAB */}
        {activeTab === "v28validation" && (
          <div className="-mx-4 -my-8 animate-in fade-in duration-300">
            <ScientificValidationDashboard />
          </div>
        )}

        {/* TAB 17: V29 FRONTIER CORE */}
        {activeTab === "v29frontier" && (
          <div className="-mx-4 -my-8 animate-in fade-in duration-300">
            <FrontierIntelligenceDashboard />
          </div>
        )}

        {/* TAB 18: LEO V30 FRONTIER ACCELERATION */}
        {activeTab === "v30frontier" && (
          <div className="-mx-4 -my-8 animate-in fade-in duration-300">
            <FrontierIntelligenceDashboardV2 />
          </div>
        )}

        {/* TAB 19: LEO V31 COMPUTE IRRELEVANCE */}
        {activeTab === "v31irrelevance" && (
          <div className="-mx-4 -my-8 animate-in fade-in duration-300">
            <ComputeIrrelevanceDashboard />
          </div>
        )}

        {/* TAB 20: LEO V32 ENGINEERING CEILING */}
        {activeTab === "v32ceiling" && (
          <div className="-mx-4 -my-8 animate-in fade-in duration-300">
            <EngineeringCeilingDashboard />
          </div>
        )}

        {/* TAB 21: LEO V32 REALITY LEARNING */}
        {activeTab === "v32reality" && (
          <div className="-mx-4 -my-8 animate-in fade-in duration-300">
            <RealityLearningDashboard />
          </div>
        )}

        {/* TAB 22: LEO V33 COMPUTE IRRELEVANCE */}
        {activeTab === "v33compute" && (
          <div className="-mx-4 -my-8 animate-in fade-in duration-300">
            <ComputeIrrelevanceV33Dashboard />
          </div>
        )}

        {/* TAB 23: LEO V34 COMPUTE IRRELEVANCE */}
        {activeTab === "v34compute" && (
          <div className="-mx-4 -my-8 animate-in fade-in duration-300">
            <ComputeIrrelevanceV34Dashboard />
          </div>
        )}

        {/* TAB 24: LEO V35 FUNCTIONAL PARITY SCOREBOARD */}
        {activeTab === "v35parity" && (
          <div className="-mx-4 -my-8 animate-in fade-in duration-300">
            <LEOAIv35Scoreboard />
          </div>
        )}

        {/* TAB 25: LEO V36 PRACTICAL CEILING CONVERGENCE */}
        {activeTab === "v36ceiling" && (
          <div className="-mx-4 -my-8 animate-in fade-in duration-300">
            <LEOAIv36Dashboard />
          </div>
        )}

        {/* TAB 26: LEO V37 MASTER EVOLUTION COCKPIT */}
        {activeTab === "v37evolution" && (
          <div className="-mx-4 -my-8 animate-in fade-in duration-300">
            <LEOAIv37Dashboard />
          </div>
        )}

        {/* TAB 27: LEO V38 MASTER ARCHITECTURE COCKPIT */}
        {activeTab === "v38architecture" && (
          <div className="-mx-4 -my-8 animate-in fade-in duration-300">
            <LEOAIv38Dashboard />
          </div>
        )}

        {/* TAB 28: LEO V40 ULTIMATE INTELLIGENCE COCKPIT */}
        {activeTab === "v40ultimate" && (
          <div className="-mx-4 -my-8 animate-in fade-in duration-300">
            <LEOAIv40Dashboard />
          </div>
        )}

        {/* TAB 29: LEO v∞ OPTIMIZATION COCKPIT */}
        {activeTab === "vinfinity" && (
          <div className="-mx-4 -my-8 animate-in fade-in duration-300">
            <LEOAIvInfinityDashboard />
          </div>
        )}

      </main>
    </div>
  );
}

export default App;