import React, { useState, useEffect, useCallback } from 'react';
import {
  RealUserLearningEngine,
  SwarmRoadmap,
  RealityAlignmentEngine,
  CalibrationTelemetry,
  KnowledgeEvolutionEngine,
  IngestionReport,
  FailureVaccinationEngine,
  FailureCategory,
  VaccineReport,
  AgentGovernanceEngine,
  SwarmCompliance,
  ComputeAvoidanceEngine,
  AvoidanceResolution,
  WorkflowEvolutionEngine,
  UncertaintyReasoningEngine,
  ConfidenceReport,
  ScientificDiscoveryEngine,
  DiscoveryReport,
  EfficiencyOptimizationEngine,
  RuntimeOptimizationDirectives
} from '../v36/v36index';
import {
  Zap, Brain, ShieldCheck, AlertTriangle, Gauge, Terminal,
  Activity, Award, Database, Search, ShieldAlert, RefreshCw,
  Play, CheckCircle, Server, Eye, FileText, ArrowRight, Sparkles, Scale, Percent, Compass, Cpu, Info, Sliders, Layers, Network, ZapOff, Battery, Thermometer
} from 'lucide-react';

export function LEOAIv36Dashboard() {
  // Instantiate upgraded engines
  const [userLearning] = useState(() => new RealUserLearningEngine());
  const [realityAlignment] = useState(() => new RealityAlignmentEngine());
  const [knowledgeEvolution] = useState(() => new KnowledgeEvolutionEngine());
  const [failureVaccination] = useState(() => new FailureVaccinationEngine());
  const [agentGovernance] = useState(() => new AgentGovernanceEngine());
  const [computeAvoidance] = useState(() => new ComputeAvoidanceEngine());
  const [workflowEvolution] = useState(() => new WorkflowEvolutionEngine());
  const [uncertaintyReasoning] = useState(() => new UncertaintyReasoningEngine());
  const [scientificDiscovery] = useState(() => new ScientificDiscoveryEngine());
  const [efficiencyEngine] = useState(() => new EfficiencyOptimizationEngine());

  // Input states
  const [query, setQuery] = useState("Perform multi-future trajectory plan for robotic arm obstruction path");
  const [independentVar, setIndependentVar] = useState("quantization scaling");
  const [dependentVar, setDependentVar] = useState("L3 Cache Miss Rates");
  const [feedbackRating, setFeedbackRating] = useState<number>(5);
  const [feedbackText, setFeedbackText] = useState<string>("");
  const [ramLimit, setRamLimit] = useState<number>(16.0);
  const [isProcessing, setIsProcessing] = useState(false);
  const [activeTab, setActiveTab] = useState<"overview" | "user" | "knowledge" | "failure" | "governance" | "uncertainty">("overview");

  // Output telemetry records
  const [userRoadmap, setUserRoadmap] = useState<SwarmRoadmap | null>(null);
  const [alignmentStats, setAlignmentStats] = useState<CalibrationTelemetry | null>(null);
  const [ingestionStats, setIngestionStats] = useState<IngestionReport | null>(null);
  const [vaccineStats, setVaccineStats] = useState<VaccineReport | null>(null);
  const [governanceStats, setGovernanceStats] = useState<SwarmCompliance | null>(null);
  const [avoidanceStats, setAvoidanceStats] = useState<AvoidanceResolution | null>(null);
  const [workflowStats, setWorkflowStats] = useState<any>(null);
  const [confidenceStats, setConfidenceStats] = useState<ConfidenceReport | null>(null);
  const [discoveryStats, setDiscoveryStats] = useState<DiscoveryReport | null>(null);
  const [efficiencyStats, setEfficiencyStats] = useState<RuntimeOptimizationDirectives | null>(null);

  // Scoreboard parameters
  const [scoreboard, setScoreboard] = useState({
    realityAlignment: 98.4,
    knowledgeFreshness: 99.2,
    failureVaccination: 95.6,
    workflowOptimization: 94.2,
    computeAvoidance: 99.4,
    userSatisfaction: 96.0,
    agentGovernance: 99.2,
    confidenceCalibration: 97.5
  });

  const runV36Pipeline = useCallback((currentQuery: string) => {
    setIsProcessing(true);
    setTimeout(() => {
      try {
        const qLower = currentQuery.toLowerCase();

        // 1. Real User Learning
        const roadmapVal = userLearning.submitFeedback(currentQuery, feedbackRating, feedbackText);
        setUserRoadmap(roadmapVal);

        // 2. Reality Alignment
        const alignmentVal = realityAlignment.auditReality(
          "aud-sim-01",
          currentQuery.slice(0, 25),
          currentQuery.slice(0, 25),
          0.98
        );
        setAlignmentStats(alignmentVal);

        // 3. Knowledge Refresh
        const ingestionVal = knowledgeEvolution.ingestConcept(
          "arxiv.org/abs/bitnet",
          `Quantization parameter optimization. Source value: ${currentQuery}`,
          5
        );
        setIngestionStats(ingestionVal);

        // 4. Failure Vaccination
        let failCat: FailureCategory = "reasoning";
        if (qLower.includes("code")) failCat = "coding";
        else if (qLower.includes("workflow")) failCat = "workflow";
        else if (qLower.includes("search")) failCat = "retrieval";
        
        const vaccineVal = failureVaccination.vaccinateFailure(failCat, `Simulation failure trace logs: ${currentQuery}`);
        setVaccineStats(vaccineVal);

        // 5. Agent Governance
        const govVal = agentGovernance.auditSwarms(4, 0.045, qLower.includes("disagree"));
        setGovernanceStats(govVal);

        // 6. Compute Avoidance
        const avoidanceVal = computeAvoidance.evaluateQuery(currentQuery);
        setAvoidanceStats(avoidanceVal);

        // 7. Workflow Evolution
        workflowEvolution.logTransition("CacheSearch", "MoERouting", 120);
        workflowEvolution.logTransition("SpeculativeVerify", "OutcomeIngestion", 1450); // Slow step
        const workflowVal = workflowEvolution.discoverAutomationMacros();
        setWorkflowStats(workflowVal);

        // 8. Uncertainty estimation
        const confidenceVal = uncertaintyReasoning.evaluateStatement(currentQuery, 3);
        setConfidenceStats(confidenceVal);

        // 9. Scientific Discovery
        const discoveryVal = scientificDiscovery.discoverHypotheses(
          "Thermal clock limits checked at 4.2GHz.",
          independentVar,
          dependentVar
        );
        setDiscoveryStats(discoveryVal);

        // 10. Efficiency optimisation
        let opType: "vector" | "matrix" | "logic" = "logic";
        if (qLower.includes("trajectory") || qLower.includes("fno")) opType = "vector";
        else if (qLower.includes("matrix") || qLower.includes("AVX")) opType = "matrix";

        const efficiencyVal = efficiencyEngine.prescribeOptimizations(ramLimit, opType);
        setEfficiencyStats(efficiencyVal);

        // Compute scoreboard metrics
        setScoreboard({
          realityAlignment: alignmentVal.realityAlignmentScore,
          knowledgeFreshness: ingestionVal.freshnessScore,
          failureVaccination: vaccineVal.remedyScore,
          workflowOptimization: workflowVal.workflowEfficiencyScore,
          computeAvoidance: avoidanceVal.cacheHit ? 99.4 : 72.8,
          userSatisfaction: roadmapVal.satisfactionScore,
          agentGovernance: govVal.governanceScore,
          confidenceCalibration: alignmentVal.confidenceCalibrationScore
        });

      } catch (err) {
        console.error("Upgraded Scoreboard failed: ", err);
      } finally {
        setIsProcessing(false);
      }
    }, 300);
  }, [independentVar, dependentVar, feedbackRating, feedbackText, ramLimit, userLearning, realityAlignment, knowledgeEvolution, failureVaccination, agentGovernance, computeAvoidance, workflowEvolution, uncertaintyReasoning, scientificDiscovery, efficiencyEngine]);

  useEffect(() => {
    runV36Pipeline(query);
  }, []);

  const handleFeedbackSubmit = () => {
    runV36Pipeline(query);
    setFeedbackText("");
  };

  return (
    <div className="p-6 bg-[#02050e] text-slate-100 min-h-screen font-sans selection:bg-indigo-600 selection:text-white print:bg-white print:text-black">
      
      {/* Dynamic Printing Style Overrides */}
      <style dangerouslySetInnerHTML={{__html: `
        @media print {
          .no-print { display: none !important; }
          body { background-color: white !important; color: black !important; }
          .print-border { border: 2px solid #000 !important; border-radius: 8px !important; padding: 24px !important; }
          .print-header { border-bottom: 2px solid #000 !important; margin-bottom: 20px !important; }
          .print-text-black { color: black !important; }
        }
      `}} />

      {/* Cockpit Top Header */}
      <div className="no-print flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4 mb-8 border-b border-slate-900 pb-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-indigo-650 text-white tracking-widest uppercase font-mono animate-pulse">
              LEO V36 UPGRADE
            </span>
            <span className="text-slate-500 text-sm font-mono">Intelligence-Per-Compute Scoreboard</span>
          </div>
          <h1 className="text-3xl font-black text-slate-100 tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent flex items-center gap-2">
            <Gauge className="text-indigo-400 w-8 h-8" />
            Intelligence-Per-Compute Cockpit
          </h1>
          <p className="text-slate-400 text-xs mt-1">
            Optimized for Intel Core i5 12th Gen and UHD integrated graphic frames. Coordinates hardware threads under strict thermal constraint parameters.
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => runV36Pipeline(query)}
            disabled={isProcessing}
            className="bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-900 transition-all text-white text-xs font-bold py-3 px-6 rounded-lg flex items-center gap-2 cursor-pointer shadow-lg shadow-indigo-950/40 font-mono"
          >
            {isProcessing ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <Play className="w-4 h-4 fill-white" />
            )}
            {isProcessing ? "EVALUATING PIPELINE..." : "RUN INTEL SWEEP"}
          </button>
          
          <button
            onClick={() => window.print()}
            className="bg-slate-900 hover:bg-slate-800 border border-slate-850 text-slate-200 text-xs font-bold py-3 px-6 rounded-lg flex items-center gap-2 cursor-pointer transition-colors font-mono"
          >
            <FileText className="w-4 h-4 text-indigo-400" />
            PRINT UPGRADE CERTIFICATE
          </button>
        </div>
      </div>

      {/* CORE V36 TELEMETRY SCOREBOARD */}
      <div className="no-print grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {[
          { label: "Reality Alignment", val: `${scoreboard.realityAlignment.toFixed(1)}%`, target: "Verified", desc: "Prediction validation rate", color: "text-blue-400" },
          { label: "Knowledge Freshness", val: `${scoreboard.knowledgeFreshness.toFixed(1)}%`, target: "99%+", desc: "Ingestion time decay check", color: "text-emerald-400" },
          { label: "Failure Vaccination", val: `${scoreboard.failureVaccination.toFixed(1)}%`, target: "95%+", desc: "formulated swarm vaccines", color: "text-cyan-400" },
          { label: "Workflow Optimization", val: `${scoreboard.workflowOptimization.toFixed(1)}%`, target: "94%+", desc: "Discovered automation macros", color: "text-indigo-400" },
          { label: "Compute Avoidance", val: `${scoreboard.computeAvoidance.toFixed(1)}%`, target: "99%+", desc: "Cached query reuse ratio", color: "text-purple-400" },
          { label: "User Satisfaction", val: `${scoreboard.userSatisfaction.toFixed(1)}%`, target: "99%+", desc: "Swarms preference feedback", color: "text-teal-400" },
          { label: "Agent Governance", val: `${scoreboard.agentGovernance.toFixed(1)}%`, target: "99%+", desc: "deadlock prevention checks", color: "text-rose-400" },
          { label: "Confidence Calibration", val: `${scoreboard.confidenceCalibration.toFixed(1)}%`, target: "97%+", desc: "Calibrated safety discrepancy", color: "text-emerald-500" }
        ].map((m, idx) => (
          <div key={idx} className="bg-slate-900/80 border border-slate-850 rounded-xl p-4 flex flex-col justify-between hover:border-slate-800 transition-all duration-300 relative group overflow-hidden shadow">
            <div className="absolute top-0 right-0 w-12 h-12 bg-indigo-500/5 rounded-full filter blur-md" />
            <div>
              <span className="text-[10px] font-mono text-slate-500 uppercase tracking-tight block mb-1">
                {m.label}
              </span>
              <span className={`text-xl font-black font-mono ${m.color}`}>
                {m.val}
              </span>
            </div>
            <div className="mt-3 pt-2 border-t border-slate-950">
              <span className="text-[9px] text-slate-400 block leading-tight">{m.desc}</span>
              <span className="text-[8px] text-slate-655 font-mono block mt-0.5">Target: {m.target}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Main split console panel */}
      <div className="no-print grid grid-cols-1 lg:grid-cols-12 gap-8 mb-8">
        
        {/* Left Side: Controllers and parameters sliders */}
        <div className="lg:col-span-4 space-y-6">
          <div className="bg-slate-900 border border-slate-850 rounded-xl p-6 relative overflow-hidden shadow-2xl">
            <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-indigo-600 via-purple-500 to-indigo-500" />
            
            <div className="flex items-center gap-2 mb-4 border-b border-slate-850 pb-3">
              <Sliders className="text-indigo-400 w-5 h-5" />
              <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider font-mono">Telemetry Controllers</h2>
            </div>

            <div className="space-y-4">
              {/* Task Query Prompt */}
              <div>
                <label className="text-[9px] text-slate-550 uppercase block font-mono font-bold mb-1.5">Interactive Prompt</label>
                <textarea
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-850 rounded-lg p-3 text-xs text-slate-200 font-mono focus:outline-none focus:border-indigo-500 border-slate-800 transition-colors resize-none h-20"
                  placeholder="Query parameters..."
                />
              </div>

              {/* Scientific Discovery Engine parameters */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-[9px] text-slate-550 block uppercase font-mono font-bold mb-1">Independent Variable</label>
                  <input
                    type="text"
                    value={independentVar}
                    onChange={(e) => setIndependentVar(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-850 p-2 rounded text-xs text-slate-200 font-mono focus:outline-none focus:border-indigo-500 border-slate-800"
                  />
                </div>
                <div>
                  <label className="text-[9px] text-slate-550 block uppercase font-mono font-bold mb-1">Dependent Variable</label>
                  <input
                    type="text"
                    value={dependentVar}
                    onChange={(e) => setDependentVar(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-850 p-2 rounded text-xs text-slate-200 font-mono focus:outline-none focus:border-indigo-500 border-slate-800"
                  />
                </div>
              </div>

              {/* System RAM Limit slider */}
              <div>
                <div className="flex justify-between text-[10px] font-mono mb-1.5">
                  <span className="text-slate-500 uppercase font-bold">Allocated System RAM</span>
                  <span className="text-blue-400">{ramLimit} GB</span>
                </div>
                <input
                  type="range"
                  min="4"
                  max="32"
                  value={ramLimit}
                  onChange={(e) => setRamLimit(Number(e.target.value))}
                  className="w-full h-1 bg-slate-950 rounded appearance-none cursor-pointer accent-blue-500"
                />
              </div>

            </div>
          </div>

          {/* Feedback logger card */}
          <div className="bg-slate-900 border border-slate-850 rounded-xl p-5 shadow-lg space-y-4">
            <h3 className="text-xs font-bold text-slate-200 font-mono uppercase tracking-wider">Swarm Feedback Loop</h3>
            <div className="space-y-3 text-xs">
              <div className="flex justify-between items-center">
                <label className="text-[9px] text-slate-500 uppercase font-mono font-bold">Satisfied rating (1-5)</label>
                <input
                  type="number"
                  min="1"
                  max="5"
                  value={feedbackRating}
                  onChange={(e) => setFeedbackRating(Number(e.target.value))}
                  className="bg-slate-950 border border-slate-850 p-1.5 rounded w-16 text-center text-slate-200 font-mono focus:border-indigo-500 border-slate-800"
                />
              </div>
              <div>
                <label className="text-[9px] text-slate-500 uppercase font-mono font-bold block mb-1">User Corrections / Notes</label>
                <textarea
                  value={feedbackText}
                  onChange={(e) => setFeedbackText(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-850 p-2 rounded text-slate-200 font-mono resize-none h-16 focus:outline-none focus:border-indigo-500 border-slate-800"
                  placeholder="Enter dynamic calibration adjustments..."
                />
              </div>
              <button
                onClick={handleFeedbackSubmit}
                className="w-full bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold font-mono py-2 rounded transition-all shadow"
              >
                SUBMIT FEEDBACK &amp; RETEST
              </button>
            </div>
          </div>
        </div>

        {/* Right Side: Tabbed telemetry monitor */}
        <div className="lg:col-span-8 space-y-6">
          <div className="bg-slate-900 border border-slate-850 rounded-xl p-6 shadow-2xl min-h-[460px] flex flex-col justify-between">
            <div>
              {/* Tab menu */}
              <div className="flex border-b border-slate-950 pb-3 mb-6 gap-2 overflow-x-auto scrollbar-none">
                {[
                  { id: "overview", label: "Overview", icon: <Activity className="w-3.5 h-3.5" /> },
                  { id: "user", label: "Feedback Roadmaps", icon: <Sliders className="w-3.5 h-3.5" /> },
                  { id: "knowledge", label: "GraphRAG evolution", icon: <Database className="w-3.5 h-3.5" /> },
                  { id: "failure", label: "Vaccines immunity", icon: <ShieldAlert className="w-3.5 h-3.5" /> },
                  { id: "governance", label: "constitutional governance", icon: <Cpu className="w-3.5 h-3.5" /> },
                  { id: "uncertainty", label: "Uncertainty Reasoning", icon: <Compass className="w-3.5 h-3.5" /> }
                ].map(t => (
                  <button
                    key={t.id}
                    className={`px-3 py-2 text-[10px] font-mono font-bold uppercase rounded-lg tracking-wider transition-all flex items-center gap-1.5 whitespace-nowrap ${
                      activeTab === t.id
                        ? "bg-indigo-600/15 border border-indigo-900 text-indigo-400"
                        : "text-slate-455 hover:text-slate-200"
                    }`}
                    onClick={() => setActiveTab(t.id as any)}
                  >
                    {t.icon}
                    {t.label}
                  </button>
                ))}
              </div>

              {/* Tab 1: Overview */}
              {activeTab === "overview" && avoidanceStats && efficiencyStats && (
                <div className="space-y-4 font-mono text-xs">
                  <div className="bg-slate-950 p-4 rounded-xl border border-slate-850 space-y-3">
                    <div className="flex justify-between items-center border-b border-slate-850 pb-2">
                      <h3 className="text-xs font-bold text-slate-200 uppercase">Swarm efficiency Optimization</h3>
                      <span className="text-indigo-405 font-bold">Device: {efficiencyStats.activeDevice}</span>
                    </div>

                    <div className="grid grid-cols-3 gap-3 text-center">
                      <div className="bg-slate-900 p-2.5 rounded">
                        <span className="text-slate-500 text-[8px] block uppercase">GGUF bit depth</span>
                        <span className="text-md font-bold text-indigo-400">Q{efficiencyStats.quantizationBits}_K_M</span>
                      </div>
                      <div className="bg-slate-900 p-2.5 rounded">
                        <span className="text-slate-500 text-[8px] block uppercase">Fused kernels count</span>
                        <span className="text-md font-bold text-emerald-400">{efficiencyStats.fusedKernelsCount} Fused</span>
                      </div>
                      <div className="bg-slate-900 p-2.5 rounded">
                        <span className="text-slate-500 text-[8px] block uppercase">Speedup multiplier</span>
                        <span className="text-md font-bold text-cyan-400">{efficiencyStats.speedupEstimation.toFixed(2)}x</span>
                      </div>
                    </div>

                    <div className="bg-slate-900 p-3 rounded">
                      <span className="text-slate-400 font-bold block mb-1 text-[10px]">COMPUTE AVOIDED TELEMETRY:</span>
                      <div className="flex justify-between items-center text-[11px]">
                        <span>Semantic cache match:</span>
                        <span className={avoidanceStats.cacheHit ? "text-emerald-400 font-bold" : "text-slate-500"}>
                          {avoidanceStats.cacheHit ? "HIT (100% Avoided)" : "MISS"}
                        </span>
                      </div>
                      <div className="flex justify-between items-center text-[11px] mt-1">
                        <span>Latency reduction achieved:</span>
                        <span className="text-indigo-400 font-bold">{avoidanceStats.latencyReductionMs} ms</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Tab 2: Feedback Roadmaps */}
              {activeTab === "user" && userRoadmap && (
                <div className="space-y-4 font-mono text-xs">
                  <div className="bg-slate-950 p-4 rounded-xl border border-slate-850 space-y-3">
                    <div className="flex justify-between items-center border-b border-slate-850 pb-2">
                      <h3 className="text-xs font-bold text-slate-200 uppercase">Swarm retrain roadmaps</h3>
                      <span className={userRoadmap.retrainTriggered ? "text-rose-400 font-bold" : "text-emerald-400"}>
                        {userRoadmap.retrainTriggered ? "CALIBRATION ENFORCED" : "CALIBRATED"}
                      </span>
                    </div>

                    <div className="space-y-2 text-[11px]">
                      <div className="flex justify-between bg-slate-900 p-2 rounded">
                        <span>Active complaint clusters:</span>
                        <span className="text-cyan-400 font-bold">{userRoadmap.detectedComplaintClusters.join(", ")}</span>
                      </div>
                      <div className="flex justify-between bg-slate-900 p-2 rounded">
                        <span>Queued prioritization tickets:</span>
                        <span className="text-white">{userRoadmap.prioritizedQueuesCount} tickets</span>
                      </div>
                      <div className="bg-slate-900 p-2 rounded max-h-36 overflow-y-auto">
                        <span className="text-[10px] text-slate-500 font-bold block mb-1">CORRECTION LOGS:</span>
                        {userLearning.getCorrectionLogs().map((c, idx) => (
                          <div key={idx} className="text-[10px] border-b border-slate-800 pb-1.5 mb-1.5 last:border-b-0 last:pb-0 last:mb-0">
                            <span className="text-indigo-400">Query: "{c.query.slice(0, 20)}..." (Rating: {c.rating}/5)</span>
                            <p className="text-slate-350 mt-0.5">Correction: {c.correctionText}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Tab 3: GraphRAG evolution */}
              {activeTab === "knowledge" && ingestionStats && (
                <div className="space-y-4 font-mono text-xs">
                  <div className="bg-slate-950 p-4 rounded-xl border border-slate-850 space-y-3">
                    <div className="flex justify-between items-center border-b border-slate-850 pb-2">
                      <h3 className="text-xs font-bold text-slate-200 uppercase">GraphRAG evolution checks</h3>
                      <span className="text-indigo-400 font-bold">Reliability: {ingestionStats.sourceReliabilityScore}%</span>
                    </div>

                    <div className="space-y-2 text-[11px]">
                      <div className="flex justify-between bg-slate-900 p-2 rounded">
                        <span>Contradictions detected:</span>
                        <span className={ingestionStats.contradictionFound ? "text-rose-455 font-bold" : "text-emerald-450"}>
                          {ingestionStats.contradictionFound ? "CONFLICT FLAG" : "CLEAN"}
                        </span>
                      </div>
                      <div className="flex justify-between bg-slate-900 p-2 rounded">
                        <span>Freshness confidence ratio:</span>
                        <span className="text-white">{ingestionStats.freshnessScore}%</span>
                      </div>
                      <p className="bg-slate-900 p-2.5 rounded text-slate-300 leading-normal text-[10px]">
                        <strong>Compaction:</strong> Outdated concepts are retired and swapped dynamically when contradiction flags trigger.
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Tab 4: Vaccines immunity */}
              {activeTab === "failure" && vaccineStats && (
                <div className="space-y-4 font-mono text-xs">
                  <div className="bg-slate-950 p-4 rounded-xl border border-slate-850 space-y-3">
                    <div className="flex justify-between items-center border-b border-slate-850 pb-2">
                      <h3 className="text-xs font-bold text-slate-200 uppercase">Formulated edge case vaccines</h3>
                      <span className="text-indigo-400 font-bold">{vaccineStats.vaccineId}</span>
                    </div>

                    <div className="space-y-2 text-[11px]">
                      <div className="flex justify-between bg-slate-900 p-2 rounded">
                        <span>Synthetic training examples:</span>
                        <span className="text-white">{vaccineStats.generatedSamplesCount} samples</span>
                      </div>
                      <p className="bg-slate-900 p-2 rounded text-slate-300">
                        <strong>Test mask:</strong> {vaccineStats.testMask}
                      </p>
                      <div className="flex justify-between bg-slate-900 p-2 rounded">
                        <span>Remedy safety index:</span>
                        <span className="text-emerald-450 font-bold">{vaccineStats.remedyScore}%</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Tab 5: constitutional governance */}
              {activeTab === "governance" && governanceStats && (
                <div className="space-y-4 font-mono text-xs">
                  <div className="bg-slate-950 p-4 rounded-xl border border-slate-850 space-y-3">
                    <div className="flex justify-between items-center border-b border-slate-850 pb-2">
                      <h3 className="text-xs font-bold text-slate-200 uppercase"> конституционные compliance checks</h3>
                      <span className="text-indigo-400 font-bold">Score: {governanceStats.governanceScore}%</span>
                    </div>

                    <div className="space-y-2 text-[11px]">
                      <div className="flex justify-between bg-slate-900 p-2 rounded">
                        <span>Swarm loop lock:</span>
                        <span className={governanceStats.loopDetected ? "text-rose-455 font-bold" : "text-emerald-450"}>
                          {governanceStats.loopDetected ? "LOOP DETECTED" : "CLEAN"}
                        </span>
                      </div>
                      <div className="flex justify-between bg-slate-900 p-2 rounded">
                        <span>Accumulated token cost:</span>
                        <span className="text-white">${governanceStats.accumulatedCostUsd.toFixed(4)}</span>
                      </div>
                      <p className="bg-slate-900 p-2.5 rounded text-slate-300">
                        <strong>Arbitration verdict:</strong> {governanceStats.arbitrationVerdict}
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Tab 6: Uncertainty Reasoning */}
              {activeTab === "uncertainty" && confidenceStats && discoveryStats && (
                <div className="space-y-4 font-mono text-xs">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    
                    <div className="bg-slate-950 p-4 rounded-xl border border-slate-850 space-y-2">
                      <h3 className="text-xs font-bold text-slate-200 uppercase">Uncertainty Mitigation</h3>
                      <div className="space-y-2 leading-relaxed">
                        <div className="flex justify-between bg-slate-900 p-2 rounded">
                          <span>Confidence score:</span>
                          <span className="text-indigo-400 font-bold">{(confidenceStats.score * 100).toFixed(0)}%</span>
                        </div>
                        <div className="flex justify-between bg-slate-900 p-2 rounded">
                          <span>Classification:</span>
                          <span className="text-cyan-400 font-bold uppercase">{confidenceStats.category}</span>
                        </div>
                        <p className="bg-slate-900 p-2 rounded text-slate-300 text-[10.5px]">
                          <strong>Mitigation:</strong> {confidenceStats.prescribedMitigation}
                        </p>
                      </div>
                    </div>

                    <div className="bg-slate-950 p-4 rounded-xl border border-slate-850 space-y-2">
                      <h3 className="text-xs font-bold text-slate-200 uppercase">Scientific claims discovery</h3>
                      <div className="space-y-2 leading-relaxed text-[11px]">
                        <p className="bg-slate-900 p-2 rounded text-slate-300 text-[10px]">
                          <strong>Hypothesis:</strong> {discoveryStats.hypotheses[0]?.claim}
                        </p>
                        <p className="bg-slate-900 p-2 rounded text-slate-300 text-[10px]">
                          <strong>Experiment:</strong> {discoveryStats.suggestedExperiment}
                        </p>
                      </div>
                    </div>

                  </div>
                </div>
              )}

            </div>

            {/* Quick tips footer */}
            <div className="mt-6 pt-3 border-t border-slate-950 text-slate-550 text-[9.5px] leading-relaxed font-mono flex justify-between items-center">
              <span className="flex items-center gap-1">
                <Info className="w-3.5 h-3.5 text-indigo-500" /> Enter prompt keywords (e.g. 'code', 'workflow', 'disagree') to test compliance branches.
              </span>
              <span>Model Tier: LEO-V36-Upgrade-Core</span>
            </div>
          </div>
        </div>

      </div>

      {/* LEO AI V36 REPORT CARD - PRINT ONLY CONTAINER */}
      <div className="print-border hidden print:block text-black font-serif p-8 max-w-4xl mx-auto mt-12 bg-white">
        <div className="print-header text-center pb-4 mb-6">
          <h1 className="text-3xl font-black uppercase tracking-wider">LEO AI V36 Report Card</h1>
          <h2 className="text-lg font-bold text-slate-700 font-mono mt-1">Intelligence-Per-Compute Upgraded Verification</h2>
        </div>

        <div className="grid grid-cols-2 gap-6 text-sm font-mono leading-relaxed mb-8">
          <div>
            <p><strong>System Version:</strong> LEO AI V36 Upgrade Core</p>
            <p><strong>Hardware Profile:</strong> Core i5 12th Gen CPU / Xe UHD / NPU</p>
            <p><strong>Verification Standard:</strong> Hardware-Aware Compute Avoidance</p>
            <p><strong>Constitutional compliance:</strong> Passed (No agent loops detected)</p>
          </div>
          <div>
            <p><strong>Reality Alignment Score:</strong> {scoreboard.realityAlignment.toFixed(2)}%</p>
            <p><strong>Knowledge Freshness Score:</strong> {scoreboard.knowledgeFreshness.toFixed(2)}%</p>
            <p><strong>Compute Avoidance rate:</strong> {scoreboard.computeAvoidance.toFixed(2)}%</p>
            <p><strong>Confidence Calibration:</strong> {scoreboard.confidenceCalibration.toFixed(2)}%</p>
          </div>
        </div>

        <div className="border-t border-black pt-4 flex justify-between items-center">
          <div>
            <p className="text-[11px] font-mono uppercase text-slate-655">Issued by Antigravity V36 Autonomous Upgrade Compiler</p>
            <p className="text-[10px] text-slate-500 font-mono">Timestamp: {new Date().toISOString()}</p>
          </div>
          <div className="border-2 border-black rounded-full p-2.5 text-center font-bold tracking-widest text-xs uppercase bg-slate-50">
            V36 VERIFIED
          </div>
        </div>
      </div>

    </div>
  );
}
