import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { useToast } from '@/hooks/use-toast';
import {
  FileText, Shield, AlertOctagon, GitBranch, History, Send, Upload,
  Search, RefreshCw, Layers, CheckCircle2, ChevronRight, HelpCircle, ArrowRight,
  TrendingUp, Activity, Lock, Users, Info
} from 'lucide-react';
import { hyperClient } from '@/lib/api';

// ── Types ────────────────────────────────────────────────────────────────── //

interface PolicyDoc {
  id: string;
  label: string;
  type: string;
  metadata: {
    version: string;
    region: string;
    level: string;
  };
}

interface PolicyChunkNode {
  id: string;
  label: string;
  type: string;
  metadata: {
    header: string;
    content: string;
  };
}

interface RelationshipEdge {
  source: string;
  target: string;
  type: string;
  metadata: {
    confidence: number;
    rationale: string;
  };
}

interface ContradictionAlert {
  id: number;
  confidence: number;
  rationale: string;
  created_at: string;
  source: {
    filename: string;
    clause_number: string;
    content: string;
    region: string;
    level: string;
  };
  target: {
    filename: string;
    clause_number: string;
    content: string;
    region: string;
    level: string;
  };
}

interface AuditLog {
  id: number;
  action: string;
  details: string;
  actor: string;
  timestamp: string;
}

