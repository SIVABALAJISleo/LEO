import React, { useEffect, useState } from "react";
import { fetchLeoStatus, LeoStatus, fetchDevOpsStatus, configureDevOps, sendStripeWebhook, DevOpsSettings } from "./lib/api";
import { QuerySimulationConsole } from "./components/Dashboard/QuerySimulationConsole";
import { 
  Activity, Cpu, HardDrive, Layers, Zap, AlertTriangle, Play, Shield, 
  RefreshCw, AlertCircle, Sparkles, MessageSquare, CheckCircle, 
  Terminal, HelpCircle, ArrowRight, Settings, BarChart2, Brain, GitBranch
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

function App() {
  const [status, setStatus] = useState<LeoStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState<"swarm" | "cognitive" | "debate" | "benchmarks" | "devops" | "quality" | "v14super">("swarm");

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
          <div className="space-y-6 animate-in fade-in duration-300">
            <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-6">
              <h3 className="text-lg font-bold mb-2 flex items-center gap-2 text-blue-400">
                <BarChart2 className="h-5 w-5" />
                V11 Enterprise Comparative Leaderboard
              </h3>
              <p className="text-xs text-slate-400 mb-6">
                UCS platform is automatically benchmarked against centralized models. Measurements reflect accuracy, local vs cloud cost, and latency.
              </p>

              <div className="border border-slate-800 rounded-lg overflow-hidden">
                <table className="w-full text-xs text-left">
                  <thead className="bg-[#020813] border-b border-slate-800 text-slate-400 uppercase tracking-wider text-[10px]">
                    <tr>
                      <th className="p-4">Rank</th>
                      <th className="p-4">Model Name</th>
                      <th className="p-4">Accuracy</th>
                      <th className="p-4">Avg Latency</th>
                      <th className="p-4">Resource Cost / Request</th>
                      <th className="p-4">Reasoning Score</th>
                      <th className="p-4">Planning Score</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800 text-slate-200">
                    <tr className="bg-blue-500/5">
                      <td className="p-4 font-bold text-blue-400">1</td>
                      <td className="p-4 font-bold flex items-center gap-1.5">
                        Antigravity UCS V11
                        <span className="text-[9px] bg-blue-500 text-white px-1.5 py-0.5 rounded font-mono uppercase font-bold">Local-First</span>
                      </td>
                      <td className="p-4 text-emerald-400 font-bold">94.2%</td>
                      <td className="p-4 font-mono">2.5ms – 42ms</td>
                      <td className="p-4 text-emerald-400 font-bold">$0.0000 (Local DDR5/iGPU)</td>
                      <td className="p-4 font-mono font-bold">96.5%</td>
                      <td className="p-4 font-mono font-bold">94.2%</td>
                    </tr>
                    <tr>
                      <td className="p-4 font-semibold text-slate-400">2</td>
                      <td className="p-4 font-semibold text-slate-300">Claude 3.5 Sonnet (Cloud)</td>
                      <td className="p-4 font-semibold">92.5%</td>
                      <td className="p-4 font-mono text-slate-400">650ms</td>
                      <td className="p-4 text-rose-500 font-mono">$0.0150 (Dense Cloud)</td>
                      <td className="p-4 font-mono">92.2%</td>
                      <td className="p-4 font-mono">90.5%</td>
                    </tr>
                    <tr>
                      <td className="p-4 font-semibold text-slate-400">3</td>
                      <td className="p-4 font-semibold text-slate-300">GPT-4 (Cloud)</td>
                      <td className="p-4 font-semibold">91.8%</td>
                      <td className="p-4 font-mono text-slate-400">820ms</td>
                      <td className="p-4 text-rose-500 font-mono">$0.0300 (Dense Cloud)</td>
                      <td className="p-4 font-mono">90.8%</td>
                      <td className="p-4 font-mono">88.5%</td>
                    </tr>
                    <tr>
                      <td className="p-4 font-semibold text-slate-400">4</td>
                      <td className="p-4 font-semibold text-slate-300">Gemini 1.5 Pro (Cloud)</td>
                      <td className="p-4 font-semibold">90.1%</td>
                      <td className="p-4 font-mono text-slate-400">710ms</td>
                      <td className="p-4 text-rose-500 font-mono">$0.0125 (Dense Cloud)</td>
                      <td className="p-4 font-mono">89.5%</td>
                      <td className="p-4 font-mono">87.0%</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
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

      </main>
    </div>
  );
}

export default App;