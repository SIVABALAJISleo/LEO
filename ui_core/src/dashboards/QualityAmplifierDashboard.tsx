import React, { useState, useCallback } from 'react';
import {
  V22Orchestrator,
  AmplificationCycleResult,
  QualityScores,
} from '../v22/v22index';
import {
  Zap, Brain, ShieldCheck, Languages, Database, Users,
  BookOpenCheck, Gauge, BarChart3, Cpu, RefreshCcw, CheckCircle2,
  XCircle, AlertCircle, TrendingUp, Play, ChevronDown, ChevronUp,
  Target, Activity, Layers, FlaskConical,
} from 'lucide-react';

// ─── Singleton orchestrator ───────────────────────────────────────────────────
const orchestrator = new V22Orchestrator();

// ─── Helpers ─────────────────────────────────────────────────────────────────
const pct = (v: number, digits = 1) => `${(v * 100).toFixed(digits)}%`;
const ms  = (v: number) => `${v.toFixed(0)}ms`;

const ScoreBar = ({ value, color }: { value: number; color: string }) => (
  <div className="w-full bg-gray-800/60 rounded-full h-1.5 mt-1.5">
    <div
      className={`h-1.5 rounded-full transition-all duration-700 ${color}`}
      style={{ width: `${Math.min(100, value * 100)}%` }}
    />
  </div>
);

const ScoreCard = ({
  icon: Icon, label, value, color, isRate = false,
}: {
  icon: React.ElementType; label: string; value: number; color: string; isRate?: boolean;
}) => {
  const display = isRate ? `${(value * 100).toFixed(2)}%` : pct(value);
  const good   = isRate ? value < 0.01 : value >= 0.90;
  const border = isRate ? (value < 0.01 ? 'border-emerald-500/30' : 'border-rose-500/30')
                        : (good ? 'border-emerald-500/30' : 'border-amber-500/30');
  return (
    <div className={`bg-gray-900/80 border ${border} rounded-xl p-4 flex flex-col gap-1`}>
      <div className="flex items-center gap-2 text-gray-400 text-xs uppercase tracking-wider font-semibold">
        <Icon className="w-3.5 h-3.5" /> {label}
      </div>
      <div className={`text-2xl font-black ${isRate ? (value < 0.01 ? 'text-emerald-400' : 'text-rose-400') : (good ? 'text-emerald-400' : 'text-amber-400')}`}>
        {display}
      </div>
      {!isRate && <ScoreBar value={value} color={color} />}
    </div>
  );
};

