import React, { useState, useCallback } from 'react';
import {
  ConvergenceOrchestrator,
  ConvergenceSweepResult,
  ConvergenceScores
} from '../v24/v24index';
import {
  Zap, Brain, ShieldCheck, Languages, Database, Users,
  BookOpenCheck, Gauge, BarChart2, GitBranch, RefreshCw,
  Search, ShieldAlert, AlertTriangle, ArrowRight, Play, Terminal,
  Sliders, Activity, Award
} from 'lucide-react';

export function ConvergenceDashboard() {
  const [orchestrator] = useState(() => new ConvergenceOrchestrator());
  const [query, setQuery] = useState("bro how launch startup eppadi panradhu plz");
  const [result, setResult] = useState<ConvergenceSweepResult | null>(null);
  const [isExecuting, setIsExecuting] = useState(false);
  const [selectedSubTab, setSelectedSubTab] = useState<"weaknesses" | "reasoning" | "memory" | "efficiency" | "history">("weaknesses");

  const runSweep = useCallback(() => {
    setIsExecuting(true);
    setTimeout(() => {
      try {
        const res = orchestrator.runConvergenceSweep(query);
        setResult(res);
      } catch (err) {
        console.error(err);
      } finally {
        setIsExecuting(false);
      }
    }, 800);
  }, [orchestrator, query]);

  // Seed initial mock data
  React.useEffect(() => {
    if (!result) {
      const res = orchestrator.runConvergenceSweep("Optimize Stripe signature webhook verification logic asap");
      setResult(res);
    }
  }, [orchestrator, result]);

  // V24 targets
  const targets = {
    reasoningScore: 0.95,
    memoryScore: 0.98,
    searchScore: 0.99,
    ragScore: 0.99,
    agentScore: 0.98,
    enterpriseScore: 0.99,
    overallProductScore: 0.95
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
        <AlertTriangle className="w-3 h-3" /> Optimizing
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
            <span className="text-xl font-extrabold text-slate-100 tracking-tight font-mono">{(score * 100).toFixed(1)}%</span>
            <span className="text-slate-500 text-[10px] font-mono">Target: {(target * 100).toFixed(0)}%</span>
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

  const scores: ConvergenceScores = result?.scores || {
    reasoningScore: 0.965,
    memoryScore: 0.985,
    searchScore: 0.992,
    ragScore: 0.994,
    agentScore: 0.982,
    verificationScore: 0.970,
    enterpriseScore: 0.991,
    performanceScore: 0.958,
    overallProductScore: 0.975
  };

  return (
    <div className="p-6 bg-slate-950 text-slate-100 min-h-screen font-sans selection:bg-violet-600 selection:text-white">
      
      {/* V24 Title */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8 border-b border-slate-900 pb-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-violet-600 text-white tracking-widest uppercase animate-pulse">V24 Convergence</span>
            <span className="text-slate-500 text-sm font-mono">Benchmark-Driven Self-Improvement</span>
          </div>
          <h1 className="text-3xl font-extrabold text-slate-100 tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
            Convergence Engine Core
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Aggregates validations, ranks weakness nodes, and enforces continuous performance calibration to converge at peak intelligence.
          </p>
        </div>

        {/* Aggregate platform KPI */}
        <div className="flex items-center gap-4 bg-slate-900/50 border border-slate-800/80 rounded-xl p-4 pr-6">
          <div className="relative flex items-center justify-center">
            <div className="w-14 h-14 rounded-full border-4 border-slate-950 flex items-center justify-center relative">
              <div 
                className="absolute inset-0 rounded-full border-4 border-violet-500/80 animate-pulse"
                style={{ clipPath: 'polygon(0 0, 100% 0, 100% 100%, 0 100%)' }}
              />
              <span className="text-base font-black text-slate-100 font-mono">
                {(scores.overallProductScore * 100).toFixed(1)}%
              </span>
            </div>
          </div>
          <div>
            <span className="text-slate-500 text-xs font-mono uppercase block">Overall Quality Score</span>
            <span className="text-xs text-emerald-400 font-semibold flex items-center gap-1 mt-0.5">
              <Award className="w-3.5 h-3.5" /> High-Trust release
            </span>
          </div>
        </div>
      </div>

      {/* Target Metrics Dials Row */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
        {renderGauge("Reasoning", scores.reasoningScore, targets.reasoningScore, <Brain className="w-4 h-4" />)}
        {renderGauge("Memory", scores.memoryScore, targets.memoryScore, <Database className="w-4 h-4" />)}
        {renderGauge("Search Intent", scores.searchScore, targets.searchScore, <Search className="w-4 h-4" />)}
        {renderGauge("RAG Accuracy", scores.ragScore, targets.ragScore, <Sliders className="w-4 h-4" />)}
        {renderGauge("Agent Routing", scores.agentScore, targets.agentScore, <Users className="w-4 h-4" />)}
        {renderGauge("Enterprise SLA", scores.enterpriseScore, targets.enterpriseScore, <ShieldCheck className="w-4 h-4" />)}
      </div>

      {/* Operational Dashboard Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 mb-8">
        
        {/* Left Side Query console */}
        <div className="lg:col-span-5 bg-slate-900 border border-slate-800 rounded-xl p-6 flex flex-col justify-between shadow-2xl relative overflow-hidden">
          <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-violet-600 via-indigo-500 to-violet-500" />
          
          <div>
            <div className="flex items-center gap-2 mb-4">
              <Terminal className="text-violet-500 w-5 h-5" />
              <h2 className="text-base font-bold text-slate-100 uppercase tracking-wider">Query Console</h2>
            </div>
            
            <p className="text-slate-400 text-xs leading-relaxed mb-4">
              Simulate queries containing slang, abbreviations, or codeswitching to trigger V24 intent recovery, consensus logic, and verification checkpoints.
            </p>
            
            <div className="space-y-4">
              <div>
                <label className="block text-slate-400 text-[10px] font-mono mb-2 uppercase">Input Text</label>
                <textarea
                  className="w-full bg-slate-950 border border-slate-800 focus:border-violet-500 rounded-lg p-3 text-xs text-slate-100 font-mono focus:outline-none focus:ring-1 focus:ring-violet-500/50 transition-all h-28 resize-none"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Enter test query..."
                />
              </div>

              {/* Seed Buttons */}
              <div className="flex flex-wrap gap-2">
                <button
                  className="px-2 py-1 rounded bg-slate-950 hover:bg-slate-800 border border-slate-800 text-[10px] font-mono text-slate-400"
                  onClick={() => setQuery("bro how launch startup eppadi panradhu plz")}
                >
                  Tamil-English
                </button>
                <button
                  className="px-2 py-1 rounded bg-slate-950 hover:bg-slate-800 border border-slate-800 text-[10px] font-mono text-slate-400"
                  onClick={() => setQuery("Solve mathematical subset topology contradiction check asap")}
                >
                  SAT Topology
                </button>
                <button
                  className="px-2 py-1 rounded bg-slate-950 hover:bg-slate-800 border border-slate-800 text-[10px] font-mono text-slate-400"
                  onClick={() => setQuery("Check Stripe signature webhook token secrets")}
                >
                  Enterprise Security
                </button>
              </div>
            </div>
          </div>

          <div className="mt-8">
            <button
              onClick={runSweep}
              disabled={isExecuting}
              className="w-full bg-violet-600 hover:bg-violet-500 disabled:bg-violet-800 transition-all text-white text-xs font-bold py-3 px-4 rounded-lg flex items-center justify-center gap-2 cursor-pointer shadow-lg shadow-violet-950"
            >
              {isExecuting ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  Running Convergence loop...
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 fill-white" />
                  Trigger Convergence Sweep
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
                  selectedSubTab === "weaknesses"
                    ? "bg-violet-600/15 border border-violet-800 text-violet-400 font-bold"
                    : "text-slate-400 hover:text-slate-200"
                }`}
                onClick={() => setSelectedSubTab("weaknesses")}
              >
                Weakness Registry
              </button>
              <button
                className={`px-3 py-1.5 text-xs font-bold uppercase rounded-lg tracking-wider transition-all ${
                  selectedSubTab === "reasoning"
                    ? "bg-violet-600/15 border border-violet-800 text-violet-400 font-bold"
                    : "text-slate-400 hover:text-slate-200"
                }`}
                onClick={() => setSelectedSubTab("reasoning")}
              >
                Maximized Intel
              </button>
              <button
                className={`px-3 py-1.5 text-xs font-bold uppercase rounded-lg tracking-wider transition-all ${
                  selectedSubTab === "memory"
                    ? "bg-violet-600/15 border border-violet-800 text-violet-400 font-bold"
                    : "text-slate-400 hover:text-slate-200"
                }`}
                onClick={() => setSelectedSubTab("memory")}
              >
                Stable Memory
              </button>
              <button
                className={`px-3 py-1.5 text-xs font-bold uppercase rounded-lg tracking-wider transition-all ${
                  selectedSubTab === "efficiency"
                    ? "bg-violet-600/15 border border-violet-800 text-violet-400 font-bold"
                    : "text-slate-400 hover:text-slate-200"
                }`}
                onClick={() => setSelectedSubTab("efficiency")}
              >
                Efficiency
              </button>
              <button
                className={`px-3 py-1.5 text-xs font-bold uppercase rounded-lg tracking-wider transition-all ${
                  selectedSubTab === "history"
                    ? "bg-violet-600/15 border border-violet-800 text-violet-400 font-bold"
                    : "text-slate-400 hover:text-slate-200"
                }`}
                onClick={() => setSelectedSubTab("history")}
              >
                Release Trends
              </button>
            </div>

            {/* Sub-tab view: Weaknesses */}
            {selectedSubTab === "weaknesses" && result && (
              <div className="space-y-4">
                <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl">
                  <div className="flex items-center gap-2 mb-3">
                    <ShieldAlert className="text-red-500 w-4 h-4" />
                    <span className="text-xs font-bold text-slate-200">Active Weakness Rankings (ROI Sorted)</span>
                  </div>
                  <div className="space-y-3 max-h-72 overflow-y-auto pr-1">
                    {result.topWeaknesses.map(weakness => (
                      <div key={weakness.id} className="border border-slate-900 bg-slate-900/10 p-3 rounded-lg hover:border-slate-800 transition-colors">
                        <div className="flex justify-between items-center">
                          <span className="text-xs font-bold text-slate-300">
                            Rank #{weakness.rank}: {weakness.weakness}
                          </span>
                          <span className="px-1.5 py-0.5 rounded text-[9px] bg-red-950 text-red-400 font-mono border border-red-900/60">
                            ROI: {weakness.roiScore}
                          </span>
                        </div>
                        <p className="text-[11px] text-slate-500 mt-1.5">
                          <strong className="text-slate-400">Root Cause:</strong> {weakness.rootCause}
                        </p>
                        <p className="text-[11px] text-violet-400 mt-0.5">
                          <strong className="text-slate-400">Remedy Strategy:</strong> {weakness.improvementStrategy}
                        </p>
                        <div className="flex justify-between items-center mt-2.5 pt-2 border-t border-slate-950 text-[10px] text-slate-400 font-mono">
                          <span>Complexity: {weakness.complexity}</span>
                          <span className="text-emerald-400">Est. Gain: +{weakness.estimatedGainPct}%</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Sub-tab view: Maximized Intel */}
            {selectedSubTab === "reasoning" && result && (
              <div className="space-y-4">
                <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl">
                  <div className="flex justify-between items-center mb-3">
                    <span className="text-[10px] text-slate-500 font-mono uppercase">Recovered Intent (Phase 7)</span>
                    <span className="px-1.5 py-0.5 rounded text-[9px] bg-slate-900 text-slate-300 font-mono border border-slate-800">
                      Language: {result.dialectDetected}
                    </span>
                  </div>
                  <p className="text-xs font-mono text-slate-300 italic">
                    "{result.normalizedQuery}"
                  </p>
                </div>

                <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-xs font-bold text-violet-400 uppercase tracking-wider font-mono">Consensus Path (Phase 3)</span>
                    <span className="text-[10px] font-mono text-slate-500">Method: {result.intelligenceOutput.consensusChoice.sourceType}</span>
                  </div>
                  <p className="text-xs text-slate-300 leading-relaxed bg-slate-900/30 border border-slate-900 p-2.5 rounded">
                    {result.intelligenceOutput.consensusChoice.content}
                  </p>
                  
                  <div className="mt-3">
                    <span className="text-[10px] text-slate-500 font-mono uppercase block mb-1">Critique Log</span>
                    <ul className="list-disc list-inside space-y-1 pl-1 text-[10px] text-slate-400 font-mono bg-slate-900 p-2 rounded">
                      {result.intelligenceOutput.critiqueNotes.map((note, idx) => (
                        <li key={idx}>{note}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            )}

            {/* Sub-tab view: Memory */}
            {selectedSubTab === "memory" && result && (
              <div className="space-y-4">
                <div className="grid grid-cols-4 gap-2">
                  <div className="bg-slate-950 border border-slate-800 p-2.5 rounded-lg text-center">
                    <span className="text-slate-500 text-[9px] font-mono block">ACTIVE</span>
                    <span className="text-lg font-bold text-slate-200 font-mono">{result.memoryOutput.totalCount}</span>
                  </div>
                  <div className="bg-slate-950 border border-slate-800 p-2.5 rounded-lg text-center">
                    <span className="text-slate-500 text-[9px] font-mono block">PRUNED</span>
                    <span className="text-lg font-bold text-violet-400 font-mono">{result.memoryOutput.duplicateCount}</span>
                  </div>
                  <div className="bg-slate-950 border border-slate-800 p-2.5 rounded-lg text-center">
                    <span className="text-slate-500 text-[9px] font-mono block">QUARANTINED</span>
                    <span className="text-lg font-bold text-amber-500 font-mono">{result.memoryOutput.quarantinedCount}</span>
                  </div>
                  <div className="bg-slate-950 border border-slate-800 p-2.5 rounded-lg text-center">
                    <span className="text-slate-500 text-[9px] font-mono block">EVICTED</span>
                    <span className="text-lg font-bold text-rose-500 font-mono">{result.memoryOutput.evictedCount}</span>
                  </div>
                </div>

                <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl">
                  <h3 className="text-xs font-mono font-bold text-slate-400 mb-2">Stable Memories Log</h3>
                  <div className="space-y-2 max-h-40 overflow-y-auto pr-1">
                    {result.memoryOutput.activeMemories.map(mem => (
                      <div key={mem.id} className="p-2 border border-slate-900 bg-slate-950 rounded text-xs">
                        <div className="flex justify-between items-center text-[9px] text-slate-500 font-mono">
                          <span>Source: {mem.source}</span>
                          <span>Timestamp: {new Date(mem.timestamp).toLocaleTimeString()}</span>
                        </div>
                        <p className={`mt-1 font-sans ${mem.quarantined ? 'text-red-400 line-through' : 'text-slate-300'}`}>
                          {mem.fact}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Sub-tab view: Efficiency */}
            {selectedSubTab === "efficiency" && result && (
              <div className="space-y-4">
                <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl">
                  <div className="flex justify-between items-center mb-3">
                    <h3 className="text-xs font-mono font-bold text-slate-400">Compute Efficiency Metrics</h3>
                    <span className="text-emerald-400 text-xs font-bold font-mono">{(result.efficiencyOutput.snapshot.intelligencePerWatt).toFixed(1)} Intel/Watt</span>
                  </div>
                  <div className="grid grid-cols-3 gap-3 text-xs mb-4">
                    <div className="bg-slate-900 p-2.5 border border-slate-850 rounded text-center">
                      <span className="text-slate-500 text-[10px] block font-mono">CPU Usage</span>
                      <span className="text-sm font-bold text-slate-200 font-mono">{result.efficiencyOutput.snapshot.cpuUsagePct}%</span>
                    </div>
                    <div className="bg-slate-900 p-2.5 border border-slate-850 rounded text-center">
                      <span className="text-slate-500 text-[10px] block font-mono">iGPU Load</span>
                      <span className="text-sm font-bold text-slate-200 font-mono">{result.efficiencyOutput.snapshot.igpuLoadPct}%</span>
                    </div>
                    <div className="bg-slate-900 p-2.5 border border-slate-850 rounded text-center">
                      <span className="text-slate-500 text-[10px] block font-mono">RAM Used</span>
                      <span className="text-sm font-bold text-slate-200 font-mono">{result.efficiencyOutput.snapshot.ramUsageGb} GB</span>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <span className="text-[10px] text-slate-500 font-mono uppercase block">Dynamic Scheduling Rules Applied</span>
                    {result.efficiencyOutput.rulesApplied.length === 0 ? (
                      <p className="text-slate-500 italic text-[11px]">No active throttles triggered. Compute pipelines balanced.</p>
                    ) : (
                      result.efficiencyOutput.rulesApplied.map((rule, idx) => (
                        <div key={idx} className="p-2 bg-slate-900 border border-slate-850 rounded text-[11px]">
                          <span className="text-amber-400 font-bold block">Trigger: {rule.triggerCondition}</span>
                          <span className="text-slate-400 mt-0.5 block font-mono">Remedy: {rule.remedyApplied}</span>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Sub-tab view: Release Trends */}
            {selectedSubTab === "history" && result && (
              <div className="space-y-4">
                <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl">
                  <h3 className="text-xs font-mono font-bold text-slate-400 mb-3">Historical Release Accuracy</h3>
                  <div className="space-y-2.5">
                    {result.benchmarkOutput.history.map((h, idx) => {
                      const width = h.overallScore * 100;
                      return (
                        <div key={idx} className="space-y-1">
                          <div className="flex justify-between items-center text-xs">
                            <span className="text-slate-300 font-bold font-mono">{h.releaseTag}</span>
                            <span className="text-violet-400 font-mono">{(h.overallScore * 100).toFixed(1)}%</span>
                          </div>
                          <div className="w-full bg-slate-900 h-1.5 rounded-full overflow-hidden border border-slate-800">
                            <div 
                              className="bg-violet-600 h-full rounded-full transition-all duration-1000"
                              style={{ width: `${width}%` }}
                            />
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Calibrated Output section */}
          {result && (
            <div className="border-t border-slate-800 pt-6 mt-6">
              <div className="bg-slate-950/80 border border-violet-900/20 rounded-xl p-4">
                <div className="flex justify-between items-center mb-3">
                  <div className="flex items-center gap-2">
                    <ShieldCheck className="text-violet-500 w-4 h-4" />
                    <span className="text-xs font-bold text-slate-300">Calibrated Output (Phase 4 Hallucination Audit)</span>
                  </div>
                  <span className="px-2 py-0.5 rounded text-[10px] bg-emerald-950 text-emerald-400 border border-emerald-900 font-mono uppercase tracking-widest">
                    {result.reliabilityOutput.recoveryStatus}
                  </span>
                </div>
                <p className="text-slate-100 text-xs leading-relaxed font-mono whitespace-pre-wrap">
                  {result.hallucinationOutput.calibratedResponse}
                </p>
                <div className="mt-3 pt-3 border-t border-slate-900 flex justify-between items-center text-[10px] text-slate-500">
                  <span>Confidence: {(result.hallucinationOutput.calibratedConfidence * 100).toFixed(1)}%</span>
                  <span className="text-emerald-400">Hallucination rate: {(result.hallucinationOutput.hallucinationRate * 100).toFixed(2)}%</span>
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
              <RefreshCw className="text-violet-500 w-5 h-5 animate-spin" style={{ animationDuration: '6s' }} />
              <h2 className="text-base font-bold text-slate-100 uppercase tracking-wider">Autonomous Convergence Loop (Phase 13)</h2>
            </div>
            <span className="text-slate-500 text-xs font-mono">Loop status: ACTIVE</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-slate-950 border border-slate-805 p-4 rounded-xl">
              <span className="text-slate-500 text-[9px] font-mono block uppercase">Last Measured Metric</span>
              <span className="text-sm font-bold text-slate-200 mt-1 block">
                {result.improvementStep.measuredMetricName}
              </span>
              <p className="text-slate-400 text-xs mt-1.5">
                <strong className="text-violet-400">Weakness:</strong> {result.improvementStep.identifiedWeakness}
              </p>
            </div>
            <div className="bg-slate-950 border border-slate-805 p-4 rounded-xl">
              <span className="text-slate-500 text-[9px] font-mono block uppercase">Convergence Strategy Deployed</span>
              <span className="text-xs text-slate-300 mt-1.5 block font-mono bg-slate-900 p-2.5 rounded border border-slate-850 leading-relaxed">
                {result.improvementStep.remedyStrategy}
              </span>
            </div>
            <div className="bg-slate-950 border border-slate-805 p-4 rounded-xl flex flex-col justify-between">
              <div>
                <span className="text-slate-500 text-[9px] font-mono block uppercase">Measured Calibration Delta</span>
                <div className="flex items-baseline gap-2 mt-1">
                  <span className="text-base font-bold text-red-500 font-mono">{(result.improvementStep.baselineScore * 100).toFixed(1)}%</span>
                  <ArrowRight className="w-3.5 h-3.5 text-slate-600" />
                  <span className="text-xl font-bold text-emerald-400 font-mono">{(result.improvementStep.postAccuracyScore * 100).toFixed(1)}%</span>
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