export default function LeoOrchestrationMaster() {
  const { toast } = useToast();
  const [activeTab, setActiveTab] = useState<'contradictions' | 'ingestion' | 'graph' | 'lineage' | 'audit'>('contradictions');
  
  // States
  const [loading, setLoading] = useState(false);
  const [contradictions, setContradictions] = useState<ContradictionAlert[]>([]);
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [graphData, setGraphData] = useState<{ nodes: any[]; edges: RelationshipEdge[] }>({ nodes: [], edges: [] });
  
  // Search state
  const [searchQuery, setSearchQuery] = useState('');
  
  // Upload States
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [level, setLevel] = useState('Global');
  const [department, setDepartment] = useState('General');
  const [region, setRegion] = useState('Global');
  const [version, setVersion] = useState('1.0');

  // Escalation States
  const [selectedConflict, setSelectedConflict] = useState<ContradictionAlert | null>(null);
  const [routeDept, setRouteDept] = useState('legal');
  const [routeSeverity, setRouteSeverity] = useState('high');
  const [routeRationale, setRouteRationale] = useState('');

  // ── Load Data ──────────────────────────────────────────────────────────── //
  
  const loadData = async () => {
    setLoading(true);
    try {
      const contrList = await hyperClient.getContradictions();
      setContradictions(contrList);
      
      const logs = await hyperClient.getAuditTimeline();
      setAuditLogs(logs);

      const graph = await hyperClient.getPolicyGraph();
      setGraphData(graph);
    } catch (e: any) {
      console.error("Failed to load governance dataset.", e);
      toast({
        title: "Database Sync Mismatch",
        description: "Verify that the FastAPI SQLite engine is running on port 8005.",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // ── File Upload Ingestion ─────────────────────────────────────────────── //
  
  const handleUpload = async () => {
    if (!selectedFile) return;
    setLoading(true);
    try {
      const res = await hyperClient.uploadPolicyDoc(selectedFile, level, department, region, version);
      toast({
        title: "Ingestion Succeeded",
        description: `Ingested ${selectedFile.name}. Extracted ${res.clauses_extracted} policy clauses.`,
      });
      setSelectedFile(null);
      loadData();
    } catch (e: any) {
      toast({
        title: "Deduplication Active",
        description: e.message || "An identical document content hash already exists in SQLite.",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  // ── Escalation Routing ────────────────────────────────────────────────── //
  
  const handleRoute = async () => {
    if (!selectedConflict) return;
    try {
      const res = await hyperClient.routeContradictionAlert(routeDept, routeSeverity, routeRationale || selectedConflict.rationale);
      toast({
        title: "Escalation Successful",
        description: `Alert routed to ${res.authority_target}. Immutable trail logged.`,
      });
      setSelectedConflict(null);
      setRouteRationale('');
      loadData();
    } catch (e: any) {
      toast({
        title: "Routing Failure",
        description: e.message,
        variant: "destructive"
      });
    }
  };

  // ── Helpers ────────────────────────────────────────────────────────────── //
  
  const getSeverityBadge = (conf: number) => {
    if (conf >= 0.9) return <Badge className="bg-red-500/20 text-red-400 border-red-500/30">CRITICAL</Badge>;
    if (conf >= 0.8) return <Badge className="bg-orange-500/20 text-orange-400 border-orange-500/30">HIGH</Badge>;
    return <Badge className="bg-yellow-500/20 text-yellow-400 border-yellow-500/30">WARNING</Badge>;
  };

  // Filter contradictions
  const filteredContradictions = contradictions.filter(c => {
    const q = searchQuery.toLowerCase();
    return (
      c.source.filename.toLowerCase().includes(q) ||
      c.target.filename.toLowerCase().includes(q) ||
      c.source.content.toLowerCase().includes(q) ||
      c.target.content.toLowerCase().includes(q) ||
      c.rationale.toLowerCase().includes(q)
    );
  });

  return (
    <div className="min-h-screen bg-background p-6 space-y-6 max-w-[1700px] mx-auto text-foreground">
      
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-border pb-6">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-primary/10 border border-primary/20 text-primary shadow-[0_0_15px_rgba(var(--primary),0.2)]">
              <Shield className="w-7 h-7" />
            </div>
            <div>
              <h1 className="text-2xl font-black tracking-tight flex items-center gap-2">
                Enterprise Policy Relationship Intelligence System
                <Badge variant="outline" className="text-[10px] border-primary/30 text-primary font-mono font-bold">
                  CODENAME: SEMANTIC AUDIT MEMORY
                </Badge>
              </h1>
              <p className="text-xs text-muted-foreground mt-0.5">
                Deterministic governance analysis tool · Policy override & scope validation · Immutable provenance trace memory
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={loadData} disabled={loading} className="gap-2 h-9 border-primary/20">
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            Sync System Logs
          </Button>
        </div>
      </div>

      {/* Main Grid Section */}
      <div className="grid grid-cols-1 xl:grid-cols-4 gap-6">

        {/* Sidebar Nav */}
        <div className="xl:col-span-1 flex flex-col gap-4">
          <Card className="border-primary/10 bg-card/60 backdrop-blur-sm">
            <CardHeader className="py-4">
              <CardTitle className="text-xs font-bold uppercase tracking-wider text-muted-foreground">Governance Navigator</CardTitle>
            </CardHeader>
            <CardContent className="p-2 space-y-1">
              {[
                { id: 'contradictions', label: 'Contradiction Alerts', icon: AlertOctagon, count: contradictions.length },
                { id: 'ingestion', label: 'Document Ingestion', icon: Upload },
                { id: 'graph', label: 'Governance Topology Map', icon: GitBranch, count: graphData.edges.length },
                { id: 'lineage', label: 'Lineage & Override Explorer', icon: Layers },
                { id: 'audit', label: 'Audit Provenance Ledger', icon: History, count: auditLogs.length },
              ].map(tab => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-semibold transition-all ${
                    activeTab === tab.id
                      ? 'bg-primary/10 text-primary border border-primary/20 shadow-[0_0_10px_rgba(var(--primary),0.1)]'
                      : 'text-muted-foreground hover:bg-muted/50 border border-transparent'
                  }`}
                >
                  <span className="flex items-center gap-2.5">
                    <tab.icon className="w-4 h-4" />
                    {tab.label}
                  </span>
                  {tab.count !== undefined && (
                    <Badge variant="secondary" className="text-[9px] px-1.5 bg-black/40">
                      {tab.count}
                    </Badge>
                  )}
                </button>
              ))}
            </CardContent>
          </Card>

          {/* Quick Metrics KPI Panel */}
          <Card className="border-primary/10 bg-card/50">
            <CardHeader className="py-4">
              <CardTitle className="text-xs font-bold uppercase tracking-wider text-muted-foreground">Severity & Efficiency metrics</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 pt-1">
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="bg-black/30 p-2.5 rounded border border-white/5">
                  <span className="text-[10px] text-muted-foreground block">Active Conflicts</span>
                  <span className="text-lg font-bold text-red-400">{contradictions.length}</span>
                </div>
                <div className="bg-black/30 p-2.5 rounded border border-white/5">
                  <span className="text-[10px] text-muted-foreground block">Audit Lineage Trails</span>
                  <span className="text-lg font-bold text-primary">{auditLogs.length}</span>
                </div>
              </div>
              <div className="text-[10px] text-muted-foreground flex items-center gap-1.5 bg-primary/5 p-2.5 rounded border border-primary/10">
                <Lock className="w-3.5 h-3.5 text-primary shrink-0" />
                <span>Running fully local inside enterprise firewall (CPU-Only Mode).</span>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Content Area */}
        <div className="xl:col-span-3 flex flex-col gap-4">

          {/* Tab 1: Contradictions Matrix */}
          {activeTab === 'contradictions' && (
            <Card className="border-primary/15 flex-1 flex flex-col min-h-[500px]">
              <CardHeader className="border-b border-primary/10 py-4 flex flex-row items-center justify-between gap-4 flex-wrap">
                <div>
                  <CardTitle className="text-base flex items-center gap-2">
                    <AlertOctagon className="w-5 h-5 text-red-400" />
                    Contradiction Resolution Dashboard
                  </CardTitle>
                  <CardDescription className="text-xs">
                    Deterministic logic override detection mapping conflicting operational clauses
                  </CardDescription>
                </div>
                <div className="relative w-full sm:w-64">
                  <Search className="w-3.5 h-3.5 text-muted-foreground absolute left-3 top-3" />
                  <Input
                    placeholder="Search query context..."
                    className="h-8 pl-8 text-xs bg-background/50 border-primary/20"
                    value={searchQuery}
                    onChange={e => setSearchQuery(e.target.value)}
                  />
                </div>
              </CardHeader>
              <CardContent className="p-0 flex-1 overflow-hidden">
                <ScrollArea className="h-[600px] p-4">
                  {filteredContradictions.length === 0 ? (
                    <div className="h-full flex flex-col items-center justify-center text-muted-foreground/30 py-20 space-y-3">
                      <CheckCircle2 className="w-12 h-12 text-emerald-400/50" />
                      <p className="text-sm">Zero Active Contradictions Found in local governance graph.</p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {filteredContradictions.map(alert => (
                        <div key={alert.id} className="p-4 bg-black/40 rounded-xl border border-white/5 space-y-3.5">
                          <div className="flex items-center justify-between gap-3 flex-wrap">
                            <div className="flex items-center gap-2">
                              {getSeverityBadge(alert.confidence)}
                              <span className="text-[10px] text-muted-foreground font-mono">Confidence: {Math.round(alert.confidence*100)}%</span>
                            </div>
                            <Button 
                              size="sm" 
                              variant="outline" 
                              className="h-7 text-[10px] border-primary/20 text-primary hover:bg-primary/10"
                              onClick={() => setSelectedConflict(alert)}
                            >
                              Escalate / Route Action
                            </Button>
                          </div>

                          {/* Side by side comparison */}
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="p-3 bg-white/[0.02] rounded border border-white/5 space-y-1.5">
                              <div className="flex items-center justify-between text-[9px] uppercase tracking-wider text-muted-foreground font-mono">
                                <span>Source Clause {alert.source.clause_number}</span>
                                <span className="bg-black/50 px-1.5 rounded">{alert.source.level}</span>
                              </div>
                              <p className="text-xs font-bold text-primary truncate mb-1">{alert.source.filename}</p>
                              <p className="text-xs text-foreground/80 leading-relaxed italic">"{alert.source.content}"</p>
                              <div className="text-[8px] text-muted-foreground font-mono">Region: {alert.source.region}</div>
                            </div>
                            <div className="p-3 bg-white/[0.02] rounded border border-white/5 space-y-1.5">
                              <div className="flex items-center justify-between text-[9px] uppercase tracking-wider text-muted-foreground font-mono">
                                <span>Conflict Clause {alert.target.clause_number}</span>
                                <span className="bg-black/50 px-1.5 rounded">{alert.target.level}</span>
                              </div>
                              <p className="text-xs font-bold text-primary truncate mb-1">{alert.target.filename}</p>
                              <p className="text-xs text-foreground/80 leading-relaxed italic">"{alert.target.content}"</p>
                              <div className="text-[8px] text-muted-foreground font-mono">Region: {alert.target.region}</div>
                            </div>
                          </div>

                          {/* Explainability explanation */}
                          <div className="bg-red-500/5 p-3 rounded border border-red-500/10 flex items-start gap-2.5">
                            <Info className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
                            <div>
                              <p className="text-[10px] font-bold text-red-400 uppercase tracking-wide">Explainable Contradiction Rationale</p>
                              <p className="text-xs text-foreground/90 mt-0.5 leading-relaxed">{alert.rationale}</p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </ScrollArea>
              </CardContent>
            </Card>
          )}

          {/* Tab 2: Ingestion Queue Panel */}
          {activeTab === 'ingestion' && (
            <Card className="border-primary/15 flex-1 min-h-[500px]">
              <CardHeader className="border-b border-primary/10 py-4">
                <CardTitle className="text-base flex items-center gap-2">
                  <Upload className="w-5 h-5 text-primary" />
                  Policy Ingestion Queue
                </CardTitle>
                <CardDescription className="text-xs">
                  Upload PDF, DOCX, TXT compliance logs to analyze relationships asynchronously
                </CardDescription>
              </CardHeader>
              <CardContent className="p-6 space-y-6">
                <div className="border-2 border-dashed border-primary/20 rounded-xl p-8 flex flex-col items-center justify-center space-y-3 bg-black/20">
                  <FileText className="w-10 h-10 text-primary/60" />
                  <div className="text-center">
                    <p className="text-xs font-semibold text-foreground/80">Drag and drop policy document</p>
                    <p className="text-[10px] text-muted-foreground mt-0.5">Supports PDF, DOCX, TXT, HTML (Deduplication enabled)</p>
                  </div>
                  <input
                    type="file"
                    id="file-upload"
                    className="hidden"
                    onChange={e => setSelectedFile(e.target.files ? e.target.files[0] : null)}
                  />
                  <Button asChild size="sm" className="h-8 text-xs">
                    <label htmlFor="file-upload" className="cursor-pointer">
                      Select File
                    </label>
                  </Button>
                  {selectedFile && (
                    <Badge variant="outline" className="text-xs border-primary/40 text-primary mt-2">
                      {selectedFile.name} ({(selectedFile.size / 1024).toFixed(1)} KB)
                    </Badge>
                  )}
                </div>

                {/* Document Metadata Form */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div>
                    <label className="text-[10px] uppercase text-muted-foreground font-mono block mb-1">Authority Level</label>
                    <Select value={level} onValueChange={setLevel}>
                      <SelectTrigger className="text-xs h-9 bg-background/50 border-primary/20">
                        <SelectValue placeholder="Select level" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Global">Global Policy</SelectItem>
                        <SelectItem value="Regional">Regional Directive</SelectItem>
                        <SelectItem value="Departmental">Departmental SOP</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <label className="text-[10px] uppercase text-muted-foreground font-mono block mb-1">Target Department</label>
                    <Select value={department} onValueChange={setDepartment}>
                      <SelectTrigger className="text-xs h-9 bg-background/50 border-primary/20">
                        <SelectValue placeholder="Select dept" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="General">General / All</SelectItem>
                        <SelectItem value="HR">HR Policies</SelectItem>
                        <SelectItem value="Legal">Legal & Compliance</SelectItem>
                        <SelectItem value="Security">InfoSec & IT</SelectItem>
                        <SelectItem value="Finance">Finance Audit</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <label className="text-[10px] uppercase text-muted-foreground font-mono block mb-1">Region Scope</label>
                    <Input 
                      className="text-xs h-9 bg-background/50 border-primary/20"
                      value={region} 
                      onChange={e => setRegion(e.target.value)} 
                    />
                  </div>
                  <div>
                    <label className="text-[10px] uppercase text-muted-foreground font-mono block mb-1">Version ID</label>
                    <Input 
                      className="text-xs h-9 bg-background/50 border-primary/20"
                      value={version} 
                      onChange={e => setVersion(e.target.value)} 
                    />
                  </div>
                </div>

                <Button 
                  onClick={handleUpload} 
                  disabled={loading || !selectedFile}
                  className="w-full h-11 bg-primary text-primary-foreground font-bold hover:opacity-90 transition-all shadow-[0_0_15px_rgba(var(--primary),0.2)]"
                >
                  {loading ? 'Executing Ingestion Cascade...' : 'PROCESS COMPLIANCE INGESTION'}
                </Button>
              </CardContent>
            </Card>
          )}

          {/* Tab 3: Governance Graph Map */}
          {activeTab === 'graph' && (
            <Card className="border-primary/15 flex-1 min-h-[500px] flex flex-col">
              <CardHeader className="border-b border-primary/10 py-4">
                <CardTitle className="text-base flex items-center gap-2">
                  <GitBranch className="w-5 h-5 text-primary" />
                  Semantic Governance Map
                </CardTitle>
                <CardDescription className="text-xs">
                  Relational mapping showing contains dependencies, references, and logic conflicts
                </CardDescription>
              </CardHeader>
              <CardContent className="p-4 flex-1">
                <ScrollArea className="h-[550px]">
                  <div className="space-y-4">
                    {/* Node / Edge breakdown as an interactive hierarchy tree list */}
                    <div className="bg-black/30 p-3 rounded-lg border border-white/5">
                      <p className="text-[10px] font-mono uppercase text-muted-foreground mb-3">Graph Hierarchy traversal</p>
                      {graphData.nodes.filter(n => n.type === 'document').map(doc => {
                        const childClauses = graphData.nodes.filter(n => 
                          n.type === 'clause' && 
                          graphData.edges.some(e => e.source === doc.id && e.target === n.id)
                        );
                        
                        return (
                          <div key={doc.id} className="mb-4 border-b border-white/5 pb-3 last:border-0 last:pb-0">
                            <div className="flex items-center gap-2 mb-2">
                              <FileText className="w-4 h-4 text-primary" />
                              <span className="text-xs font-bold text-foreground">{doc.label}</span>
                              <Badge className="text-[8px] bg-primary/10 text-primary border-primary/20">
                                {doc.metadata.level} / {doc.metadata.region}
                              </Badge>
                            </div>
                            
                            <div className="pl-6 space-y-1.5">
                              {childClauses.map(clause => {
                                // Find conflicts involving this clause
                                const conflicts = graphData.edges.filter(e => 
                                  e.type === 'CONTRADICTS' && 
                                  (e.source === clause.id || e.target === clause.id)
                                );

                                return (
                                  <div key={clause.id} className="p-2 bg-white/[0.01] hover:bg-white/[0.03] rounded border border-white/5 flex items-center justify-between text-xs transition-colors">
                                    <div>
                                      <span className="font-mono text-primary mr-2 font-bold">{clause.label}</span>
                                      <span className="text-muted-foreground text-[10px]">{clause.metadata.header}</span>
                                    </div>
                                    <div className="flex items-center gap-1.5">
                                      {conflicts.map((conf, ci) => (
                                        <Badge key={ci} className="bg-red-500/10 text-red-400 border-red-500/20 text-[8px] flex items-center gap-1">
                                          <AlertOctagon className="w-2.5 h-2.5" />
                                          Conflict ({conf.type})
                                        </Badge>
                                      ))}
                                    </div>
                                  </div>
                                );
                              })}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>
          )}

          {/* Tab 4: Lineage & Overrides */}
          {activeTab === 'lineage' && (
            <Card className="border-primary/15 flex-1 min-h-[500px]">
              <CardHeader className="border-b border-primary/10 py-4">
                <CardTitle className="text-base flex items-center gap-2">
                  <Layers className="w-5 h-5 text-primary" />
                  Lineage & Scope Override Explorer
                </CardTitle>
                <CardDescription className="text-xs">
                  Analysis of version updates and regional exception overrides
                </CardDescription>
              </CardHeader>
              <CardContent className="p-4">
                <ScrollArea className="h-[550px]">
                  <div className="space-y-3">
                    {graphData.edges
                      .filter(e => ['SUPERSEDES', 'REGION_EXCEPTION', 'DEPENDS_ON'].includes(e.type))
                      .map((edge, idx) => {
                        const srcNode = graphData.nodes.find(n => n.id === edge.source);
                        const tgtNode = graphData.nodes.find(n => n.id === edge.target);

                        return (
                          <div key={idx} className="p-3 bg-black/40 rounded-lg border border-white/5 flex items-center justify-between gap-4">
                            <div className="flex items-center gap-3 w-5/12">
                              <FileText className="w-4 h-4 text-muted-foreground shrink-0" />
                              <span className="text-xs truncate font-semibold">{srcNode ? srcNode.label : edge.source}</span>
                            </div>
                            <div className="flex flex-col items-center shrink-0 w-2/12">
                              <Badge variant="outline" className="text-[8px] uppercase tracking-wider font-mono">
                                {edge.type}
                              </Badge>
                              <ArrowRight className="w-3.5 h-3.5 text-muted-foreground mt-1" />
                            </div>
                            <div className="flex items-center gap-3 w-5/12 justify-end text-right">
                              <span className="text-xs truncate font-semibold">{tgtNode ? tgtNode.label : edge.target}</span>
                              <FileText className="w-4 h-4 text-primary shrink-0" />
                            </div>
                          </div>
                        );
                      })}
                    {graphData.edges.filter(e => ['SUPERSEDES', 'REGION_EXCEPTION', 'DEPENDS_ON'].includes(e.type)).length === 0 && (
                      <div className="py-20 text-center text-muted-foreground/30">
                        <Layers className="w-10 h-10 mx-auto mb-2" />
                        <p className="text-xs">No scope overrides or supersedes relationships mapped yet.</p>
                      </div>
                    )}
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>
          )}

          {/* Tab 5: Audit Ledger */}
          {activeTab === 'audit' && (
            <Card className="border-primary/15 flex-1 min-h-[500px]">
              <CardHeader className="border-b border-primary/10 py-4">
                <CardTitle className="text-base flex items-center gap-2">
                  <History className="w-5 h-5 text-primary" />
                  Audit Provenance Ledger
                </CardTitle>
                <CardDescription className="text-xs">
                  Immutable trace recording policy ingestion, override routes, and resolution events
                </CardDescription>
              </CardHeader>
              <CardContent className="p-0">
                <ScrollArea className="h-[600px] p-4">
                  <div className="space-y-4">
                    {auditLogs.map((log, idx) => (
                      <div key={log.id} className="relative pl-6 border-l-2 border-primary/20 pb-4 last:pb-0">
                        <div className="absolute -left-[6px] top-1.5 w-2.5 h-2.5 rounded-full bg-primary shadow-[0_0_8px_rgba(var(--primary),0.5)]" />
                        <div className="flex items-center justify-between gap-3 flex-wrap mb-1 text-[10px] text-muted-foreground font-mono">
                          <span>{new Date(log.timestamp).toLocaleString()}</span>
                          <span className="bg-white/5 px-2 py-0.5 rounded text-primary">{log.actor}</span>
                        </div>
                        <p className="text-xs font-bold text-foreground mb-1">Governance Action: {log.action}</p>
                        <p className="text-xs text-muted-foreground leading-relaxed">{log.details}</p>
                      </div>
                    ))}
                    {auditLogs.length === 0 && (
                      <div className="py-20 text-center text-muted-foreground/30">
                        <History className="w-10 h-10 mx-auto mb-2" />
                        <p className="text-xs">Audit ledger currently empty. Ingest documents to populate logs.</p>
                      </div>
                    )}
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>
          )}

        </div>
      </div>

      {/* Escalation routing modal popup */}
      {selectedConflict && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <Card className="border-primary/20 bg-background max-w-lg w-full">
            <CardHeader className="border-b border-white/5 py-4">
              <CardTitle className="text-base flex items-center gap-2">
                <Shield className="w-5 h-5 text-primary" />
                Escalate Conflict Alert
              </CardTitle>
              <CardDescription className="text-xs">
                Route contradiction to the correct organizational authority
              </CardDescription>
            </CardHeader>
            <CardContent className="p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-[10px] uppercase text-muted-foreground font-mono block mb-1">Target Department</label>
                  <Select value={routeDept} onValueChange={setRouteDept}>
                    <SelectTrigger className="text-xs h-9 bg-background border-primary/20">
                      <SelectValue placeholder="Select dept" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="hr">HR Governance</SelectItem>
                      <SelectItem value="legal">Legal Counsel</SelectItem>
                      <SelectItem value="security">InfoSec Security</SelectItem>
                      <SelectItem value="finance">Finance Controllers</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <label className="text-[10px] uppercase text-muted-foreground font-mono block mb-1">Priority Severity</label>
                  <Select value={routeSeverity} onValueChange={setRouteSeverity}>
                    <SelectTrigger className="text-xs h-9 bg-background border-primary/20">
                      <SelectValue placeholder="Select priority" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="critical">Critical Impact</SelectItem>
                      <SelectItem value="high">High priority</SelectItem>
                      <SelectItem value="medium">Medium Priority</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div>
                <label className="text-[10px] uppercase text-muted-foreground font-mono block mb-1">Conflict Escalation Rationale</label>
                <Textarea 
                  placeholder={selectedConflict.rationale}
                  className="text-xs bg-background border-primary/20 min-h-[100px]"
                  value={routeRationale}
                  onChange={e => setRouteRationale(e.target.value)}
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-2">
                <Button size="sm" variant="ghost" onClick={() => setSelectedConflict(null)}>
                  Cancel
                </Button>
                <Button size="sm" onClick={handleRoute} className="bg-primary text-primary-foreground font-bold">
                  Escalate Conflict
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

    </div>
  );
}
