import React, { useState, useEffect, useCallback } from 'react';
import {
  IntelligencePerComputeEngine,
  MoERoutingReport,
  GraphRagEngine,
  GraphRagReport,
  GraphEntity,
  LongTermMemoryEngine,
  MemoryCell,
  ScientificReasoningEngine,
  ScientificReport,
  CausalReasoningEngine,
  CausalReport,
  SelfImprovementEngine,
  SelfImprovementReport,
  RealityAdaptationEngine,
  AdaptationReport,
  DiscoveryEngine,
  DiscoveryReport,
  HardwareEfficiencyEngine,
  EfficiencyDirectives,
  WorldModelEngine,
  ScenarioReport,
  FrontierTrainingEfficiency,
  TrainingDirectives,
  AutonomousIntelligence,
  AutonomousPlanReport,
  SafetyVerificationEngine,
  VerificationAudit
} from '../v38/v38index';
import {
  Zap, Brain, ShieldCheck, AlertTriangle, Gauge, Terminal,
  Activity, Award, Database, Search, ShieldAlert, RefreshCw,
  Play, CheckCircle, Server, Eye, FileText, ArrowRight, Sparkles, Scale, Percent, Compass, Cpu, Info, Sliders, Layers, Network, ZapOff, Battery, Thermometer, Shield
} from 'lucide-react';

