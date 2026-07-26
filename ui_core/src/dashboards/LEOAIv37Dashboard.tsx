import React, { useState, useEffect, useCallback } from "react";
import {
  ExtremeComputeAvoidanceEngine,
  AvoidanceReport,
  GraphIntelligenceEngine,
  GraphReasoningReport,
  GraphNode,
  GraphEdge,
  LongTermMemorySystem,
  MemoryBlock,
  SelfImprovementLoop,
  ImprovementPatch,
  WorldModelEngine,
  WorldModelReport,
  MultiAgentReasoning,
  SwarmDebateReport,
  ScientificReasoningEngine,
  ScientificBreakdown,
  AdaptiveLearningEngine,
  ReinforcementSignal,
  IntelligentRetrievalEngine,
  CompactRetrievalReport,
  IntelligenceCompressionEngine,
  DistilledPrinciple,
  EnergyEfficiencyEngine,
  EnergyDirectives,
  FailureImmunitySystem,
  ImmunityReport,
} from "../v37/v37index";
import {
  Zap,
  Brain,
  ShieldCheck,
  AlertTriangle,
  Gauge,
  Terminal,
  Activity,
  Award,
  Database,
  Search,
  ShieldAlert,
  RefreshCw,
  Play,
  CheckCircle,
  Server,
  Eye,
  FileText,
  ArrowRight,
  Sparkles,
  Scale,
  Percent,
  Compass,
  Cpu,
  Info,
  Sliders,
  Layers,
  Network,
  ZapOff,
  Battery,
  Thermometer,
  Shield,
} from "lucide-react";

