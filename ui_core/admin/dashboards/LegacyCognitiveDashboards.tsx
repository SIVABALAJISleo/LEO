import React, { useState, useEffect } from "react";
import {
  fetchLeoStatus,
  fetchDevOpsStatus,
  configureDevOps,
  sendStripeWebhook,
  DevOpsSettings,
} from "../../lib/api";
import { QuerySimulationConsole } from "../../components/dashboard/QuerySimulationConsole";
import { BenchmarkLeaderboard } from "../../components/dashboard/BenchmarkLeaderboard";
import { useLeoStatus } from "../../contexts/LeoStatusContext";

import {
  Activity,
  Cpu,
  HardDrive,
  Layers,
  Zap,
  AlertTriangle,
  Play,
  Shield,
  RefreshCw,
  AlertCircle,
  Sparkles,
  MessageSquare,
  CheckCircle,
  Terminal,
  HelpCircle,
  ArrowRight,
  Settings,
  BarChart2,
  Brain,
  GitBranch,
  Crosshair,
  FlaskConical,
  Gauge,
  LineChart,
  Award,
  Scale,
  ShieldCheck,
} from "lucide-react";

import {
  IntentCanonicalizer,
  LanguageRecoveryEngine,
  ReasoningValidator,
  DeepPlanner,
  SelfCritic,
  DebateCoordinator,
  EvaluationCenter,
  MemoryQualityMonitor,
  CrystalAuditor,
  NoveltyResearchEngine,
  FormalReasoningEngine,
  VerificationOrchestrator,
  WorldModelEngineV2,
  RealityFeedbackLoop,
  MetaLearningGovernor,
  KnowledgeGovernor,
  MemoryGovernorV2,
  IntentCanonicalizerV2,
  LanguageRecoveryEngineV2,
  DebateEngineV2,
  PlannerV2,
  NoveltyDiscoveryEngineV2,
  ResearchEngineV2,
  EvaluationCenterV2,
} from "../../src/cognitive";

import { V42Dashboard } from "../../components/v42/V42Dashboard";

// Import V14 Engines
import {
  IntentReconstructionEngine,
  ReconstructedIntent,
} from "../../src/engines/intentReconstructionEngine";
import {
  DeepReasoningEngine,
  ReasoningType,
  ReasoningResult,
} from "../../src/engines/deepReasoningEngine";
import {
  ToolVerificationEngine,
  VerificationOutput,
} from "../../src/engines/toolVerificationEngine";
import { SelfCritiqueEngine, CritiqueReport } from "../../src/engines/selfCritiqueEngine";
import {
  EvaluationCenter as EvaluationCenterV14,
  EvaluationReport,
} from "../../src/evaluation/evaluationCenter";
import { RealityFeedbackEngine, FeedbackEntry } from "../../src/engines/realityFeedbackEngine";
import {
  KnowledgeGovernor as KnowledgeGovernorV14,
  KnowledgeItem,
} from "../../src/engines/knowledgeGovernor";
import {
  MemoryGovernor as MemoryGovernorV14,
  V14MemoryBlock,
} from "../../src/engines/memoryGovernor";
import { DebateEngine as DebateEngineV14, DebateSessionV14 } from "../../src/engines/debateEngine";

// Import V15 Engines
import {
  EvaluationUniverse,
  UniverseEvaluationReport,
  SelfCritiqueEngineV2,
  SelfCritiqueV2Report,
  UniversalReasoningEngine,
  ParadigmResult,
  ReasoningParadigm,
  DebateFramework,
  DebateSessionReport,
  ToolVerifier,
  ToolVerifierReport,
  RealityFeedbackSystem,
  FeedbackLog,
  CalibrationReport,
  KnowledgeImmuneSystem,
  KnowledgeCrystal,
  MemoryImmuneSystem,
  MemoryBlock,
  ImmuneAuditReport,
  MetaLearningGovernor as MetaLearningGovernorV15,
  StrategyMetric,
  WorldModelV3,
  SimulationResultV3,
  DiscoveryEngineV3,
  DiscoveryReport,
  IntentReconstructionEngine as IntentReconstructionEngineV15,
  IntentReconstructionReport,
  ConfidenceEngine as ConfidenceEngineV15,
  CalibrationResponse,
  DistributedMesh,
  MeshNode,
  ConflictResolutionReport,
  HardeningTelemetry,
  TelemetryEvent,
  iGPUAccelerationEngine as iGPUAccelerationEngineV15,
  iGPUMetrics as iGPUMetricsV15,
  SelfImprovementLoop,
  SelfImprovementReport,
} from "../../src/cognitive/v15index";

