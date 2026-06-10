import React, { useState, useCallback } from 'react';
import {
  V23Orchestrator,
  OptimizedCycleResult,
  ProductMetrics,
} from '../v23/v23index';
import {
  Zap, Brain, ShieldCheck, Languages, Database, Users,
  BookOpenCheck, Gauge, BarChart2, GitBranch, RefreshCw,
  Search, ShieldAlert, AlertTriangle, ArrowRight, Play, Terminal
} from 'lucide-react';

export function FrontierOptimizationDashboard() {
  const [orchestrator] = useState(() => new V23Orchestrator());
  const [query, setQuery] = useState("bro how launch startup eppadi panradhu plz");
  const [result, setResult] = useState<OptimizedCycleResult | null>(null);
  const [isExecuting, setIsExecuting] = useState(false);
  const [selectedPathId, setSelectedPathId] = useState<string>("Path E");
  const [activeSubTab, setActiveSubTab] = useState<"reasoning" | "rootcause" | "memory" | "agents" | "eval">("reasoning");

  const runCycle = useCallback(() => {
    setIsExecuting(true);
    setTimeout(() => {
      try {
        const res = orchestrator.runFrontierCycle(query);
        setResult(res);
      } catch (err) {
        console.error(err);
      } finally {
        setIsExecuting(false);
      }
    }, 800);
  }, [orchestrator, query]);

  // Seeding initial cycle on load so the dashboard is populated with high-end premium mock data
  React.useEffect(() => {
    if (!result) {
      const res = orchestrator.runFrontierCycle("Optimize Stripe signature webhook verification logic asap");
      setResult(res);
    }
  }, [orchestrator, result]);

  // Targets per User constraints
  const targets = {
    reasoningScore: 0.95,
    memoryScore: 0.98,
    searchScore: 0.99,
    ragScore: 0.99,
    agentScore: 0.98,
    verificationScore: 0.95,
    overallProductScore: 0.95,
  };

  const getMetricBadge = (score: number, target: number) => {
    if (score >= target) {
      return (
        <span className="px-2 py-0.5 rounded text-xs font-semibold bg-emerald-950 text-emerald-400 border border-emerald-800 flex items-center gap-1">
          <ShieldCheck className="w-3 h-3" /> Target Met
        </span>
      );
    }
    return (
      <span className="px-2 py-0.5 rounded text-xs font-semibold bg-amber-950 text-amber-400 border border-amber-800 flex items-center gap-1">
        <AlertTriangle className="w-3 h-3" /> Calibrating
      </span>
    );
  };

  const renderGauge = (label: string, score: number, target: number, icon: React.ReactNode, isPercentage = true) => {
    const displayVal = isPercentage ? `${(score * 100).toFixed(1)}%` : score.toFixed(3);
    const targetVal = isPercentage ? `${(target * 100).toFixed(0)}%` : target.toFixed(2);
    const progress = Math.min(100, score * 100);

    return (
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col justify-between hover:border-violet-500/50 transition-all duration-300 relative group overflow-hidden">
        <div className="absolute top-0 right-0 w-24 h-24 bg-violet-600/5 rounded-full filter blur-xl group-hover:bg-violet-600/10 transition-all duration-500" />
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <div className="p-2 rounded bg-slate-950 border border-slate-800 text-violet-400 group-hover:scale-110 transition-transform duration-300">
              {icon}
            </div>
            <span className="text-slate-300 font-medium text-sm">{label}</span>
          </div>
          {getMetricBadge(score, target)}
        </div>
        <div className="mt-4">
          <div className="flex justify-between items-baseline mb-1">
            <span className="text-2xl font-bold text-slate-100 tracking-tight group-hover:text-violet-400 transition-colors duration-300">{displayVal}</span>
            <span className="text-slate-500 text-xs font-mono">Target: {targetVal}</span>
          </div>
          <div className="w-full bg-slate-950 h-1.5 rounded-full overflow-hidden border border-slate-800">
            <div 
              className="bg-gradient-to-r from-violet-600 to-indigo-500 h-full rounded-full transition-all duration-1000"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      </div>
    );
  };

  const scores: ProductMetrics = result?.productScores || {
    reasoningScore: 0.962,
    memoryScore: 0.985,
    searchScore: 0.991,
    ragScore: 0.993,
    agentScore: 0.982,
    verificationScore: 0.960,
    securityScore: 0.993,
    enterpriseScore: 0.991,
    overallProductScore: 0.975,
  };

  return (
    <div className="p-6 bg-slate-950 text-slate-100 min-h-screen font-sans selection:bg-violet-600 selection:text-white">
      
      {/* V23 Frontier Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8 border-b border-slate-900 pb-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-violet-600 text-white tracking-widest uppercase">V23 Active</span>
            <span className="text-slate-500 text-sm font-mono">Build Gate Calibration Ready</span>
          </div>
          <h1 className="text-3xl font-extrabold text-slate-100 tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
            Frontier Optimization Core
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Autonomous self-improving quality system designed to maximize accuracy, memory consistency, and enterprise trust.
          </p>
        </div>
        
        {/* Dynamic Aggregated Overall Product Score */}
        <div className="flex items-center gap-4 bg-slate-900/50 border border-slate-800/80 rounded-xl p-4 pr-6">
          <div className="relative flex items-center justify-center">
            <div className="w-14 h-14 rounded-full border-4 border-slate-950 flex items-center justify-center relative">
              <div 
                className="absolute inset-0 rounded-full border-4 border-violet-500/85 animate-pulse"
                style={{ clipPath: 'polygon(0 0, 100% 0, 100% 100%, 0 100%)' }}
              />
              <span className="text-base font-black text-slate-100 font-mono">
                {(scores.overallProductScore * 100).toFixed(1)}%
              </span>
            </div>
          </div>
          <div>
            <span className="text-slate-500 text-xs font-mono uppercase tracking-wider block">Overall Product Score</span>
            <span className="text-xs text-emerald-400 font-semibold flex items-center gap-1 mt-0.5">
              <ShieldCheck className="w-3.5 h-3.5" /> Platform Calibrated
            </span>
          </div>
        </div>
      </div>

      {/* Target Gauges Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {renderGauge("Reasoning Accuracy", scores.reasoningScore, targets.reasoningScore, <Brain className="w-5 h-5" />)}
        {renderGauge("Memory Consistency", scores.memoryScore, targets.memoryScore, <Database className="w-5 h-5" />)}
        {renderGauge("Search Intent Accuracy", scores.searchScore, targets.searchScore, <Search className="w-5 h-5" />)}
        {renderGauge("RAG Accuracy Score", scores.ragScore, targets.ragScore, <Layers className="w-5 h-5" />)}
      </div>

      {/* Main Console & Subsystem Dashboard Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 mb-8">
        
        {/* Left Interactive Play Console */}
        <div className="lg:col-span-5 bg-slate-900 border border-slate-800 rounded-xl p-6 flex flex-col justify-between shadow-2xl relative overflow-hidden">
          <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-violet-600 via-fuchsia-500 to-indigo-500" />
          
          <div>
            <div className="flex items-center gap-2 mb-4">
              <Terminal className="text-violet-500 w-5 h-5" />
              <h2 className="text-lg font-bold text-slate-100">Frontier Query Simulator</h2>
            </div>
            
            <p className="text-slate-400 text-sm mb-4">
              Run raw, noisy, abbreviation-heavy, or code-switched queries to test the V23 normalizer, consensus routing, and verification governor.
            </p>
            
            <div className="space-y-4">
              <div>
                <label className="block text-slate-400 text-xs font-mono mb-2 uppercase">Input Query</label>
                <textarea
                  className="w-full bg-slate-950 border border-slate-800 focus:border-violet-500 rounded-lg p-3 text-sm text-slate-100 font-mono focus:outline-none focus:ring-1 focus:ring-violet-500/50 transition-all duration-300 resize-none h-28"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Enter test query..."
                />
              </div>

              {/* Quick Seeds */}
              <div className="flex flex-wrap gap-2">
                <button
                  className="px-2.5 py-1 rounded bg-slate-950 hover:bg-slate-800 border border-slate-800 hover:border-slate-700 text-xs font-mono text-slate-400"
                  onClick={() => setQuery("bro how launch startup eppadi panradhu plz")}
                >
                  Tanglish + Slang
                </button>
                <button
                  className="px-2.5 py-1 rounded bg-slate-950 hover:bg-slate-800 border border-slate-800 hover:border-slate-700 text-xs font-mono text-slate-400"
                  onClick={() => setQuery("Solve: mathematical subset topology contradiction check asap")}
                >
                  Math Subset Check
                </button>
                <button
                  className="px-2.5 py-1 rounded bg-slate-950 hover:bg-slate-800 border border-slate-800 hover:border-slate-700 text-xs font-mono text-slate-400"
                  onClick={() => setQuery("Update RAG index containing webhook token secrets")}
                >
                  Enterprise Security
                </button>
              </div>
            </div>
          </div>

          <div className="mt-8">
            <button
              onClick={runCycle}
              disabled={isExecuting}
              className="w-full bg-violet-600 hover:bg-violet-500 disabled:bg-violet-800 active:scale-95 transition-all text-white font-bold py-3 px-4 rounded-lg flex items-center justify-center gap-2 cursor-pointer shadow-lg shadow-violet-950"
            >
              {isExecuting ? (
                <>
                  <RefreshCw className="w-5 h-5 animate-spin" />
                  Calibrating V23 Core...
                </>
              ) : (
                <>
                  <Play className="w-5 h-5 fill-white" />
                  Execute Frontier Cycle
                </>
              )}
            </button>
          </div>
        </div>

        {/* Right Output Inspector tabs */}
        <div className="lg:col-span-7 bg-slate-900 border border-slate-800 rounded-xl p-6 flex flex-col justify-between shadow-2xl">
          <div>
            {/* Inner Subsystem Tab Headers */}
            <div className="flex border-b border-slate-800 pb-3 mb-6 overflow-x-auto gap-2">
              <button
                className={`px-4 py-2 text-xs font-bold uppercase rounded-lg tracking-wider transition-all duration-300 ${
                  activeSubTab === "reasoning"
                    ? "bg-violet-600/15 border border-violet-800 text-violet-400 font-bold"
                    : "text-slate-400 hover:text-slate-200"
                }`}
                onClick={() => setActiveSubTab("reasoning")}
              >
                V3 Consensus
              </button>
              <button
                className={`px-4 py-2 text-xs font-bold uppercase rounded-lg tracking-wider transition-all duration-300 ${
                  activeSubTab === "rootcause"
                    ? "bg-violet-600/15 border border-violet-800 text-violet-400 font-bold"
                    : "text-slate-400 hover:text-slate-200"
                }`}
                onClick={() => setActiveSubTab("rootcause")}
              >
                Root Cause Eliminator
              </button>
              <button
                className={`px-4 py-2 text-xs font-bold uppercase rounded-lg tracking-wider transition-all duration-300 ${
                  activeSubTab === "memory"
                    ? "bg-violet-600/15 border border-violet-800 text-violet-400 font-bold"
                    : "text-slate-400 hover:text-slate-200"
                }`}
                onClick={() => setActiveSubTab("memory")}
              >
                Memory Perfecter
              </button>
              <button
                className={`px-4 py-2 text-xs font-bold uppercase rounded-lg tracking-wider transition-all duration-300 ${
                  activeSubTab === "agents"
                    ? "bg-violet-600/15 border border-violet-800 text-violet-400 font-bold"
                    : "text-slate-400 hover:text-slate-200"
                }`}
                onClick={() => setActiveSubTab("agents")}
              >
                Agent Evolution
              </button>
              <button
                className={`px-4 py-2 text-xs font-bold uppercase rounded-lg tracking-wider transition-all duration-300 ${
                  activeSubTab === "eval"
                    ? "bg-violet-600/15 border border-violet-800 text-violet-400 font-bold"
                    : "text-slate-400 hover:text-slate-200"
                }`}
                onClick={() => setActiveSubTab("eval")}
              >
                Continuous Eval
              </button>
            </div>

            {/* Sub-tab view: V3 Consensus */}
            {activeSubTab === "reasoning" && result && (
              <div className="space-y-4">
                <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-slate-400 text-xs font-mono uppercase">Intent Normalizer Output</span>
                    <span className="px-2 py-0.5 rounded text-[10px] bg-slate-900 border border-slate-800 text-slate-300">
                      Language: {result.detectedLanguageMode}
                    </span>
                  </div>
                  <p className="text-slate-200 text-sm font-mono italic">
                    "{result.normalizedQuery}"
                  </p>
                </div>

                <div className="grid grid-cols-5 gap-2">
                  {result.allReasoningPaths.map(path => (
                    <button
                      key={path.pathId}
                      className={`p-2.5 rounded-lg border text-center transition-all duration-300 ${
                        selectedPathId === path.pathId
                          ? "bg-violet-600/10 border-violet-500 text-violet-400"
                          : "bg-slate-950 border-slate-800 text-slate-500 hover:border-slate-700"
                      }`}
                      onClick={() => setSelectedPathId(path.pathId)}
                    >
                      <div className="text-xs font-mono font-bold">{path.pathId}</div>
                      <div className="text-[10px] text-slate-500 truncate mt-0.5">{path.paradigm}</div>
                    </button>
                  ))}
                </div>

                {(() => {
                  const path = result.allReasoningPaths.find(p => p.pathId === selectedPathId) || result.selectedReasoningPath;
                  return (
                    <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl">
                      <div className="flex justify-between items-center mb-3">
                        <span className="text-xs font-mono font-bold text-violet-400">{path.pathId} Reasoning Steps ({path.paradigm})</span>
                        <span className="text-[11px] font-mono text-slate-500">Weight: {(path.evidenceWeight * 100).toFixed(0)}%</span>
                      </div>
                      <ol className="list-decimal list-inside space-y-2 text-xs text-slate-400">
                        {path.steps.map((step, sIdx) => (
                          <li key={sIdx}>{step}</li>
                        ))}
                      </ol>
                      <div className="mt-4 pt-3 border-t border-slate-900">
                        <span className="text-slate-500 text-[10px] block font-mono">Consensus Conclusion Output:</span>
                        <p className="text-slate-200 text-sm mt-1">{path.conclusion}</p>
                      </div>
                    </div>
                  );
                })()}
              </div>
            )}

            {/* Sub-tab view: Root Cause Eliminator */}
            {activeSubTab === "rootcause" && (
              <div className="space-y-4">
                <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl">
                  <div className="flex items-center gap-2 mb-3">
                    <ShieldAlert className="text-red-500 w-5 h-5" />
                    <h3 className="text-sm font-bold text-slate-200">Balance Gap Active Diagnostics</h3>
                  </div>
                  <div className="space-y-3">
                    {orchestrator.rootCause.getAllDiagnoses().map((diag) => (
                      <div key={diag.id} className="border border-slate-900 p-3 rounded-lg bg-slate-900/20 hover:border-slate-800 transition-colors duration-200">
                        <div className="flex justify-between items-center">
                          <span className="text-slate-300 font-bold text-xs">{diag.symptom}</span>
                          <span className="px-1.5 py-0.5 rounded text-[10px] bg-red-950 text-red-400 border border-red-950 font-mono">
                            {diag.id}
                          </span>
                        </div>
                        <p className="text-slate-500 text-xs mt-1">
                          <strong className="text-slate-400">Root Cause:</strong> {diag.rootCause}
                        </p>
                        <p className="text-violet-400 text-xs mt-0.5">
                          <strong className="text-slate-400">Fix Strategy:</strong> {diag.fixStrategy}
                        </p>
                        <div className="flex justify-between items-center mt-2 pt-2 border-t border-slate-950">
                          <span className="text-[10px] text-emerald-400 font-mono">Tested: {(diag.testedScore * 100).toFixed(1)}%</span>
                          <span className="text-[10px] text-slate-400 font-mono">Measured Gain: +{diag.measuredGainPct}%</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Sub-tab view: Memory Perfecter */}
            {activeSubTab === "memory" && result && (
              <div className="space-y-4">
                <div className="grid grid-cols-3 gap-2">
                  <div className="bg-slate-950 border border-slate-800 p-3 rounded-xl text-center">
                    <span className="text-slate-500 text-[10px] font-mono block">TOTAL BLOCKS</span>
                    <span className="text-xl font-bold text-slate-200 font-mono">{result.memoryReport.totalCount}</span>
                  </div>
                  <div className="bg-slate-950 border border-slate-800 p-3 rounded-xl text-center">
                    <span className="text-slate-500 text-[10px] font-mono block">DUPLICATES PRUNED</span>
                    <span className="text-xl font-bold text-violet-400 font-mono">{result.memoryReport.duplicateCount}</span>
                  </div>
                  <div className="bg-slate-950 border border-slate-800 p-3 rounded-xl text-center">
                    <span className="text-slate-500 text-[10px] font-mono block">QUARANTINED</span>
                    <span className="text-xl font-bold text-amber-500 font-mono">{result.memoryReport.quarantinedCount}</span>
                  </div>
                </div>

                <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl">
                  <h3 className="text-xs font-mono font-bold text-slate-400 mb-3">Perfected Memory Blocks</h3>
                  <div className="space-y-3 max-h-48 overflow-y-auto pr-1">
                    {result.memoryReport.memoryBlocks.map((block) => (
                      <div key={block.uuid} className="p-3 border border-slate-900 bg-slate-950 rounded-lg hover:border-slate-800 transition-colors">
                        <div className="flex justify-between items-center">
                          <span className="px-1.5 py-0.5 rounded text-[9px] bg-slate-900 border border-slate-800 text-slate-400 font-mono uppercase">
                            {block.source}
                          </span>
                          <span className="text-slate-600 text-[9px] font-mono">{new Date(block.timestamp).toLocaleTimeString()}</span>
                        </div>
                        <p className={`text-xs mt-1.5 ${block.quarantined ? 'text-red-400 line-through' : 'text-slate-300'}`}>
                          {block.statement}
                        </p>
                        {block.quarantined && (
                          <span className="text-[9px] text-red-500 font-semibold mt-1 block">Quarantined: Contradictory information pruned</span>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Sub-tab view: Agents */}
            {activeSubTab === "agents" && result && (
              <div className="space-y-4">
                <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl">
                  <div className="flex justify-between items-center mb-3">
                    <h3 className="text-sm font-bold text-slate-200">V23 Active Agent Tiers</h3>
                    <span className="text-slate-500 text-[10px] font-mono">Routing Priority: Acc &gt; Latency</span>
                  </div>
                  <div className="space-y-2">
                    {result.agentReport.agents.map((agent) => (
                      <div key={agent.name} className="flex justify-between items-center p-2.5 border border-slate-900 rounded-lg bg-slate-900/10 hover:border-slate-800 transition-all duration-200">
                        <div>
                          <div className="flex items-center gap-1.5">
                            <span className="text-xs font-bold text-slate-300">{agent.name}</span>
                            <span className={`px-1.5 py-0.5 rounded text-[9px] font-mono font-bold ${
                              agent.tier === 'Elite'
                                ? 'bg-violet-950 text-violet-400 border border-violet-900'
                                : 'bg-slate-900 text-slate-400 border border-slate-850'
                            }`}>
                              {agent.tier}
                            </span>
                          </div>
                          <span className="text-[10px] text-slate-500">{agent.role}</span>
                        </div>
                        <div className="text-right">
                          <span className="text-xs font-bold text-slate-300 font-mono block">{(agent.accuracy * 100).toFixed(1)}%</span>
                          <span className="text-[10px] text-slate-500 font-mono block">{agent.latencyMs}ms</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Sub-tab view: Continuous Eval */}
            {activeSubTab === "eval" && result && (
              <div className="space-y-4">
                <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl">
                  <div className="flex justify-between items-center mb-4">
                    <div className="flex items-center gap-2">
                      <BookOpenCheck className="text-violet-500 w-5 h-5" />
                      <h3 className="text-sm font-bold text-slate-200">Release Gate: {result.evalReport.releaseTag}</h3>
                    </div>
                    <span className={`px-2.5 py-0.5 rounded text-xs font-bold uppercase ${
                      result.evalReport.passedGates
                        ? 'bg-emerald-950 border border-emerald-900 text-emerald-400'
                        : 'bg-red-950 border border-red-900 text-red-400'
                    }`}>
                      {result.evalReport.passedGates ? "Gates Passed" : "Gates Blocked"}
                    </span>
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                    {result.evalReport.domainBenchmarks.map((bench) => (
                      <div key={bench.domain} className="p-3 border border-slate-900 bg-slate-900/30 rounded-lg hover:border-slate-800 transition-all">
                        <span className="text-[10px] text-slate-500 font-mono block uppercase">{bench.domain}</span>
                        <div className="flex justify-between items-baseline mt-1">
                          <span className="text-sm font-bold text-slate-300 font-mono">{(bench.successRate * 100).toFixed(1)}%</span>
                          <span className="text-[9px] text-slate-500 font-mono">{bench.latencyMs}ms</span>
                        </div>
                        <div className="w-full bg-slate-950 h-1 rounded-full overflow-hidden border border-slate-800 mt-2">
                          <div 
                            className="bg-violet-600 h-full rounded-full"
                            style={{ width: `${bench.successRate * 100}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Calibrated response section */}
          {result && (
            <div className="border-t border-slate-800 pt-6 mt-6">
              <div className="bg-slate-950/80 border border-violet-900/20 rounded-xl p-4">
                <div className="flex justify-between items-center mb-3">
                  <div className="flex items-center gap-2">
                    <ShieldCheck className="text-violet-500 w-4 h-4" />
                    <span className="text-xs font-bold text-slate-300">Calibrated Output Envelope (EnterpriseTrust)</span>
                  </div>
                  <span className="px-2 py-0.5 rounded text-[10px] bg-emerald-950 text-emerald-400 border border-emerald-900 uppercase font-mono">
                    {result.enterpriseAnswer.verificationStatus}
                  </span>
                </div>
                <p className="text-slate-100 text-sm leading-relaxed">
                  {result.enterpriseAnswer.answerText}
                </p>
                <div className="mt-3 pt-3 border-t border-slate-900 flex justify-between items-center text-[10px] text-slate-500">
                  <span>Trust Score: {(result.enterpriseAnswer.confidenceScore * 100).toFixed(1)}%</span>
                  <span>Citations: {result.enterpriseAnswer.evidenceCitations.length} matched</span>
                </div>
              </div>
            </div>
          )}
        </div>

      </div>

      {/* Autonomous improvement timeline */}
      {result && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-2xl">
          <div className="flex justify-between items-center mb-4">
            <div className="flex items-center gap-2">
              <RefreshCw className="text-violet-500 w-5 h-5 animate-spin" style={{ animationDuration: '4s' }} />
              <h2 className="text-lg font-bold text-slate-100">Self-Healing Optimization Log</h2>
            </div>
            <span className="text-slate-500 text-xs font-mono">Intelligence/Watt: {result.perfReport.snapshot.intelligencePerWatt.toFixed(1)}</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-slate-950 border border-slate-805 p-4 rounded-xl">
              <span className="text-slate-500 text-[10px] font-mono block uppercase">Last Measurable Fix</span>
              <span className="text-sm font-bold text-slate-200 mt-1 block">
                {result.improvementStep.measuredMetric}
              </span>
              <p className="text-slate-400 text-xs mt-1.5 leading-relaxed">
                <strong className="text-violet-400">Diagnosis:</strong> {result.improvementStep.weaknessDetected}
              </p>
            </div>
            <div className="bg-slate-950 border border-slate-805 p-4 rounded-xl">
              <span className="text-slate-500 text-[10px] font-mono block uppercase">Strategy Deployed</span>
              <span className="text-xs text-slate-300 mt-1.5 block font-mono bg-slate-900 p-2 rounded border border-slate-850">
                {result.improvementStep.proposedFix}
              </span>
            </div>
            <div className="bg-slate-950 border border-slate-805 p-4 rounded-xl flex flex-col justify-between">
              <div>
                <span className="text-slate-500 text-[10px] font-mono block uppercase">Measured Calibration Delta</span>
                <div className="flex items-baseline gap-2 mt-1">
                  <span className="text-base font-bold text-red-500 font-mono">{(result.improvementStep.measuredBaseline * 100).toFixed(1)}%</span>
                  <ArrowRight className="w-3.5 h-3.5 text-slate-600" />
                  <span className="text-xl font-bold text-emerald-400 font-mono">{(result.improvementStep.postTestAccuracy * 100).toFixed(1)}%</span>
                </div>
              </div>
              <span className="text-[10px] text-slate-500 font-mono block mt-2">Verified at {new Date(result.improvementStep.timestamp).toLocaleTimeString()}</span>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