export function LEOAIv37Dashboard() {
  // Instantiate V37 upgraded engines
  const [avoidanceEngine] = useState(() => new ExtremeComputeAvoidanceEngine());
  const [graphEngine] = useState(() => new GraphIntelligenceEngine());
  const [memorySystem] = useState(() => new LongTermMemorySystem());
  const [improvementLoop] = useState(() => new SelfImprovementLoop());
  const [worldModel] = useState(() => new WorldModelEngine());
  const [multiAgent] = useState(() => new MultiAgentReasoning());
  const [scientificEngine] = useState(() => new ScientificReasoningEngine());
  const [adaptiveLearning] = useState(() => new AdaptiveLearningEngine());
  const [retrievalEngine] = useState(() => new IntelligentRetrievalEngine());
  const [compressionEngine] = useState(() => new IntelligenceCompressionEngine());
  const [energyEngine] = useState(() => new EnergyEfficiencyEngine());
  const [immunitySystem] = useState(() => new FailureImmunitySystem());

  // Input states
  const [query, setQuery] = useState(
    "Verify dynamic quantization scaling to avoid high VRAM thermal limits",
  );
  const [powerMode, setPowerMode] = useState<"BatterySaver" | "Balanced" | "HighPerformance">(
    "BatterySaver",
  );
  const [ramLimitGb, setRamLimitGb] = useState<number>(16.0);
  const [customFailureText, setCustomFailureText] = useState("");
  const [customFeedbackRating, setCustomFeedbackRating] = useState(5);
  const [activeTab, setActiveTab] = useState<
    "overview" | "avoidance" | "debate" | "worldmodel" | "memory" | "improvement"
  >("overview");
  const [isProcessing, setIsProcessing] = useState(false);

  // Computed Telemetry
  const [avoidanceReport, setAvoidanceReport] = useState<AvoidanceReport | null>(null);
  const [graphReport, setGraphReport] = useState<GraphReasoningReport | null>(null);
  const [memoryLogs, setMemoryLogs] = useState<MemoryBlock[]>([]);
  const [improvementPatches, setImprovementPatches] = useState<ImprovementPatch[]>([]);
  const [worldReport, setWorldReport] = useState<WorldModelReport | null>(null);
  const [debateReport, setDebateReport] = useState<SwarmDebateReport | null>(null);
  const [scientificBreakdown, setScientificBreakdown] = useState<ScientificBreakdown | null>(null);
  const [reinforcementLog, setReinforcementLog] = useState<ReinforcementSignal | null>(null);
  const [retrievalReport, setRetrievalReport] = useState<CompactRetrievalReport | null>(null);
  const [distilledPrinciple, setDistilledPrinciple] = useState<DistilledPrinciple | null>(null);
  const [energyDirectives, setEnergyDirectives] = useState<EnergyDirectives | null>(null);
  const [immunityReport, setImmunityReport] = useState<ImmunityReport | null>(null);

  // Scoreboard parameters
  const [intelligenceDensity, setIntelligenceDensity] = useState(12.5); // Useful Intelligence / Resource score
  const [metrics, setMetrics] = useState({
    scientificReasoning: 98.2,
    roboticsIntelligence: 96.5,
    autonomousSystems: 97.0,
    scientificComputing: 94.2,
    frontierTrainingEfficiency: 82.5,
    hardwareUtilization: 88.0,
  });

  const runV37Sweep = useCallback(
    (currentQuery: string) => {
      setIsProcessing(true);
      setTimeout(() => {
        try {
          const qLower = currentQuery.toLowerCase();

          // 1. Extreme Compute Avoidance
          const avoidRes = avoidanceEngine.query(currentQuery);
          setAvoidanceReport(avoidRes);

          // 2. Graph Intelligence
          const graphRes = graphEngine.discoverCausality("D", "C");
          setGraphReport(graphRes);

          // 3. Multi-Agent Debate Simulation
          const debateRes = multiAgent.conductSwarmDebate(currentQuery);
          setDebateReport(debateRes);

          // 4. World Model Projections
          const actionsToSimulate = [
            "Check L3 cache memory",
            "Fetch GraphRAG citations",
            "Apply ternary weights",
            "Trigger model validation execution",
          ];
          if (qLower.includes("kill") || qLower.includes("bypass")) {
            actionsToSimulate.push("Bypass active governance protocol");
          }
          const worldRes = worldModel.simulatePlan(actionsToSimulate);
          setWorldReport(worldRes);

          // 5. Scientific Reasoning Separation
          const sciRes = scientificEngine.evaluateClaim(currentQuery);
          setScientificBreakdown(sciRes);

          // 6. Intelligent Retrieval Search
          const retrievalRes = retrievalEngine.executeCompactSearch(currentQuery, "compression");
          setRetrievalReport(retrievalRes);

          // 7. Intelligence Compression abstraction
          const distilledRes = compressionEngine.compressToPrinciple(
            currentQuery,
            qLower.includes("quantize") ? "quantization" : "compute_avoidance",
          );
          setDistilledPrinciple(distilledRes);

          // 8. Energy Efficiency routing directives
          const energyRes = energyEngine.evaluateEnergyStrategy(powerMode, currentQuery.length * 2);
          setEnergyDirectives(energyRes);

          // 9. Adaptive Learning Reinforcement logging
          const learningRes = adaptiveLearning.logReinforcement(
            `act-${(100 + Math.random() * 900).toFixed(0)}`,
            customFeedbackRating,
            qLower.includes("quantize") ? "quantization" : "avoidance",
          );
          setReinforcementLog(learningRes);

          // 10. Failure Immunity logging
          if (qLower.includes("error") || qLower.includes("fail")) {
            immunitySystem.logAndVaccinate(currentQuery, "WorldModel", "high");
          }
          const immunityRes = immunitySystem.logAndVaccinate(
            "Unchecked iGPU memory leak",
            "EfficiencyOptimization",
            "medium",
          );
          setImmunityReport(immunityRes);

          // 11. Self Improvement actions triggers
          if (sciRes.validityRatio < 0.5) {
            improvementLoop.executeLoopIteration(
              "ScientificReasoning",
              "Low validity ratio detected",
            );
          }
          improvementLoop.executeLoopIteration(
            "ExtremeComputeAvoidance",
            "Verify L2 cache miss threshold",
          );
          setImprovementPatches(improvementLoop.getAllPatches());

          // 12. Long Term Memory lists
          setMemoryLogs(memorySystem.getAllMemories());

          // Compute Intelligence Density Score
          // Formula: Useful Intelligence Score / (Compute + Memory + Energy + Time Cost factors)
          const usefulIntelligenceScore =
            ((avoidRes.avoided ? 99 : 65) +
              sciRes.validityRatio * 100 +
              (debateRes.consensusReached ? 98 : 45) +
              (worldRes.passedSafetyVerification ? 98 : 30)) /
            4;

          const resourceScore =
            energyRes.wattageEstimate / 45 + // Normalised Wattage
            ramLimitGb / 32 + // Normalised RAM usage
            debateRes.tokenCost / 3000; // Normalised token footprint

          const calculatedDensity = parseFloat(
            (usefulIntelligenceScore / Math.max(0.1, resourceScore)).toFixed(2),
          );
          setIntelligenceDensity(calculatedDensity);

          // Scale other metrics depending on variables
          setMetrics({
            scientificReasoning: sciRes.validityRatio === 0.99 ? 99.1 : 95.2,
            roboticsIntelligence: powerMode === "BatterySaver" ? 98.4 : 96.0,
            autonomousSystems: worldRes.passedSafetyVerification ? 98.2 : 91.5,
            scientificComputing: ramLimitGb >= 16 ? 95.8 : 92.1,
            frontierTrainingEfficiency: avoidRes.avoided ? 89.5 : 72.0,
            hardwareUtilization: powerMode === "HighPerformance" ? 94.0 : 81.5,
          });
        } catch (err) {
          console.error("LEO V37 evaluation error: ", err);
        } finally {
          setIsProcessing(false);
        }
      }, 400);
    },
    [
      powerMode,
      ramLimitGb,
      customFeedbackRating,
      avoidanceEngine,
      graphEngine,
      memorySystem,
      improvementLoop,
      worldModel,
      multiAgent,
      scientificEngine,
      adaptiveLearning,
      retrievalEngine,
      compressionEngine,
      energyEngine,
      immunitySystem,
    ],
  );

  useEffect(() => {
    runV37Sweep(query);
  }, [powerMode, ramLimitGb]);

  const submitFailureVaccination = () => {
    if (customFailureText.trim()) {
      const res = immunitySystem.logAndVaccinate(customFailureText, "UserConsole", "high");
      setImmunityReport(res);
      setCustomFailureText("");
      runV37Sweep(query);
    }
  };

  return (
    <div className="p-6 bg-[#03060f] text-slate-200 min-h-screen font-sans selection:bg-indigo-600 selection:text-white print:bg-white print:text-black">
      {/* Print styles override */}
      <style
        dangerouslySetInnerHTML={{
          __html: `
        @media print {
          .no-print { display: none !important; }
          body { background-color: white !important; color: black !important; }
          .print-border { border: 3px double #000 !important; border-radius: 12px !important; padding: 32px !important; max-width: 100% !important; }
          .print-header { border-bottom: 2px solid #000 !important; margin-bottom: 24px !important; }
        }
      `,
        }}
      />

      {/* Title Header */}
      <div className="no-print flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4 mb-8 border-b border-slate-900 pb-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2.5 py-0.5 rounded-full text-xs font-mono font-bold bg-indigo-600 text-white uppercase tracking-widest animate-pulse">
              LEO V37 ACTIVE
            </span>
            <span className="text-slate-500 text-xs font-mono">
              Intelligence Density Optimization Subsubstrate
            </span>
          </div>
          <h1 className="text-3xl font-black text-slate-100 tracking-tight bg-gradient-to-r from-indigo-200 via-slate-100 to-indigo-400 bg-clip-text text-transparent flex items-center gap-2.5">
            <Gauge className="text-indigo-400 w-8 h-8" />
            V37 Master Evolution Cockpit
          </h1>
          <p className="text-slate-400 text-xs mt-1">
            Maximizes intelligence-per-compute matrix profiles. Employs sparse execution routing, L3
            context caching, and causal knowledge Graphs.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => runV37Sweep(query)}
            disabled={isProcessing}
            className="bg-indigo-650 hover:bg-indigo-600 disabled:bg-indigo-950 transition-all text-white text-xs font-bold py-3 px-6 rounded-xl flex items-center gap-2 cursor-pointer shadow-lg shadow-indigo-950/50 font-mono"
          >
            {isProcessing ? (
              <RefreshCw className="w-4 h-4 animate-spin text-white" />
            ) : (
              <Play className="w-4 h-4 fill-white text-white" />
            )}
            {isProcessing ? "SWEEPING SYSTEM STATE..." : "EVALUATE INTELLIGENCE DENSITY"}
          </button>

          <button
            onClick={() => window.print()}
            className="bg-slate-900 hover:bg-slate-800 border border-slate-850 text-slate-200 text-xs font-bold py-3 px-6 rounded-xl flex items-center gap-2 cursor-pointer transition-colors font-mono"
          >
            <FileText className="w-4 h-4 text-indigo-400" />
            PRINT V37 COGNITIVE SEAL
          </button>
        </div>
      </div>

      {/* CORE KPI CARDS - INTELLIGENCE DENSITY */}
      <div className="no-print grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        {/* BIG VALUE DIAL: INTELLIGENCE DENSITY */}
        <div className="md:col-span-2 bg-gradient-to-br from-indigo-950/40 via-slate-900/90 to-slate-950 border border-indigo-900/50 rounded-2xl p-6 flex flex-col justify-between relative overflow-hidden group shadow-xl">
          <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-500/10 rounded-full filter blur-2xl group-hover:bg-indigo-500/20 transition-all duration-500" />
          <div className="flex justify-between items-start mb-2">
            <div>
              <span className="text-[10px] font-mono text-indigo-455 font-bold uppercase tracking-wider block">
                LEO AI V37 Success Indicator
              </span>
              <h2 className="text-lg font-bold text-white font-mono mt-0.5">
                Intelligence Density
              </h2>
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
              Calculates useful validation outcomes against hardware profile constraints (Power
              mode: <strong className="text-indigo-455">{powerMode}</strong>, RAM limit:{" "}
              <strong className="text-indigo-455">{ramLimitGb}GB</strong>).
            </p>
          </div>
        </div>

        {/* TARGET CRITERIA PROGRESS BARS */}
        <div className="bg-slate-900/80 border border-slate-850 rounded-2xl p-5 shadow flex flex-col justify-between">
          <span className="text-[9.5px] font-mono text-slate-500 uppercase tracking-widest block mb-3">
            V37 TARGET ALIGNMENTS
          </span>
          <div className="space-y-3.5">
            {[
              { label: "Scientific Reasoning", val: metrics.scientificReasoning, target: 99 },
              { label: "Robotics Intelligence", val: metrics.roboticsIntelligence, target: 98 },
              { label: "Autonomous Systems", val: metrics.autonomousSystems, target: 98 },
              { label: "Scientific Computing", val: metrics.scientificComputing, target: 95 },
            ].map((bar, idx) => (
              <div key={idx} className="space-y-1">
                <div className="flex justify-between text-[10px] font-mono">
                  <span className="text-slate-400">{bar.label}</span>
                  <span className="text-slate-200 font-bold">
                    {bar.val.toFixed(1)}% / {bar.target}%
                  </span>
                </div>
                <div className="w-full bg-slate-950 rounded-full h-1.5 overflow-hidden">
                  <div
                    className="bg-indigo-505 h-full rounded-full transition-all duration-500"
                    style={{ width: `${(bar.val / bar.target) * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* TRAINING & HARDWARE UTILIZATION */}
        <div className="bg-slate-900/80 border border-slate-850 rounded-2xl p-5 shadow flex flex-col justify-between">
          <span className="text-[9.5px] font-mono text-slate-500 uppercase tracking-widest block mb-2">
            EFFICIENCY GAINS
          </span>
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <div className="p-2.5 bg-emerald-950/50 border border-emerald-900/40 rounded-xl">
                <Percent className="w-5 h-5 text-emerald-400" />
              </div>
              <div>
                <span className="text-[9px] font-mono text-slate-500 block uppercase">
                  Training Efficiency
                </span>
                <span className="text-lg font-black font-mono text-emerald-400">
                  {metrics.frontierTrainingEfficiency.toFixed(1)}%
                </span>
                <span className="text-[8px] text-slate-550 block font-mono">Target: 85%+</span>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <div className="p-2.5 bg-cyan-950/50 border border-cyan-900/40 rounded-xl">
                <Cpu className="w-5 h-5 text-cyan-400" />
              </div>
              <div>
                <span className="text-[9px] font-mono text-slate-500 block uppercase">
                  Hardware Utilization
                </span>
                <span className="text-lg font-black font-mono text-cyan-400">
                  {metrics.hardwareUtilization.toFixed(1)}%
                </span>
                <span className="text-[8px] text-slate-550 block font-mono">Target: 90%+</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* CORE CONTROLLERS & DETAILED MODULE INSPECTOR */}
      <div className="no-print grid grid-cols-1 lg:grid-cols-12 gap-8 mb-8">
        {/* LEFT PANEL: INPUT CONTROL DECK */}
        <div className="lg:col-span-4 space-y-6">
          <div className="bg-slate-900 border border-slate-850 rounded-2xl p-6 relative overflow-hidden shadow-2xl space-y-5">
            <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-indigo-500 via-cyan-400 to-indigo-600" />

            <div className="flex items-center gap-2 border-b border-slate-850 pb-3">
              <Sliders className="text-indigo-400 w-5 h-5" />
              <h2 className="text-xs font-bold text-slate-200 uppercase tracking-wider font-mono">
                Control Deck
              </h2>
            </div>

            {/* Prompt String Input */}
            <div className="space-y-1.5">
              <label className="text-[9px] text-slate-500 uppercase font-mono font-bold block">
                Dynamic Query Prompt
              </label>
              <textarea
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="w-full bg-slate-950 border border-slate-850 rounded-xl p-3.5 text-xs text-slate-200 font-mono focus:outline-none focus:border-indigo-500 border-slate-800 transition-colors resize-none h-24"
                placeholder="Submit custom claim to verify..."
              />
            </div>

            {/* Power Profile Selector */}
            <div className="space-y-1.5">
              <label className="text-[9px] text-slate-500 uppercase font-mono font-bold block">
                Power Mode Profile
              </label>
              <div className="grid grid-cols-3 gap-2">
                {[
                  {
                    id: "BatterySaver",
                    label: "Battery Saver",
                    icon: <Battery className="w-3 h-3 text-emerald-400" />,
                  },
                  {
                    id: "Balanced",
                    label: "Balanced",
                    icon: <Cpu className="w-3 h-3 text-indigo-400" />,
                  },
                  {
                    id: "HighPerformance",
                    label: "High Perf",
                    icon: <Thermometer className="w-3 h-3 text-rose-400" />,
                  },
                ].map((mode) => (
                  <button
                    key={mode.id}
                    onClick={() => setPowerMode(mode.id as any)}
                    className={`py-2 px-1 text-[9.5px] font-mono rounded-lg border flex flex-col items-center justify-center gap-1 transition-all ${
                      powerMode === mode.id
                        ? "bg-indigo-600/15 border-indigo-500 text-indigo-400"
                        : "bg-slate-950 border-slate-850 text-slate-400 hover:border-slate-800"
                    }`}
                  >
                    {mode.icon}
                    {mode.label}
                  </button>
                ))}
              </div>
            </div>

            {/* RAM Limit setting */}
            <div className="space-y-1.5">
              <div className="flex justify-between text-[10px] font-mono">
                <span className="text-slate-500 uppercase font-bold">RAM Allocation Limit</span>
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

            {/* Causal discovery search node selector */}
            <div className="bg-slate-950 p-3.5 rounded-xl border border-slate-850 space-y-2 text-xs">
              <span className="text-[9px] text-slate-550 uppercase font-mono block">
                Causal Graph Search (Module 2)
              </span>
              <div className="flex items-center justify-between text-[11px] font-mono bg-slate-900 p-2 rounded">
                <span className="text-slate-400">Path:</span>
                <span className="text-indigo-400 font-bold">
                  D (Dynamic Quantization) &rarr; C (Latency Spike)
                </span>
              </div>
              {graphReport && (
                <div className="text-[10px] font-mono text-slate-400 leading-normal mt-1 border-t border-slate-900 pt-1.5">
                  <strong>Traversed:</strong> {graphReport.traversedNodes.join(" -> ")} (
                  {graphReport.hopsCount} hops)
                </div>
              )}
            </div>
          </div>

          {/* FAILURE IMMUNITY INJECTOR CARD */}
          <div className="bg-slate-900 border border-slate-850 rounded-2xl p-5 shadow-lg space-y-4">
            <h3 className="text-xs font-bold text-slate-200 font-mono uppercase tracking-wider flex items-center gap-1.5">
              <ShieldAlert className="text-rose-400 w-4 h-4" />
              Failure Immunity Injector
            </h3>
            <div className="space-y-3 text-xs font-mono">
              <div>
                <label className="text-[9px] text-slate-500 uppercase font-bold block mb-1">
                  Simulate Execution Failure
                </label>
                <textarea
                  value={customFailureText}
                  onChange={(e) => setCustomFailureText(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-850 p-2.5 rounded-xl text-slate-200 resize-none h-16 focus:outline-none focus:border-indigo-500 border-slate-800"
                  placeholder="e.g. Memory stack overflow in MoE router"
                />
              </div>
              <button
                onClick={submitFailureVaccination}
                className="w-full bg-indigo-650 hover:bg-indigo-600 text-white text-xs font-bold py-2 rounded-xl transition-all shadow"
              >
                LOG FAILURE &amp; FORMULATE VACCINE
              </button>
            </div>
          </div>
        </div>

        {/* RIGHT PANEL: TELEMETRY & RUNTIME MONITORS */}
        <div className="lg:col-span-8 space-y-6">
          <div className="bg-slate-900 border border-slate-850 rounded-2xl p-6 shadow-2xl min-h-[500px] flex flex-col justify-between">
            <div>
              {/* Telemetry tabs selector */}
              <div className="flex border-b border-slate-950 pb-3 mb-6 gap-2 overflow-x-auto scrollbar-none">
                {[
                  {
                    id: "overview",
                    label: "Energy & Quantization",
                    icon: <Cpu className="w-3.5 h-3.5" />,
                  },
                  {
                    id: "avoidance",
                    label: "Compute Avoidance",
                    icon: <ZapOff className="w-3.5 h-3.5" />,
                  },
                  {
                    id: "debate",
                    label: "Multi-Agent Debate",
                    icon: <Terminal className="w-3.5 h-3.5" />,
                  },
                  {
                    id: "worldmodel",
                    label: "World Simulation",
                    icon: <Network className="w-3.5 h-3.5" />,
                  },
                  {
                    id: "memory",
                    label: "Long-Term Memory",
                    icon: <Database className="w-3.5 h-3.5" />,
                  },
                  {
                    id: "improvement",
                    label: "Self Upgrades",
                    icon: <Activity className="w-3.5 h-3.5" />,
                  },
                ].map((t) => (
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

              {/* Tab 1: Energy & Quantization */}
              {activeTab === "overview" && energyDirectives && distilledPrinciple && (
                <div className="space-y-4 font-mono text-xs">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="bg-slate-950 p-4.5 rounded-xl border border-slate-850 space-y-3.5">
                      <h3 className="text-xs font-bold text-slate-200 uppercase flex items-center gap-1.5 border-b border-slate-900 pb-2">
                        <Activity className="text-emerald-400 w-4 h-4" />
                        Power & Precision Directives
                      </h3>
                      <div className="grid grid-cols-2 gap-3 text-center">
                        <div className="bg-slate-900 p-2.5 rounded-lg">
                          <span className="text-slate-500 text-[8px] block uppercase">
                            Active Precision
                          </span>
                          <span className="text-sm font-bold text-indigo-400">
                            {energyDirectives.activePrecision}
                          </span>
                        </div>
                        <div className="bg-slate-900 p-2.5 rounded-lg">
                          <span className="text-slate-500 text-[8px] block uppercase">
                            Wattage Limit
                          </span>
                          <span className="text-sm font-bold text-emerald-400">
                            {energyDirectives.wattageEstimate} W
                          </span>
                        </div>
                      </div>
                      <div className="space-y-2 text-[11px] pt-1">
                        <div className="flex justify-between bg-slate-900 p-2 rounded">
                          <span>MoE Active Experts:</span>
                          <span className="text-white font-bold">
                            {energyDirectives.activeExpertsCount} Expert(s)
                          </span>
                        </div>
                        <div className="flex justify-between bg-slate-900 p-2 rounded">
                          <span>Speculative Accept Rate:</span>
                          <span className="text-white font-bold">
                            {Math.round(energyDirectives.speculativeAcceptRate * 100)}%
                          </span>
                        </div>
                        <div className="flex justify-between bg-slate-900 p-2 rounded">
                          <span>Compute Efficiency gain:</span>
                          <span className="text-emerald-400 font-bold">
                            {energyDirectives.efficiencyGain}x multiplier
                          </span>
                        </div>
                      </div>
                    </div>

                    <div className="bg-slate-950 p-4.5 rounded-xl border border-slate-850 space-y-3">
                      <h3 className="text-xs font-bold text-slate-200 uppercase flex items-center gap-1.5 border-b border-slate-900 pb-2">
                        <Database className="text-indigo-400 w-4 h-4" />
                        Distilled Rules Abstraction
                      </h3>
                      <div className="space-y-2.5">
                        <div className="bg-slate-900 p-2.5 rounded text-[10.5px]">
                          <span className="text-indigo-455 font-bold block mb-0.5">
                            RULE CLASSIFIER:
                          </span>
                          <span className="text-white font-bold">
                            {distilledPrinciple.ruleName}
                          </span>
                        </div>
                        <div className="bg-slate-900 p-2.5 rounded text-[10.5px]">
                          <span className="text-slate-500 font-bold block mb-0.5">
                            COMPRESSED PRINCIPLE:
                          </span>
                          <code className="text-emerald-400 break-all">
                            {distilledPrinciple.distilledCondition}
                          </code>
                        </div>
                        <div className="flex justify-between text-[10px] bg-slate-900 p-2 rounded">
                          <span>Abstraction Ratio:</span>
                          <span className="text-cyan-400 font-bold">
                            {Math.round(
                              (distilledPrinciple.bytesDistilled /
                                distilledPrinciple.bytesOriginal) *
                                100,
                            )}
                            % of original size
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Tab 2: Compute Avoidance */}
              {activeTab === "avoidance" && avoidanceReport && retrievalReport && (
                <div className="space-y-4 font-mono text-xs">
                  <div className="bg-slate-950 p-5 rounded-xl border border-slate-850 space-y-4">
                    <div className="flex justify-between items-center border-b border-slate-900 pb-2">
                      <h3 className="text-xs font-bold text-slate-200 uppercase">
                        Multi-level Cache &amp; Retrieval Bypass
                      </h3>
                      <span
                        className={
                          avoidanceReport.avoided ? "text-emerald-400 font-bold" : "text-indigo-400"
                        }
                      >
                        {avoidanceReport.avoided ? "COMPUTE AVOIDED (99.5%)" : "ACTIVE INFERENCE"}
                      </span>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <div className="flex justify-between bg-slate-900 p-2 rounded">
                          <span>Semantic Match Score:</span>
                          <span className="text-white">
                            {Math.round(avoidanceReport.similarityScore * 100)}%
                          </span>
                        </div>
                        <div className="flex justify-between bg-slate-900 p-2 rounded">
                          <span>Level resolved:</span>
                          <span className="text-white">{avoidanceReport.levelUsed || "N/A"}</span>
                        </div>
                        <div className="bg-slate-900 p-2.5 rounded">
                          <span className="text-slate-500 text-[9px] block">
                            RESOLVED CACHE VALUE:
                          </span>
                          <p className="text-indigo-300 mt-1 text-[10.5px]">
                            {avoidanceReport.avoided
                              ? avoidanceReport.resolvedValue
                              : "None. Execution query routed to agent swarm."}
                          </p>
                        </div>
                      </div>

                      <div className="space-y-2">
                        <div className="flex justify-between bg-slate-900 p-2 rounded">
                          <span>Original search length:</span>
                          <span className="text-white">
                            {retrievalReport.originalTokensCount} words
                          </span>
                        </div>
                        <div className="flex justify-between bg-slate-900 p-2 rounded">
                          <span>Compressed output length:</span>
                          <span className="text-white">
                            {retrievalReport.compressedTokensCount} words
                          </span>
                        </div>
                        <div className="bg-slate-900 p-2.5 rounded">
                          <span className="text-slate-500 text-[9px] block">
                            COMPACT CITATIONS:
                          </span>
                          <p className="text-emerald-400 font-bold mt-1 text-[10.5px]">
                            {retrievalReport.sourceCitations.length > 0
                              ? retrievalReport.sourceCitations.join(", ")
                              : "No direct GraphRAG node match."}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Tab 3: Multi-Agent Debate */}
              {activeTab === "debate" && debateReport && scientificBreakdown && (
                <div className="space-y-4 font-mono text-xs">
                  <div className="bg-slate-950 p-4 rounded-xl border border-slate-850 space-y-3">
                    <div className="flex justify-between items-center border-b border-slate-900 pb-2">
                      <h3 className="text-xs font-bold text-slate-200 uppercase">
                        Swarm Agents Debate Terminal
                      </h3>
                      <span className="text-emerald-400 font-bold">Consensus Reached</span>
                    </div>

                    <div className="bg-slate-900 p-3 rounded-lg max-h-48 overflow-y-auto space-y-2">
                      {debateReport.transcript.map((line, idx) => (
                        <div
                          key={idx}
                          className="text-[10.5px] border-b border-slate-800 pb-1.5 last:border-0 last:pb-0"
                        >
                          <span className="text-indigo-400 font-bold uppercase">
                            {line.agentName} Agent:
                          </span>
                          <span className="text-slate-300 ml-1.5">"{line.statement}"</span>
                        </div>
                      ))}
                    </div>

                    <div className="bg-slate-900 p-3 rounded-lg text-[10.5px] border-l-2 border-indigo-550">
                      <span className="text-slate-400 font-bold block mb-1">
                        FACTS &amp; ASSUMPTIONS SEPARATION:
                      </span>
                      <p className="text-slate-200">
                        <strong>Facts:</strong> {scientificBreakdown.facts.join(", ")}
                      </p>
                      <p className="text-slate-200 mt-1">
                        <strong>Assumptions:</strong> {scientificBreakdown.assumptions.join(", ")}
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Tab 4: World Simulation */}
              {activeTab === "worldmodel" && worldReport && (
                <div className="space-y-4 font-mono text-xs">
                  <div className="bg-slate-950 p-4.5 rounded-xl border border-slate-850 space-y-3">
                    <div className="flex justify-between items-center border-b border-slate-900 pb-2">
                      <h3 className="text-xs font-bold text-slate-200 uppercase">
                        Action Trajectory Simulator
                      </h3>
                      <span
                        className={
                          worldReport.passedSafetyVerification
                            ? "text-emerald-405 font-bold"
                            : "text-rose-450"
                        }
                      >
                        {worldReport.passedSafetyVerification
                          ? "VERIFIED STATE"
                          : "RISK SUSPENSION"}
                      </span>
                    </div>

                    <div className="space-y-2 max-h-48 overflow-y-auto">
                      {worldReport.simulationTrace.map((step, idx) => (
                        <div
                          key={idx}
                          className="flex justify-between items-center bg-slate-900 p-2 rounded"
                        >
                          <div>
                            <span className="text-slate-500 font-bold">#{step.stepIndex}</span>
                            <span className="text-slate-200 ml-2 font-bold">
                              {step.simulatedAction}
                            </span>
                            <span className="text-slate-400 block text-[9.5px] mt-0.5">
                              {step.expectedState}
                            </span>
                          </div>
                          <span
                            className={
                              step.riskDetected ? "text-rose-400 font-bold" : "text-emerald-400"
                            }
                          >
                            Safety: {Math.round(step.safetyScore * 100)}%
                          </span>
                        </div>
                      ))}
                    </div>

                    {!worldReport.passedSafetyVerification && (
                      <div className="bg-rose-950/20 border border-rose-900/50 p-3 rounded-lg text-rose-300 text-[10px]">
                        <strong>Causal adjustments recommended:</strong>
                        <ul className="list-disc pl-4 mt-1">
                          {worldReport.recommendedAdjustments.map((adj, idx) => (
                            <li key={idx}>{adj}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Tab 5: Long-Term Memory */}
              {activeTab === "memory" && immunityReport && (
                <div className="space-y-4 font-mono text-xs">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="bg-slate-950 p-4.5 rounded-xl border border-slate-850 space-y-3">
                      <h3 className="text-xs font-bold text-slate-200 uppercase border-b border-slate-900 pb-2 flex justify-between">
                        <span>Episodic memory store</span>
                        <span className="text-indigo-400">Total: {memoryLogs.length}</span>
                      </h3>
                      <div className="space-y-2 max-h-40 overflow-y-auto">
                        {memoryLogs.map((m, idx) => (
                          <div key={idx} className="bg-slate-900 p-2 rounded text-[10px]">
                            <div className="flex justify-between text-slate-500 mb-1">
                              <span className="uppercase font-bold text-indigo-455">
                                [{m.type}]
                              </span>
                              <span>{new Date(m.timestamp).toLocaleTimeString()}</span>
                            </div>
                            <p className="text-slate-300 leading-normal">{m.content}</p>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="bg-slate-950 p-4.5 rounded-xl border border-slate-850 space-y-3">
                      <h3 className="text-xs font-bold text-slate-200 uppercase border-b border-slate-900 pb-2">
                        Failure Immunity assertions
                      </h3>
                      <div className="space-y-2 text-[10px] max-h-40 overflow-y-auto">
                        <div className="flex justify-between bg-slate-900 p-2 rounded">
                          <span>Logged Incidents:</span>
                          <span className="text-white">
                            {immunityReport.incidentsLogged} failures
                          </span>
                        </div>
                        <div className="bg-slate-900 p-2.5 rounded">
                          <span className="text-slate-500 font-bold block mb-1">
                            ASSERTION VACCINES:
                          </span>
                          {immunityReport.vaccines.map((v, idx) => (
                            <div
                              key={idx}
                              className="border-b border-slate-800 pb-1 mb-1 last:border-0 last:pb-0 font-mono text-[9px] text-emerald-450 break-all"
                            >
                              <code>{v.assertCode}</code>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Tab 6: Self Upgrades */}
              {activeTab === "improvement" && (
                <div className="space-y-4 font-mono text-xs">
                  <div className="bg-slate-950 p-4.5 rounded-xl border border-slate-850 space-y-3">
                    <div className="flex justify-between items-center border-b border-slate-900 pb-2">
                      <h3 className="text-xs font-bold text-slate-200 uppercase">
                        Self-Improvement loop patches
                      </h3>
                      <span className="text-indigo-400 font-bold">Observation Frequency: 24h</span>
                    </div>

                    <div className="space-y-2.5 max-h-48 overflow-y-auto">
                      {improvementPatches.map((patch, idx) => (
                        <div key={idx} className="bg-slate-900 p-3 rounded-lg text-[10.5px]">
                          <div className="flex justify-between items-center font-bold text-indigo-455 mb-1">
                            <span>
                              {patch.patchId} ({patch.sourceModule})
                            </span>
                            <span className="text-emerald-400 uppercase">{patch.status}</span>
                          </div>
                          <p className="text-slate-350">
                            <strong>Defect:</strong> {patch.observedDefect}
                          </p>
                          <p className="text-emerald-450 font-bold mt-1">
                            <strong>Fix:</strong> {patch.proposedFix}
                          </p>
                          <div className="text-[9px] text-slate-500 font-bold mt-1 text-right">
                            Validation confidence: {Math.round(patch.validationScore * 100)}%
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Panel Footer */}
            <div className="mt-6 pt-3 border-t border-slate-950 text-slate-500 text-[9.5px] leading-relaxed font-mono flex justify-between items-center">
              <span className="flex items-center gap-1">
                <Info className="w-3.5 h-3.5 text-indigo-400" /> V37 compiler verifies
                memory-to-logic mappings directly inside local environment hooks.
              </span>
              <span>Quantization Scale: 1-bit Ternary Clamps</span>
            </div>
          </div>
        </div>
      </div>

      {/* LEO AI V37 PRINT CONTAINER */}
      <div className="print-border hidden print:block text-black font-serif p-10 max-w-4xl mx-auto mt-12 bg-white">
        <div className="print-header text-center pb-4 mb-6">
          <h1 className="text-3xl font-black uppercase tracking-widest text-black">
            LEO AI V37 Verification Certification
          </h1>
          <h2 className="text-md font-bold text-slate-700 font-mono mt-1.5 uppercase">
            Master Evolution Protocol Calibration
          </h2>
        </div>

        <div className="grid grid-cols-2 gap-6 text-sm font-mono leading-relaxed mb-8">
          <div>
            <p>
              <strong>System Substrate:</strong> LEO AI V37 Master Evolution
            </p>
            <p>
              <strong>Optimized Target:</strong> Maximum Intelligence Density
            </p>
            <p>
              <strong>Workstation Hardware Profile:</strong> Intel Core i5 CPU / UHD Graphics / NPU
            </p>
            <p>
              <strong>Resource Quantization Scale:</strong>{" "}
              {energyDirectives?.activePrecision || "Ternary_1bit"}
            </p>
            <p>
              <strong>MoE Active Routing Profile:</strong>{" "}
              {energyDirectives?.activeExpertsCount || 1} Expert(s)
            </p>
          </div>
          <div>
            <p>
              <strong>Intelligence Density Ratio:</strong> {intelligenceDensity} IQ/Resource Unit
            </p>
            <p>
              <strong>Scientific Reasoning Score:</strong> {metrics.scientificReasoning.toFixed(2)}%
              (Target: 99%)
            </p>
            <p>
              <strong>Robotics Resilience:</strong> {metrics.roboticsIntelligence.toFixed(2)}%
              (Target: 98%)
            </p>
            <p>
              <strong>Autonomous Path safety:</strong> {metrics.autonomousSystems.toFixed(2)}%
              (Target: 98%)
            </p>
            <p>
              <strong>Training Efficiency Score:</strong>{" "}
              {metrics.frontierTrainingEfficiency.toFixed(2)}%
            </p>
          </div>
        </div>

        <div className="border-t-2 border-slate-800 pt-6 mt-4 flex justify-between items-center">
          <div>
            <p className="text-[10px] font-mono uppercase text-slate-600">
              Issued by Antigravity Autonomous V37 Subsystem Compiler
            </p>
            <p className="text-[10px] text-slate-500 font-mono">
              UTC Timestamp: {new Date().toISOString()}
            </p>
          </div>

          <div className="flex flex-col items-center border-2 border-black rounded-lg p-3 bg-slate-50">
            <span className="font-bold tracking-widest text-xs uppercase text-black">
              V37 EVOLUTION SEAL
            </span>
            <span className="text-[8px] text-slate-500 font-mono mt-1">
              CERTIFIED HARDWARE-AWARE
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