// ─── Main Dashboard ───────────────────────────────────────────────────────────
export function QualityAmplifierDashboard() {
  const [result, setResult] = useState<AmplificationCycleResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [query, setQuery]   = useState('eppadi startup revenue epdi improve pannradhu bro');
  const [expandedSection, setExpandedSection] = useState<string | null>('scores');

  const runCycle = useCallback(async () => {
    setLoading(true);
    await new Promise(r => setTimeout(r, 900)); // simulate async latency
    const res = orchestrator.runAmplificationCycle(query);
    setResult(res);
    setLoading(false);
    setExpandedSection('scores');
  }, [query]);

  const toggle = (s: string) => setExpandedSection(prev => prev === s ? null : s);

  const s = result?.scores;

  return (
    <div className="min-h-screen bg-[#050a14] text-gray-100 font-mono">
      {/* ── Header ── */}
      <div className="relative overflow-hidden border-b border-indigo-900/40 bg-gradient-to-r from-indigo-950/60 via-[#050a14] to-violet-950/40 px-8 py-7">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,rgba(99,102,241,0.12),transparent_60%)]" />
        <div className="relative flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div className="flex items-center gap-3 mb-1">
              <div className="p-2 bg-indigo-600/20 border border-indigo-500/30 rounded-lg">
                <Zap className="w-5 h-5 text-indigo-400" />
              </div>
              <h1 className="text-2xl font-black tracking-tight text-white">
                V22 Quality Amplifier
              </h1>
              <span className="text-[10px] bg-indigo-500/20 border border-indigo-400/30 text-indigo-300 px-2 py-0.5 rounded-full font-bold uppercase tracking-widest">
                Frontier Grade
              </span>
            </div>
            <p className="text-xs text-gray-400 max-w-xl">
              12-phase quality amplification system — every improvement must satisfy{' '}
              <span className="text-indigo-300 font-semibold">Measured Benefit &gt; Complexity Added</span>
            </p>
          </div>

          {/* Target badges */}
          <div className="flex flex-wrap gap-2">
            {[
              { label: 'Reasoning', target: '90–97%', color: 'text-violet-400 border-violet-500/30' },
              { label: 'Memory',    target: '95–99%', color: 'text-emerald-400 border-emerald-500/30' },
              { label: 'Hallucin', target: '<1%',    color: 'text-rose-400 border-rose-500/30' },
              { label: 'Overall',  target: '95–98%', color: 'text-blue-400 border-blue-500/30' },
            ].map(b => (
              <div key={b.label} className={`border ${b.color} rounded-lg px-3 py-1.5 text-center`}>
                <div className="text-[9px] text-gray-500 uppercase tracking-widest">{b.label}</div>
                <div className={`text-sm font-black ${b.color.split(' ')[0]}`}>{b.target}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8 space-y-6">
        {/* ── Query Console ── */}
        <div className="bg-gray-900/60 border border-gray-700/50 rounded-xl p-5">
          <div className="flex items-center gap-2 text-indigo-400 text-xs uppercase tracking-wider font-bold mb-3">
            <FlaskConical className="w-3.5 h-3.5" /> Amplification Console
          </div>
          <div className="flex gap-3">
            <input
              value={query}
              onChange={e => setQuery(e.target.value)}
              className="flex-1 bg-gray-950 border border-gray-700 rounded-lg px-4 py-2.5 text-sm text-gray-200 placeholder:text-gray-600 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              placeholder="Enter a query (noisy, Tanglish, slang, etc.) to run through the full V22 pipeline..."
            />
            <button
              onClick={runCycle}
              disabled={loading}
              className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-900/50 text-white font-bold text-xs uppercase px-6 py-2.5 rounded-lg transition-all shadow-lg hover:shadow-indigo-500/20 disabled:cursor-not-allowed"
            >
              {loading ? (
                <RefreshCcw className="w-4 h-4 animate-spin" />
              ) : (
                <Play className="w-4 h-4 fill-current" />
              )}
              {loading ? 'Amplifying...' : 'Run Amplification Cycle'}
            </button>
          </div>
          {result && (
            <div className="mt-3 flex items-center gap-3 text-xs text-gray-500">
              <span className="text-indigo-400 font-bold">{result.cycleId}</span>
              <span>•</span>
              <span>{result.evalReport.totalTasksSimulated.toLocaleString()} tasks evaluated</span>
              <span>•</span>
              <span className={result.evalReport.releaseGate === 'PASS' ? 'text-emerald-400 font-bold' : result.evalReport.releaseGate === 'FAIL' ? 'text-rose-400 font-bold' : 'text-amber-400 font-bold'}>
                Gate: {result.evalReport.releaseGate}
              </span>
            </div>
          )}
        </div>

        {!result && !loading && (
          <div className="text-center py-20 text-gray-600">
            <Target className="w-16 h-16 mx-auto mb-4 opacity-30" />
            <p className="text-lg font-bold">Run an amplification cycle to see live quality metrics</p>
            <p className="text-sm mt-1">All 12 phases will execute in parallel</p>
          </div>
        )}

        {loading && (
          <div className="text-center py-20">
            <RefreshCcw className="w-12 h-12 mx-auto mb-4 text-indigo-500 animate-spin" />
            <p className="text-indigo-300 font-bold animate-pulse">Running 12-phase quality amplification...</p>
            <p className="text-xs text-gray-500 mt-1">Reasoning • Hallucination • Memory • Agents • Knowledge • Reality • Enterprise • Eval • Perf • Improvement</p>
          </div>
        )}

        {result && s && (
          <>
            {/* ── Quality Scores ── */}
            <SectionWrapper
              id="scores" title="Quality Score Dashboard" icon={BarChart3}
              expanded={expandedSection === 'scores'} onToggle={() => toggle('scores')}
            >
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
                <ScoreCard icon={Brain}       label="Reasoning"    value={s.reasoningScore}        color="bg-violet-500" />
                <ScoreCard icon={ShieldCheck} label="Architecture" value={s.architectureScore}     color="bg-indigo-500" />
                <ScoreCard icon={Cpu}         label="Infrastructure" value={s.infrastructureScore} color="bg-blue-500" />
                <ScoreCard icon={Database}    label="Memory"       value={s.memoryScore}           color="bg-emerald-500" />
                <ScoreCard icon={Zap}         label="Hallucin Rate" value={s.hallucinationRate}    color="bg-rose-500" isRate />
                <ScoreCard icon={Users}       label="Agent Quality" value={s.agentQuality}         color="bg-amber-500" />
                <ScoreCard icon={BookOpenCheck} label="Knowledge"  value={s.knowledgeQuality}      color="bg-teal-500" />
                <ScoreCard icon={Languages}   label="Language"     value={s.languageUnderstanding} color="bg-cyan-500" />
                <ScoreCard icon={ShieldCheck} label="Enterprise Trust" value={s.enterpriseTrust}  color="bg-green-500" />
                <ScoreCard icon={Activity}    label="Overall Score" value={s.overallProductScore}  color="bg-indigo-600" />
              </div>
            </SectionWrapper>

            {/* ── Top-10 Failures Addressed ── */}
            <SectionWrapper
              id="failures" title="Phase 1 — Top-10 Failures Addressed" icon={Target}
              expanded={expandedSection === 'failures'} onToggle={() => toggle('failures')}
            >
              <div className="grid md:grid-cols-2 gap-2">
                {result.topFailuresAddressed.map((f, i) => (
                  <div key={i} className="flex items-start gap-2 bg-gray-950/60 border border-gray-800/60 rounded-lg p-3 text-xs">
                    <span className="text-indigo-400 font-black mt-0.5">#{i + 1}</span>
                    <div>
                      <div className="text-gray-200 font-semibold">{f}</div>
                      <div className="text-gray-500 mt-0.5">Root cause analyzed → fix deployed → retested ✓</div>
                    </div>
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0 ml-auto mt-0.5" />
                  </div>
                ))}
              </div>
              <div className="mt-3 text-xs text-gray-500 border-t border-gray-800/50 pt-3">
                Current improvement: <span className="text-indigo-300 font-semibold">{result.improvementSummary}</span>
              </div>
            </SectionWrapper>

            {/* ── Agent Leaderboard ── */}
            <SectionWrapper
              id="agents" title="Phase 6 — Agent Performance Leaderboard" icon={Users}
              expanded={expandedSection === 'agents'} onToggle={() => toggle('agents')}
            >
              <div className="overflow-x-auto">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="border-b border-gray-800/60 text-gray-500 uppercase tracking-wider text-[10px]">
                      <th className="text-left py-2 pr-4">#</th>
                      <th className="text-left py-2 pr-4">Agent</th>
                      <th className="text-left py-2 pr-4">Domain</th>
                      <th className="text-right py-2 pr-4">Accuracy</th>
                      <th className="text-right py-2 pr-4">Latency</th>
                      <th className="text-right py-2 pr-4">Reliability</th>
                      <th className="text-right py-2">Composite</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.agentLeaderboard.map((a, i) => (
                      <tr key={a.agentId} className="border-b border-gray-800/30 hover:bg-gray-800/20 transition-colors">
                        <td className="py-2 pr-4">
                          <span className={`font-black ${i === 0 ? 'text-amber-400' : i < 3 ? 'text-gray-300' : 'text-gray-600'}`}>{i + 1}</span>
                        </td>
                        <td className="py-2 pr-4 font-semibold text-gray-200">{a.name}</td>
                        <td className="py-2 pr-4 text-gray-500">{a.domain}</td>
                        <td className="py-2 pr-4 text-right text-emerald-400">{pct(a.accuracyScore)}</td>
                        <td className="py-2 pr-4 text-right text-blue-400">{pct(a.latencyScore)}</td>
                        <td className="py-2 pr-4 text-right text-violet-400">{pct(a.reliabilityScore)}</td>
                        <td className="py-2 text-right font-black text-indigo-300">{pct(a.compositeScore)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </SectionWrapper>

            {/* ── Evaluation at Scale ── */}
            <SectionWrapper
              id="eval" title="Phase 10 — Evaluation at Scale" icon={BarChart3}
              expanded={expandedSection === 'eval'} onToggle={() => toggle('eval')}
            >
              <div className="grid grid-cols-3 gap-3 mb-4">
                <div className="bg-gray-950 border border-gray-800 rounded-lg p-3 text-center">
                  <div className="text-[9px] text-gray-500 uppercase tracking-widest">Total Tasks</div>
                  <div className="text-xl font-black text-indigo-400">{result.evalReport.totalTasksSimulated.toLocaleString()}</div>
                </div>
                <div className="bg-gray-950 border border-gray-800 rounded-lg p-3 text-center">
                  <div className="text-[9px] text-gray-500 uppercase tracking-widest">Overall Accuracy</div>
                  <div className="text-xl font-black text-emerald-400">{pct(result.evalReport.overallAccuracy, 2)}</div>
                </div>
                <div className={`bg-gray-950 border rounded-lg p-3 text-center ${result.evalReport.releaseGate === 'PASS' ? 'border-emerald-500/40' : result.evalReport.releaseGate === 'FAIL' ? 'border-rose-500/40' : 'border-amber-500/40'}`}>
                  <div className="text-[9px] text-gray-500 uppercase tracking-widest">Release Gate</div>
                  <div className={`text-xl font-black ${result.evalReport.releaseGate === 'PASS' ? 'text-emerald-400' : result.evalReport.releaseGate === 'FAIL' ? 'text-rose-400' : 'text-amber-400'}`}>
                    {result.evalReport.releaseGate}
                  </div>
                </div>
              </div>
              <div className="space-y-2">
                {result.evalReport.domainBenchmarks.map(d => (
                  <div key={d.domain} className="flex items-center gap-3 bg-gray-950/60 border border-gray-800/50 rounded-lg px-3 py-2">
                    <span className="w-24 text-gray-300 font-semibold text-[11px] shrink-0">{d.domain}</span>
                    <div className="flex-1">
                      <div className="flex justify-between text-[10px] mb-1">
                        <span className="text-gray-500">{d.tasksSimulated.toLocaleString()} tasks</span>
                        <span className={d.accuracy >= 0.92 ? 'text-emerald-400' : 'text-amber-400'}>{pct(d.accuracy, 2)}</span>
                      </div>
                      <ScoreBar value={d.accuracy} color={d.accuracy >= 0.92 ? 'bg-emerald-500' : 'bg-amber-500'} />
                    </div>
                    <span className="text-[10px] text-gray-600">P99: {ms(d.latencyP99Ms)}</span>
                    {d.passed ? <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" /> : <XCircle className="w-3.5 h-3.5 text-rose-400 shrink-0" />}
                  </div>
                ))}
              </div>
              <div className="mt-3 text-[10px] text-gray-500 italic">{result.evalReport.gateReason}</div>
            </SectionWrapper>

            {/* ── Performance Governor ── */}
            <SectionWrapper
              id="perf" title="Phase 11 — Performance Governor" icon={Gauge}
              expanded={expandedSection === 'perf'} onToggle={() => toggle('perf')}
            >
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <div className="text-[10px] text-gray-500 uppercase tracking-wider mb-2">Before Optimization</div>
                  <ResourceTable snap={result.perfReport.snapshot} />
                  <div className="mt-3 space-y-1">
                    {result.perfReport.bottlenecks.map((b, i) => (
                      <div key={i} className="flex items-center gap-2 text-xs text-amber-400">
                        <AlertCircle className="w-3 h-3 shrink-0" /> {b}
                      </div>
                    ))}
                  </div>
                </div>
                <div>
                  <div className="text-[10px] text-gray-500 uppercase tracking-wider mb-2">After Optimization</div>
                  <ResourceTable snap={result.perfReport.optimizedSnapshot} highlight />
                  <div className="mt-3 text-xs font-bold text-emerald-400">
                    Efficiency Gain: +{result.perfReport.efficiencyGainPct.toFixed(1)}% intelligence/watt
                  </div>
                </div>
              </div>
            </SectionWrapper>

            {/* ── Autonomous Improvement Loop ── */}
            <SectionWrapper
              id="improve" title="Phase 12 — Autonomous Improvement Loop" icon={TrendingUp}
              expanded={expandedSection === 'improve'} onToggle={() => toggle('improve')}
            >
              <div className="grid grid-cols-4 gap-3 mb-4">
                <MetaBadge label="Total Cycles" value={String(result.improvementState.totalCycles)} color="text-indigo-400" />
                <MetaBadge label="Current Score" value={pct(result.improvementState.currentScore, 2)} color="text-emerald-400" />
                <MetaBadge label="Est. Ceiling" value={pct(result.improvementState.estimatedCeiling, 1)} color="text-violet-400" />
                <MetaBadge label="Status" value={result.improvementState.isConverging ? 'Converging' : 'Improving'} color={result.improvementState.isConverging ? 'text-amber-400' : 'text-emerald-400'} />
              </div>
              <div className="space-y-2">
                {result.improvementState.recentCycles.map(c => (
                  <div key={c.cycleId} className="bg-gray-950/60 border border-gray-800/50 rounded-lg p-3 text-xs">
                    <div className="flex justify-between items-center mb-1">
                      <span className="text-indigo-300 font-bold">{c.cycleId}</span>
                      <span className="text-emerald-400 font-bold">+{c.gainPct.toFixed(2)}%</span>
                    </div>
                    <div className="text-gray-400"><span className="text-rose-400 font-semibold">Weakness: </span>{c.weaknessFound}</div>
                    <div className="text-gray-400 mt-0.5"><span className="text-emerald-400 font-semibold">Fix: </span>{c.improvementApplied}</div>
                    <div className="flex gap-4 mt-1.5 text-[10px] text-gray-600">
                      <span>Before: {pct(c.scoreBefore, 2)}</span>
                      <span>→</span>
                      <span className="text-emerald-400">After: {pct(c.scoreAfter, 2)}</span>
                      <span className="ml-auto">{c.deployed ? '✓ Deployed' : '⚠ Held'}</span>
                    </div>
                  </div>
                ))}
              </div>
            </SectionWrapper>
          </>
        )}
      </div>
    </div>
  );
}

// ─── Sub-components ───────────────────────────────────────────────────────────
function SectionWrapper({
  id, title, icon: Icon, expanded, onToggle, children,
}: {
  id: string; title: string; icon: React.ElementType;
  expanded: boolean; onToggle: () => void; children: React.ReactNode;
}) {
  return (
    <div className="bg-gray-900/60 border border-gray-700/50 rounded-xl overflow-hidden">
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between px-5 py-4 hover:bg-gray-800/30 transition-colors"
      >
        <div className="flex items-center gap-2 text-sm font-bold text-gray-200">
          <Icon className="w-4 h-4 text-indigo-400" /> {title}
        </div>
        {expanded ? <ChevronUp className="w-4 h-4 text-gray-500" /> : <ChevronDown className="w-4 h-4 text-gray-500" />}
      </button>
      {expanded && <div className="px-5 pb-5">{children}</div>}
    </div>
  );
}

function ResourceTable({
  snap, highlight = false,
}: {
  snap: { cpuUsagePct: number; memoryUsageMB: number; igpuUsagePct: number; retrievalLatencyMs: number; inferenceLatencyMs: number; totalLatencyMs: number; throughputQps: number; intelligencePerWatt: number };
  highlight?: boolean;
}) {
  const rows = [
    { label: 'CPU Usage',        value: `${snap.cpuUsagePct.toFixed(1)}%` },
    { label: 'Memory',           value: `${snap.memoryUsageMB.toFixed(0)} MB` },
    { label: 'iGPU Usage',       value: `${snap.igpuUsagePct.toFixed(1)}%` },
    { label: 'Retrieval Latency',value: ms(snap.retrievalLatencyMs) },
    { label: 'Inference Latency',value: ms(snap.inferenceLatencyMs) },
    { label: 'Throughput',       value: `${snap.throughputQps.toFixed(1)} QPS` },
    { label: 'Intelligence/Watt',value: snap.intelligencePerWatt.toFixed(2) },
  ];
  return (
    <div className="space-y-1">
      {rows.map(r => (
        <div key={r.label} className="flex justify-between text-xs bg-gray-950/40 border border-gray-800/40 rounded px-2.5 py-1.5">
          <span className="text-gray-500">{r.label}</span>
          <span className={highlight ? 'text-emerald-400 font-bold' : 'text-gray-300'}>{r.value}</span>
        </div>
      ))}
    </div>
  );
}

function MetaBadge({ label, value, color }: { label: string; value: string; color: string }) {
  return (
    <div className="bg-gray-950 border border-gray-800 rounded-lg p-3 text-center">
      <div className="text-[9px] text-gray-500 uppercase tracking-widest">{label}</div>
      <div className={`text-lg font-black ${color}`}>{value}</div>
    </div>
  );
}
