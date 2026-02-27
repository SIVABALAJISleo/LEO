import React, { useState, useEffect } from 'react';
import { Shield, Zap, Search, Activity, Cpu, Database, RefreshCw, AlertTriangle, Layers, Maximize } from 'lucide-react';
import { hyperClient, HyperResponse } from './lib/api';

function App() {
    const [query, setQuery] = useState('');
    const [result, setResult] = useState<HyperResponse | null>(null);
    const [optimisticMode, setOptimisticMode] = useState(false);
    const [loading, setLoading] = useState(false);
    const [history, setHistory] = useState<HyperResponse[]>([]);

    const handleExecute = async () => {
        if (!query) return;

        // OPTIMISTIC UPDATE
        setOptimisticMode(true);
        const optimisticAnswer = hyperClient.getOptimisticResult(query);
        setResult({
            status: "pending",
            mode: "OPTIMISTIC_PREDICTION",
            expert: "UI_Engine",
            result: optimisticAnswer,
            compute_cost_avoided: true,
            latency_ms: 0
        });

        setLoading(true);
        const actualResult = await hyperClient.orchestrate(query);

        // VERIFY PREDICTION (UX Illusion)
        setTimeout(() => {
            setResult(actualResult);
            setOptimisticMode(false);
            setLoading(false);
            setHistory(prev => [actualResult, ...prev].slice(0, 5));
        }, 400); // Small delay to show prediction->reality transition
    };

    return (
        <div className="min-h-screen bg-[#0f172a] text-slate-200 p-8 font-sans">
            <nav className="flex justify-between items-center mb-12 border-b border-slate-800 pb-6">
                <div className="flex items-center gap-3">
                    <div className="p-2 bg-cyan-500/10 rounded-lg">
                        <Zap className="text-cyan-400" size={24} />
                    </div>
                    <h1 className="text-xl font-bold tracking-tight">PROJECT <span className="text-cyan-400">HYPER</span> SaaS</h1>
                </div>
                <div className="flex gap-4">
                    <div className="flex items-center gap-2 px-3 py-1 bg-slate-800 rounded-full text-xs">
                        <Activity size={14} className="text-green-400" />
                        <span>99.9% Reliability</span>
                    </div>
                    <div className="flex items-center gap-2 px-3 py-1 bg-slate-800 rounded-full text-xs">
                        <Cpu size={14} className="text-cyan-400" />
                        <span>CPU Optimized</span>
                    </div>
                </div>
            </nav>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* LEFT: Capabilities & Controls */}
                <div className="lg:col-span-1 space-y-6">
                    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">
                        <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4 flex items-center gap-2">
                            <Layers size={16} /> Intelligent Routing
                        </h3>
                        <div className="space-y-3">
                            <div className="p-3 bg-slate-800/50 rounded-lg border border-slate-700">
                                <div className="text-sm font-medium">Mixture-of-Experts</div>
                                <div className="text-[10px] text-slate-500">Routing tasks to specialized CPU inference pools.</div>
                            </div>
                            <div className="p-3 bg-slate-800/50 rounded-lg border border-slate-700">
                                <div className="text-sm font-medium">Semantic Cache</div>
                                <div className="text-[10px] text-slate-500">Detecting query similarity to bypass inference.</div>
                            </div>
                            <div className="p-3 bg-slate-800/50 rounded-lg border border-slate-700">
                                <div className="text-sm font-medium">Predictive Sharding</div>
                                <div className="text-[10px] text-slate-500">Pre-calculating likely user trajectories.</div>
                            </div>
                        </div>
                    </div>

                    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">
                        <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4 flex items-center gap-2">
                            <Shield size={16} /> Reliability Deck
                        </h3>
                        <div className="flex justify-between items-center text-xs mb-2">
                            <span>Circuit Breaker</span>
                            <span className="text-green-400 font-mono">CLOSED</span>
                        </div>
                        <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                            <div className="bg-green-500 h-full w-full"></div>
                        </div>
                        <p className="text-[10px] text-slate-500 mt-2 italic">Automatically degrades to cached approximations if backend latency {">"} 2s.</p>
                    </div>
                </div>

                {/* MIDDLE: Primary Interface */}
                <div className="lg:col-span-2 space-y-8">
                    <div className="relative">
                        <input
                            className="w-full bg-slate-900 border border-slate-700 rounded-2xl py-5 px-6 focus:ring-2 focus:ring-cyan-500 outline-none text-lg transition-all"
                            placeholder="Inject query into SaaS pipeline..."
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && handleExecute()}
                        />
                        <button
                            className="absolute right-3 top-2.5 px-6 py-3 bg-cyan-600 hover:bg-cyan-500 text-white rounded-xl font-bold transition-colors flex items-center gap-2"
                            onClick={handleExecute}
                            disabled={loading}
                        >
                            {loading ? <RefreshCw className="animate-spin" size={18} /> : <Zap size={18} />}
                            ORCHESTRATE
                        </button>
                    </div>

                    {/* DYNAMIC RESULT */}
                    {result && (
                        <div className={`transition-all duration-500 transform ${optimisticMode ? 'scale-95 opacity-60' : 'scale-100 opacity-100'}`}>
                            <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-2xl">
                                <div className="bg-slate-800/50 px-6 py-3 flex justify-between items-center border-b border-slate-800">
                                    <div className="flex items-center gap-2 text-xs font-mono">
                                        <span className="text-slate-500">MODE:</span>
                                        <span className={optimisticMode ? "text-yellow-400 animate-pulse" : "text-cyan-400"}>{result.mode}</span>
                                    </div>
                                    <div className="flex items-center gap-2 text-xs font-mono">
                                        <span className="text-slate-500">EXPERT:</span>
                                        <span className="text-purple-400">{result.expert}</span>
                                    </div>
                                </div>
                                <div className="p-8">
                                    <div className="text-2xl font-light text-slate-100 leading-relaxed mb-6">
                                        {result.result}
                                    </div>
                                    <div className="grid grid-cols-3 gap-4">
                                        <div className="bg-slate-800/30 p-3 rounded-lg border border-slate-800">
                                            <div className="text-[10px] text-slate-500 uppercase font-bold mb-1">Compute Avoided</div>
                                            <div className="text-lg font-mono text-cyan-400">{result.compute_cost_avoided ? 'YES' : 'NO'}</div>
                                        </div>
                                        <div className="bg-slate-800/30 p-3 rounded-lg border border-slate-800">
                                            <div className="text-[10px] text-slate-500 uppercase font-bold mb-1">Latency</div>
                                            <div className="text-lg font-mono text-cyan-400">{result.latency_ms}ms</div>
                                        </div>
                                        <div className="bg-slate-800/30 p-3 rounded-lg border border-slate-800">
                                            <div className="text-[10px] text-slate-500 uppercase font-bold mb-1">Reliability Score</div>
                                            <div className="text-lg font-mono text-cyan-400">1.0</div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* HISTORY / STREAMING MOCK */}
                    <div className="space-y-4">
                        <h4 className="text-xs font-bold text-slate-500 uppercase tracking-widest px-2 flex items-center gap-2">
                            <Maximize size={12} /> Recent Pipeline Outcomes
                        </h4>
                        <div className="space-y-2">
                            {history.map((h, i) => (
                                <div key={i} className="bg-slate-900/40 border border-slate-800/60 rounded-lg p-3 flex justify-between items-center text-xs">
                                    <div className="flex items-center gap-3">
                                        <span className="text-slate-600 font-mono">#{history.length - i}</span>
                                        <span className="text-slate-400 truncate max-w-[300px]">{h.result}</span>
                                    </div>
                                    <div className="flex gap-4 items-center">
                                        <span className="text-[10px] font-mono text-cyan-500/70">{h.mode}</span>
                                        <span className="text-slate-700 font-mono">{h.latency_ms}ms</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default App;
