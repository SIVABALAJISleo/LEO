import { useState, useEffect } from 'react';
import axios from 'axios';
import { Shield, Zap, Search, Activity, Cpu, Database, RefreshCw } from 'lucide-react';

interface Metrics {
    total_requests: number;
    compute_avoidance_rate: number;
    cache_hits: number;
    retrieval_usage: number;
    prediction_usage: number;
    avg_latency_ms: number;
}

function App() {
    const [query, setQuery] = useState('');
    const [result, setResult] = useState<any>(null);
    const [metrics, setMetrics] = useState<Metrics | null>(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        fetchMetrics();
        const interval = setInterval(fetchMetrics, 5000);
        return () => clearInterval(interval);
    }, []);

    const fetchMetrics = async () => {
        try {
            const resp = await axios.get('/api/v1/metrics');
            setMetrics(resp.data);
        } catch (e) {
            console.error("Failed to fetch metrics", e);
        }
    };

    const handleOrchestrate = async () => {
        if (!query) return;
        setLoading(true);
        try {
            const resp = await axios.post('/api/v1/orchestrate', { query });
            setResult(resp.data);
            fetchMetrics();
        } catch (e) {
            console.error("Orchestration failed", e);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ textAlign: 'left' }}>
            <header style={{ marginBottom: '40px' }}>
                <h1 style={{ color: '#38bdf8', marginBottom: '8px' }}>Project Alpha: Compute-Avoidance Intelligence</h1>
                <p style={{ color: '#94a3b8' }}>Orchestrating outcomes through retrieval, prediction, and reasoning.</p>
            </header>

            {/* MONITORING DASHBOARD */}
            <div className="metrics-grid">
                <div className="metric-card">
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                        <span className="badge">Compute Avoided</span>
                        <Zap size={16} color="#38bdf8" />
                    </div>
                    <div style={{ fontSize: '24px', fontWeight: 'bold' }}>{metrics?.compute_avoidance_rate || 0}%</div>
                    <div style={{ fontSize: '12px', color: '#64748b' }}>Efficiency Rate</div>
                </div>
                <div className="metric-card">
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                        <span className="badge" style={{ background: '#4ade80', color: '#064e3b' }}>Latency</span>
                        <Activity size={16} color="#4ade80" />
                    </div>
                    <div style={{ fontSize: '24px', fontWeight: 'bold' }}>{metrics?.avg_latency_ms || 0}ms</div>
                    <div style={{ fontSize: '12px', color: '#64748b' }}>Avg Processing Time</div>
                </div>
                <div className="metric-card">
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                        <span className="badge" style={{ background: '#f472b6', color: '#500724' }}>Sources</span>
                        <Database size={16} color="#f472b6" />
                    </div>
                    <div style={{ fontSize: '24px', fontWeight: 'bold' }}>{metrics?.retrieval_usage || 0}</div>
                    <div style={{ fontSize: '12px', color: '#64748b' }}>Retrieval Hits</div>
                </div>
            </div>

            {/* QUERY INTERFACE */}
            <div className="card">
                <h3 style={{ marginTop: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Search size={20} /> Capability Router
                </h3>
                <input
                    placeholder="Ask a question, propose a hypothesis, or request a perceptual rendering..."
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleOrchestrate()}
                />
                <button onClick={handleOrchestrate} disabled={loading}>
                    {loading ? 'Processing...' : 'Execute Workflow'}
                </button>
            </div>

            {/* RESULT PANEL */}
            {result && (
                <div className="card" style={{ borderLeft: '4px solid #38bdf8' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '16px' }}>
                        <h4 style={{ margin: 0 }}>System Outcome</h4>
                        <span className="badge" style={{ background: result.heavy_computation_avoided ? '#38bdf8' : '#64748b' }}>
                            {result.heavy_computation_avoided ? 'COMPUTE AVOIDED' : 'FULL CALC'}
                        </span>
                    </div>

                    <div style={{ marginBottom: '20px', fontSize: '18px' }}>{result.answer}</div>

                    <div style={{ background: '#0f172a', padding: '16px', borderRadius: '4px', border: '1px solid #334155' }}>
                        <div style={{ fontSize: '12px', color: '#64748b', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '1px' }}>Reasoning Trace</div>
                        <div style={{ fontSize: '14px', color: '#cbd5e1' }}>{result.reasoning}</div>
                    </div>

                    <div style={{ marginTop: '16px', display: 'flex', gap: '24px' }}>
                        <div>
                            <div style={{ fontSize: '10px', color: '#64748b', textTransform: 'uppercase' }}>Confidence</div>
                            <div style={{ fontSize: '14px' }}>{(result.confidence_score * 100).toFixed(1)}%</div>
                        </div>
                        <div>
                            <div style={{ fontSize: '10px', color: '#64748b', textTransform: 'uppercase' }}>Sources</div>
                            <div style={{ fontSize: '14px' }}>{result.data_sources.length > 0 ? result.data_sources.join(', ') : 'Synthetic'}</div>
                        </div>
                        <div>
                            <div style={{ fontSize: '10px', color: '#64748b', textTransform: 'uppercase' }}>Internal Latency</div>
                            <div style={{ fontSize: '14px' }}>{result.latency_ms}ms</div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default App;
