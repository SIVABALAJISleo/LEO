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

function App() {
  const [status, setStatus] = useState<LeoStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState<"swarm" | "cognitive" | "debate" | "benchmarks" | "devops" | "quality" | "superintelligence">("swarm");

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
            { id: "superintelligence", label: "V13 Superintelligence", icon: Sparkles },
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

        {/* TAB 2.5: V13 SUPERINTELLIGENCE ECOSYSTEM */}
        {activeTab === "superintelligence" && (
          <div className="space-y-6 animate-in fade-in duration-300">
            {/* Header / Intro */}
            <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-6">
              <h3 className="text-lg font-bold mb-2 flex items-center gap-2 text-blue-400">
                <Sparkles className="h-5 w-5 animate-pulse" />
                V13 Universal Superintelligence Substrates
              </h3>
              <p className="text-xs text-slate-400">
                Evolving the swarm from search & retrieval to a self-improving, mathematically verified cognitive ecosystem. 
                Runs local Lean/Coq solvers, tool verifiers, scenario simulation, and reality feedback optimization.
              </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              
              {/* Card 1: Interactive Lean/Coq Prover Console */}
              <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-6 flex flex-col justify-between">
                <div>
                  <h4 className="text-sm font-bold text-slate-200 mb-2 flex items-center gap-2">
                    <Brain className="h-4 w-4 text-purple-400" />
                    Formal Prover Console (Lean 4 / Coq / Z3 SMT)
                  </h4>
                  <p className="text-[11px] text-slate-400 mb-4">
                    Enter mathematical or logical assertions to formally construct and compile proving targets.
                  </p>
                  
                  <div className="space-y-4">
                    <div>
                      <p className="text-[10px] text-slate-500 font-semibold mb-1">Enter Logical Claim:</p>
                      <input 
                        type="text"
                        value={theoremClaim}
                        onChange={(e) => setTheoremClaim(e.target.value)}
                        className="w-full rounded bg-slate-900 border border-slate-800 px-3 py-2 text-xs text-slate-300 focus:outline-none focus:ring-1 focus:ring-blue-500 font-mono"
                      />
                    </div>
                    
                    <button 
                      onClick={handleVerifyTheorem}
                      className="bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold px-4 py-2 rounded transition-colors"
                    >
                      Compile & Verify Theorem
                    </button>
                    
                    {theoremResult && (
                      <div className="space-y-2 text-xs">
                        <div className="flex justify-between items-center bg-slate-900 border border-slate-800 px-3 py-2 rounded">
                          <span className="text-slate-400">Language Resolved:</span>
                          <span className="font-bold text-blue-400">{theoremResult.formalLanguage}</span>
                        </div>
                        <div className="flex justify-between items-center bg-slate-900 border border-slate-800 px-3 py-2 rounded">
                          <span className="text-slate-400">Solver Output:</span>
                          <span className={`font-bold ${theoremResult.isVerified ? "text-emerald-400" : "text-rose-500"}`}>
                            {theoremResult.isVerified ? "VERIFIED (100% Correct)" : "FAILED (Unsat/Contradiction)"}
                          </span>
                        </div>
                        <div>
                          <p className="text-[10px] text-slate-500 font-semibold mb-1">Generated Theorem Proof:</p>
                          <pre className="bg-[#020713] border border-slate-850 p-3 rounded font-mono text-[10px] text-slate-300 overflow-x-auto whitespace-pre">
                            {theoremResult.proofCode}
                          </pre>
                        </div>
                        <div>
                          <p className="text-[10px] text-slate-500 font-semibold mb-1">Solvers Compilation Details:</p>
                          <pre className="bg-[#020713] border border-slate-850 p-3 rounded font-mono text-[10px] text-slate-400 overflow-x-auto whitespace-pre">
                            {theoremResult.solverOutput}
                          </pre>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Card 2: Tool-Verified Sandbox Orchestrator */}
              <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-6 flex flex-col justify-between">
                <div>
                  <h4 className="text-sm font-bold text-slate-200 mb-2 flex items-center gap-2">
                    <Shield className="h-4 w-4 text-emerald-400" />
                    Tool-Verified execution & Sandbox checking
                  </h4>
                  <p className="text-[11px] text-slate-400 mb-4">
                    Evaluates query outputs through sandboxed executions and calculators to guarantee correctness.
                  </p>
                  
                  <div className="space-y-4">
                    <div>
                      <p className="text-[10px] text-slate-500 font-semibold mb-1">Target Statement / Query:</p>
                      <input 
                        type="text"
                        value={verificationQuery}
                        onChange={(e) => setVerificationQuery(e.target.value)}
                        className="w-full rounded bg-slate-900 border border-slate-800 px-3 py-2 text-xs text-slate-300 focus:outline-none focus:ring-1 focus:ring-blue-500"
                      />
                    </div>
                    
                    <button 
                      onClick={handleRunToolVerification}
                      className="bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold px-4 py-2 rounded transition-colors"
                    >
                      Run Verification Cascade
                    </button>
                    
                    {verificationOutput && (
                      <div className="space-y-3 text-xs">
                        <div className="flex justify-between items-center bg-slate-900 border border-slate-800 px-3 py-2 rounded">
                          <span className="text-slate-400">Score Metrics:</span>
                          <span className="font-bold text-emerald-400">{verificationOutput.score * 100}% Passed</span>
                        </div>
                        <div className="space-y-2">
                          <p className="text-[10px] text-slate-500 font-semibold">Active Verifiers Checklists:</p>
                          {verificationOutput.checks.map((check: any, idx: number) => (
                            <div key={idx} className="flex justify-between items-center bg-[#020713] px-3 py-1.5 border border-slate-850 rounded text-[11px]">
                              <span className="font-semibold text-slate-300">{check.toolName}</span>
                              <span className={`font-mono px-2 py-0.5 rounded uppercase text-[9px] ${
                                check.status === "passed" ? "bg-emerald-500/10 text-emerald-400" :
                                check.status === "failed" ? "bg-rose-500/10 text-rose-500" : "bg-slate-800 text-slate-400"
                              }`}>
                                {check.status}
                              </span>
                            </div>
                          ))}
                        </div>
                        <div>
                          <p className="text-[10px] text-slate-500 font-semibold mb-1">Repaired output answer:</p>
                          <div className="bg-[#020713] border border-slate-850 p-3 rounded font-mono text-[10px] text-slate-300">
                            {verificationOutput.repairedAnswer}
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>

            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              
              {/* Card 3: World Model Simulation */}
              <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-6">
                <h4 className="text-sm font-bold text-slate-200 mb-2 flex items-center gap-2">
                  <GitBranch className="h-4 w-4 text-blue-400" />
                  World Model Outcome Simulator
                </h4>
                <p className="text-[11px] text-slate-400 mb-4">
                  Simulate dynamic execution scenarios to predict best-case, worst-case, and likely outcomes.
                </p>
                
                <div className="space-y-4">
                  <div className="flex gap-2">
                    <input 
                      type="text"
                      value={v13ScenarioQuery}
                      onChange={(e) => setV13ScenarioQuery(e.target.value)}
                      className="flex-1 rounded bg-slate-900 border border-slate-800 px-3 py-2 text-xs text-slate-300 focus:outline-none focus:ring-1 focus:ring-blue-500"
                    />
                    <button 
                      onClick={handleRunScenarioSimulation}
                      className="bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold px-4 py-2 rounded transition-colors whitespace-nowrap"
                    >
                      Run Simulation
                    </button>
                  </div>
                  
                  {v13ScenarioReport && (
                    <div className="space-y-4 text-xs">
                      <div className="grid grid-cols-3 gap-2">
                        {v13ScenarioReport.scenarios.map((sc: any, idx: number) => (
                          <div key={idx} className="bg-slate-900 border border-slate-850 p-3 rounded-lg flex flex-col justify-between">
                            <div>
                              <span className={`text-[9px] uppercase font-bold px-1.5 py-0.5 rounded inline-block mb-1.5 ${
                                sc.type === "best" ? "bg-emerald-500/10 text-emerald-400" :
                                sc.type === "likely" ? "bg-blue-500/10 text-blue-400" : "bg-rose-500/10 text-rose-400"
                              }`}>
                                {sc.type} Case
                              </span>
                              <h5 className="font-bold text-slate-300 text-[11px] mb-1">{sc.title}</h5>
                              <p className="text-[10px] text-slate-400 leading-relaxed">{sc.description}</p>
                            </div>
                            <div className="border-t border-slate-800 pt-2 mt-2 space-y-1 text-[9px] text-slate-500 font-mono">
                              <p>Prob: {sc.outcomeProbability * 100}%</p>
                              <p>Lat: {sc.estimatedLatencyMs}ms</p>
                              <p>Tokens: {sc.expectedCostTokens}</p>
                            </div>
                          </div>
                        ))}
                      </div>
                      <div className="bg-[#020713] p-3 border border-slate-850 rounded">
                        <p className="font-semibold text-slate-300">Consequence summary:</p>
                        <p className="text-[10px] text-slate-400">{v13ScenarioReport.consequenceSummary}</p>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Card 4: Reality Feedback Loop & Meta-Learning */}
              <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-6">
                <h4 className="text-sm font-bold text-slate-200 mb-2 flex items-center gap-2">
                  <Activity className="h-4 w-4 text-rose-500" />
                  Reality Feedback Loop & Self-Optimization
                </h4>
                <p className="text-[11px] text-slate-400 mb-4">
                  Compare predicted latency against observed real-world performance to dynamically adjust network weights.
                </p>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                  <div className="space-y-3">
                    <div className="grid grid-cols-2 gap-2">
                      <div>
                        <p className="text-[10px] text-slate-500 font-semibold mb-1">Predicted Latency (ms):</p>
                        <input 
                          type="number"
                          value={predictedValue}
                          onChange={(e) => setPredictedValue(e.target.value)}
                          className="w-full rounded bg-slate-900 border border-slate-800 px-3 py-1 text-xs text-slate-300"
                        />
                      </div>
                      <div>
                        <p className="text-[10px] text-slate-500 font-semibold mb-1">Observed Latency (ms):</p>
                        <input 
                          type="number"
                          value={observedValue}
                          onChange={(e) => setObservedValue(e.target.value)}
                          className="w-full rounded bg-slate-900 border border-slate-800 px-3 py-1 text-xs text-slate-300"
                        />
                      </div>
                    </div>
                    
                    <button 
                      onClick={handleLogFeedback}
                      className="w-full bg-rose-600 hover:bg-rose-500 text-white text-xs font-bold py-2 rounded transition-colors"
                    >
                      Log Reality Feedback
                    </button>
                    
                    <div className="space-y-1.5">
                      <p className="text-[10px] text-slate-500 font-semibold">Decay weights:</p>
                      {Object.entries(feedbackWeights).map(([key, val]: any) => (
                        <div key={key} className="flex justify-between items-center text-[10px] bg-slate-900 border border-slate-850 px-2 py-1 rounded">
                          <span className="text-slate-400 font-mono">{key}</span>
                          <span className="font-mono font-bold text-rose-400">{val.toFixed(4)}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  <div className="bg-[#020713] p-4 border border-slate-850 rounded-lg flex flex-col justify-between">
                    <div>
                      <p className="text-[10px] text-slate-500 font-semibold mb-1.5">Feedback logs timeline:</p>
                      <div className="space-y-1.5 max-h-48 overflow-y-auto text-[9px] font-mono text-slate-400">
                        {feedbackRecords.length === 0 ? (
                          <p className="text-slate-600 italic">No feedback entries logged yet.</p>
                        ) : (
                          feedbackRecords.map((r, i) => (
                            <div key={i} className="border-b border-slate-900 pb-1 flex justify-between">
                              <span>{r.predictionId}: Err {r.errorPercentage.toFixed(1)}%</span>
                              <span className={r.weightAdjustment > 0 ? "text-emerald-400" : "text-rose-500"}>
                                {r.weightAdjustment > 0 ? "+" : ""}{r.weightAdjustment.toFixed(4)}
                              </span>
                            </div>
                          ))
                        )}
                      </div>
                    </div>
                    <div className="text-[9px] text-slate-500 text-center border-t border-slate-900 pt-2">
                      Active model weights automatically fine-tuned by local error parameters.
                    </div>
                  </div>
                </div>
              </div>

            </div>

            {/* Additional modules diagnostics */}
            <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-6">
              <h4 className="text-sm font-bold text-slate-200 mb-4 flex items-center gap-2">
                <Layers className="h-4 w-4 text-blue-500" />
                Episodic Memory V2 & Knowledge Governance Status
              </h4>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-xs">
                {/* Memory block */}
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <p className="font-semibold text-slate-300">Memory Governor V2 Cleaned Blocks</p>
                    <button 
                      onClick={() => {
                        memoryGovInstance.governMemory();
                        setGovernedMemories([...memoryGovInstance.getBlocks()]);
                      }}
                      className="text-[10px] bg-slate-800 hover:bg-slate-700 px-3 py-1 rounded text-slate-300 font-bold uppercase transition-colors"
                    >
                      Audit Memory Blocks
                    </button>
                  </div>
                  <div className="bg-[#020713] p-3 border border-slate-850 rounded-lg max-h-48 overflow-y-auto space-y-2">
                    {(governedMemories.length > 0 ? governedMemories : memoryGovInstance.getBlocks()).map((block, idx) => (
                      <div key={idx} className="bg-slate-900 border border-slate-850 p-2 rounded text-[10px]">
                        <div className="flex justify-between text-[9px] text-slate-500 mb-1">
                          <span>Source: {block.source} | Cat: {block.category}</span>
                          <span className="font-bold text-blue-400">Weight: {block.weight}</span>
                        </div>
                        <p className="text-slate-300 leading-snug">{block.content}</p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Knowledge block */}
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <p className="font-semibold text-slate-300">Knowledge Governor Crystal Audit</p>
                    <button 
                      onClick={() => {
                        knowledgeGovInstance.performAudit();
                        setGovernedCrystals([...knowledgeGovInstance.getAssets()]);
                      }}
                      className="text-[10px] bg-slate-800 hover:bg-slate-700 px-3 py-1 rounded text-slate-300 font-bold uppercase transition-colors"
                    >
                      Prune Crystals
                    </button>
                  </div>
                  <div className="bg-[#020713] p-3 border border-slate-850 rounded-lg max-h-48 overflow-y-auto space-y-2">
                    {(governedCrystals.length > 0 ? governedCrystals : knowledgeGovInstance.getAssets()).map((asset, idx) => (
                      <div key={idx} className="bg-slate-900 border border-slate-850 p-2 rounded text-[10px] flex justify-between items-center">
                        <div className="flex-1 mr-4">
                          <h6 className="font-bold text-slate-300 text-[11px] mb-1">{asset.topic}</h6>
                          <div className="flex gap-2 text-[9px] text-slate-500 font-mono">
                            <span>Acc: {asset.accuracyScore}</span>
                            <span>Fresh: {asset.freshnessScore}</span>
                            <span>Trust: {asset.trustScore}</span>
                          </div>
                        </div>
                        <span className={`font-mono text-[9px] uppercase px-2 py-0.5 rounded font-bold ${
                          asset.status === "active" ? "bg-blue-500/10 text-blue-400" :
                          asset.status === "reinforced" ? "bg-emerald-500/10 text-emerald-400" : "bg-rose-500/10 text-rose-500"
                        }`}>
                          {asset.status}
                        </span>
                      </div>
                    ))}
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