// Import V16 Engines
import {
  EvaluationUniverseV16,
  UniverseV16Report,
  UniversalReasoningCore,
  FormalProofEngine,
  TheoremSolver,
  ProofTelemetry,
  ProofEngineReport,
  VerificationMesh,
  VerificationCheckV16,
  VerificationMeshReport,
  RealityFeedbackEngineV3,
  KnowledgeImmuneSystem as KnowledgeImmuneSystemV16,
  MemoryImmuneSystem as MemoryImmuneSystemV16,
  MetaLearningGovernor as MetaLearningGovernorV16,
  DiscoveryEngineV4,
  WorldModelV4,
  DebateFrameworkV16,
  DebateV16Report,
  IntentReconstructionEngine as IntentReconstructionEngineV16,
  IntentReconstructionReport as IntentReconstructionReportV16,
  ConfidenceEngineV16,
  HardeningTelemetryV16,
  IncidentAlertV16,
  iGPUAccelerationEngineV16,
  iGPUMetricsV16,
} from "../../src/cognitive/v16index";

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
  KnowledgeImmuneSystem as KnowledgeImmuneSystemV17,
} from "../../src/cognitive/v17index";

interface LegacyCognitiveDashboardsProps {
  activeTab: string;
}

export default function LegacyCognitiveDashboards({ activeTab }: LegacyCognitiveDashboardsProps) {
  const { status, error } = useLeoStatus();

  // --- V17 Domain Dominance States ---
  const [v17QueryInput, setV17QueryInput] = useState("Issue transaction refund invoice");
  const [v17SelectedDomain, setV17SelectedDomain] = useState<string>("Finance/HR Workflow");
  const [v17SelectedBackend, setV17SelectedBackend] = useState<
    "WebGPU" | "ONNX Runtime" | "GGUF" | "llama.cpp"
  >("WebGPU");
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
  const [v16SelectedParadigm, setV16SelectedParadigm] =
    useState<ReasoningParadigm>("Systems Thinking");
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
  const [v16ReconstructReport, setV16ReconstructReport] =
    useState<IntentReconstructionReportV16 | null>(null);
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
  const [v15SelectedParadigm, setV15SelectedParadigm] =
    useState<ReasoningParadigm>("Systems Thinking");
  const [v15EvalReport, setV15EvalReport] = useState<UniverseEvaluationReport | null>(null);
  const [v15CritiqueReport, setV15CritiqueReport] = useState<SelfCritiqueV2Report | null>(null);
  const [v15ReasoningResult, setV15ReasoningResult] = useState<ParadigmResult | null>(null);
  const [v15DebateReport, setV15DebateReport] = useState<DebateSessionReport | null>(null);
  const [v15VerifierReport, setV15VerifierReport] = useState<ToolVerifierReport | null>(null);
  const [v15FeedbackHistory, setV15FeedbackHistory] = useState<FeedbackLog[]>([]);
  const [v15Calibration, setV15Calibration] = useState<CalibrationReport | null>(null);
  const [v15Crystals, setV15Crystals] = useState<KnowledgeCrystal[]>([]);
  const [v15Memories, setV15Memories] = useState<MemoryBlock[]>([]);
  const [v15ImprovementReport, setV15ImprovementReport] = useState<SelfImprovementReport | null>(
    null,
  );
  const [v15DiscoveryReport, setV15DiscoveryReport] = useState<DiscoveryReport | null>(null);
  const [v15ReconstructReport, setV15ReconstructReport] =
    useState<IntentReconstructionReport | null>(null);
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
    const enterprise = enterpriseV17.searchCompanyKnowledge(v17QueryInput);
    setV17EnterpriseReport(enterprise);

    const rag = ragV17.queryRAG(v17QueryInput);
    setV17RagReport(rag);

    const search = searchV17.executeUniversalSearch(v17QueryInput);
    setV17SearchReport(search);

    const code = codeV17.generateAndVerifyCode(v17QueryInput);
    setV17CodeReport(code);

    const workflow = workflowV17.executeBusinessWorkflow(v17QueryInput);
    setV17WorkflowReport(workflow);

    const edge = edgeV17.executeLocalTask(v17QueryInput, v17SelectedBackend);
    setV17EdgeReport(edge);

    const inspection = inspectionV17.runVisualInspection(v17QueryInput);
    setV17InspectionReport(inspection);

    const camera = cameraV17.processCameraFeed(v17QueryInput, 15.4);
    setV17CameraReport(camera);

    const robotics = roboticsV17.planRoute("agv-dashboard", { x: 45, y: 72 });
    setV17RoboticsReport(robotics);

    const autonomy = autonomyV17.verifyAutonomyAction(v17QueryInput);
    setV17AutonomyReport(autonomy);

    const critiqueResult = intelligenceV17.auditAnswerQuality(
      v17QueryInput,
      enterprise.verifiedAnswer ||
        rag.chunksRetrieved.map((c) => c.content).join("\n") ||
        "No source text.",
    );
    setV17IntelligenceReport(critiqueResult);

    realityV17.logRealityCheck(
      "decision-" + Date.now().toString().slice(-4),
      v17SelectedDomain,
      100,
      106,
    );
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
    const recon = reconV15.reconstructIntent(v15QueryInput);
    setV15ReconstructReport(recon);

    const reason = reasoningV15.performReasoning(recon.reconstructedQuery, v15SelectedParadigm);
    setV15ReasoningResult(reason);

    const verify = verifierV15.verifyAnswer(recon.reconstructedQuery, reason.conclusion);
    setV15VerifierReport(verify);

    const critique = selfCritiqueV15.executeSelfCritique(
      recon.reconstructedQuery,
      verify.repairedAnswer,
    );
    setV15CritiqueReport(critique);

    const confidence = confidenceV15.calibrateOutput(
      critique.finalAnswer,
      reason.confidenceScore,
      1.0 - critique.hallucinationRatePct,
      verify.checks.filter((c) => c.status === "verified").length,
      verify.checks.length,
    );
    setV15ConfidenceReport(confidence);

    hardeningV15.logTelemetry("V15 Query Processed", {
      query: v15QueryInput,
      confidence: confidence.calibratedConfidence,
    });
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
    feedbackV15.logRealityFeedback(
      "p-v15-" + Date.now().toString().slice(-4),
      "intentAccuracyWeight",
      100,
      108,
    );
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
    const recon = reconV16.reconstructIntent(v16QueryInput);
    setV16ReconstructReport(recon);

    const reason = reasoningV16.reason(recon.reconstructedQuery, v16SelectedParadigm);
    setV16ReasoningResult(reason);

    const verify = verifierV16.verifyAnswer(recon.reconstructedQuery, reason.conclusion);
    setV16VerifierReport(verify);

    const confidence = confidenceV16.calibrateOutputV16(
      verify.repairedAnswer,
      reason.confidenceScore,
      verify.overallScore,
      verify.checksLog.filter((c) => c.status === "verified").length,
      verify.checksLog.length,
    );
    setV16ConfidenceReport(confidence);

    const scenario = worldV16.simulateWorldState(recon.reconstructedQuery);
    setV16ScenarioReport(scenario);

    hardeningV16.logV16Event(
      "V16 Query Processed",
      { query: v16QueryInput, confidence: confidence.calibratedConfidence },
      "info",
    );
    setV16HardeningLogs([...hardeningV16.getEventsLog()]);
    setV16Alerts([...hardeningV16.getV16Alerts()]);
  };

  const handleV16Debate = () => {
    const report = debateV16.executeDebateCycle(v16QueryInput);
    setV16DebateReport(report);
  };

  const handleV16RunProof = () => {
    const report = proofV16.verifyClaim(
      v16QueryInput,
      "local logic correctness",
      v16SelectedSolver,
    );
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
    feedbackV16.logRealityEvent(
      "p-v16-" + Date.now().toString().slice(-4),
      "predictionAccuracy",
      100,
      110,
    );
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
    reasoningConfidence: 0.9,
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
  const [theoremClaim, setTheoremClaim] = useState(
    "Sum of two positive integers is always positive",
  );
  const [theoremResult, setTheoremResult] = useState<any>(null);
  const [verificationQuery, setVerificationQuery] = useState("Solve: 452 * 231");
  const [verificationOutput, setVerificationOutput] = useState<any>(null);
  const [v13ScenarioQuery, setV13ScenarioQuery] = useState(
    "Startup SaaS launch dynamic compute pricing",
  );
  const [v13ScenarioReport, setV13ScenarioReport] = useState<any>(null);
  const [predictedValue, setPredictedValue] = useState("250");
  const [observedValue, setObservedValue] = useState("410");
  const [feedbackRecords, setFeedbackRecords] = useState<any[]>([]);
  const [feedbackWeights, setFeedbackWeights] = useState<any>({
    crystallizationWeight: 0.95,
    localInferenceConfidence: 0.9,
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
    const rawAnswer =
      v14ReasoningResult?.conclusion ||
      "Setting up local model training needs correct GPU configuration.";
    const res = toolVerifyV14.verifyOutput(v14Query, rawAnswer);
    setV14VerifyOutput(res);
  };

  const handleV14Critique = () => {
    const rawAnswer =
      v14VerifyOutput?.repairedContent ||
      v14ReasoningResult?.conclusion ||
      "Setting up local model training needs correct GPU configuration.";
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
    realityFeedbackV14.logFeedback(
      "v14-pred-" + Date.now().toString().slice(-4),
      "intentAccuracyWeight",
      p,
      o,
    );
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
    knowledgeGovV14.addCrystal(v14NewCrystalTopic, 0.95, 0.9);
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
    feedbackLoopInstance.logReality(
      "pred-" + Date.now().toString().slice(-4),
      "localInferenceConfidence",
      p,
      o,
    );
    setFeedbackRecords([...feedbackLoopInstance.getHistory()]);
    setFeedbackWeights({ ...feedbackLoopInstance.getModelWeights() });
  };

  // Release Evaluation Report
  const evalCenter = new EvaluationCenter();
  const evaluationReport = evalCenter.runReleaseVerification();

  useEffect(() => {
    const loadDevOps = async () => {
      try {
        const data = await fetchDevOpsStatus();
        setDevOps(data);
      } catch (err) {
        console.error("Failed to load DevOps status:", err);
      }
    };
    loadDevOps();
  }, []);

  // Run V11 Cognitive Engines
  const handleRunCognitivePlayground = () => {
    const canonicalizer = new IntentCanonicalizer();
    const recoveryEngine = new LanguageRecoveryEngine();
    const validator = new ReasoningValidator();
    const planner = new DeepPlanner();
    const critic = new SelfCritic();
    const researchEngine = new NoveltyResearchEngine();

    const recovery = recoveryEngine.recover(cogQuery);
    setRecoveryResult(recovery);

    const canonical = canonicalizer.canonicalize(recovery.recoveredText);
    setCanonicalResult(canonical);

    const plan = planner.generatePlan(canonical.intent);
    setPlanResult(plan);

    const rawAnswer =
      "Setting up model training requires dataloaders, model layers, and optimizer configurations.";
    const critique = critic.critique(canonical.intent, rawAnswer);
    setCriticResult(critique);

    const steps = plan.milestones.map((m) => m.title);
    const validation = validator.validate(canonical.intent, critique.improvedAnswer, steps);
    setValidationResult(validation);

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
            customer_details: { email: "user@hyper.app" },
          },
        },
      };

      const timestamp = Math.floor(Date.now() / 1000).toString();
      const rawBody = JSON.stringify(payload);

      let signature = "";
      if (isValidSig) {
        const CryptoJS = await import("crypto-js");
        const signedPayload = `${timestamp}.${rawBody}`;
        const key = "whsec_prod_verification_token_key_2026";
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

  // RENDER BASED ON activeTab PROP
  switch (activeTab) {
    case "swarm":
      return (
        <div className="space-y-8 animate-in fade-in duration-300">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-5 shadow-sm">
              <div className="flex items-center gap-2 text-slate-400 mb-3">
                <Activity className="h-4 w-4" />
                <h3 className="text-xs font-semibold uppercase tracking-wider">
                  Novelty Reduction
                </h3>
              </div>
              <div className="text-3xl font-extrabold text-blue-500">
                {status?.telemetry?.avoidance_rate_pct?.toFixed(1) || "99.3"}%
              </div>
              <p className="text-[10px] text-slate-400 mt-1">
                Novelty eliminated via Swarm Pipeline
              </p>
            </div>

            <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-5 shadow-sm">
              <div className="flex items-center gap-2 text-emerald-400 mb-3">
                <Zap className="h-4 w-4 text-emerald-400" />
                <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                  GPU Energy Saved
                </h3>
              </div>
              <div className="text-3xl font-extrabold text-emerald-400">
                {status?.telemetry?.gpu_watts_saved
                  ? (status.telemetry.gpu_watts_saved / 1000).toFixed(1)
                  : "490.0"}{" "}
                kW
              </div>
              <p className="text-[10px] text-slate-400 mt-1">NVIDIA GPU irrelevance threshold</p>
            </div>

            <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-5 shadow-sm">
              <div className="flex items-center gap-2 text-slate-400 mb-3">
                <HardDrive className="h-4 w-4" />
                <h3 className="text-xs font-semibold uppercase tracking-wider">
                  Predictive Pre-resolutions
                </h3>
              </div>
              <div className="text-3xl font-extrabold">
                {status?.semantic_store_size?.toLocaleString() || "11,500,000"}
              </div>
              <p className="text-[10px] text-slate-400 mt-1">Precomputed future states in memory</p>
            </div>

            <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-5 shadow-sm">
              <div className="flex items-center gap-2 text-slate-400 mb-3">
                <Layers className="h-4 w-4" />
                <h3 className="text-xs font-semibold uppercase tracking-wider">
                  Discovery Crystals
                </h3>
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
      );

    case "cognitive":
      return (
        <div className="space-y-6 animate-in fade-in duration-300">
          <div className="bg-[#030d1e] border border-slate-800 rounded-xl shadow-sm p-6">
            <h3 className="text-lg font-bold mb-2 flex items-center gap-2 text-blue-400">
              <Cpu className="h-5 w-5" />
              V11 Cognitive Engine Playground
            </h3>
            <p className="text-xs text-slate-400 mb-6">
              Assault the recovery engines with spelling typos, slang, and mixed Tamil-English
              dialects to see how the inputs are reconstructed into pristine intents, planned, and
              validated.
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

            {recoveryResult && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 animate-in slide-in-from-bottom-2 duration-300">
                <div className="space-y-6">
                  <div className="bg-[#020813] border border-slate-800 rounded-lg p-5">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-blue-400 mb-3 flex items-center gap-1.5">
                      <AlertCircle className="h-4 w-4" />
                      Noisy Language Recovery Engine
                    </h4>
                    <div className="text-xs space-y-2">
                      <p className="text-slate-400">
                        Raw Input:{" "}
                        <span className="font-mono text-rose-400">"{recoveryResult.raw}"</span>
                      </p>
                      <p className="text-slate-400">
                        Recovered Output:{" "}
                        <span className="font-mono text-emerald-400">
                          "{recoveryResult.recoveredText}"
                        </span>
                      </p>
                      <p className="text-slate-400">
                        Recovery Confidence:{" "}
                        <span className="font-semibold text-slate-200">
                          {(recoveryResult.confidence * 100).toFixed(1)}%
                        </span>
                      </p>
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

                  <div className="bg-[#020813] border border-slate-800 rounded-lg p-5">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-blue-400 mb-3 flex items-center gap-1.5">
                      <Sparkles className="h-4 w-4" />
                      Intent Canonicalization Engine
                    </h4>
                    <div className="text-xs space-y-2">
                      <p className="text-slate-400">
                        Input Text: <span className="font-mono">"{canonicalResult.original}"</span>
                      </p>
                      <p className="text-slate-400">
                        Canonical Intent:{" "}
                        <span className="font-semibold text-blue-300">
                          "{canonicalResult.intent}"
                        </span>
                      </p>
                      <div>
                        <p className="font-semibold mb-1 text-slate-300">
                          Normalization Operations:
                        </p>
                        <ul className="list-disc list-inside space-y-1 pl-1 text-[11px] text-slate-400">
                          {canonicalResult.changes.map((ch: string, i: number) => (
                            <li key={i}>{ch}</li>
                          ))}
                          {canonicalResult.changes.length === 0 && (
                            <li>No slang, dialects, or typo replacements required.</li>
                          )}
                        </ul>
                      </div>
                    </div>
                  </div>

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
                      <p className="text-slate-400">
                        Simulation Run:{" "}
                        <span className="text-emerald-400">{noveltyResult.simulationResult}</span>
                      </p>
                    </div>
                  </div>
                </div>

                <div className="space-y-6">
                  <div className="bg-[#020813] border border-slate-800 rounded-lg p-5">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-blue-400 mb-3 flex items-center gap-1.5">
                      <Terminal className="h-4 w-4" />
                      Multi-Step Planner
                    </h4>
                    <div className="text-xs space-y-3">
                      <p className="text-slate-400">
                        Plan depth level: <span className="font-semibold">{planResult.depth}</span>
                      </p>
                      <div className="space-y-3 border-l border-blue-500/20 pl-3">
                        {planResult.milestones.map((m: any) => (
                          <div key={m.id} className="relative">
                            <span className="absolute -left-[18px] top-0.5 w-2.5 h-2.5 rounded-full bg-blue-500 border border-slate-900" />
                            <h5 className="font-semibold text-slate-200">{m.title}</h5>
                            <p className="text-slate-400 text-[10px]">{m.description}</p>
                            {m.dependencies.length > 0 && (
                              <p className="text-[9px] text-slate-500">
                                Dependencies: {m.dependencies.join(", ")}
                              </p>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

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
                        </ul>
                      </div>
                      <div>
                        <p className="font-semibold text-amber-500">Assumptions flagged:</p>
                        <ul className="list-disc list-inside pl-1 text-slate-400">
                          {criticResult.missingAssumptions.map((a: string, i: number) => (
                            <li key={i}>{a}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>

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
                          <span className="text-amber-400 font-bold">
                            RECONSTRUCTED (AUTO-FIXED)
                          </span>
                        )}
                      </p>
                      <div>
                        <p className="font-semibold text-slate-300">
                          Corrected/Refined Output Answer:
                        </p>
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
      );

    case "v14super":
      return (
        <div className="space-y-6 animate-in fade-in duration-300">
          <div className="relative overflow-hidden bg-gradient-to-r from-blue-955 via-slate-900 to-indigo-955 border border-blue-500/20 rounded-2xl p-6 shadow-xl">
            <div className="absolute top-0 right-0 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl pointer-events-none -mr-20 -mt-20" />
            <div className="relative flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <Sparkles className="h-6 w-6 text-blue-400 animate-pulse" />
                  <h2 className="text-xl font-bold tracking-tight text-white">
                    V14 Cognitive Breakthrough Engine
                  </h2>
                </div>
                <p className="text-xs text-slate-400 max-w-xl">
                  Unified edge cognitive substrate executing intent reconstruction, deductive
                  reasoning, tool-verified pipelines, and consensus agent debates.
                </p>
              </div>
            </div>
          </div>

          <div className="bg-gradient-to-b from-[#030d1e] to-[#020815] border border-slate-800 rounded-xl shadow-lg p-6">
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200 mb-2 flex items-center gap-2">
              <Terminal className="h-4 w-4 text-blue-400" />
              Phase 1 &amp; Phase 9: Intent Reconstruction &amp; Multi-Agent Consensus Debate
            </h3>
            <div className="flex flex-col md:flex-row gap-3 mb-6">
              <input
                type="text"
                className="flex-1 rounded-md border border-slate-700 bg-slate-900/50 px-3 py-2 text-xs text-slate-100 placeholder:text-slate-505 focus:outline-none font-mono"
                value={v14Query}
                onChange={(e) => setV14Query(e.target.value)}
              />
              <div className="flex gap-2">
                <button
                  onClick={handleV14Reconstruct}
                  className="bg-blue-600 text-white text-xs font-bold px-4 py-2 rounded-md"
                >
                  Reconstruct
                </button>
                <button
                  onClick={handleV14Debate}
                  className="bg-indigo-600 text-white text-xs font-bold px-4 py-2 rounded-md"
                >
                  Debate
                </button>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {v14ReconResult && (
                <div className="bg-[#020713] border border-slate-800 p-4 rounded-lg text-xs space-y-2">
                  <p className="text-slate-400">Raw: "{v14ReconResult.original}"</p>
                  <p className="text-slate-450 text-emerald-400 font-mono">
                    Reconstructed: "{v14ReconResult.reconstructed}"
                  </p>
                </div>
              )}

              {v14DebateSession && (
                <div className="bg-[#020713] border border-slate-800 p-4 rounded-lg text-xs space-y-2">
                  <p className="text-emerald-450 font-bold">
                    Consensus: {v14DebateSession.consensus}
                  </p>
                </div>
              )}
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-6">
              <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200 mb-2">
                Phase 2: Multi-Pathway Reasoning
              </h3>
              <select
                value={v14ReasoningType}
                onChange={(e) => setV14ReasoningType(e.target.value as ReasoningType)}
                className="bg-slate-900 border border-slate-700 rounded p-1 text-xs text-white"
              >
                <option value="Deductive">Deductive</option>
                <option value="Inductive">Inductive</option>
                <option value="Abductive">Abductive</option>
              </select>
              <button
                onClick={handleV14Reason}
                className="bg-purple-600 text-white text-xs font-bold px-4 py-1.5 rounded ml-2"
              >
                Reason
              </button>
              {v14ReasoningResult && (
                <p className="text-xs text-slate-300 mt-4">{v14ReasoningResult.conclusion}</p>
              )}
            </div>

            <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-6">
              <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200 mb-2">
                Phase 3 &amp; 4: Verification &amp; Critique
              </h3>
              <button
                onClick={handleV14Verify}
                className="bg-emerald-600 text-white text-xs font-bold px-4 py-2 rounded"
              >
                Verify
              </button>
              <button
                onClick={handleV14Critique}
                className="bg-rose-600 text-white text-xs font-bold px-4 py-2 rounded ml-2"
              >
                Critique
              </button>
              {v14VerifyOutput && (
                <p className="text-xs text-slate-350 mt-4">
                  Verified Repaired: {v14VerifyOutput.repairedContent}
                </p>
              )}
            </div>
          </div>
        </div>
      );

    case "v15substrate":
      return (
        <div className="space-y-6 animate-in fade-in duration-300">
          <div className="relative overflow-hidden bg-gradient-to-r from-slate-900 via-indigo-955 to-slate-900 border border-indigo-500/20 rounded-2xl p-6 shadow-xl">
            <h2 className="text-xl font-bold tracking-tight text-white">V15 Evolving Substrate</h2>
          </div>

          <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-5">
            <div className="flex gap-2">
              <input
                type="text"
                value={v15QueryInput}
                onChange={(e) => setV15QueryInput(e.target.value)}
                className="flex-1 bg-slate-900 border border-slate-700 px-3 py-2 text-xs text-white"
              />
              <button
                onClick={handleV15RunPipeline}
                className="bg-indigo-600 text-white text-xs font-bold px-4 py-2 rounded"
              >
                Trigger Cascade
              </button>
            </div>
            {v15ReconstructReport && (
              <p className="text-xs text-emerald-400 mt-4">
                {v15ReconstructReport.reconstructedQuery}
              </p>
            )}
          </div>
        </div>
      );

    case "v16substrate":
      return (
        <div className="space-y-6 animate-in fade-in duration-300">
          <div className="relative overflow-hidden bg-gradient-to-r from-slate-950 via-slate-900 to-blue-955 border border-blue-500/30 rounded-2xl p-6">
            <h2 className="text-xl font-extrabold tracking-tight text-white">
              V16 Intelligence Density Substrate
            </h2>
          </div>

          <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-5">
            <div className="flex gap-2">
              <input
                type="text"
                value={v16QueryInput}
                onChange={(e) => setV16QueryInput(e.target.value)}
                className="flex-1 bg-slate-900 border border-slate-700 px-3 py-2 text-xs text-white"
              />
              <button
                onClick={handleV16RunPipeline}
                className="bg-blue-600 text-white text-xs font-bold px-4 py-2 rounded"
              >
                Run Substrate V16
              </button>
            </div>
            {v16ReconstructReport && (
              <p className="text-xs text-emerald-400 mt-4">
                {v16ReconstructReport.reconstructedQuery}
              </p>
            )}
          </div>
        </div>
      );

    case "v17dominance":
      return (
        <div className="space-y-6 animate-in fade-in duration-300">
          <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-6">
            <h2 className="text-lg font-bold text-white mb-2">
              V17 Multi-Domain Automation Engine
            </h2>
            <div className="flex gap-2">
              <input
                type="text"
                value={v17QueryInput}
                onChange={(e) => setV17QueryInput(e.target.value)}
                className="flex-1 bg-slate-900 border border-slate-700 px-3 py-2 text-xs text-white"
              />
              <button
                onClick={handleV17RunQuery}
                className="bg-emerald-600 text-white text-xs font-bold px-4 py-2 rounded"
              >
                Process Domains
              </button>
            </div>
            {v17EdgeReport && (
              <p className="text-xs text-emerald-400 mt-4">
                Local Execution: {v17EdgeReport.conclusion}
              </p>
            )}
          </div>
        </div>
      );

    case "debate":
      return (
        <div className="space-y-6 animate-in fade-in duration-300">
          <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-6">
            <h3 className="text-lg font-bold text-white mb-4">Constitutional Debate Arena</h3>
            <div className="flex gap-2">
              <input
                type="text"
                value={debateQuery}
                onChange={(e) => setDebateQuery(e.target.value)}
                className="flex-1 bg-slate-900 border border-slate-700 px-3 py-2 text-xs text-white"
              />
              <button
                onClick={handleRunSwarmDebate}
                className="bg-blue-600 text-white text-xs font-bold px-4 py-2 rounded"
              >
                Debate
              </button>
            </div>
            {debateSession && (
              <p className="text-xs text-emerald-400 mt-4">
                Debated Outcome: {debateSession.consensus}
              </p>
            )}
          </div>
        </div>
      );

    case "quality":
      return (
        <div className="space-y-6 animate-in fade-in duration-300">
          <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-6">
            <h3 className="text-lg font-bold text-white mb-4">
              Crystallization &amp; Memory Auditors
            </h3>
            <button
              onClick={handleMemoryAudit}
              className="bg-slate-800 text-white text-xs px-4 py-2 rounded mr-2"
            >
              Audit Memory
            </button>
            <button
              onClick={handleCrystalAudit}
              className="bg-slate-800 text-white text-xs px-4 py-2 rounded"
            >
              Audit Crystals
            </button>
            {memoryAudit && (
              <p className="text-xs text-emerald-400 mt-4">
                Memory Quality: {memoryAudit.memoryScore * 100}%
              </p>
            )}
          </div>
        </div>
      );

    case "benchmarks":
      return <BenchmarkLeaderboard />;

    case "devops":
      return (
        <div className="space-y-6 animate-in fade-in duration-300">
          <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-6">
            <h3 className="text-lg font-bold text-white mb-4">
              OTel Telemetry &amp; Gateway Sandboxes
            </h3>
            <button
              onClick={() => handleSendMockWebhook(true)}
              className="bg-emerald-600 text-white text-xs px-4 py-2 rounded mr-2"
            >
              Verified webhook
            </button>
            <button
              onClick={() => handleSendMockWebhook(false)}
              className="bg-rose-600 text-white text-xs px-4 py-2 rounded"
            >
              Malformed webhook
            </button>
            {webhookStatus && <p className="text-xs text-slate-300 mt-4">{webhookStatus}</p>}
          </div>
        </div>
      );

    default:
      return null;
  }
}
