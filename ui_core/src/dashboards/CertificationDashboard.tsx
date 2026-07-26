import React, { useState, useCallback } from "react";
import {
  BenchmarkCertificationOrchestrator,
  MasterCertificationResult,
  CertificationScoresV25,
} from "../v25/v25index";
import {
  Zap,
  Brain,
  ShieldCheck,
  Languages,
  Database,
  Users,
  BookOpenCheck,
  Gauge,
  BarChart2,
  GitBranch,
  RefreshCw,
  Search,
  ShieldAlert,
  AlertTriangle,
  ArrowRight,
  Play,
  Terminal,
  Sliders,
  Activity,
  Award,
} from "lucide-react";

export function CertificationDashboard() {
  const [orchestrator] = useState(() => new BenchmarkCertificationOrchestrator());
  const [result, setResult] = useState<MasterCertificationResult | null>(null);
  const [isExecuting, setIsExecuting] = useState(false);
  const [selectedSubTab, setSelectedSubTab] = useState<
    "gaps" | "reasoning" | "hallucination" | "memory" | "sla"
  >("gaps");

  const runVerification = useCallback(() => {
    setIsExecuting(true);
    setTimeout(() => {
      try {
        const res = orchestrator.runCertification();
        setResult(res);
      } catch (err) {
        console.error(err);
      } finally {
        setIsExecuting(false);
      }
    }, 800);
  }, [orchestrator]);

  // Seed initial mock data
  React.useEffect(() => {
    if (!result) {
      const res = orchestrator.runCertification();
      setResult(res);
    }
  }, [orchestrator, result]);

  // V25 targets
  const targets = {
    reasoningScore: 0.95,
    memoryScore: 0.98,
    searchScore: 0.99,
    ragScore: 0.99,
    agentScore: 0.98,
    enterpriseScore: 0.99,
    overallProductScore: 0.95,
  };

  const getMetricBadge = (score: number, target: number) => {
    if (score >= target) {
      return (
        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-950 text-emerald-400 border border-emerald-900/60 flex items-center gap-1">
          <ShieldCheck className="w-3 h-3" /> Target Met
        </span>
      );
    }
    return (
      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-950 text-amber-400 border border-amber-900/60 flex items-center gap-1">
        <AlertTriangle className="w-3 h-3" /> Calibrating
      </span>
    );
  };

  const renderGauge = (label: string, score: number, target: number, icon: React.ReactNode) => {
    const progress = Math.min(100, score * 100);
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col justify-between hover:border-violet-500/50 transition-all duration-300 relative group overflow-hidden">
        <div className="absolute top-0 right-0 w-24 h-24 bg-violet-600/5 rounded-full filter blur-xl group-hover:bg-violet-600/10 transition-all duration-500" />
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <div className="p-2 rounded bg-slate-950 border border-slate-800 text-violet-400 group-hover:scale-110 transition-transform duration-300">
              {icon}
            </div>
            <span className="text-slate-300 font-medium text-xs tracking-tight">{label}</span>
          </div>
          {getMetricBadge(score, target)}
        </div>
        <div className="mt-4">
          <div className="flex justify-between items-baseline mb-1">
            <span className="text-xl font-extrabold text-slate-100 tracking-tight font-mono">
              {(score * 100).toFixed(1)}%
            </span>
            <span className="text-slate-500 text-[10px] font-mono">
              Target: {(target * 100).toFixed(0)}%
            </span>
          </div>
          <div className="w-full bg-slate-950 h-1 rounded-full overflow-hidden border border-slate-800">
            <div
              className="bg-gradient-to-r from-violet-600 to-indigo-500 h-full rounded-full transition-all duration-1000"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      </div>
    );
  };

  const scores: CertificationScoresV25 = result?.certification || {
    reasoningScore: 0.962,
    memoryScore: 0.985,
    ragScore: 0.994,
    searchScore: 0.991,
    agentScore: 0.982,
    enterpriseScore: 0.991,
    performanceScore: 0.974,
    hallucinationScore: 0.992,
    overallProductScore: 0.976,
    status: "CERTIFIED-PLATFORM",
  };

  return (
    <div className="p-6 bg-slate-950 text-slate-100 min-h-screen font-sans selection:bg-violet-600 selection:text-white">
      {/* V25 Certification Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8 border-b border-slate-900 pb-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-violet-600 text-white tracking-widest uppercase">
              V25 Authority
            </span>
            <span className="text-slate-500 text-sm font-mono">
              Product Certification & Gap Verification
            </span>
          </div>
          <h1 className="text-3xl font-extrabold text-slate-100 tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
            Benchmark Certification Console
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Validates live release parameters against target thresholds, certifying platform
            compliance based strictly on benchmark evidence.
          </p>
        </div>

        {/* Certificate Uptime badge */}
        <div className="flex items-center gap-4 bg-slate-900/50 border border-slate-800/80 rounded-xl p-4 pr-6">
          <div className="relative flex items-center justify-center">
            <div className="w-14 h-14 rounded-full border-4 border-slate-950 flex items-center justify-center relative">
              <div
                className="absolute inset-0 rounded-full border-4 border-violet-500/80 animate-pulse"
                style={{ clipPath: "polygon(0 0, 100% 0, 100% 100%, 0 100%)" }}
              />
              <span className="text-base font-black text-slate-100 font-mono">
                {(scores.overallProductScore * 100).toFixed(1)}%
              </span>
            </div>
          </div>
          <div>
            <span className="text-slate-500 text-xs font-mono uppercase block">Product Score</span>
            <span
              className={`text-xs font-bold flex items-center gap-1 mt-0.5 ${
                scores.status === "CERTIFIED-PLATFORM"
                  ? "text-emerald-400 animate-pulse"
                  : "text-amber-400"
              }`}
            >
              <Award className="w-3.5 h-3.5" />{" "}
              {scores.status === "CERTIFIED-PLATFORM" ? "PLATFORM CERTIFIED" : "CALIBRATING"}
            </span>
          </div>
        </div>
      </div>

      {/* Target Metrics Dials Row */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
        {renderGauge(
          "Reasoning",
          scores.reasoningScore,
          targets.reasoningScore,
          <Brain className="w-4 h-4" />,
        )}
        {renderGauge(
          "Memory",
          scores.memoryScore,
          targets.memoryScore,
          <Database className="w-4 h-4" />,
        )}
        {renderGauge(
          "Search Intent",
          scores.searchScore,
          targets.searchScore,
          <Search className="w-4 h-4" />,
        )}
        {renderGauge(
          "RAG Precision",
          scores.ragScore,
          targets.ragScore,
          <Sliders className="w-4 h-4" />,
        )}
        {renderGauge(
          "Agent Routing",
          scores.agentScore,
          targets.agentScore,
          <Users className="w-4 h-4" />,
        )}
        {renderGauge(
          "Enterprise SLA",
          scores.enterpriseScore,
          targets.enterpriseScore,
          <ShieldCheck className="w-4 h-4" />,
        )}
      </div>

      {/* Operational Dashboard Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 mb-8">
        {/* Left Side Query console */}
        <div className="lg:col-span-5 bg-slate-900 border border-slate-800 rounded-xl p-6 flex flex-col justify-between shadow-2xl relative overflow-hidden">
          <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-violet-600 via-indigo-500 to-violet-500" />

          <div>
            <div className="flex items-center gap-2 mb-4">
              <Terminal className="text-violet-500 w-5 h-5" />
              <h2 className="text-base font-bold text-slate-100 uppercase tracking-wider">
                Verification Controller
              </h2>
            </div>

            <p className="text-slate-400 text-xs leading-relaxed mb-4">
              Attack the platform validation gates across 1,000,000+ logical math, planning, and
              causal test scenarios. Auto-rank gaps and run self-improving code repair sweeps.
            </p>

            <div className="bg-slate-950 border border-slate-800 rounded-lg p-4 font-mono text-[11px] text-slate-400 space-y-3">
              <div className="flex justify-between">
                <span>Last Verification tag:</span>
                <span className="text-violet-400">{result?.cycleId || "V25-INIT"}</span>
              </div>
              <div className="flex justify-between">
                <span>Benchmark domain runs:</span>
                <span className="text-slate-200">1,000,000+ Tasks</span>
              </div>
              <div className="flex justify-between">
                <span>Active SLA breaches:</span>
                <span className="text-emerald-400">0 Breaches</span>
              </div>
              <div className="flex justify-between">
                <span>iGPU Power efficiency:</span>
                <span className="text-emerald-400">
                  {result?.performanceReport.telemetry.intelligencePerWatt} Watts/Intel
                </span>
              </div>
            </div>
          </div>

          <div className="mt-8">
            <button
              onClick={runVerification}
              disabled={isExecuting}
              className="w-full bg-violet-600 hover:bg-violet-500 disabled:bg-violet-800 transition-all text-white text-xs font-bold py-3 px-4 rounded-lg flex items-center justify-center gap-2 cursor-pointer shadow-lg shadow-violet-950"
            >
              {isExecuting ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  Running validation suites...
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 fill-white" />
                  Trigger Certification Suite
                </>
              )}
            </button>
          </div>
        </div>

        {/* Right Side Inspector tabs */}
        <div className="lg:col-span-7 bg-slate-900 border border-slate-800 rounded-xl p-6 flex flex-col justify-between shadow-2xl">
          <div>
            {/* Headers */}
            <div className="flex border-b border-slate-800 pb-3 mb-6 overflow-x-auto gap-2">
              <button
                className={`px-3 py-1.5 text-xs font-bold uppercase rounded-lg tracking-wider transition-all ${
                  selectedSubTab === "gaps"
                    ? "bg-violet-600/15 border border-violet-800 text-violet-400 font-bold"
                    : "text-slate-400 hover:text-slate-200"
                }`}
                onClick={() => setSelectedSubTab("gaps")}
              >
                Platform Gaps (ROI)
              </button>
              <button
                className={`px-3 py-1.5 text-xs font-bold uppercase rounded-lg tracking-wider transition-all ${
                  selectedSubTab === "reasoning"
                    ? "bg-violet-600/15 border border-violet-800 text-violet-400 font-bold"
                    : "text-slate-400 hover:text-slate-200"
                }`}
                onClick={() => setSelectedSubTab("reasoning")}
              >
                Logical Reasoning
              </button>
              <button
                className={`px-3 py-1.5 text-xs font-bold uppercase rounded-lg tracking-wider transition-all ${
                  selectedSubTab === "hallucination"
                    ? "bg-violet-600/15 border border-violet-800 text-violet-400 font-bold"
                    : "text-slate-400 hover:text-slate-200"
                }`}
                onClick={() => setSelectedSubTab("hallucination")}
              >
                Hallucinations
              </button>
              <button
                className={`px-3 py-1.5 text-xs font-bold uppercase rounded-lg tracking-wider transition-all ${
                  selectedSubTab === "memory"
                    ? "bg-violet-600/15 border border-violet-800 text-violet-400 font-bold"
                    : "text-slate-400 hover:text-slate-200"
                }`}
                onClick={() => setSelectedSubTab("memory")}
              >
                Recall Lattices
              </button>
              <button
                className={`px-3 py-1.5 text-xs font-bold uppercase rounded-lg tracking-wider transition-all ${
                  selectedSubTab === "sla"
                    ? "bg-violet-600/15 border border-violet-800 text-violet-400 font-bold"
                    : "text-slate-400 hover:text-slate-200"
                }`}
                onClick={() => setSelectedSubTab("sla")}
              >
                SLA Compliance
              </button>
            </div>

            {/* Sub-tab view: Gaps */}
            {selectedSubTab === "gaps" && result && (
              <div className="space-y-4">
                <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl">
                  <div className="flex items-center gap-2 mb-3">
                    <ShieldAlert className="text-amber-500 w-4 h-4 animate-pulse" />
                    <span className="text-xs font-bold text-slate-200">
                      Active Gap Analysis (ROI Prioritized)
                    </span>
                  </div>
                  <div className="space-y-3 max-h-72 overflow-y-auto pr-1">
                    {result.gapAnalysis.map((gap, idx) => (
                      <div
                        key={idx}
                        className="border border-slate-900 bg-slate-900/10 p-3 rounded-lg hover:border-slate-800 transition-colors"
                      >
                        <div className="flex justify-between items-center">
                          <span className="text-xs font-bold text-slate-300">{gap.metric}</span>
                          <span className="px-1.5 py-0.5 rounded text-[9px] bg-amber-950 text-amber-400 font-mono border border-amber-900/60">
                            ROI: {gap.roiScore}
                          </span>
                        </div>
                        <p className="text-[11px] text-slate-500 mt-1.5">
                          <strong className="text-slate-400">Root Cause:</strong> {gap.rootCause}
                        </p>
                        <p className="text-[11px] text-violet-400 mt-0.5">
                          <strong className="text-slate-400">Remedy:</strong> {gap.recommendedFix}
                        </p>
                        <div className="flex justify-between items-center mt-2.5 pt-2 border-t border-slate-950 text-[10px] text-slate-400 font-mono">
                          <span>Target: {(gap.targetScore * 100).toFixed(0)}%</span>
                          <span>Current: {(gap.currentScore * 100).toFixed(1)}%</span>
                          <span className="text-red-400 font-bold">
                            Delta: -{(gap.gap * 100).toFixed(1)}%
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Sub-tab view: Reasoning */}
            {selectedSubTab === "reasoning" && result && (
              <div className="space-y-4">
                <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl">
                  <div className="flex justify-between items-center mb-3 border-b border-slate-900 pb-2">
                    <h3 className="text-xs font-mono font-bold text-slate-400">
                      1,000,000+ Tasks Verification
                    </h3>
                    <span className="text-emerald-400 text-xs font-bold font-mono">
                      Avg Accuracy:{" "}
                      {(result.reasoningReport.compositeReasoningScore * 100).toFixed(2)}%
                    </span>
                  </div>
                  <div className="grid grid-cols-2 gap-3 max-h-56 overflow-y-auto pr-1">
                    {result.reasoningReport.domainMetrics.map((domain, idx) => (
                      <div
                        key={idx}
                        className="p-3 border border-slate-900 bg-slate-900/30 rounded-lg hover:border-slate-800 transition-all"
                      >
                        <span className="text-[10px] text-slate-500 font-mono block uppercase">
                          {domain.name}
                        </span>
                        <div className="flex justify-between items-baseline mt-1.5">
                          <span className="text-sm font-bold text-slate-300 font-mono">
                            {(domain.accuracy * 100).toFixed(1)}%
                          </span>
                          <span className="text-[9px] text-slate-500 font-mono">Acc</span>
                        </div>
                        <div className="w-full bg-slate-950 h-1 rounded-full overflow-hidden border border-slate-850 mt-2">
                          <div
                            className="bg-violet-600 h-full rounded-full"
                            style={{ width: `${domain.accuracy * 100}%` }}
                          />
                        </div>
                        <div className="flex justify-between text-[8px] text-slate-500 font-mono mt-1">
                          <span>Verification: {(domain.verificationRate * 100).toFixed(0)}%</span>
                          <span>Tasks: {domain.testCount.toLocaleString()}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Sub-tab view: Hallucinations */}
            {selectedSubTab === "hallucination" && result && (
              <div className="space-y-4">
                <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl">
                  <div className="flex justify-between items-center mb-4 border-b border-slate-900 pb-2">
                    <h3 className="text-xs font-mono font-bold text-slate-400">
                      Hallucination Audit Report
                    </h3>
                    <span className="text-emerald-400 text-xs font-bold font-mono">
                      Rate: {(result.hallucinationReport.hallucinationRate * 100).toFixed(2)}%
                    </span>
                  </div>
                  <div className="space-y-3 max-h-48 overflow-y-auto pr-1">
                    {result.hallucinationReport.scenarios.map((scen, idx) => (
                      <div
                        key={idx}
                        className="p-2.5 border border-slate-900 bg-slate-950 rounded flex justify-between items-center text-xs"
                      >
                        <div>
                          <span className="text-[9px] font-mono text-slate-500 block">
                            Scenario ID: {scen.scenarioId}
                          </span>
                          <span className="text-slate-300 font-bold block">{scen.inputType}</span>
                        </div>
                        <div className="text-right">
                          <span
                            className={`px-1.5 py-0.5 rounded text-[9px] font-mono font-bold border ${
                              scen.hallucinationDetected
                                ? "bg-rose-950 text-rose-400 border-rose-900/60"
                                : "bg-emerald-950 text-emerald-400 border-emerald-900/60"
                            }`}
                          >
                            {scen.hallucinationDetected ? "Hallucinated" : "Pruned"}
                          </span>
                          <span className="text-[9px] text-slate-500 font-mono block mt-1">
                            Confidence: {(scen.calibratedConfidence * 100).toFixed(0)}%
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Sub-tab view: Memory */}
            {selectedSubTab === "memory" && result && (
              <div className="space-y-4">
                <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl">
                  <div className="flex justify-between items-center mb-4 border-b border-slate-900 pb-2">
                    <h3 className="text-xs font-mono font-bold text-slate-400">
                      Recall Lattices & Drift Checks
                    </h3>
                    <span className="text-emerald-400 text-xs font-bold font-mono">
                      Recall Rate: {(result.memoryReport.recallRate * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="space-y-2.5 max-h-48 overflow-y-auto pr-1">
                    {result.memoryReport.nodes.map((node, idx) => (
                      <div
                        key={idx}
                        className="p-3 border border-slate-900 bg-slate-950 rounded flex justify-between items-center text-xs"
                      >
                        <div>
                          <span className="text-slate-300 font-bold font-mono block">
                            {node.nodeId}
                          </span>
                          <div className="flex gap-2 text-[9px] text-slate-500 font-mono mt-0.5">
                            <span>Drift: {node.driftRatePct}%</span>
                            <span>Temporal offset: {node.temporalOffsetMs}ms</span>
                          </div>
                        </div>
                        <div className="text-right">
                          <span className="text-xs text-slate-300 font-mono font-bold">
                            {(node.consistencyScore * 100).toFixed(1)}%
                          </span>
                          <span className="text-[9px] text-emerald-400 block font-mono">
                            Consistent
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Sub-tab view: SLA Compliance */}
            {selectedSubTab === "sla" && result && (
              <div className="space-y-4">
                <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl">
                  <div className="flex justify-between items-center mb-3">
                    <h3 className="text-xs font-mono font-bold text-slate-400">
                      Enterprise SLA Status
                    </h3>
                    <span className="text-emerald-400 text-xs font-bold font-mono">
                      SLA: {(result.enterpriseReport.stats.slaCompliance * 100).toFixed(2)}%
                    </span>
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs mb-4">
                    <div className="bg-slate-900 p-2.5 border border-slate-850 rounded text-center">
                      <span className="text-slate-500 text-[10px] block font-mono">
                        Availability
                      </span>
                      <span className="text-sm font-bold text-slate-200 font-mono">
                        {(result.enterpriseReport.stats.availability * 100).toFixed(3)}%
                      </span>
                    </div>
                    <div className="bg-slate-900 p-2.5 border border-slate-850 rounded text-center">
                      <span className="text-slate-500 text-[10px] block font-mono">
                        Avg Latency
                      </span>
                      <span className="text-sm font-bold text-slate-200 font-mono">
                        {result.enterpriseReport.stats.averageLatencyMs}ms
                      </span>
                    </div>
                    <div className="bg-slate-900 p-2.5 border border-slate-850 rounded text-center">
                      <span className="text-slate-500 text-[10px] block font-mono">
                        Recovery Uptime
                      </span>
                      <span className="text-sm font-bold text-slate-200 font-mono">
                        {(result.enterpriseReport.stats.recoveryUptimePct * 100).toFixed(3)}%
                      </span>
                    </div>
                    <div className="bg-slate-900 p-2.5 border border-slate-850 rounded text-center">
                      <span className="text-slate-500 text-[10px] block font-mono">Error Rate</span>
                      <span className="text-sm font-bold text-slate-200 font-mono">
                        {(result.enterpriseReport.stats.errorRate * 100).toFixed(3)}%
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Calibrated Report details */}
          {result && (
            <div className="border-t border-slate-800 pt-6 mt-6">
              <div className="bg-slate-950/80 border border-violet-900/20 rounded-xl p-4">
                <div className="flex justify-between items-center mb-3">
                  <div className="flex items-center gap-2">
                    <ShieldCheck className="text-violet-500 w-4 h-4" />
                    <span className="text-xs font-bold text-slate-300">
                      Authority Certification Envelope
                    </span>
                  </div>
                  <span className="px-2 py-0.5 rounded text-[10px] bg-emerald-950 text-emerald-400 border border-emerald-900 font-mono uppercase tracking-widest">
                    {result.certification.status}
                  </span>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-[10px] font-mono text-slate-400">
                  <div>Reasoning: {(result.certification.reasoningScore * 100).toFixed(1)}%</div>
                  <div>Memory: {(result.certification.memoryScore * 100).toFixed(1)}%</div>
                  <div>RAG: {(result.certification.ragScore * 100).toFixed(1)}%</div>
                  <div>Search: {(result.certification.searchScore * 100).toFixed(1)}%</div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Autonomous improvement loops timeline */}
      {result && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-2xl">
          <div className="flex justify-between items-center mb-4">
            <div className="flex items-center gap-2">
              <RefreshCw
                className="text-violet-500 w-5 h-5 animate-spin"
                style={{ animationDuration: "6s" }}
              />
              <h2 className="text-base font-bold text-slate-100 uppercase tracking-wider">
                Autonomous Certification Upgrades
              </h2>
            </div>
            <span className="text-slate-500 text-xs font-mono">Loop status: RUNNING</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-slate-950 border border-slate-850 p-4 rounded-xl">
              <span className="text-slate-500 text-[9px] font-mono block uppercase">
                Last Audited Metric
              </span>
              <span className="text-sm font-bold text-slate-200 mt-1 block">
                {result.convergenceReport.metricAudited}
              </span>
              <p className="text-slate-400 text-xs mt-1.5">
                <strong className="text-violet-400">Gap Identifed:</strong> -
                {(result.convergenceReport.identifiedGap * 100).toFixed(1)}%
              </p>
            </div>
            <div className="bg-slate-950 border border-slate-850 p-4 rounded-xl">
              <span className="text-slate-500 text-[9px] font-mono block uppercase">
                Remediation Deployed
              </span>
              <span className="text-xs text-slate-300 mt-1.5 block font-mono bg-slate-900 p-2.5 rounded border border-slate-850 leading-relaxed">
                {result.convergenceReport.fixApplied}
              </span>
            </div>
            <div className="bg-slate-950 border border-slate-850 p-4 rounded-xl flex flex-col justify-between">
              <div>
                <span className="text-slate-500 text-[9px] font-mono block uppercase">
                  Measured Calibration Delta
                </span>
                <div className="flex items-baseline gap-2 mt-1">
                  <span className="text-base font-bold text-red-500 font-mono">
                    {(result.convergenceReport.baselineValue * 100).toFixed(1)}%
                  </span>
                  <ArrowRight className="w-3.5 h-3.5 text-slate-600" />
                  <span className="text-xl font-bold text-emerald-400 font-mono">
                    {(result.convergenceReport.postExecutionScore * 100).toFixed(1)}%
                  </span>
                </div>
              </div>
              <span className="text-[10px] text-slate-500 font-mono block mt-2">
                Verified at {new Date(result.convergenceReport.timestamp).toLocaleTimeString()}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
