import React, { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { 
  Cpu, LayoutDashboard, Zap, FileText, Activity, Settings, LogOut, Bell, User, 
  Layers, CheckCircle2, FolderOpen, RefreshCw, Search, SlidersHorizontal, 
  Trash2, Download, Globe, Database, Mail, HardDrive, Terminal,
  Sparkles, MessageSquare, CheckCircle, HelpCircle, ArrowRight, GitBranch, FlaskConical, Gauge, LineChart, Award, Scale, ShieldCheck, Sliders
} from "lucide-react";
import { Button } from "./ui/button";
import { Card, CardContent } from "./ui/card";

interface IntelliGPUDashboardProps {
  onSignOut: () => void;
  onNavigateToLegacy?: () => void;
  activeSection?: string;
  setActiveSection?: (section: any) => void;
  children?: React.ReactNode;
}

export const IntelliGPUDashboard: React.FC<IntelliGPUDashboardProps> = ({ 
  onSignOut, 
  onNavigateToLegacy,
  activeSection: propActiveSection,
  setActiveSection: propSetActiveSection,
  children
}) => {
  const [localActiveSection, setLocalActiveSection] = useState<"dashboard" | "inference" | "results" | "modules" | "monitoring" | "settings">("dashboard");
  const activeSection = propActiveSection || localActiveSection;
  const setActiveSection = (section: any) => {
    if (propSetActiveSection) {
      propSetActiveSection(section);
    } else {
      setLocalActiveSection(section);
    }
  };

  const navigate = useNavigate();
  const { tabId } = useParams<{ tabId: string }>();
  const activeTab = tabId || "v45singularity";
  const [isSelectorOpen, setIsSelectorOpen] = useState(false);

  const [activeSettingsTab, setActiveSettingsTab] = useState<"profile" | "api" | "notifications" | "advanced">("profile");
  const [fullName, setFullName] = useState("");
  const [company, setCompany] = useState("");
  const [activeTrend, setActiveTrend] = useState<"latency" | "throughput" | "cache">("latency");
  const [webhookUrl, setWebhookUrl] = useState("https://your-server.com/webhook");

  // Notifications Toggles
  const [emailNotif, setEmailNotif] = useState(true);
  const [jobCompletionAlert, setJobCompletionAlert] = useState(true);
  const [systemAlerts, setSystemAlerts] = useState(true);
  const [weeklySummary, setWeeklySummary] = useState(false);

  // API Keys state
  const [apiKeys, setApiKeys] = useState<Array<{ name: string; key: string; status: string; created: string; lastUsed: string }>>([]);

  const generateApiKey = () => {
    const key = `igpu_live_${Math.random().toString(36).substring(2, 10)}${Math.random().toString(36).substring(2, 10)}`;
    setApiKeys((prev) => [
      ...prev,
      {
        name: `Key ${prev.length + 1}`,
        key,
        status: "Active",
        created: "Dec 9, 2025",
        lastUsed: "Never",
      },
    ]);
  };

  // Modules Enabled/Disabled Toggles
  const [modulesState, setModulesState] = useState<Record<string, boolean>>({
    quantization: false,
    kernel: false,
    approx: false,
    compression: false,
    cache: false,
    parallel: false,
    distributed: false,
    serving: false,
    streaming: false,
    jit: false,
    memory: false,
    speculative: false,
    precision: false,
    graph: false,
    sparsity: false,
  });

  const toggleModule = (id: string) => {
    setModulesState((prev) => ({
      ...prev,
      [id]: !prev[id],
    }));
  };

  return (
    <div className="bg-[#020813] text-slate-100 min-h-screen flex">
      {/* Left Sidebar */}
      <aside className="w-64 bg-[#080f1d] border-r border-slate-800/80 flex flex-col justify-between flex-shrink-0">
        <div>
          {/* Logo */}
          <div className="h-16 flex items-center gap-2 px-6 border-b border-slate-800/80">
            <Cpu className="h-5 w-5 text-[#76B900]" />
            <span className="font-black text-white tracking-tight font-display text-sm uppercase">IntelliGPU</span>
          </div>

          {/* Nav Groupings */}
          <div className="px-4 py-6 space-y-6">
            <div>
              <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider px-3 mb-2">Main</div>
              <nav className="space-y-1">
                {[
                  { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
                  { id: "inference", label: "Inference", icon: Zap },
                  { id: "results", label: "Results", icon: FileText },
                  { id: "modules", label: "Modules", icon: Cpu },
                  { id: "monitoring", label: "Monitoring", icon: Activity },
                ].map((item) => {
                  const Icon = item.icon;
                  const active = activeSection === item.id;
                  return (
                    <button
                      key={item.id}
                      onClick={() => setActiveSection(item.id as any)}
                      className={`w-full flex items-center gap-3 px-3 py-2 rounded text-xs font-bold transition-all ${
                        active 
                          ? "bg-[#76B900]/10 text-[#76B900] border-l-2 border-[#76B900]" 
                          : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/20"
                      }`}
                    >
                      <Icon className="h-4 w-4" />
                      {item.label}
                    </button>
                  );
                })}
              </nav>
            </div>

            <div>
              <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider px-3 mb-2">Settings</div>
              <nav className="space-y-1">
                <button
                  onClick={() => setActiveSection("settings")}
                  className={`w-full flex items-center gap-3 px-3 py-2 rounded text-xs font-bold transition-all ${
                    activeSection === "settings"
                      ? "bg-[#76B900]/10 text-[#76B900] border-l-2 border-[#76B900]" 
                      : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/20"
                  }`}
                >
                  <Settings className="h-4 w-4" />
                  Settings
                </button>
              </nav>
            </div>

            {onNavigateToLegacy && (
              <div>
                <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider px-3 mb-2">Legacy</div>
                <nav className="space-y-1">
                  <button
                    onClick={onNavigateToLegacy}
                    className={`w-full flex items-center gap-3 px-3 py-2 rounded text-xs font-bold transition-all ${
                      activeSection === "legacy" || activeSection === "legacy_swarms"
                        ? "bg-[#76B900]/10 text-[#76B900] border-l-2 border-[#76B900]" 
                        : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/20 animate-pulse"
                    }`}
                  >
                    <Layers className="h-4 w-4" />
                    Legacy Swarms
                  </button>
                </nav>
              </div>
            )}
          </div>
        </div>

        {/* Sign Out Button */}
        <div className="p-4 border-t border-slate-800/80">
          <button
            onClick={onSignOut}
            className="w-full flex items-center gap-3 px-3 py-2 rounded text-xs font-bold text-slate-400 hover:text-slate-200 hover:bg-rose-950/20 transition-all"
          >
            <LogOut className="h-4 w-4" />
            Sign Out
          </button>
        </div>
      </aside>

      {/* Main Body */}
      <div className="flex-grow flex flex-col min-w-0">
        {/* Top Header */}
        <header className="h-16 border-b border-slate-800/80 flex items-center justify-between px-8 bg-[#030914]/90 backdrop-blur-sm z-10 flex-shrink-0">
          <div>
            <h2 className="text-xs font-bold text-slate-100">Welcome back, sivabalajipulavanur</h2>
            <p className="text-[9px] text-slate-500 font-semibold mt-0.5">Tuesday, December 9, 2025</p>
          </div>

          <div className="flex items-center gap-4">
            <Button variant="outline" className="border-slate-800 text-slate-300 text-xs px-4 py-2 bg-[#0b1329]/40">
              View Jobs
            </Button>
            <Button className="bg-[#76B900] hover:bg-[#659e00] text-black font-extrabold text-xs px-4 py-2 rounded">
              + New Job
            </Button>

            {/* Alerts Bell */}
            <div className="relative cursor-pointer hover:bg-slate-800/40 p-1.5 rounded">
              <Bell className="h-4.5 w-4.5 text-slate-400" />
              <span className="absolute top-1 right-1 h-2 w-2 rounded-full bg-rose-500 ring-2 ring-[#020813]" />
            </div>

            <div className="h-8 w-8 rounded-full bg-slate-800 flex items-center justify-center border border-slate-700/60 cursor-pointer">
              <User className="h-4 w-4 text-[#76B900]" />
            </div>
          </div>
        </header>

        {/* Sticky Sub-Header bar */}
        {(() => {
          const versionCategories = [
            {
              title: "Foundational Cognitive",
              items: [
                { id: "swarm", label: "Swarm Console", icon: Terminal },
                { id: "cognitive", label: "Cognitive Engine", icon: Cpu },
                { id: "v14super", label: "V14 Breakthrough", icon: Sparkles },
                { id: "v15substrate", label: "V15 Substrate", icon: Brain },
                { id: "v16substrate", label: "V16 Substrate", icon: Sparkles },
                { id: "v17dominance", label: "V17 Dominance", icon: Zap }
              ]
            },
            {
              title: "Validation & Stability",
              items: [
                { id: "v18validation", label: "V18 Validation", icon: Shield },
                { id: "failureHunting", label: "Failure Hunting", icon: Crosshair },
                { id: "v22quality", label: "V22 Quality", icon: FlaskConical },
                { id: "v23frontier", label: "V23 Frontier", icon: Gauge },
                { id: "v24convergence", label: "V24 Convergence", icon: LineChart }
              ]
            },
            {
              title: "Product Verification",
              items: [
                { id: "v25certification", label: "V25 Certification", icon: Award },
                { id: "v26reality", label: "V26 Reality Core", icon: Sparkles },
                { id: "v27certification", label: "V27 Scientific Proof", icon: Scale },
                { id: "v28validation", label: "V28 Validation Lab", icon: ShieldCheck },
                { id: "v29frontier", label: "V29 Frontier Core", icon: Cpu },
                { id: "v30frontier", label: "V30 Acceleration", icon: Cpu }
              ]
            },
            {
              title: "Compute Efficiency",
              items: [
                { id: "v31irrelevance", label: "V31 Compute Avoidance", icon: Gauge },
                { id: "v32ceiling", label: "V32 Eng Ceiling", icon: Cpu },
                { id: "v32reality", label: "V32 Reality Learning", icon: Gauge },
                { id: "v33compute", label: "V33 Irrelevance", icon: Gauge },
                { id: "v34compute", label: "V34 Irrelevance", icon: Cpu }
              ]
            },
            {
              title: "Convergence & Cockpits",
              items: [
                { id: "v35parity", label: "V35 Scoreboard", icon: Award },
                { id: "v36ceiling", label: "V36 Scoreboard", icon: Gauge },
                { id: "v37evolution", label: "V37 Cockpit", icon: Sparkles },
                { id: "v38architecture", label: "V38 Cockpit", icon: Sparkles },
                { id: "v40ultimate", label: "V40 Cockpit", icon: Sparkles },
                { id: "vinfinity", label: "v∞ Cockpit", icon: Zap },
                { id: "v42irrelevance", label: "V42 Cockpit", icon: Sparkles },
                { id: "v43omega", label: "V43 OMEGA", icon: Zap }
              ]
            },
            {
              title: "Quantum Frontier & Utils",
              items: [
                { id: "v45singularity", label: "V45 SINGULARITY", icon: Zap },
                { id: "debate", label: "Multi-Agent Debate", icon: MessageSquare },
                { id: "quality", label: "Verification & Quality", icon: Shield },
                { id: "benchmarks", label: "Benchmarks", icon: BarChart2 },
                { id: "devops", label: "DevOps Stage", icon: Settings }
              ]
            }
          ];

          const activeTabItem = versionCategories
            .flatMap(cat => cat.items)
            .find(item => item.id === activeTab);
          const activeTabLabel = activeTabItem ? activeTabItem.label : "V45 SINGULARITY";

          return (
            <div className="relative border-b border-slate-800 bg-[#020813] py-3 px-8 flex items-center justify-between z-30">
              <div className="flex items-center gap-2 text-xs font-semibold text-slate-400">
                <Sliders className="h-4 w-4 text-[#76B900]" />
                <span>Active Substrate Mode:</span>
                <span className="text-[#76B900] font-extrabold uppercase tracking-wider bg-[#76B900]/10 px-2 py-0.5 rounded border border-[#76B900]/20">
                  {activeTabLabel}
                </span>
              </div>

              <div className="relative">
                <button
                  onClick={() => setIsSelectorOpen(!isSelectorOpen)}
                  className="flex items-center gap-2 border border-slate-800 bg-[#0b1329]/60 hover:bg-[#0b1329]/95 text-slate-200 text-xs px-4 py-2 rounded transition-all font-bold uppercase tracking-wider shadow-[0_0_10px_rgba(0,0,0,0.5)]"
                >
                  <span>Explore Substrates</span>
                  <span className={`text-[10px] transition-transform duration-200 ${isSelectorOpen ? 'rotate-180' : ''}`}>▼</span>
                </button>

                {isSelectorOpen && (
                  <>
                    <div className="fixed inset-0 z-40" onClick={() => setIsSelectorOpen(false)} />
                    <div className="absolute right-0 mt-2 bg-[#050e1f]/95 border border-slate-800 rounded-xl p-6 shadow-2xl z-50 grid grid-cols-2 md:grid-cols-3 gap-6 w-[760px] animate-in fade-in zoom-in-95 duration-200 backdrop-blur-md">
                      {versionCategories.map((category, catIdx) => (
                        <div key={catIdx} className="space-y-2.5">
                          <div className="text-[10px] font-black text-slate-500 uppercase tracking-widest border-b border-slate-800/80 pb-1.5 font-mono">
                            {category.title}
                          </div>
                          <div className="space-y-1">
                            {category.items.map((item) => {
                              const Icon = item.icon;
                              const active = activeTab === item.id;
                              return (
                                <button
                                  key={item.id}
                                  onClick={() => {
                                    navigate(`/admin/legacy/${item.id}`);
                                    setIsSelectorOpen(false);
                                  }}
                                  className={`w-full flex items-center gap-2.5 px-2.5 py-1.5 rounded text-[11px] font-semibold tracking-wide transition-all text-left ${
                                    active
                                      ? "bg-[#76B900]/10 text-[#76B900] border-l-2 border-[#76B900] font-bold"
                                      : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/20"
                                  }`}
                                >
                                  <Icon className={`h-3.5 w-3.5 ${active ? 'text-[#76B900]' : 'text-slate-500'}`} />
                                  <span>{item.label}</span>
                                </button>
                              );
                            })}
                          </div>
                        </div>
                      ))}
                    </div>
                  </>
                )}
              </div>
            </div>
          );
        })()}

        {/* Workspace Body */}
        <main className="flex-1 overflow-y-auto p-8">
          {children}
          
          {!children && activeSection === "dashboard" && (
            <div className="space-y-6 max-w-6xl mx-auto animate-in fade-in duration-300">
              <div className="flex items-center justify-between">
                <h1 className="text-xl font-black text-white tracking-tight">System Overview</h1>
                <div className="flex items-center gap-1.5 px-3 py-1 bg-emerald-500/10 border border-emerald-500/30 rounded-full text-[10px] font-bold text-emerald-400 uppercase">
                  <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
                  System Healthy
                </div>
              </div>

              {/* Status Grid Row */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* System Status Card */}
                <Card className="bg-[#0b1329]/50 border-slate-800/80 shadow-md">
                  <CardContent className="p-6">
                    <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-4 border-b border-slate-800/60 pb-2">
                      System Status
                    </h3>
                    <div className="grid grid-cols-3 sm:grid-cols-5 gap-4 text-center">
                      {[
                        { label: "CPU", val: "0.0%" },
                        { label: "Memory", val: "0 MB" },
                        { label: "Disk", val: "0 GB" },
                        { label: "Temperature", val: "0 °C" },
                        { label: "Active Jobs", val: "0" },
                      ].map((metric, idx) => (
                        <div key={idx} className="p-2 bg-[#020813]/60 border border-slate-800/40 rounded">
                          <div className="text-[10px] text-slate-500 uppercase font-semibold">{metric.label}</div>
                          <div className="text-sm font-extrabold text-[#76B900] mt-1">{metric.val}</div>
                        </div>
                      ))}
                    </div>
                    <div className="mt-6 flex flex-col items-center justify-center p-6 border border-slate-800/60 border-dashed rounded bg-[#020813]/30">
                      <Activity className="h-6 w-6 text-slate-700 mb-2" />
                      <span className="text-[10px] text-slate-500 font-medium">No system metrics available</span>
                    </div>
                  </CardContent>
                </Card>

                {/* Performance Overview Card */}
                <Card className="bg-[#0b1329]/50 border-slate-800/80 shadow-md">
                  <CardContent className="p-6">
                    <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-4 border-b border-slate-800/60 pb-2">
                      Performance Overview
                    </h3>
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-center">
                      {[
                        { label: "Avg Latency", val: "0.0 ms" },
                        { label: "Throughput", val: "0.0 req/s" },
                        { label: "Cache Hit", val: "0.0%" },
                        { label: "Avg Speedup", val: "0.0%" },
                      ].map((p, idx) => (
                        <div key={idx} className="p-2 bg-[#020813]/60 border border-slate-800/40 rounded">
                          <div className="text-[10px] text-slate-500 uppercase font-semibold">{p.label}</div>
                          <div className="text-sm font-extrabold text-[#76B900] mt-1">{p.val}</div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Active Jobs & Recent Alerts cards */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Active Jobs Card */}
                <Card className="bg-[#0b1329]/40 border-slate-800/80">
                  <CardContent className="p-6">
                    <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-4 border-b border-slate-800/60 pb-2 flex justify-between">
                      <span>Active Jobs</span>
                      <span className="text-[9px] text-slate-500 lowercase">0 active</span>
                    </h3>
                    <div className="flex flex-col items-center justify-center p-12 text-center">
                      <FolderOpen className="h-8 w-8 text-slate-700 mb-2" />
                      <p className="text-[11px] text-slate-500 font-semibold">No active jobs</p>
                    </div>
                  </CardContent>
                </Card>

                {/* Recent Alerts Card */}
                <Card className="bg-[#0b1329]/40 border-slate-800/80">
                  <CardContent className="p-6">
                    <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-4 border-b border-slate-800/60 pb-2 flex justify-between">
                      <span>Recent Alerts</span>
                      <span className="text-[9px] text-slate-500 lowercase">0 unresolved</span>
                    </h3>
                    <div className="flex flex-col items-center justify-center p-12 text-center">
                      <Bell className="h-8 w-8 text-slate-700 mb-2" />
                      <p className="text-[11px] text-slate-500 font-semibold">No alerts</p>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Performance Trends 24h Card */}
              <Card className="bg-[#0b1329]/40 border-slate-800/80">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between border-b border-slate-800/60 pb-3 mb-6">
                    <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                      Performance Trends (24h)
                    </h3>
                    <div className="flex bg-[#020813] border border-slate-800 p-0.5 rounded-lg">
                      {[
                        { id: "latency", label: "Latency" },
                        { id: "throughput", label: "Throughput" },
                        { id: "cache", label: "Cache Hit" }
                      ].map((t) => (
                        <button
                          key={t.id}
                          onClick={() => setActiveTrend(t.id as any)}
                          className={`px-3 py-1 rounded text-[10px] font-bold uppercase transition-all ${
                            activeTrend === t.id
                              ? "bg-[#76B900] text-black"
                              : "text-slate-400 hover:text-slate-200"
                          }`}
                        >
                          {t.label}
                        </button>
                      ))}
                    </div>
                  </div>
                  <div className="flex flex-col items-center justify-center p-16 border border-slate-800/60 border-dashed rounded bg-[#020813]/20">
                    <Activity className="h-8 w-8 text-slate-700 mb-3" />
                    <p className="text-[11px] text-slate-500 font-bold">No performance data available</p>
                  </div>
                </CardContent>
              </Card>

              {/* Optimization Modules Card */}
              <Card className="bg-[#0b1329]/40 border-slate-800/80 shadow-md">
                <CardContent className="p-6">
                  <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-6 border-b border-slate-800/60 pb-3">
                    Optimization Modules
                  </h3>

                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-2 gap-4">
                    {[
                      "Quantization",
                      "Kernel Optimization",
                      "Neural Approximation",
                      "Memory Compression",
                      "Cache Optimization",
                      "Parallel Execution",
                      "Distributed Computing",
                      "Model Serving",
                      "Streaming Inference",
                      "JIT Compilation",
                      "Memory Management",
                      "Speculative Execution",
                      "Adaptive Precision",
                      "Graph Optimization",
                      "Sparsity & Pruning",
                    ].map((name, idx) => (
                      <div key={idx} className="p-4 bg-[#020813]/80 border border-slate-800/60 rounded-lg flex flex-col justify-between min-h-[110px]">
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-bold text-slate-200">{name}</span>
                          <span className="flex items-center gap-1 text-[9px] font-bold text-slate-500 uppercase px-2 py-0.5 bg-slate-900/60 border border-slate-800 rounded">
                            <span className="h-1 w-1 rounded-full bg-slate-500" />
                            Idle
                          </span>
                        </div>

                        <div className="mt-4">
                          <div className="flex justify-between text-[10px] text-slate-400 mb-1">
                            <span>Health</span>
                            <span className="font-bold text-white">100%</span>
                          </div>
                          <div className="w-full bg-slate-800/60 h-1 rounded-full overflow-hidden">
                            <div className="bg-[#76B900] h-full rounded-full w-full" />
                          </div>
                        </div>

                        <div className="flex justify-between text-[9px] text-slate-500 font-bold uppercase mt-3">
                          <span>Speedup: <strong className="text-slate-400">N/A</strong></span>
                          <span>Comp: <strong className="text-slate-400">N/A</strong></span>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* VIEW 2: Inference View */}
          {activeSection === "inference" && (
            <div className="space-y-6 max-w-6xl mx-auto animate-in fade-in duration-300">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-[#76B900]/10 border border-[#76B900]/20 rounded-lg text-[#76B900]">
                    <Database className="h-5 w-5" />
                  </div>
                  <div>
                    <h1 className="text-xl font-black text-white tracking-tight">Inference Jobs</h1>
                    <p className="text-xs text-slate-500 font-semibold mt-0.5">Manage and monitor your GPU inference jobs</p>
                  </div>
                </div>

                <div className="flex gap-2">
                  <Button variant="outline" className="border-slate-800 text-slate-300 text-xs px-4 py-2 bg-[#0b1329]/40 flex items-center gap-1.5">
                    <RefreshCw className="h-3.5 w-3.5" />
                    Refresh
                  </Button>
                  <Button className="bg-[#76B900] hover:bg-[#659e00] text-black font-extrabold text-xs px-4 py-2 rounded">
                    + New Job
                  </Button>
                </div>
              </div>

              {/* Inference Filter Bar & Empty state */}
              <div className="flex bg-[#0b1329]/30 border border-slate-800/60 p-1.5 rounded-lg w-max mb-4 gap-1.5">
                {["All Jobs (0)", "Active (0)", "Completed (0)", "Failed (0)"].map((tab, idx) => (
                  <button
                    key={idx}
                    className={`px-3 py-1.5 rounded text-xs font-bold transition-all ${
                      idx === 0
                        ? "bg-[#76B900]/10 text-[#76B900] border border-[#76B900]/20"
                        : "text-slate-400 hover:text-slate-200"
                    }`}
                  >
                    {tab}
                  </button>
                ))}
              </div>

              {/* Filters list */}
              <div className="flex flex-wrap gap-3 items-center bg-[#0b1329]/45 border border-slate-800/60 p-4 rounded-lg">
                <div className="relative flex-grow max-w-sm">
                  <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-600" />
                  <input
                    type="text"
                    placeholder="Search jobs..."
                    className="w-full pl-9 pr-4 py-2 bg-[#020813] border border-slate-800 rounded focus:outline-none focus:ring-1 focus:ring-[#76B900] text-xs font-semibold placeholder-slate-600 text-slate-100"
                  />
                </div>

                <div className="flex gap-2">
                  <select className="bg-[#020813] border border-slate-800 rounded text-xs font-bold text-slate-300 px-3 py-2 outline-none">
                    <option>All Status</option>
                  </select>
                  <select className="bg-[#020813] border border-slate-800 rounded text-xs font-bold text-slate-300 px-3 py-2 outline-none">
                    <option>All Priority</option>
                  </select>
                  <select className="bg-[#020813] border border-slate-800 rounded text-xs font-bold text-slate-300 px-3 py-2 outline-none">
                    <option>Created</option>
                  </select>
                  <Button variant="outline" className="border-slate-800 p-2 bg-[#020813]">
                    <SlidersHorizontal className="h-4 w-4 text-slate-400" />
                  </Button>
                </div>
              </div>

              {/* Jobs Empty State */}
              <Card className="bg-[#0b1329]/20 border-slate-800/80 py-24 shadow-inner">
                <CardContent className="flex flex-col items-center justify-center text-center">
                  <FolderOpen className="h-10 w-10 text-slate-700 mb-3" />
                  <h3 className="text-sm font-extrabold text-slate-300 uppercase tracking-wider">No jobs found matching your criteria</h3>
                  <p className="text-[11px] text-slate-500 font-semibold mt-1">Create a new job to get started.</p>
                </CardContent>
              </Card>
            </div>
          )}

          {/* VIEW 3: GPU Modules View */}
          {activeSection === "modules" && (
            <div className="space-y-6 max-w-6xl mx-auto animate-in fade-in duration-300">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-[#76B900]/10 border border-[#76B900]/20 rounded-lg text-[#76B900]">
                    <Cpu className="h-5 w-5" />
                  </div>
                  <div>
                    <h1 className="text-xl font-black text-white tracking-tight">GPU Modules</h1>
                    <p className="text-xs text-slate-500 font-semibold mt-0.5">Manage and configure optimization modules</p>
                  </div>
                </div>

                <Button variant="outline" className="border-slate-800 text-slate-300 text-xs px-4 py-2 bg-[#0b1329]/40 flex items-center gap-1.5">
                  <RefreshCw className="h-3.5 w-3.5" />
                  Refresh
                </Button>
              </div>

              {/* Filter controls */}
              <div className="flex flex-wrap gap-3 items-center bg-[#0b1329]/45 border border-slate-800/60 p-4 rounded-lg">
                <div className="relative flex-grow max-w-sm">
                  <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-600" />
                  <input
                    type="text"
                    placeholder="Search modules..."
                    className="w-full pl-9 pr-4 py-2 bg-[#020813] border border-slate-800 rounded focus:outline-none focus:ring-1 focus:ring-[#76B900] text-xs font-semibold placeholder-slate-600 text-slate-100"
                  />
                </div>

                <div className="flex gap-2">
                  <select className="bg-[#020813] border border-slate-800 rounded text-xs font-bold text-slate-300 px-3 py-2 outline-none">
                    <option>All Status</option>
                  </select>
                  <select className="bg-[#020813] border border-slate-800 rounded text-xs font-bold text-slate-300 px-3 py-2 outline-none">
                    <option>Name</option>
                  </select>
                  <Button variant="outline" className="border-slate-800 p-2 bg-[#020813]">
                    <SlidersHorizontal className="h-4 w-4 text-slate-400" />
                  </Button>
                </div>
              </div>

              {/* GPU Modules List */}
              <div className="space-y-4">
                {[
                  { id: "quantization", label: "Quantization", desc: "Reduce model precision to INT8/FP16 for faster inference with minimal accuracy loss." },
                  { id: "kernel", label: "Kernel Optimization", desc: "Optimize CUDA kernels for maximum GPU utilization and throughput." },
                  { id: "approx", label: "Neural Approximation", desc: "Replace expensive operations with learned approximations." },
                  { id: "compression", label: "Memory Compression", desc: "Compress intermediate tensors to reduce memory footprint." },
                  { id: "cache", label: "Cache Optimization", desc: "Intelligent caching of repeated computations and activations." },
                  { id: "parallel", label: "Parallel Execution", desc: "Execute independent operations concurrently on GPU streams." },
                  { id: "distributed", label: "Distributed Computing", desc: "Scale inference across multiple GPUs and nodes." },
                  { id: "serving", label: "Model Serving", desc: "Optimized model loading and request batching for production." },
                  { id: "streaming", label: "Streaming Inference", desc: "Stream model weights and outputs for low-latency pipelines." },
                  { id: "jit", label: "JIT Compilation", desc: "Just-in-time compilation of model graphs for target hardware." },
                  { id: "memory", label: "Memory Management", desc: "Advanced memory allocation and defragmentation strategies." },
                  { id: "speculative", label: "Speculative Execution", desc: "Predict and pre-compute likely execution paths." },
                  { id: "precision", label: "Adaptive Precision", desc: "Dynamically adjust precision based on input characteristics." },
                  { id: "graph", label: "Graph Optimization", desc: "Fuse operations and eliminate redundancies in computation graphs." },
                  { id: "sparsity", label: "Sparsity & Pruning", desc: "Remove unnecessary weights and leverage sparse computation." }
                ].map((mod) => (
                  <Card key={mod.id} className="bg-[#0b1329]/40 border-slate-800/80 shadow-md">
                    <CardContent className="p-6">
                      <div className="flex items-start justify-between">
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="text-sm font-extrabold text-slate-200">{mod.label}</span>
                            <span className="flex items-center gap-1 text-[9px] font-bold text-slate-500 uppercase px-2 py-0.5 bg-slate-900/60 border border-slate-800 rounded">
                              <span className="h-1 w-1 rounded-full bg-slate-500" />
                              Idle
                            </span>
                          </div>
                          <p className="text-[11px] text-slate-400 mt-1 font-semibold">{mod.desc}</p>
                        </div>
                        <div className="flex items-center gap-1.5">
                          <div className="h-3 w-3 rounded-full border border-slate-700 bg-transparent flex items-center justify-center">
                            <span className="h-1.5 w-1.5 rounded-full bg-slate-500" />
                          </div>
                        </div>
                      </div>

                      {/* Health score status bar */}
                      <div className="mt-4">
                        <div className="flex justify-between text-[10px] text-slate-400 mb-1">
                          <span>Health Score</span>
                          <span className="font-bold text-[#76B900]">100%</span>
                        </div>
                        <div className="w-full bg-[#131d35] h-1.5 rounded-full overflow-hidden">
                          <div className="bg-[#76B900] h-full rounded-full w-full" />
                        </div>
                      </div>

                      {/* Speedup Compression subgrid stats */}
                      <div className="grid grid-cols-2 gap-4 mt-4">
                        <div className="p-2 bg-[#020813]/60 border border-slate-800/40 rounded flex items-center gap-2">
                          <Zap className="h-4 w-4 text-emerald-500" />
                          <div>
                            <div className="text-[9px] text-slate-500 font-bold uppercase">Speedup</div>
                            <div className="text-xs font-bold text-slate-300">-</div>
                          </div>
                        </div>
                        <div className="p-2 bg-[#020813]/60 border border-slate-800/40 rounded flex items-center gap-2">
                          <FileText className="h-4 w-4 text-blue-500" />
                          <div>
                            <div className="text-[9px] text-slate-500 font-bold uppercase">Compression</div>
                            <div className="text-xs font-bold text-slate-300">-</div>
                          </div>
                        </div>
                      </div>

                      {/* Enabled checkbox toggle and actions row */}
                      <div className="flex items-center justify-between border-t border-slate-800/60 pt-4 mt-6">
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => toggleModule(mod.id)}
                            className={`w-10 h-5 rounded-full transition-colors relative flex items-center px-0.5 ${
                              modulesState[mod.id] ? "bg-[#76B900]" : "bg-slate-800"
                            }`}
                          >
                            <span
                              className={`h-4 w-4 rounded-full bg-white transition-transform ${
                                modulesState[mod.id] ? "translate-x-5" : "translate-x-0"
                              }`}
                            />
                          </button>
                          <span className="text-[10px] text-slate-400 font-bold uppercase">Enabled</span>
                        </div>

                        <div className="flex gap-2">
                          <Button variant="outline" className="border-slate-800 text-xs px-3.5 py-1.5 bg-[#0b1329]/40 flex items-center gap-1">
                            <Settings className="h-3.5 w-3.5 text-slate-500" />
                            Configure
                          </Button>
                          <Button variant="outline" className="border-slate-800 text-xs px-3.5 py-1.5 bg-[#0b1329]/40 flex items-center gap-1">
                            <Activity className="h-3.5 w-3.5 text-slate-500" />
                            Stats
                          </Button>
                        </div>
                      </div>

                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          )}

          {/* VIEW 4: Results & VIEW 5: Monitoring area */}
          {["results", "monitoring"].includes(activeSection) && (
            <div className="flex flex-col items-center justify-center p-24 text-center border border-slate-800/60 border-dashed rounded bg-[#0b1329]/10 max-w-4xl mx-auto animate-in fade-in duration-300">
              <Cpu className="h-10 w-10 text-[#76B900] mb-4 animate-pulse" />
              <h2 className="text-lg font-bold text-slate-100 uppercase tracking-wider mb-1">
                {activeSection} Area
              </h2>
              <p className="text-slate-500 text-xs max-w-sm leading-relaxed">
                This console section is currently offline. Complete server setup to activate active telemetry channels.
              </p>
            </div>
          )}

          {/* VIEW 6: Settings Section */}
          {activeSection === "settings" && (
            <div className="space-y-6 max-w-3xl mx-auto animate-in fade-in duration-300">
              <div>
                <h1 className="text-xl font-black text-white tracking-tight">Settings</h1>
                <p className="text-xs text-slate-500 mt-1 font-semibold">Manage your account and preferences</p>
              </div>

              {/* Settings Subnav Tabs */}
              <div className="flex bg-[#0b1329]/60 border border-slate-800/80 p-0.5 rounded-lg w-max mb-6">
                {[
                  { id: "profile", label: "Profile" },
                  { id: "api", label: "API Keys" },
                  { id: "notifications", label: "Notifications" },
                  { id: "advanced", label: "Advanced" }
                ].map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveSettingsTab(tab.id as any)}
                    className={`px-4 py-2 rounded text-xs font-bold transition-all ${
                      activeSettingsTab === tab.id
                        ? "bg-[#76B900]/10 text-[#76B900] border border-[#76B900]/20"
                        : "text-slate-400 hover:text-slate-200"
                    }`}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>

              {/* Sub-tab 1: Profile */}
              {activeSettingsTab === "profile" && (
                <div className="space-y-6">
                  {/* Profile Info Card */}
                  <Card className="bg-[#0b1329]/50 border-slate-800/80">
                    <CardContent className="p-6 space-y-4">
                      <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider mb-2 border-b border-slate-800/60 pb-2">
                        Profile Information
                      </h3>
                      <p className="text-[10px] text-slate-400 font-semibold mb-4">Update your account details</p>

                      <div className="space-y-4">
                        <div>
                          <label className="block text-[10px] text-slate-400 font-bold uppercase mb-1.5">Email</label>
                          <input
                            type="email"
                            disabled
                            value="sivabalajipulavanur@gmail.com"
                            className="w-full px-4 py-2.5 bg-[#020813]/60 border border-slate-800 rounded text-xs text-slate-500 font-medium cursor-not-allowed"
                          />
                        </div>

                        <div>
                          <label className="block text-[10px] text-slate-400 font-bold uppercase mb-1.5">Full Name</label>
                          <input
                            type="text"
                            placeholder="Enter your full name"
                            value={fullName}
                            onChange={(e) => setFullName(e.target.value)}
                            className="w-full px-4 py-2.5 bg-[#020813] border border-slate-800 rounded focus:outline-none focus:ring-1 focus:ring-[#76B900] text-xs text-slate-200 font-medium placeholder-slate-600"
                          />
                        </div>

                        <div>
                          <label className="block text-[10px] text-slate-400 font-bold uppercase mb-1.5">Company</label>
                          <input
                            type="text"
                            placeholder="Enter your company name"
                            value={company}
                            onChange={(e) => setCompany(e.target.value)}
                            className="w-full px-4 py-2.5 bg-[#020813] border border-slate-800 rounded focus:outline-none focus:ring-1 focus:ring-[#76B900] text-xs text-slate-200 font-medium placeholder-slate-600"
                          />
                        </div>

                        <Button className="bg-[#76B900] hover:bg-[#659e00] text-black font-extrabold text-xs px-6 py-2.5 rounded transition-all">
                          Save Changes
                        </Button>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Subscription Card */}
                  <Card className="bg-[#0b1329]/50 border-slate-800/80">
                    <CardContent className="p-6">
                      <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider mb-2 border-b border-slate-800/60 pb-2">
                        Subscription
                      </h3>
                      <p className="text-[10px] text-slate-400 font-semibold mb-4">Your current plan details</p>
                      <div className="p-4 bg-[#020813]/60 border border-slate-800/40 rounded text-xs text-slate-400">
                        No subscription found
                      </div>
                    </CardContent>
                  </Card>
                </div>
              )}

              {/* Sub-tab 2: API Keys */}
              {activeSettingsTab === "api" && (
                <div className="space-y-6">
                  <Card className="bg-[#0b1329]/50 border-slate-800/80">
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between border-b border-slate-800/60 pb-3 mb-4">
                        <div>
                          <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider">
                            API Keys
                          </h3>
                          <p className="text-[10px] text-slate-400 font-semibold mt-0.5">Manage your API keys for programmatic access</p>
                        </div>
                        <Button
                          onClick={generateApiKey}
                          className="bg-[#76B900] hover:bg-[#659e00] text-black font-extrabold text-xs px-4 py-2 rounded"
                        >
                          + Generate New Key
                        </Button>
                      </div>

                      {apiKeys.length === 0 ? (
                        <div className="py-12 flex flex-col items-center justify-center text-center text-xs text-slate-500 font-medium">
                          No API keys. Generate one to get started.
                        </div>
                      ) : (
                        <div className="overflow-x-auto">
                          <table className="w-full text-left text-xs font-semibold">
                            <thead>
                              <tr className="border-b border-slate-800 text-slate-400">
                                <th className="py-2.5 px-3 uppercase text-[10px]">Name</th>
                                <th className="py-2.5 px-3 uppercase text-[10px]">Key</th>
                                <th className="py-2.5 px-3 uppercase text-[10px]">Status</th>
                                <th className="py-2.5 px-3 uppercase text-[10px]">Created</th>
                                <th className="py-2.5 px-3 uppercase text-[10px]">Last Used</th>
                              </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-800/40 text-slate-300">
                              {apiKeys.map((item, idx) => (
                                <tr key={idx} className="hover:bg-slate-800/10">
                                  <td className="py-3 px-3 text-white font-bold">{item.name}</td>
                                  <td className="py-3 px-3 font-mono text-[10px] text-[#76B900]">{item.key}</td>
                                  <td className="py-3 px-3 text-emerald-400 font-bold">{item.status}</td>
                                  <td className="py-3 px-3">{item.created}</td>
                                  <td className="py-3 px-3">{item.lastUsed}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </div>
              )}

              {/* Sub-tab 3: Notifications */}
              {activeSettingsTab === "notifications" && (
                <div className="space-y-6">
                  <Card className="bg-[#0b1329]/50 border-slate-800/80">
                    <CardContent className="p-6 space-y-5">
                      <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider mb-2 border-b border-slate-800/60 pb-2">
                        Notification Preferences
                      </h3>
                      <p className="text-[10px] text-slate-400 font-semibold mb-6">Configure how you receive updates</p>

                      <div className="space-y-4">
                        {[
                          {
                            id: "email",
                            title: "Email Notifications",
                            desc: "Receive notifications via email",
                            state: emailNotif,
                            toggle: setEmailNotif,
                          },
                          {
                            id: "jobs",
                            title: "Job Completion Alerts",
                            desc: "Get notified when inference jobs complete",
                            state: jobCompletionAlert,
                            toggle: setJobCompletionAlert,
                          },
                          {
                            id: "system",
                            title: "System Alerts",
                            desc: "Critical alerts about system status",
                            state: systemAlerts,
                            toggle: setSystemAlerts,
                          },
                          {
                            id: "weekly",
                            title: "Weekly Summary",
                            desc: "Receive a weekly performance summary",
                            state: weeklySummary,
                            toggle: setWeeklySummary,
                          },
                        ].map((pref) => (
                          <div key={pref.id} className="flex items-center justify-between border-b border-slate-800/40 pb-4 last:border-b-0">
                            <div>
                              <div className="text-xs font-bold text-slate-200">{pref.title}</div>
                              <div className="text-[10px] text-slate-400 mt-0.5 font-semibold">{pref.desc}</div>
                            </div>

                            <button
                              onClick={() => pref.toggle(!pref.state)}
                              className={`w-10 h-5 rounded-full transition-colors relative flex items-center px-0.5 ${
                                pref.state ? "bg-[#76B900]" : "bg-slate-800"
                              }`}
                            >
                              <span
                                className={`h-4 w-4 rounded-full bg-white transition-transform ${
                                  pref.state ? "translate-x-5" : "translate-x-0"
                                }`}
                              />
                            </button>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                </div>
              )}

              {/* Sub-tab 4: Advanced */}
              {activeSettingsTab === "advanced" && (
                <div className="space-y-6">
                  {/* Webhook Config */}
                  <Card className="bg-[#0b1329]/50 border-slate-800/80">
                    <CardContent className="p-6 space-y-4">
                      <div className="flex items-center gap-2 border-b border-slate-800/60 pb-2 mb-2">
                        <Globe className="h-4 w-4 text-[#76B900]" />
                        <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider">
                          Webhook Configuration
                        </h3>
                      </div>
                      <p className="text-[10px] text-slate-400 font-semibold mb-4">Test webhook endpoints</p>

                      <div className="space-y-4">
                        <div>
                          <label className="block text-[10px] text-slate-400 font-bold uppercase mb-1.5">Webhook URL</label>
                          <input
                            type="text"
                            value={webhookUrl}
                            onChange={(e) => setWebhookUrl(e.target.value)}
                            placeholder="https://your-server.com/webhook"
                            className="w-full px-4 py-2.5 bg-[#020813] border border-slate-800 rounded focus:outline-none focus:ring-1 focus:ring-[#76B900] text-xs text-slate-200 font-medium placeholder-slate-600"
                          />
                        </div>

                        <Button className="bg-[#76B900] hover:bg-[#659e00] text-black font-extrabold text-xs px-6 py-2.5 rounded transition-all">
                          Test Webhook
                        </Button>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Data Management */}
                  <Card className="bg-[#0b1329]/50 border-slate-800/80">
                    <CardContent className="p-6">
                      <div className="flex items-center gap-2 border-b border-slate-800/60 pb-2 mb-2">
                        <HardDrive className="h-4 w-4 text-[#76B900]" />
                        <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider">
                          Data Management
                        </h3>
                      </div>
                      <p className="text-[10px] text-slate-400 font-semibold mb-6">Export or delete your data</p>

                      <div className="space-y-3">
                        <Button variant="outline" className="w-full py-6 border-slate-800 text-xs font-bold text-slate-200 bg-[#0b1329]/40 flex items-center justify-center gap-2">
                          <Download className="h-4 w-4" />
                          Export All Data
                        </Button>
                        <Button className="w-full py-6 bg-rose-600 hover:bg-rose-500 text-white font-bold text-xs rounded flex items-center justify-center gap-2">
                          <Trash2 className="h-4 w-4" />
                          Delete Account
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              )}
            </div>
          )}

        </main>
      </div>
    </div>
  );
};
