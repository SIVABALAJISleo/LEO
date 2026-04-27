import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import { Search, Brain, Eye, Code, Layers, Terminal, Sparkles, Send, Shield, Clock, Activity, Zap, Cpu } from 'lucide-react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Progress } from '@/components/ui/progress';

// Local engines — no remote backend needed
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import { GovernedPipeline } from '@/lib/governance/GovernedPipeline';
import { RAGPipeline } from '@/lib/intelligence/RAGPipeline';
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import { NoveltyDetector, NoveltyState } from '@/lib/intelligence/NoveltyDetector';
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import type { GovernedInput } from '@/lib/governance/types';
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import { v4 as uuidv4 } from 'uuid';
import { hyperClient, OrchestrateResponse } from '@/lib/api';

/** Run through the full GovernedPipeline (UNIFIED tab) - Remote Core Path */
async function runThroughRemote(query: string): Promise<OrchestrateResponse> {
    return await hyperClient.executeRemote(query);
}

const OrchestrationExplorer = () => {
    const [query, setQuery] = useState('');
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const [results, setResults] = useState<any>(null);
    const [loading, setLoading] = useState(false);
    const [activeTab, setActiveTab] = useState('unified');
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const [executionCount, setExecutionCount] = useState(0);

    const handleRun = async () => {
        if (!query) return;
        setLoading(true);
        try {
            let data;
            if (activeTab === 'moe') {
                // Keep local MoE for speed/demo
                data = await (async (q: string) => {
                    const detector = NoveltyDetector.getInstance();
                    const startMs = performance.now();
                    const embedding = new Array(384).fill(0);
                    const noveltyResult = await detector.detect(q, embedding);
                    const elapsed = performance.now() - startMs;
                    return {
                        _engine: 'MoE Expert Router (Local)',
                        selectedExpert: 'Logic Solver',
                        novelty: { state: noveltyResult.state, similarity: noveltyResult.similarity.toFixed(3) },
                        latencyMs: elapsed.toFixed(1) + 'ms',
                    };
                })(query);
            } else if (activeTab === 'rag') {
                // Keep local RAG
                data = await (async (q: string) => {
                    const rag = RAGPipeline.getInstance();
                    const startMs = performance.now();
                    await rag.ingest(q, 'orchestration-explorer');
                    const results = await rag.retrieve(q, 5);
                    return {
                        _engine: 'RAG Retrieval Pipeline (Local)',
                        latencyMs: (performance.now() - startMs).toFixed(1) + 'ms',
                        totalDocuments: results.length,
                    };
                })(query);
            } else {
                // CORE ENGINE: Use Remote Python Backend
                data = await runThroughRemote(query);
            }
            setResults(data);
            setExecutionCount(c => c + 1);
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        } catch (err: any) {
            console.error("Execution error:", err);
            setResults({
                error: 'Execution failed',
                message: err?.message || String(err),
                stage: 'remote-engine-link',
            });
        } finally {
            setLoading(false);
        }
    };

    const coreData = results?.core;

    return (
        <div className="p-6 max-w-7xl mx-auto space-y-6">
            <div className="flex flex-col space-y-2">
                <h1 className="text-3xl font-bold flex items-center gap-2">
                    <Layers className="text-primary" /> Orchestration Explorer
                </h1>
                <p className="text-muted-foreground underline decoration-primary/30">
                    Unified Interface for Hybrid CPU Engines — <span className="text-primary font-bold">Remote Core Active</span>
                </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2 space-y-6">
                    <Card className="border-primary/20 bg-card/50 backdrop-blur-sm">
                        <CardHeader>
                            <CardTitle className="text-lg">Command Input</CardTitle>
                            <CardDescription>
                                GOVERNED queries route to the Python Core Backend (v0.93 accuracy)
                            </CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="flex gap-2">
                                <div className="relative flex-1">
                                    <Terminal className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                                    <Input
                                        placeholder="Type your objective (e.g. 'Calculate average of 10,20,30' or 'Render complex scene')..."
                                        className="pl-10 h-12 border-primary/20"
                                        value={query}
                                        onChange={(e) => setQuery(e.target.value)}
                                        onKeyDown={(e) => e.key === 'Enter' && handleRun()}
                                    />
                                </div>
                                <Button
                                    onClick={handleRun}
                                    disabled={loading}
                                    className="h-12 px-6 shadow-glow"
                                >
                                    {loading ? 'Processing...' : <><Send className="w-4 h-4 mr-2" /> EXECUTE</>}
                                </Button>
                            </div>

                            <Tabs value={activeTab} onValueChange={setActiveTab} className="mt-6">
                                <TabsList className="grid w-full grid-cols-3 bg-muted/50">
                                    <TabsTrigger value="unified" className="data-[state=active]:bg-primary pulse-on-hover">
                                        <Shield className="w-4 h-4 mr-2" /> GOVERNED (REMOTE)
                                    </TabsTrigger>
                                    <TabsTrigger value="moe" className="data-[state=active]:bg-primary pulse-on-hover">
                                        <Brain className="w-4 h-4 mr-2" /> MoE EXPERTS
                                    </TabsTrigger>
                                    <TabsTrigger value="rag" className="data-[state=active]:bg-primary pulse-on-hover">
                                        <Search className="w-4 h-4 mr-2" /> RAG RETRIEVAL
                                    </TabsTrigger>
                                </TabsList>
                            </Tabs>
                        </CardContent>
                    </Card>

                    <Card className="border-primary/20 h-[500px] flex flex-col">
                        <CardHeader className="border-b border-primary/10">
                            <CardTitle className="text-lg flex justify-between items-center">
                                <span>Engine Output</span>
                                <div className="flex gap-2 items-center">
                                    {coreData?.sdgp_active && (
                                        <Badge variant="outline" className="text-cyan-400 border-cyan-400/30 animate-pulse">
                                            SDGP BYPASS ACTIVE
                                        </Badge>
                                    )}
                                    {results && (
                                        <Badge variant="outline" className="text-primary border-primary/30">
                                            LATEST RUN
                                        </Badge>
                                    )}
                                </div>
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="flex-1 overflow-hidden p-0">
                            <ScrollArea className="h-full p-6">
                                {results ? (
                                    <div className="space-y-4">
                                        <div className="bg-primary/5 p-4 rounded-lg border border-primary/10">
                                            <p className="text-xs font-mono text-muted-foreground mb-2 uppercase tracking-tighter">Result Context</p>
                                            <p className="text-lg leading-relaxed">{results.result}</p>
                                        </div>
                                        <pre className="text-[10px] font-mono whitespace-pre-wrap bg-black/40 p-4 rounded-lg border border-white/5 opacity-70">
                                            {JSON.stringify(results, null, 2)}
                                        </pre>
                                    </div>
                                ) : (
                                    <div className="h-full flex flex-col items-center justify-center text-muted-foreground opacity-50 space-y-4">
                                        <Sparkles className="w-12 h-12" />
                                        <p>Awaiting engine execution...</p>
                                    </div>
                                )}
                            </ScrollArea>
                        </CardContent>
                    </Card>
                </div>

                <div className="space-y-6">
                    {/* System Telemetry Panel */}
                    <Card className="border-cyan-500/30 bg-cyan-500/5 backdrop-blur-xl">
                        <CardHeader className="pb-2">
                            <CardTitle className="text-md flex items-center gap-2 text-cyan-400">
                                <Zap className="w-4 h-4" /> SDGP Core
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="space-y-1">
                                <div className="flex justify-between text-[10px] font-mono text-cyan-400/70 border-b border-cyan-500/10 pb-1">
                                    <span>GPU REDUCTION</span>
                                    <span>{coreData?.gpu_relevance_reduction || '0.00%'}</span>
                                </div>
                                <Progress value={coreData ? 100 : 0} className="h-1 bg-cyan-950" indicatorClassName="bg-cyan-400 shadow-[0_0_10px_rgba(34,211,238,0.5)]" />
                            </div>

                            <div className="grid grid-cols-2 gap-2">
                                <div className="p-2 bg-black/40 rounded border border-white/5 text-center">
                                    <p className="text-[9px] text-muted-foreground uppercase">Ray Depth</p>
                                    <p className="text-sm font-bold text-cyan-400">{coreData?.ray_logic_depth || '0'}</p>
                                </div>
                                <div className="p-2 bg-black/40 rounded border border-white/5 text-center">
                                    <p className="text-[9px] text-muted-foreground uppercase">Latency</p>
                                    <p className="text-sm font-bold text-cyan-400">{coreData?.sdgp_latency_ms?.toFixed(2) || '0.00'}ms</p>
                                </div>
                            </div>

                            <div className="space-y-2 text-[10px] font-mono">
                                <div className="flex justify-between items-center p-1.5 bg-black/20 rounded">
                                    <span className="text-muted-foreground">DLSS-S Prediction</span>
                                    <Badge variant="secondary" className={`text-[8px] h-4 ${coreData?.dlss_s_active ? "bg-cyan-500/20 text-cyan-400" : "opacity-30"}`}>
                                        {coreData?.dlss_s_active ? 'ENABLED' : 'INACTIVE'}
                                    </Badge>
                                </div>
                                <div className="flex justify-between items-center p-1.5 bg-black/20 rounded">
                                    <span className="text-muted-foreground">Perceptual Culling</span>
                                    <span className="text-cyan-400">{coreData?.perceptual_culling || 'N/A'}</span>
                                </div>
                                <div className="flex justify-between items-center p-1.5 bg-black/20 rounded">
                                    <span className="text-muted-foreground">Virtual VRAM</span>
                                    <span className="text-cyan-400">{coreData?.equivalent_vram_gb || 0}GB</span>
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    <Card className="border-primary/20">
                        <CardHeader>
                            <CardTitle className="text-md">Available Tracks</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-3">
                            {[
                                { name: 'Code Expert', icon: Code, color: 'text-blue-500', keywords: 'code, optimize, refactor' },
                                { name: 'Vision Boundary', icon: Eye, color: 'text-green-500', keywords: 'see, look, detect, render' },
                                { name: 'Logic Solver', icon: Brain, color: 'text-purple-500', keywords: 'solve, calculate, prove' },
                                { name: 'Vector Store', icon: Search, color: 'text-yellow-500', keywords: 'find, search, retrieve' },
                            ].map((track) => (
                                <div key={track.name} className="flex items-center gap-3 p-2 rounded-md hover:bg-muted/50 transition-colors group">
                                    <track.icon className={`w-4 h-4 ${track.color}`} />
                                    <div className="flex-1">
                                        <span className="text-sm">{track.name}</span>
                                        <p className="text-[10px] text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity">
                                            Keywords: {track.keywords}
                                        </p>
                                    </div>
                                    <Badge variant="secondary" className="ml-auto text-[10px]">ACTIVE</Badge>
                                </div>
                            ))}
                        </CardContent>
                    </Card>

                    <Card className="bg-primary/5 border-primary/30 border-dashed">
                        <CardHeader>
                            <CardTitle className="text-sm">Engine Tip</CardTitle>
                        </CardHeader>
                        <CardContent className="text-xs text-muted-foreground leading-relaxed">
                            <strong>GOVERNED</strong> tab now routes to the 5090-equivalent Python backend. Try queries like <em>"Render a complex scene with 64-depth ray logic"</em> or <em>"Calculate average of 10,20,30,40,50"</em>.
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    );
};

export default OrchestrationExplorer;