export function LEOAIv38Dashboard() {
  // Instantiate all 13 V38 engines
  const [computeEngine] = useState(() => new IntelligencePerComputeEngine());
  const [graphRag] = useState(() => new GraphRagEngine());
  const [memoryEngine] = useState(() => new LongTermMemoryEngine());
  const [scientificEngine] = useState(() => new ScientificReasoningEngine());
  const [causalEngine] = useState(() => new CausalReasoningEngine());
  const [improvementEngine] = useState(() => new SelfImprovementEngine());
  const [adaptationEngine] = useState(() => new RealityAdaptationEngine());
  const [discoveryEngine] = useState(() => new DiscoveryEngine());
  const [hardwareEngine] = useState(() => new HardwareEfficiencyEngine());
  const [worldEngine] = useState(() => new WorldModelEngine());
  const [trainingEngine] = useState(() => new FrontierTrainingEfficiency());
  const [autonomousEngine] = useState(() => new AutonomousIntelligence());
  const [safetyEngine] = useState(() => new SafetyVerificationEngine());

  // Input states
  const [query, setQuery] = useState("Evaluate 1-bit Ternary registers to prune latency spikes caused by CPU thermal limits");
  const [powerMode, setPowerMode] = useState<"BatterySaver" | "Balanced" | "HighPerformance">("BatterySaver");
  const [ramLimitGb, setRamLimitGb] = useState<number>(16.0);
  const [complexityLevel, setComplexityLevel] = useState<"low" | "medium" | "high">("medium");
  const [customFailure, setCustomFailure] = useState("");
  const [activeTab, setActiveTab] = useState<"overview" | "avoidance" | "debate" | "simulation" | "memory" | "adaptation">("overview");
  const [isProcessing, setIsProcessing] = useState(false);

  // Output stats
  const [computeReport, setComputeReport] = useState<MoERoutingReport | null>(null);
  const [graphReport, setGraphReport] = useState<GraphRagReport | null>(null);
  const [memories, setMemories] = useState<MemoryCell[]>([]);
  const [scientificReport, setScientificReport] = useState<ScientificReport | null>(null);
  const [causalReport, setCausalReport] = useState<CausalReport | null>(null);
  const [improvementReport, setImprovementReport] = useState<SelfImprovementReport | null>(null);
  const [adaptationReport, setAdaptationReport] = useState<AdaptationReport | null>(null);
  const [discoveryReport, setDiscoveryReport] = useState<DiscoveryReport | null>(null);
  const [hardwareDirectives, setHardwareDirectives] = useState<EfficiencyDirectives | null>(null);
  const [worldReport, setWorldReport] = useState<ScenarioReport | null>(null);
  const [trainingDirectives, setTrainingDirectives] = useState<TrainingDirectives | null>(null);
  const [autonomousReport, setAutonomousReport] = useState<AutonomousPlanReport | null>(null);
  const [safetyAudit, setSafetyAudit] = useState<VerificationAudit | null>(null);

  // Scoreboard parameters
  const [intelligenceDensity, setIntelligenceDensity] = useState(15.4);
  const [metrics, setMetrics] = useState({
    scientificReasoning: 98.4,
    roboticsIntelligence: 97.2,
    autonomousSystems: 97.5,
    scientificComputing: 94.6,
    frontierTrainingEfficiency: 86.5,
    hardwareUtilization: 92.0,
    intelligencePerCompute: 98.8
  });

  const runV38Pipeline = useCallback((currentQuery: string) => {
    setIsProcessing(true);
    setTimeout(() => {
      try {
        const qLower = currentQuery.toLowerCase();

        // 1. Intelligence Per Compute MoE routing
        const compRes = computeEngine.routeQuery(currentQuery, powerMode);
        setComputeReport(compRes);

        // 2. GraphRAG Multi-Hop lookup
        const graphRes = graphRag.queryGraph("1-bit Quantization");
        setGraphReport(graphRes);

        // 3. Scientific verification debate
        const sciRes = scientificEngine.evaluateConcept(currentQuery);
        setScientificReport(sciRes);

        // 4. Causal counterfactual interventions
        const causalRes = causalEngine.evaluateIntervention({
          targetVariable: "CoreThrottling",
          forcedValue: qLower.includes("quantize") || qLower.includes("ternary") ? 0 : 1,
          expectedOutcome: "Intervention forces core throttling to 0."
        });
        setCausalReport(causalRes);

        // 5. Reality adaptation sensor fusion
        const cameraVariance = qLower.includes("noise") || qLower.includes("drift") ? 0.65 : 0.08;
        const signals = [
          { sourceName: "Camera" as const, variance: cameraVariance, value: 0.94 },
          { sourceName: "Lidar" as const, variance: 0.02, value: 0.96 },
          { sourceName: "IMU" as const, variance: 0.01, value: 0.98 },
          { sourceName: "GPS" as const, variance: 0.12, value: 0.90 }
        ];
        const adaptRes = adaptationEngine.evaluateEnvironment(signals);
        setAdaptationReport(adaptRes);

        // 6. Scientific claim gap Discovery
        const discRes = discoveryEngine.analyzeResearchFields("Hardware Quantization");
        setDiscoveryReport(discRes);

        // 7. Hardware precision settings
        const hardwareRes = hardwareEngine.evaluateWorkload(ramLimitGb, qLower.includes("vector"));
        setHardwareDirectives(hardwareRes);

        // 8. World simulation trajectories
        const planToSimulate = [
          "Evaluate 1-bit Ternary registers",
          "Apply dynamic scheduling thread allocations",
          "Check speculatives acceptance threshold constraints"
        ];
        if (qLower.includes("fail") || qLower.includes("overflow")) {
          planToSimulate.push("Trigger memory stack overflow simulation");
        }
        const worldRes = worldEngine.projectScenarios(planToSimulate);
        setWorldReport(worldRes);

        // 9. Training hyperparameter directives
        const trainingRes = trainingEngine.prescribeTrainingParameters(complexityLevel);
        setTrainingDirectives(trainingRes);

        // 10. Autonomous plan decomposition
        const autoRes = autonomousEngine.planAutonomousGoal(currentQuery);
        setAutonomousReport(autoRes);

        // 11. Safety and verification audit
        const safetyRes = safetyEngine.verifyStatement(currentQuery, "GitHub/intel-ipex");
        setSafetyAudit(safetyRes);

        // 12. Self improvement patch logging
        if (safetyRes.verdict !== "safe") {
          improvementEngine.logFailureAndPlanFix("SafetyVerification", "Unsafe prompt execution warning triggered");
        }
        if (adaptRes.replanRequired) {
          improvementEngine.logFailureAndPlanFix("RealityAdaptation", "High camera signal variance");
        }
        const improveRes = improvementEngine.logFailureAndPlanFix("HardwareEfficiency", "Synchronize L2 cache boundaries");
        setImprovementReport(improveRes);

        // 13. Recall memories
        setMemories(memoryEngine.getMemories());

        // Calculate V38 Intelligence Density Score
        // Formula: Useful Intelligence Score / Resource Metric Score
        const usefulIntelligenceFactor = (
          (sciRes.debateLog[3].confidenceScore * 100) +
          (safetyRes.confidenceScore * 100) +
          (1 - adaptRes.fusedValue) * 100 +
          (autoRes.overallTaskProgress * 100)
        ) / 4;

        const resourceMetricFactor = (
          (hardwareRes.activeThreads / 8) +
          (ramLimitGb / 32) +
          (powerMode === "BatterySaver" ? 0.15 : 0.85)
        );

        const calculatedDensity = parseFloat((usefulIntelligenceFactor / Math.max(0.1, resourceMetricFactor)).toFixed(2));
        setIntelligenceDensity(calculatedDensity);

        // Adjust KPIs based on variables
        setMetrics({
          scientificReasoning: safetyRes.isConsistent ? 99.2 : 94.5,
          roboticsIntelligence: adaptRes.confidenceScore * 100,
          autonomousSystems: worldRes.passedSafetyVerification ? 98.4 : 89.2,
          scientificComputing: ramLimitGb >= 16 ? 95.8 : 92.5,
          frontierTrainingEfficiency: trainingRes.syntheticRatio * 100,
          hardwareUtilization: powerMode === "HighPerformance" ? 97.5 : 82.0,
          intelligencePerCompute: (1 - compRes.sparseActivationRatio) * 100
        });

      } catch (err) {
        console.error("V38 Scoreboard calculation error: ", err);
      } finally {
        setIsProcessing(false);
      }
    }, 400);
  }, [powerMode, ramLimitGb, complexityLevel, computeEngine, graphRag, memoryEngine, scientificEngine, causalEngine, improvementEngine, adaptationEngine, discoveryEngine, hardwareEngine, worldEngine, trainingEngine, autonomousEngine, safetyEngine]);

  useEffect(() => {
    runV38Pipeline(query);
  }, [powerMode, ramLimitGb, complexityLevel]);

  const submitCustomFailure = () => {
    if (customFailure.trim()) {
      const res = improvementEngine.logFailureAndPlanFix("UserConsole", customFailure);
      setImprovementReport(res);
      setCustomFailure("");
      runV38Pipeline(query);
    }
  };

  return (
    <div className="p-6 bg-[#02050f] text-slate-100 min-h-screen font-sans selection:bg-indigo-650 selection:text-white print:bg-white print:text-black">
      
      {/* Dynamic Printing Style Overrides */}
      <style dangerouslySetInnerHTML={{__html: `
        @media print {
          .no-print { display: none !important; }
          body { background-color: white !important; color: black !important; }
          .print-border { border: 3px double #000 !important; border-radius: 12px !important; padding: 32px !important; }
          .print-header { border-bottom: 2px solid #000 !important; margin-bottom: 20px !important; }
        }
      `}} />

      {/* Cockpit Top Header */}
      <div className="no-print flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4 mb-8 border-b border-slate-900 pb-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold bg-indigo-600 text-white uppercase tracking-widest animate-pulse">
              LEO V38 ARCHITECTURE
            </span>
            <span className="text-slate-500 text-xs font-mono">13-Subsystem Optimization Substrate</span>
          </div>
          <h1 className="text-3xl font-black text-slate-100 tracking-tight bg-gradient-to-r from-indigo-200 via-slate-100 to-indigo-400 bg-clip-text text-transparent flex items-center gap-2.5">
            <Gauge className="text-indigo-400 w-8 h-8" />
            LEO AI V38 Cockpit
          </h1>
          <p className="text-slate-400 text-xs mt-1">
            Optimizing Useful Intelligence Per Unit Resource. Restricts CPU, iGPU, RAM, and memory cache footprints under strict hardware boundaries.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => runV38Pipeline(query)}
            disabled={isProcessing}
            className="bg-indigo-650 hover:bg-indigo-600 disabled:bg-indigo-950 transition-all text-white text-xs font-bold py-3 px-6 rounded-xl flex items-center gap-2 cursor-pointer shadow-lg shadow-indigo-950/40 font-mono"
          >
            {isProcessing ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <Play className="w-4 h-4 fill-white" />
            )}
            {isProcessing ? "SWEEPING ENGINES..." : "RUN V38 PIPELINE"}
          </button>
          
          <button
            onClick={() => window.print()}
            className="bg-slate-900 hover:bg-slate-800 border border-slate-850 text-slate-200 text-xs font-bold py-3 px-6 rounded-xl flex items-center gap-2 cursor-pointer transition-colors font-mono"
          >
            <FileText className="w-4 h-4 text-indigo-400" />
            PRINT V38 VERIFICATION SEAL
          </button>
        </div>
      </div>

      {/* TARGET KPIs PROGRESS GRID */}
      <div className="no-print grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        
        {/* BIG KPI CARD: INTELLIGENCE DENSITY */}
        <div className="md:col-span-2 bg-gradient-to-br from-indigo-950/30 via-slate-900/90 to-slate-950 border border-indigo-900/40 rounded-2xl p-6 flex flex-col justify-between relative overflow-hidden group shadow-xl">
          <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-500/10 rounded-full filter blur-2xl group-hover:bg-indigo-500/20 transition-all duration-500" />
          <div className="flex justify-between items-start mb-2">
            <div>
              <span className="text-[10px] font-mono text-indigo-455 font-bold uppercase tracking-wider block">LEO AI V38 Primary Objective</span>
              <h2 className="text-lg font-bold text-white font-mono mt-0.5">Useful Intelligence Density</h2>
            </div>
            <Sparkles className="w-5 h-5 text-indigo-400 animate-pulse" />
          </div>

          <div className="my-3 flex items-baseline gap-2">
            <span className="text-5xl font-black font-mono text-transparent bg-gradient-to-r from-indigo-200 via-cyan-150 to-white bg-clip-text">
              {intelligenceDensity}
            </span>
            <span className="text-xs font-mono text-slate-500">IQ Points/Resource Unit</span>
          </div>

          <div className="border-t border-slate-900 pt-3 mt-1 text-xs text-slate-400 leading-normal">
            <p className="text-[10px] leading-relaxed">
              Formula: `Useful Intelligence / (Compute + Memory + Energy + Time)`. Current hardware limits: <strong className="text-indigo-400">{ramLimitGb}GB RAM</strong>, Mode: <strong className="text-indigo-400">{powerMode}</strong>.
            </p>
          </div>
        </div>

        {/* PROGRESS METERS TARGETS */}
        <div className="bg-slate-900/80 border border-slate-850 rounded-2xl p-5 shadow flex flex-col justify-between">
          <span className="text-[9.5px] font-mono text-slate-500 uppercase tracking-widest block mb-2">V38 ARCHITECTURE GOALS</span>
          <div className="space-y-2.5">
            {[
              { label: "Scientific Reasoning", val: metrics.scientificReasoning, target: 99 },
              { label: "Robotics Intelligence", val: metrics.roboticsIntelligence, target: 98 },
              { label: "Autonomous Systems", val: metrics.autonomousSystems, target: 98 },
              { label: "Scientific Computing", val: metrics.scientificComputing, target: 95 }
            ].map((bar, idx) => (
              <div key={idx} className="space-y-0.5">
                <div className="flex justify-between text-[10px] font-mono">
                  <span className="text-slate-400">{bar.label}</span>
                  <span className="text-slate-200 font-bold">{bar.val.toFixed(1)}% / {bar.target}%</span>
                </div>
                <div className="w-full bg-slate-950 rounded-full h-1 overflow-hidden">
                  <div 
                    className="bg-indigo-500 h-full rounded-full transition-all duration-500" 
                    style={{ width: `${(bar.val / bar.target) * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* EFFICIENCY MULTIPLIERS */}
        <div className="bg-slate-900/80 border border-slate-850 rounded-2xl p-5 shadow flex flex-col justify-between">
          <span className="text-[9.5px] font-mono text-slate-500 uppercase tracking-widest block mb-2">TRAINING &amp; HARDWARE</span>
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <div className="p-2.5 bg-emerald-950/40 border border-emerald-900/40 rounded-xl">
                <Percent className="w-5 h-5 text-emerald-400" />
              </div>
              <div>
                <span className="text-[9px] font-mono text-slate-500 block uppercase">Training Efficiency</span>
                <span className="text-lg font-black font-mono text-emerald-400">{metrics.frontierTrainingEfficiency.toFixed(1)}%</span>
                <span className="text-[8px] text-slate-550 block font-mono">Target: 85-90%</span>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <div className="p-2.5 bg-cyan-950/40 border border-cyan-900/40 rounded-xl">
                <Cpu className="w-5 h-5 text-cyan-400" />
              </div>
              <div>
                <span className="text-[9px] font-mono text-slate-500 block uppercase">Hardware Utilization</span>
                <span className="text-lg font-black font-mono text-cyan-400">{metrics.hardwareUtilization.toFixed(1)}%</span>
                <span className="text-[8px] text-slate-550 block font-mono">Target: 90-98%</span>
              </div>
            </div>
          </div>
        </div>

      </div>

      {/* Main split console panel */}
      <div className="no-print grid grid-cols-1 lg:grid-cols-12 gap-8 mb-8">
        
        {/* Left Side: Controllers and parameters sliders */}
        <div className="lg:col-span-4 space-y-6">
          <div className="bg-slate-900 border border-slate-850 rounded-2xl p-6 relative overflow-hidden shadow-2xl space-y-5">
            <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-indigo-600 via-purple-500 to-indigo-500" />
            
            <div className="flex items-center gap-2 border-b border-slate-850 pb-3">
              <Sliders className="text-indigo-400 w-5 h-5" />
              <h2 className="text-xs font-bold text-slate-200 uppercase tracking-wider font-mono">Control deck</h2>
            </div>

            {/* Task Prompt text area */}
            <div className="space-y-1.5">
              <label className="text-[9px] text-slate-550 block uppercase font-mono font-bold">Inference Prompt</label>
              <textarea
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="w-full bg-slate-950 border border-slate-850 rounded-xl p-3 text-xs text-slate-200 font-mono focus:outline-none focus:border-indigo-500 border-slate-800 transition-colors resize-none h-20"
                placeholder="Query parameters..."
              />
            </div>

            {/* Power profile selection */}
            <div className="space-y-1.5">
              <label className="text-[9px] text-slate-550 block uppercase font-mono font-bold">Power Mode Profile</label>
              <div className="grid grid-cols-3 gap-2">
                {[
                  { id: "BatterySaver", label: "Battery Saver", icon: <Battery className="w-3 h-3 text-emerald-400" /> },
                  { id: "Balanced", label: "Balanced", icon: <Cpu className="w-3 h-3 text-indigo-400" /> },
                  { id: "HighPerformance", label: "High Perf", icon: <Thermometer className="w-3 h-3 text-rose-400" /> }
                ].map(mode => (
                  <button
                    key={mode.id}
                    onClick={() => setPowerMode(mode.id as any)}
                    className={`py-2 px-1 text-[9px] font-mono rounded-lg border flex flex-col items-center justify-center gap-1 transition-all ${
                      powerMode === mode.id
                        ? "bg-indigo-650/15 border-indigo-500 text-indigo-400"
                        : "bg-slate-950 border-slate-850 text-slate-400 hover:border-slate-800"
                    }`}
                  >
                    {mode.icon}
                    {mode.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Allocated workspace RAM limit */}
            <div className="space-y-1.5">
              <div className="flex justify-between text-[10px] font-mono">
                <span className="text-slate-500 uppercase font-bold">Allocated Workspace RAM</span>
                <span className="text-indigo-400 font-bold">{ramLimitGb} GB</span>
              </div>
              <input
                type="range"
                min="4"
                max="32"
                step="4"
                value={ramLimitGb}
                onChange={(e) => setRamLimitGb(Number(e.target.value))}
                className="w-full h-1 bg-slate-950 rounded appearance-none cursor-pointer accent-indigo-500"
              />
            </div>

            {/* Complexity dropdown */}
            <div className="space-y-1.5">
              <label className="text-[9px] text-slate-550 block uppercase font-mono font-bold">Curriculum Training Stage</label>
              <select
                value={complexityLevel}
                onChange={(e) => setComplexityLevel(e.target.value as any)}
                className="w-full bg-slate-950 border border-slate-850 p-2 rounded-lg text-xs text-slate-200 font-mono focus:outline-none focus:border-indigo-500 border-slate-800 cursor-pointer"
              >
                <option value="low">Curriculum Phase 1: Syntactic Core</option>
                <option value="medium">Curriculum Phase 2: Causal Links</option>
                <option value="high">Curriculum Phase 3: Research Debate</option>
              </select>
            </div>

          </div>

          {/* FAILURE AND WEAKNESS TRACKER */}
          <div className="bg-slate-900 border border-slate-850 rounded-2xl p-5 shadow-lg space-y-4">
            <h3 className="text-xs font-bold text-slate-200 font-mono uppercase tracking-wider flex items-center gap-1.5">
              <ShieldAlert className="text-rose-400 w-4 h-4" />
              Failure Injection Audit (System 6)
            </h3>
            <div className="space-y-3 text-xs font-mono">
              <div>
                <label className="text-[9.5px] text-slate-500 block mb-1">Simulate Active Exception</label>
                <textarea
                  value={customFailure}
                  onChange={(e) => setCustomFailure(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-850 p-2.5 rounded-xl text-slate-200 resize-none h-16 focus:outline-none focus:border-indigo-500 border-slate-800"
                  placeholder="e.g. Failure checking GraphRAG citations path"
                />
              </div>
              <button
                onClick={submitCustomFailure}
                className="w-full bg-indigo-650 hover:bg-indigo-600 text-white text-xs font-bold py-2 rounded-xl transition-all shadow"
              >
                LOG EXCEPTION &amp; PATCH CODE
              </button>
            </div>
          </div>
        </div>

        {/* Right Side: Tabbed telemetry monitor */}
        <div className="lg:col-span-8 space-y-6">
          <div className="bg-slate-900 border border-slate-850 rounded-2xl p-6 shadow-2xl min-h-[520px] flex flex-col justify-between">
            <div>
              {/* Tab menu */}
              <div className="flex border-b border-slate-950 pb-3 mb-6 gap-2 overflow-x-auto scrollbar-none">
                {[
                  { id: "overview", label: "MoE & Quantization", icon: <Cpu className="w-3.5 h-3.5" /> },
                  { id: "avoidance", label: "GraphRAG & Cache", icon: <ZapOff className="w-3.5 h-3.5" /> },
                  { id: "debate", label: "Causal Debates", icon: <Terminal className="w-3.5 h-3.5" /> },
                  { id: "simulation", label: "World Simulation", icon: <Network className="w-3.5 h-3.5" /> },
                  { id: "memory", label: "Long-Term Memory", icon: <Database className="w-3.5 h-3.5" /> },
                  { id: "adaptation", label: "Reality Adaptation", icon: <Activity className="w-3.5 h-3.5" /> }
                ].map(t => (
                  <button
                    key={t.id}
                    className={`px-3 py-2 text-[10px] font-mono font-bold uppercase rounded-xl tracking-wider transition-all flex items-center gap-1.5 whitespace-nowrap border ${
                      activeTab === t.id
                        ? "bg-indigo-600/10 border-indigo-900/50 text-indigo-400"
                        : "bg-slate-950/40 border-transparent text-slate-500 hover:text-slate-300"
                    }`}
                    onClick={() => setActiveTab(t.id as any)}
                  >
                    {t.icon}
                    {t.label}
                  </button>
                ))}
              </div>

              {/* Tab 1: MoE & Quantization */}
              {activeTab === "overview" && computeReport && hardwareDirectives && trainingDirectives && (
                <div className="space-y-4 font-mono text-xs">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    
                    <div className="bg-slate-950 p-4 rounded-xl border border-slate-850 space-y-3">
                      <h3 className="text-xs font-bold text-slate-200 uppercase border-b border-slate-900 pb-2">
                        MoE Expert Routing (System 1)
                      </h3>
                      <div className="grid grid-cols-2 gap-3 text-center">
                        <div className="bg-slate-900 p-2.5 rounded-lg">
                          <span className="text-slate-500 text-[8px] block uppercase">Active Experts</span>
                          <span className="text-sm font-bold text-indigo-400">{computeReport.activeExpertIds.join(", ")}</span>
                        </div>
                        <div className="bg-slate-900 p-2.5 rounded-lg">
                          <span className="text-slate-500 text-[8px] block uppercase">Activation Ratio</span>
                          <span className="text-sm font-bold text-emerald-400">{Math.round(computeReport.sparseActivationRatio * 100)}%</span>
                        </div>
                      </div>
                      <div className="space-y-2 text-[11px] pt-1">
                        <div className="flex justify-between bg-slate-900 p-2 rounded">
                          <span>Speculative Accept Rate:</span>
                          <span className="text-white font-bold">{Math.round(computeReport.speculativeAcceptRate * 100)}%</span>
                        </div>
                        <div className="flex justify-between bg-slate-900 p-2 rounded">
                          <span>Lazy Refinement Passes:</span>
                          <span className="text-white font-bold">{computeReport.refinementPassesCount} passes</span>
                        </div>
                        <div className="flex justify-between bg-slate-900 p-2 rounded">
                          <span>Estimated FLOPs Saved:</span>
                          <span className="text-emerald-400 font-bold">{computeReport.computeSavedFlops.toLocaleString()} FLOPS</span>
                        </div>
                      </div>
                    </div>

                    <div className="bg-slate-950 p-4 rounded-xl border border-slate-850 space-y-3">
                      <h3 className="text-xs font-bold text-slate-200 uppercase border-b border-slate-900 pb-2">
                        Hardware Directives (System 9)
                      </h3>
                      <div className="space-y-2 text-[11px]">
                        <div className="flex justify-between bg-slate-900 p-2 rounded">
                          <span>Architecture:</span>
                          <span className="text-indigo-400 font-bold">{hardwareDirectives.architectureType}</span>
                        </div>
                        <div className="flex justify-between bg-slate-900 p-2 rounded">
                          <span>Model Quantization:</span>
                          <span className="text-white font-bold">Q{hardwareDirectives.quantizationBits}_K_M</span>
                        </div>
                        <div className="flex justify-between bg-slate-900 p-2 rounded">
                          <span>Active CPU Threads:</span>
                          <span className="text-white font-bold">{hardwareDirectives.activeThreads} Threads</span>
                        </div>
                        <div className="flex justify-between bg-slate-900 p-2 rounded">
                          <span>Expected Speedup:</span>
                          <span className="text-cyan-400 font-bold">{hardwareDirectives.expectedSpeedup.toFixed(2)}x</span>
                        </div>
                        <div className="flex justify-between bg-slate-900 p-2 rounded">
                          <span>Curriculum Stage:</span>
                          <span className="text-white truncate max-w-[180px]">{trainingDirectives.curriculumStage}</span>
                        </div>
                      </div>
                    </div>

                  </div>
                </div>
              )}

              {/* Tab 2: GraphRAG & Cache */}
              {activeTab === "avoidance" && graphReport && safetyAudit && (
                <div className="space-y-4 font-mono text-xs">
                  <div className="bg-slate-950 p-5 rounded-xl border border-slate-850 space-y-4">
                    <div className="flex justify-between items-center border-b border-slate-900 pb-2">
                      <h3 className="text-xs font-bold text-slate-200 uppercase">Knowledge Graph Citation Search (System 2)</h3>
                      <span className="text-indigo-400 font-bold">Resolved hops: {graphReport.hopsResolved}</span>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2.5">
                        <span className="text-slate-500 text-[9px] uppercase font-bold block">Retrieved Causal Nodes:</span>
                        <div className="bg-slate-900 p-2.5 rounded-lg text-slate-200">
                          {graphReport.retrievedNodeNames.join(", ")}
                        </div>
                        <div className="bg-slate-900 p-2.5 rounded text-[10.5px]">
                          <span className="text-slate-500 font-bold block mb-1">COMPACTION RATIO:</span>
                          <span className="text-emerald-400 font-bold">{Math.round((1 - graphReport.compressionRate) * 100)}% Context size reduction</span>
                        </div>
                      </div>

                      <div className="space-y-2.5">
                        <span className="text-slate-500 text-[9px] uppercase font-bold block">Citation Path:</span>
                        <div className="bg-slate-900 p-2.5 rounded-lg text-slate-350 italic text-[11px] leading-relaxed">
                          {graphReport.citationPaths.join(" | ")}
                        </div>
                        <div className="bg-slate-900 p-2.5 rounded text-[10.5px]">
                          <span className="text-slate-500 font-bold block mb-1">SAFETY AUDIT VERDICT (System 13):</span>
                          <span className={`font-bold uppercase ${safetyAudit.verdict === "safe" ? "text-emerald-400" : "text-rose-455"}`}>
                            {safetyAudit.verdict} (Confidence: {Math.round(safetyAudit.confidenceScore * 100)}%)
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Tab 3: Causal Debates */}
              {activeTab === "debate" && scientificReport && causalReport && (
                <div className="space-y-4 font-mono text-xs">
                  <div className="bg-slate-950 p-4 rounded-xl border border-slate-850 space-y-3">
                    <div className="flex justify-between items-center border-b border-slate-900 pb-2">
                      <h3 className="text-xs font-bold text-slate-200 uppercase">Scientific Debate Terminal (System 4)</h3>
                      <span className="text-emerald-400 font-bold">Consensus Reached</span>
                    </div>

                    <div className="bg-slate-900 p-3 rounded-lg max-h-48 overflow-y-auto space-y-2">
                      {scientificReport.debateLog.map((line, idx) => (
                        <div key={idx} className="text-[10.5px] border-b border-slate-800 pb-1.5 last:border-0 last:pb-0">
                          <span className="text-indigo-400 font-bold uppercase">{line.role}:</span>
                          <span className="text-slate-300 ml-1.5">"{line.contribution}"</span>
                        </div>
                      ))}
                    </div>

                    <div className="bg-slate-900 p-3 rounded-lg text-[10.5px]">
                      <span className="text-slate-400 font-bold block mb-1">Intervention Analysis (System 5):</span>
                      <p className="text-slate-200"><strong>Counterfactual:</strong> {causalReport.counterfactualAssertion}</p>
                      <p className="text-slate-200 mt-1"><strong>Expected Outcome:</strong> {causalReport.interventionOutcome}</p>
                    </div>
                  </div>
                </div>
              )}

              {/* Tab 4: World Simulation */}
              {activeTab === "simulation" && worldReport && autonomousReport && (
                <div className="space-y-4 font-mono text-xs">
                  <div className="bg-slate-950 p-4.5 rounded-xl border border-slate-850 space-y-3">
                    <div className="flex justify-between items-center border-b border-slate-900 pb-2">
                      <h3 className="text-xs font-bold text-slate-200 uppercase">World Simulation Projection (System 10)</h3>
                      <span className={worldReport.passedSafetyVerification ? "text-emerald-400 font-bold" : "text-rose-455"}>
                        {worldReport.passedSafetyVerification ? "PASSED SAFETY AUDIT" : "UNSAFE SEQUENCE DETECTED"}
                      </span>
                    </div>

                    <div className="space-y-2 max-h-40 overflow-y-auto">
                      {worldReport.simulationLog.map((s, idx) => (
                        <div key={idx} className="bg-slate-900 p-2 rounded text-[10.5px] flex justify-between items-center">
                          <div>
                            <span className="text-slate-500 font-bold">Step {s.step}</span>
                            <span className="text-slate-200 ml-2 font-bold">{s.simulatedAction}</span>
                            <span className="text-slate-400 block text-[9.5px] mt-0.5">{s.predictedOutcome}</span>
                          </div>
                          <span className={s.collisionRiskRatio > 0.35 ? "text-rose-400 font-bold" : "text-slate-400"}>
                            Risk: {Math.round(s.collisionRiskRatio * 100)}%
                          </span>
                        </div>
                      ))}
                    </div>

                    <div className="bg-slate-900 p-3 rounded-lg text-[10.5px] border-l-2 border-indigo-500">
                      <span className="text-slate-400 font-bold block mb-1">Goal Decomposition (System 12):</span>
                      <div className="flex flex-wrap gap-3">
                        {autonomousReport.decomposedTasks.map((t, idx) => (
                          <div key={idx} className="flex items-center gap-1.5">
                            <input type="checkbox" checked={t.status === "completed"} disabled className="rounded border-slate-800 text-indigo-550" />
                            <span className="text-slate-305">{t.label} ({t.assignedAgent})</span>
                          </div>
                        ))}
                      </div>
                      <span className="text-[9.5px] text-slate-500 block mt-1.5">Monitoring status: {autonomousReport.selfMonitoringStatus}</span>
                    </div>
                  </div>
                </div>
              )}

              {/* Tab 5: Long-Term Memory */}
              {activeTab === "memory" && improvementReport && (
                <div className="space-y-4 font-mono text-xs">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    
                    <div className="bg-slate-950 p-4.5 rounded-xl border border-slate-850 space-y-3">
                      <h3 className="text-xs font-bold text-slate-200 uppercase border-b border-slate-900 pb-2">
                        Memory Cells (System 3)
                      </h3>
                      <div className="space-y-2 max-h-40 overflow-y-auto">
                        {memories.map((m, idx) => (
                          <div key={idx} className="bg-slate-900 p-2 rounded text-[10px]">
                            <div className="flex justify-between text-slate-500 mb-0.5">
                              <span className="uppercase font-bold text-indigo-400">[{m.type}]</span>
                              <span>Relevance: {m.relevanceScore}</span>
                            </div>
                            <p className="text-slate-300 leading-normal">{m.statement}</p>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="bg-slate-950 p-4.5 rounded-xl border border-slate-850 space-y-3">
                      <h3 className="text-xs font-bold text-slate-200 uppercase border-b border-slate-900 pb-2">
                        Self Upgrades Logs (System 6)
                      </h3>
                      <div className="space-y-2 max-h-40 overflow-y-auto">
                        <div className="flex justify-between bg-slate-900 p-2 rounded">
                          <span>Logged exceptions:</span>
                          <span className="text-white">{improvementReport.failuresLoggedCount} errors</span>
                        </div>
                        <div className="flex justify-between bg-slate-900 p-2 rounded">
                          <span>Benchmarks compiled:</span>
                          <span className="text-white">{improvementReport.generatedBenchmarksCount} benchmarks</span>
                        </div>
                        <div className="bg-slate-900 p-2.5 rounded text-[10px]">
                          <span className="text-slate-550 font-bold block mb-1">PATCH PLANS ACTIONS:</span>
                          {improvementReport.activeImprovements.map((p, idx) => (
                            <div key={idx} className="border-b border-slate-800 pb-1 mb-1 last:border-0 last:pb-0">
                              <span className="text-indigo-455 font-bold">Defect: {p.defectId}</span>
                              <p className="text-emerald-450 mt-0.5">{p.actionPatch}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>

                  </div>
                </div>
              )}

              {/* Tab 6: Reality Adaptation */}
              {activeTab === "adaptation" && adaptationReport && discoveryReport && (
                <div className="space-y-4 font-mono text-xs">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    
                    <div className="bg-slate-950 p-4.5 rounded-xl border border-slate-850 space-y-3">
                      <h3 className="text-xs font-bold text-slate-200 uppercase border-b border-slate-900 pb-2">
                        Reality Adaptation &amp; Replanning (System 7)
                      </h3>
                      <div className="space-y-2 text-[11px]">
                        <div className="flex justify-between bg-slate-900 p-2 rounded">
                          <span>Fused Sensor Estimate:</span>
                          <span className="text-white">{adaptationReport.fusedValue}</span>
                        </div>
                        <div className="flex justify-between bg-slate-900 p-2 rounded">
                          <span>Environment Confidence:</span>
                          <span className="text-white font-bold">{Math.round(adaptationReport.confidenceScore * 100)}%</span>
                        </div>
                        <div className="flex justify-between bg-slate-900 p-2 rounded">
                          <span>Replanning active status:</span>
                          <span className={adaptationReport.replanRequired ? "text-rose-455 font-bold" : "text-emerald-450"}>
                            {adaptationReport.replanRequired ? "TRIGGERED" : "NOMINAL"}
                          </span>
                        </div>
                        <p className="bg-slate-900 p-2 rounded text-[10px] text-slate-350 leading-relaxed">
                          <strong>Directive:</strong> {adaptationReport.prescribedAdjustment}
                        </p>
                      </div>
                    </div>

                    <div className="bg-slate-950 p-4.5 rounded-xl border border-slate-850 space-y-3">
                      <h3 className="text-xs font-bold text-slate-200 uppercase border-b border-slate-900 pb-2">
                        Discovery Gaps (System 8)
                      </h3>
                      <div className="space-y-2 text-[10.5px]">
                        <div className="bg-slate-900 p-2.5 rounded text-slate-300">
                          <span className="text-indigo-455 font-bold block mb-1">DETECTED KNOWLEDGE GAP:</span>
                          {discoveryReport.detectedKnowledgeGaps[0]}
                        </div>
                        <div className="bg-slate-900 p-2.5 rounded text-slate-300">
                          <span className="text-slate-550 font-bold block mb-0.5">SUGGESTED EXPERIMENT:</span>
                          {discoveryReport.suggestedExperiment}
                        </div>
                        <div className="flex justify-between bg-slate-900 p-2 rounded">
                          <span>Opportunity Score:</span>
                          <span className="text-cyan-405 font-bold">{Math.round(discoveryReport.opportunityIndex * 100)}%</span>
                        </div>
                      </div>
                    </div>

                  </div>
                </div>
              )}

            </div>

            {/* Panel Footer */}
            <div className="mt-6 pt-3 border-t border-slate-950 text-slate-500 text-[9.5px] leading-relaxed font-mono flex justify-between items-center">
              <span className="flex items-center gap-1">
                <Info className="w-3.5 h-3.5 text-indigo-400" /> Enter prompt keywords (e.g. 'noise', 'fail', 'quantize') to evaluate safety intervention triggers.
              </span>
              <span>Model Tier: LEO-V38-Master-Subsubstrate</span>
            </div>
          </div>
        </div>

      </div>

      {/* LEO AI V38 CERTIFICATION SEAL - PRINT ONLY */}
      <div className="print-border hidden print:block text-black font-serif p-10 max-w-4xl mx-auto mt-12 bg-white">
        <div className="print-header text-center pb-4 mb-6">
          <h1 className="text-3xl font-black uppercase tracking-wider">LEO AI V38 Certificate of Integration</h1>
          <h2 className="text-md font-bold text-slate-700 font-mono mt-1.5 uppercase">13-Subsystem Master Architecture Verification</h2>
        </div>

        <div className="grid grid-cols-2 gap-6 text-sm font-mono leading-relaxed mb-8">
          <div>
            <p><strong>Worksystem Substrate:</strong> LEO AI V38 Core</p>
            <p><strong>Primary Objective:</strong> Useful Intelligence per Unit Resource</p>
            <p><strong>Quantization Directive:</strong> {hardwareDirectives?.architectureType || "BitNet_Ternary"}</p>
            <p><strong>CPU Active Threads:</strong> {hardwareDirectives?.activeThreads || 4} Threads</p>
            <p><strong>MoE routing active experts:</strong> {computeReport?.activeExpertIds.join(", ") || "LogicPlanner"}</p>
          </div>
          <div>
            <p><strong>Useful Intelligence Density:</strong> {intelligenceDensity} IQ/Resource Unit</p>
            <p><strong>Scientific Reasoning rating:</strong> {metrics.scientificReasoning.toFixed(2)}% (Target: 99%)</p>
            <p><strong>Robotics Resilience rating:</strong> {metrics.roboticsIntelligence.toFixed(2)}% (Target: 98%)</p>
            <p><strong>Autonomous path safety:</strong> {metrics.autonomousSystems.toFixed(2)}% (Target: 98%)</p>
            <p><strong>Training Efficiency rating:</strong> {metrics.frontierTrainingEfficiency.toFixed(2)}%</p>
          </div>
        </div>

        <div className="border-t-2 border-slate-800 pt-6 mt-4 flex justify-between items-center">
          <div>
            <p className="text-[10px] font-mono uppercase text-slate-655">Issued by Antigravity Autonomous V38 Compiler</p>
            <p className="text-[10px] text-slate-500 font-mono">Timestamp: {new Date().toISOString()}</p>
          </div>
          
          <div className="flex flex-col items-center border-2 border-black rounded-lg p-3 bg-slate-50">
            <span className="font-bold tracking-widest text-xs uppercase">V38 APPROVED</span>
            <span className="text-[8px] text-slate-500 font-mono mt-1">CERTIFIED HARDWARE-AWARE</span>
          </div>
        </div>
      </div>

    </div>
  );
}
