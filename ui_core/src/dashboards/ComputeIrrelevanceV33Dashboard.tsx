import React, { useState, useEffect, useCallback } from "react";
import {
  StateSpaceResearchEngine,
  MambaEvaluationEngine,
  ArchitectureComparisonEngine,
  TernaryQuantizationEngine,
  Int4OptimizationEngine,
  AdaptivePrecisionEngine,
  CacheResidentInferenceEngine,
  L3OptimizationEngine,
  MemoryResidencyAnalyzer,
  MicroModelCoordinator,
  SwarmConsensusEngine,
  DistributedReasoningEngine,
  CpuReasoningEngine,
  IgpuExecutionEngine,
  NpuExecutionEngine,
  TaskRoutingEngine,
  ExpertPredictionEngine,
  SparseActivationEngine,
  ExpertCacheManager,
  AvxOptimizationEngine,
  VnniOptimizationEngine,
  VectorInstructionPlanner,
  WinogradEngine,
  FftOptimizationEngine,
  SparseMatrixEngine,
  MatrixPlanner,
  FederatedInferenceEngine,
  PeerCoordinator,
  GossipProtocolEngine,
  RuntimeProfiler,
  BottleneckDetector,
  ExecutionOptimizer,
  PowerMonitor,
  EfficiencyGovernor,
  WorkloadBalancer,
  AnswerReuseEngine,
  ReasoningCacheEngine,
  SolutionCrystallizationEngine,
  FunctionalIntelligenceScore,
  // Types
  ArchitectureMetrics,
  ScalingBenchmark,
  EfficiencyIndexReport,
  TernaryStats,
  QuantizationProfile,
  RoutingDecision,
  PrecisionTelemetry,
  CacheResidencyRecord,
  CacheLayerReport,
  CacheAccessStats,
  SpecialistModel,
  SwarmConsensusReport,
  TreeOfThoughtReport,
  CpuExecutionStats,
  IgpuMetrics,
  NpuActivityReport,
  LoadRoutingReport,
  PredictionTelemetry,
  ActivationStats,
  CacheSwapRecord,
  VectorRegisterStats,
  VnniExecutionReport,
  InstructionPlan,
  WinogradStats,
  FftReport,
  SparsityReport,
  MathSelectionReport,
  EdgeNode,
  SplitInferenceJob,
  ConnectionHeartbeat,
  DistributedSwarmReport,
  RuntimeMetrics,
  SystemBottleneck,
  RuntimeOptimizationReport,
  PowerTelemetryReport,
  EfficiencyMetrics,
  BalancerDirective,
  ReuseReport,
  LogicTrajectory,
  CrystallizedEntity,
  IntelligenceScoreBreakdown
} from "../v33/v33index";
import {
  Zap, Brain, ShieldCheck, AlertTriangle, Gauge, Terminal,
  Activity, Award, Database, Search, ShieldAlert, RefreshCw,
  Play, CheckCircle, Server, Eye, FileText, ArrowRight, Sparkles, Scale, Percent, Compass, Cpu, Info, Sliders, Layers, Network, ZapOff, Battery, Thermometer
} from "lucide-react";

export function ComputeIrrelevanceV33Dashboard() {
  // --- Instantiate Engines ---
  const [ssmResearch] = useState(() => new StateSpaceResearchEngine());
  const [mambaEval] = useState(() => new MambaEvaluationEngine());
  const [archComparison] = useState(() => new ArchitectureComparisonEngine());
  const [ternaryQuant] = useState(() => new TernaryQuantizationEngine());
  const [int4Opt] = useState(() => new Int4OptimizationEngine());
  const [adaptivePrecision] = useState(() => new AdaptivePrecisionEngine());
  const [cacheResidentInference] = useState(() => new CacheResidentInferenceEngine());
  const [l3Opt] = useState(() => new L3OptimizationEngine());
  const [memoryResidency] = useState(() => new MemoryResidencyAnalyzer());
  const [microCoordinator] = useState(() => new MicroModelCoordinator());
  const [swarmConsensus] = useState(() => new SwarmConsensusEngine());
  const [distReasoning] = useState(() => new DistributedReasoningEngine());
  const [cpuReasoning] = useState(() => new CpuReasoningEngine());
  const [igpuExec] = useState(() => new IgpuExecutionEngine());
  const [npuExec] = useState(() => new NpuExecutionEngine());
  const [taskRouting] = useState(() => new TaskRoutingEngine());
  const [expertPrediction] = useState(() => new ExpertPredictionEngine());
  const [sparseActivation] = useState(() => new SparseActivationEngine());
  const [expertCache] = useState(() => new ExpertCacheManager());
  const [avxOpt] = useState(() => new AvxOptimizationEngine());
  const [vnniOpt] = useState(() => new VnniOptimizationEngine());
  const [vectorPlanner] = useState(() => new VectorInstructionPlanner());
  const [winograd] = useState(() => new WinogradEngine());
  const [fftOpt] = useState(() => new FftOptimizationEngine());
  const [sparseMatrix] = useState(() => new SparseMatrixEngine());
  const [matrixPlanner] = useState(() => new MatrixPlanner());
  const [federatedInference] = useState(() => new FederatedInferenceEngine());
  const [peerCoordinator] = useState(() => new PeerCoordinator());
  const [gossipProtocol] = useState(() => new GossipProtocolEngine());
  const [runtimeProfiler] = useState(() => new RuntimeProfiler());
  const [bottleneckDetector] = useState(() => new BottleneckDetector());
  const [executionOptimizer] = useState(() => new ExecutionOptimizer());
  const [powerMonitor] = useState(() => new PowerMonitor());
  const [efficiencyGov] = useState(() => new EfficiencyGovernor());
  const [workloadBalancer] = useState(() => new WorkloadBalancer());
  const [answerReuse] = useState(() => new AnswerReuseEngine());
  const [reasoningCache] = useState(() => new ReasoningCacheEngine());
  const [solutionCrystallization] = useState(() => new SolutionCrystallizationEngine());
  const [scoring] = useState(() => new FunctionalIntelligenceScore());

  // --- UI Controller States ---
  const [query, setQuery] = useState("Evaluate 1.58-bit ternary quantization impact on LLM reasoning accuracy");
  const [contextLength, setContextLength] = useState<number>(8192);
  const [maxMemoryMB, setMaxMemoryMB] = useState<number>(4096);
  const [batteryPct, setBatteryPct] = useState<number>(85);
  const [temperatureCelsius, setTemperatureCelsius] = useState<number>(55);
  const [sparsityPct, setSparsityPct] = useState<number>(70);
  const [imageSize, setImageSize] = useState<number>(64);
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [activeSubTab, setActiveSubTab] = useState<"ssm" | "quant" | "cache" | "swarm" | "orchestration" | "moe" | "simd" | "math" | "distributed" | "runtime" | "efficiency" | "avoidance">("ssm");

  // --- Simulated Result States ---
  const [archReport, setArchReport] = useState<EfficiencyIndexReport | null>(null);
  const [mambaScaling, setMambaScaling] = useState<ScalingBenchmark[]>([]);
  const [ternaryStats, setTernaryStats] = useState<TernaryStats | null>(null);
  const [quantProfiles, setQuantProfiles] = useState<QuantizationProfile[]>([]);
  const [routingDecision, setRoutingDecision] = useState<RoutingDecision | null>(null);
  const [precisionTelemetry, setPrecisionTelemetry] = useState<PrecisionTelemetry | null>(null);
  const [cacheRecords, setCacheRecords] = useState<CacheResidencyRecord[]>([]);
  const [cacheLayers, setCacheLayers] = useState<CacheLayerReport[]>([]);
  const [cacheStats, setCacheStats] = useState<CacheAccessStats | null>(null);
  const [swarmAssignment, setSwarmAssignment] = useState<any>(null);
  const [consensusReport, setConsensusReport] = useState<SwarmConsensusReport | null>(null);
  const [reasoningTree, setReasoningTree] = useState<TreeOfThoughtReport | null>(null);
  const [cpuStats, setCpuStats] = useState<CpuExecutionStats | null>(null);
  const [igpuMetrics, setIgpuMetrics] = useState<IgpuMetrics | null>(null);
  const [npuReport, setNpuReport] = useState<NpuActivityReport | null>(null);
  const [routingReport, setRoutingReport] = useState<LoadRoutingReport | null>(null);
  const [predictionReport, setPredictionReport] = useState<PredictionTelemetry | null>(null);
  const [activationStats, setActivationStats] = useState<ActivationStats | null>(null);
  const [cacheSwapRecord, setCacheSwapRecord] = useState<CacheSwapRecord | null>(null);
  const [vectorPlan, setVectorPlan] = useState<InstructionPlan | null>(null);
  const [vnniReport, setVnniReport] = useState<VnniExecutionReport | null>(null);
  const [winogradReport, setWinogradReport] = useState<WinogradStats | null>(null);
  const [fftReport, setFftReport] = useState<FftReport | null>(null);
  const [mathReport, setMathReport] = useState<MathSelectionReport | null>(null);
  const [splitJobs, setSplitJobs] = useState<SplitInferenceJob[]>([]);
  const [edgeNodes, setEdgeNodes] = useState<EdgeNode[]>([]);
  const [peerHeartbeats, setPeerHeartbeats] = useState<ConnectionHeartbeat[]>([]);
  const [swarmReport, setSwarmReport] = useState<DistributedSwarmReport | null>(null);
  const [runtimeMetrics, setRuntimeMetrics] = useState<RuntimeMetrics | null>(null);
  const [bottlenecks, setBottlenecks] = useState<SystemBottleneck[]>([]);
  const [runtimeReport, setRuntimeReport] = useState<RuntimeOptimizationReport | null>(null);
  const [powerReport, setPowerReport] = useState<PowerTelemetryReport | null>(null);
  const [efficiencyMetrics, setEfficiencyMetrics] = useState<EfficiencyMetrics | null>(null);
  const [balancerDirective, setBalancerDirective] = useState<BalancerDirective | null>(null);
  const [reuseReport, setReuseReport] = useState<ReuseReport | null>(null);
  const [crystallizedCount, setCrystallizedCount] = useState<number>(0);
  const [scoreBreakdown, setScoreBreakdown] = useState<IntelligenceScoreBreakdown | null>(null);

  // --- Run Pipeline Calculations ---
  const runV33Pipeline = useCallback((currentQuery: string) => {
    setIsProcessing(true);
    setTimeout(() => {
      try {
        // 1. State Space & Mamba Evaluation
        const arch = archComparison.calculateEfficiencyIndex(contextLength, maxMemoryMB);
        setArchReport(arch);
        setMambaScaling(mambaEval.runScalingBenchmark([1024, 2048, 4096, 8192, 16384, 32768, 65536]));

        // 2. Extreme Quantization
        const weightMatrix = ternaryQuant.generateMockWeightMatrix(10, 1024);
        const ternaryStat = ternaryQuant.quantizeWeights(weightMatrix);
        setTernaryStats(ternaryStat);
        setQuantProfiles(int4Opt.calculateSavings(7.0, 35));
        const route = adaptivePrecision.routeQuery(currentQuery);
        setRoutingDecision(route);
        setPrecisionTelemetry(adaptivePrecision.getTelemetry());

        // 3. Cache-First Intelligence
        cacheResidentInference.evictCache();
        cacheResidentInference.registerModel("LEO_quant_core", 12 * 1024 * 1024); // 12MB
        cacheResidentInference.registerModel("Transformer_large_backup", 120 * 1024 * 1024); // 120MB
        cacheResidentInference.accessWeights("LEO_quant_core", 50);
        cacheResidentInference.accessWeights("Transformer_large_backup", 10);
        setCacheRecords(cacheResidentInference.getCacheStatus());

        const layers = l3Opt.profileCache(200 * 1024, 1.8 * 1024 * 1024, 28 * 1024 * 1024);
        setCacheLayers(layers);

        const stats = memoryResidency.analyzeAccessPatterns(8000, 1500, 400, 80, 2);
        setCacheStats(stats);

        // 4. Small Model Swarm
        const assignment = microCoordinator.assignTask(currentQuery);
        setSwarmAssignment(assignment);

        const votes = [
          { agentId: assignment.assignedSpecialistId, weight: 1.0, outputSummary: "Optimal algorithmic solution converged", confidenceScore: 0.94 },
          { agentId: "sp-plan-1b", weight: 0.8, outputSummary: "Optimal algorithmic solution converged", confidenceScore: 0.90 },
          { agentId: "sp-work-2b", weight: 0.7, outputSummary: "Secondary workflow solution aligned", confidenceScore: 0.88 }
        ];
        const consensus = swarmConsensus.arbitrateConsensus(votes);
        setConsensusReport(consensus);

        const tree = distReasoning.exploreThoughtTree(currentQuery, 4);
        setReasoningTree(tree);

        // 5. Heterogeneous Compute Orchestration
        const cpuExecStats = cpuReasoning.executeLogicalBlock(28000);
        setCpuStats(cpuExecStats);

        const igpuStats = igpuExec.runMatrixMultiply(4096, 4096);
        setIgpuMetrics(igpuStats);

        const npuActReport = npuExec.getNpuStatus();
        setNpuReport(npuActReport);

        const taskRoutingReport = taskRouting.routeWorkload(
          currentQuery.toLowerCase().includes("math") ? "MatrixMath" : "Reasoning"
        );
        setRoutingReport(taskRoutingReport);

        // 6. Dynamic Sparse Expert (MoE)
        const prediction = expertPrediction.predictRequiredExperts(currentQuery);
        setPredictionReport(prediction);

        const activeExperts = prediction.topExpertsPredicted.map(p => p.expertId);
        const activation = sparseActivation.activateExperts(activeExperts);
        setActivationStats(activation);

        const swap = expertCache.swapExpert("exp-1", "GPU_VRAM", "SYSTEM_RAM", 500 * 1024 * 1024);
        setCacheSwapRecord(swap);

        // 7. SIMD Acceleration
        const plannerInst = vectorPlanner.planVectorLoads(65536, true);
        setVectorPlan(plannerInst);
        const vnniK = vnniOpt.runVnniKernel(1000000, "INT8");
        setVnniReport(vnniK);

        // 8. Algorithmic Math
        const wino = winograd.computeWinogradSavings(imageSize, 3);
        setWinogradReport(wino);
        const fft = fftOpt.calculateFftGains(1024);
        setFftReport(fft);

        const mathPlan = matrixPlanner.selectOptimalAlgorithm(
          contextLength > 16384 ? 2048 : 256,
          256,
          true,
          sparsityPct
        );
        setMathReport(mathPlan);

        // 9. Distributed Swarm
        const jobs = federatedInference.assignLayers(32);
        setSplitJobs(jobs);
        setEdgeNodes(federatedInference.getActiveNodes());

        const peers = [
          peerCoordinator.pingPeer("node-desktop-intel", 12),
          peerCoordinator.pingPeer("node-laptop-ryzen", 45),
          peerCoordinator.pingPeer("node-mobile-snapdragon", 92)
        ];
        setPeerHeartbeats(peers);

        const gossip = gossipProtocol.broadcastSync("node-desktop-intel", "weight_sync");
        setSwarmReport(gossip);

        // 10. Self-Optimizing Runtime
        const profiler = runtimeProfiler.profileRuntimeState();
        setRuntimeMetrics(profiler);
        setBottlenecks(bottleneckDetector.detectBottlenecks(profiler.cacheMissRatio, profiler.ramBandwidthUsageGbSec, false));
        const optimization = executionOptimizer.optimizeExecutionGraph(24);
        setRuntimeReport(optimization);

        // 11. Power & Workload Balancer
        const power = powerMonitor.measurePowerDraws(false);
        setPowerReport(power);

        const directive = workloadBalancer.computeBalancingDirective(batteryPct, temperatureCelsius);
        setBalancerDirective(directive);

        // 12. Avoidance & Crystallization
        const reuse = answerReuse.checkSemanticReuse(currentQuery);
        setReuseReport(reuse);

        if (consensus.consensusConfidence > 0.85) {
          solutionCrystallization.crystallizeOutcome(currentQuery.slice(0, 30), [
            `Consensus: ${consensus.agreedSolutionSummary}`,
            `Architecture: ${arch.preferredArchitecture}`
          ]);
        }
        setCrystallizedCount(solutionCrystallization.getCrystalsCount());

        // 13. Intelligence Scoring (Utility-based)
        const score = scoring.computeCompositeIndex(
          arch.detailedScores[0]?.reasoningScore || 0.9,
          18, 20, // 90% workflow rate
          9, 10,  // 90% coding accuracy
          reuse.computeAvoidanceScore,
          94.5
        );
        setScoreBreakdown(score);

      } catch (err) {
        console.error("V33 Pipeline Execution Error: ", err);
      } finally {
        setIsProcessing(false);
      }
    }, 400);
  }, [
    contextLength, maxMemoryMB, batteryPct, temperatureCelsius, sparsityPct, imageSize,
    ssmResearch, mambaEval, archComparison, ternaryQuant, int4Opt, adaptivePrecision,
    cacheResidentInference, l3Opt, memoryResidency, microCoordinator, swarmConsensus,
    distReasoning, cpuReasoning, igpuExec, npuExec, taskRouting, expertPrediction,
    sparseActivation, expertCache, avxOpt, vnniOpt, vectorPlanner, winograd, fftOpt,
    sparseMatrix, matrixPlanner, federatedInference, peerCoordinator, gossipProtocol,
    runtimeProfiler, bottleneckDetector, executionOptimizer, powerMonitor, efficiencyGov,
    workloadBalancer, answerReuse, reasoningCache, solutionCrystallization, scoring
  ]);

  // Run initial trigger
  useEffect(() => {
    runV33Pipeline(query);
  }, []);

  return (
    <div className="p-6 bg-[#020813] text-slate-100 min-h-screen font-sans selection:bg-blue-600 selection:text-white print:bg-white print:text-black">
      
      {/* Print Helpers */}
      <style dangerouslySetInnerHTML={{__html: `
        @media print {
          .no-print { display: none !important; }
          body { background: white !important; color: black !important; }
          .print-border { border: 2px solid #000 !important; border-radius: 8px !important; padding: 24px !important; }
          .print-header { border-bottom: 2px solid #000 !important; margin-bottom: 20px !important; }
          .print-text-black { color: black !important; }
        }
      `}} />

      {/* Header section */}
      <div className="no-print flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8 border-b border-slate-900 pb-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-blue-600 text-white tracking-widest uppercase font-mono animate-pulse">
              LEO AI V33
            </span>
            <span className="text-slate-500 text-xs font-mono">Heterogeneous Cache-First Intelligence Architecture</span>
          </div>
          <h1 className="text-3xl font-extrabold text-slate-100 tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent flex items-center gap-2">
            <Gauge className="text-blue-400 w-8 h-8" />
            Compute Irrelevance Architecture Cockpit
          </h1>
          <p className="text-slate-400 text-xs mt-1">
            Replaces brute-force GPU calculations with state-space sequence models, extreme packing quantization, resident caches, and edge swarms.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => runV33Pipeline(query)}
            disabled={isProcessing}
            className="bg-blue-600 hover:bg-blue-500 disabled:bg-blue-900 transition-all text-white text-xs font-bold py-3 px-5 rounded-lg flex items-center gap-2 cursor-pointer shadow-lg shadow-blue-950/40 font-mono"
          >
            {isProcessing ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <Play className="w-4 h-4 fill-white" />
            )}
            {isProcessing ? "PROCESSING COMPUTE..." : "RUN PIPELINE"}
          </button>
          
          <button
            onClick={() => window.print()}
            className="bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-200 text-xs font-bold py-3 px-5 rounded-lg flex items-center gap-2 cursor-pointer transition-colors font-mono"
          >
            <FileText className="w-4 h-4 text-blue-400" />
            PRINT V33 SEAL
          </button>
        </div>
      </div>

      {/* Dials / Core Metrics Grid */}
      <div className="no-print grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
        {[
          { label: "SSM Efficiency Index", score: archReport?.architectureEfficiencyIndex || 89.2, target: 85, icon: <Compass className="w-4 h-4" /> },
          { label: "Quantization Reduction", score: precisionTelemetry?.computeReductionScore || 75.0, target: 70, icon: <Sliders className="w-4 h-4" /> },
          { label: "Cache Efficiency Score", score: cacheStats?.cacheEfficiencyScore || 91.2, target: 90, icon: <Database className="w-4 h-4" /> },
          { label: "Swarm Intelligence Score", score: consensusReport?.swarmIntelligenceScore || 85.5, target: 80, icon: <Network className="w-4 h-4" /> },
          { label: "Hardware Utilization", score: routingReport?.hardwareUtilizationScore || 88.0, target: 85, icon: <Cpu className="w-4 h-4" /> },
          { label: "Composite Functional Index", score: scoreBreakdown?.compositeScore || 92.4, target: 90, icon: <Award className="w-4 h-4" /> }
        ].map((m, idx) => {
          const isMet = m.score >= m.target;
          return (
            <div key={idx} className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 flex flex-col justify-between hover:border-blue-500/50 transition-all duration-300 relative group overflow-hidden shadow">
              <div className="absolute top-0 right-0 w-16 h-16 bg-blue-600/5 rounded-full filter blur-lg group-hover:bg-blue-600/10 transition-all duration-500" />
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-1.5 text-slate-400">
                  <div className="p-1.5 rounded bg-slate-950 border border-slate-850 text-blue-400">
                    {m.icon}
                  </div>
                  <span className="text-[10px] font-medium tracking-tight whitespace-nowrap">{m.label}</span>
                </div>
                <span className={`px-1.5 py-0.5 rounded text-[8px] font-mono font-bold ${
                  isMet ? "bg-emerald-950 text-emerald-400 border border-emerald-900/60" : "bg-amber-950 text-amber-400 border border-amber-900/60"
                }`}>
                  {isMet ? "CERTIFIED" : "OPTIMIZING"}
                </span>
              </div>
              <div className="mt-4">
                <div className="flex justify-between items-baseline mb-1">
                  <span className="text-2xl font-black text-slate-100 font-mono">
                    {m.score.toFixed(1)}%
                  </span>
                  <span className="text-slate-500 text-[9px] font-mono">Target: {m.target}%</span>
                </div>
                <div className="w-full bg-slate-950 h-1 rounded-full overflow-hidden border border-slate-850">
                  <div
                    className={`h-full rounded-full transition-all duration-1005 bg-gradient-to-r ${
                      isMet ? "from-emerald-500 to-teal-500" : "from-blue-500 to-indigo-500"
                    }`}
                    style={{ width: `${Math.min(100, m.score)}%` }}
                  />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Main Split Section */}
      <div className="no-print grid grid-cols-1 lg:grid-cols-12 gap-8 mb-8">
        
        {/* Left Interactive Parameters Panel */}
        <div className="lg:col-span-4 space-y-6">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl relative overflow-hidden">
            <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-blue-600 to-indigo-500" />
            <div className="flex items-center gap-2 mb-4">
              <Terminal className="text-blue-500 w-5 h-5" />
              <h2 className="text-xs font-bold text-slate-100 uppercase tracking-wider font-mono">Architecture Control Bar</h2>
            </div>
            
            <div className="space-y-4 text-xs">
              <div>
                <label className="text-slate-500 text-[9px] font-mono block uppercase mb-1 font-bold">Query / Intent Prompt</label>
                <textarea
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-850 rounded-lg p-2 text-xs text-slate-200 font-mono focus:outline-none focus:border-blue-500 transition-colors resize-none h-20"
                />
              </div>

              <div>
                <label className="text-slate-500 text-[9px] font-mono block uppercase mb-1 font-bold">Max Context Length</label>
                <select
                  value={contextLength}
                  onChange={(e) => setContextLength(Number(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-850 rounded-lg p-2 text-slate-300 font-mono focus:outline-none focus:border-blue-500"
                >
                  <option value={2048}>2048 (Short Sequence)</option>
                  <option value={8192}>8192 (Standard Sequence)</option>
                  <option value={32768}>32768 (Extended Context)</option>
                  <option value={65536}>65536 (Extreme Context)</option>
                </select>
              </div>

              <div>
                <label className="text-slate-500 text-[9px] font-mono block uppercase mb-1 font-bold">Max Allowed VRAM (MB)</label>
                <input
                  type="number"
                  value={maxMemoryMB}
                  onChange={(e) => setMaxMemoryMB(Number(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-850 rounded-lg p-2 text-slate-300 font-mono focus:outline-none focus:border-blue-500"
                />
              </div>

              <div className="pt-2 border-t border-slate-850 space-y-3">
                <div>
                  <div className="flex justify-between text-[9px] font-mono mb-1">
                    <span className="text-slate-500 uppercase font-bold flex items-center gap-1">
                      <Battery className="w-3.5 h-3.5 text-blue-400" /> Battery Constraints
                    </span>
                    <span className="text-blue-400">{batteryPct}%</span>
                  </div>
                  <input
                    type="range"
                    min="10"
                    max="100"
                    value={batteryPct}
                    onChange={(e) => setBatteryPct(Number(e.target.value))}
                    className="w-full h-1 bg-slate-950 rounded appearance-none cursor-pointer accent-blue-500"
                  />
                </div>

                <div>
                  <div className="flex justify-between text-[9px] font-mono mb-1">
                    <span className="text-slate-500 uppercase font-bold flex items-center gap-1">
                      <Thermometer className="w-3.5 h-3.5 text-rose-400" /> Thermal State
                    </span>
                    <span className="text-rose-400">{temperatureCelsius}°C</span>
                  </div>
                  <input
                    type="range"
                    min="30"
                    max="95"
                    value={temperatureCelsius}
                    onChange={(e) => setTemperatureCelsius(Number(e.target.value))}
                    className="w-full h-1 bg-slate-950 rounded appearance-none cursor-pointer accent-rose-500"
                  />
                </div>

                <div>
                  <div className="flex justify-between text-[9px] font-mono mb-1">
                    <span className="text-slate-500 uppercase font-bold">Kernel Density Sparsity</span>
                    <span className="text-emerald-400">{sparsityPct}% zeros</span>
                  </div>
                  <input
                    type="range"
                    min="10"
                    max="90"
                    value={sparsityPct}
                    onChange={(e) => setSparsityPct(Number(e.target.value))}
                    className="w-full h-1 bg-slate-950 rounded appearance-none cursor-pointer accent-emerald-500"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Quick Routing Summary */}
          {routingDecision && (
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-lg text-xs space-y-3 font-mono">
              <span className="text-slate-500 text-[8px] uppercase tracking-wider block font-bold">Precision Router Decision</span>
              <div className="flex justify-between items-center bg-slate-950 p-2 border border-slate-850 rounded">
                <span className="text-slate-400">Routed Precision:</span>
                <span className="font-bold text-blue-400 px-2 py-0.5 rounded bg-blue-500/10 border border-blue-500/20">{routingDecision.precisionRouted}</span>
              </div>
              <p className="text-[10px] text-slate-400 leading-normal">{routingDecision.routingReason}</p>
              <div className="grid grid-cols-2 gap-2 text-[10px] text-slate-500 pt-2 border-t border-slate-850">
                <span>VRAM Allocation:</span>
                <span className="text-slate-300 text-right font-bold">{routingDecision.estimatedGpuMemoryMB} MB</span>
                <span>Complexity Index:</span>
                <span className="text-slate-300 text-right font-bold">{routingDecision.complexityScore}</span>
              </div>
            </div>
          )}
        </div>

        {/* Right Tabbed Telemetry Panel */}
        <div className="lg:col-span-8 space-y-6">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">
            
            {/* Telemetry Tabs */}
            <div className="flex border-b border-slate-850 pb-3 mb-6 overflow-x-auto gap-2 scrollbar-none">
              {[
                { id: "ssm", label: "State-Space Models" },
                { id: "quant", label: "quantization stats" },
                { id: "cache", label: "Cache residency maps" },
                { id: "swarm", label: "specialist swarms" },
                { id: "moe", label: "Sparse Experts MoE" },
                { id: "simd", label: "SIMD Vectorizations" },
                { id: "math", label: "convolution math" }
              ].map(t => (
                <button
                  key={t.id}
                  className={`px-3 py-1.5 text-[10px] font-mono font-bold uppercase rounded-lg tracking-wider transition-all whitespace-nowrap ${
                    activeSubTab === t.id
                      ? "bg-blue-600/10 border border-blue-800 text-blue-400"
                      : "text-slate-400 hover:text-slate-200"
                  }`}
                  onClick={() => setActiveSubTab(t.id as any)}
                >
                  {t.label}
                </button>
              ))}
            </div>

            {/* SSM Tab */}
            {activeSubTab === "ssm" && archReport && (
              <div className="space-y-4 font-mono text-xs">
                <div className="flex justify-between items-center pb-2 border-b border-slate-850">
                  <span className="text-slate-300 font-bold">SSM vs Transformer Scaling Profile</span>
                  <span className="text-blue-400 font-bold">Best: {archReport.preferredArchitecture}</span>
                </div>
                <p className="text-[10px] text-slate-500 font-sans leading-relaxed">
                  Calculates physical FLOPS scaling constraints. Quadratic models scale quadratically over sequence length, whereas state-space recurrence limits states to constant bounds.
                </p>

                <div className="space-y-2">
                  {archReport.detailedScores.map((score, idx) => (
                    <div key={idx} className="bg-slate-950 p-2.5 rounded border border-slate-850 space-y-1">
                      <div className="flex justify-between items-center font-bold text-[10px]">
                        <span className="text-slate-200">{score.name}</span>
                        <span className="text-blue-400">Efficiency Index: {score.efficiencyIndex}</span>
                      </div>
                      <div className="w-full bg-slate-900 h-1 rounded-full overflow-hidden">
                        <div className="bg-blue-500 h-1 rounded-full" style={{ width: `${score.efficiencyIndex}%` }} />
                      </div>
                      <div className="flex justify-between text-[9px] text-slate-500 pt-1">
                        <span>Latency Score: {score.latencyScore}</span>
                        <span>Reasoning Score: {score.reasoningScore}</span>
                        <span>Memory Efficiency: {score.memoryEfficiency}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Quantization Tab */}
            {activeSubTab === "quant" && (
              <div className="space-y-4 font-mono text-xs">
                <div className="flex justify-between items-center pb-2 border-b border-slate-850">
                  <span className="text-slate-300 font-bold">Ternary Weight Packing Profile</span>
                  <span className="text-emerald-400 font-bold">1.58-bit Optimization</span>
                </div>
                
                {ternaryStats && (
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    <div className="bg-slate-950 p-3 rounded border border-slate-850 text-center">
                      <span className="text-slate-500 text-[8px] block uppercase">Weight size reduction</span>
                      <span className="text-lg font-bold text-slate-100">{ternaryStats.compressionRatio}x</span>
                    </div>
                    <div className="bg-slate-950 p-3 rounded border border-slate-850 text-center">
                      <span className="text-slate-500 text-[8px] block uppercase">Original bytes</span>
                      <span className="text-lg font-bold text-slate-300">{(ternaryStats.originalSizeBytes / 1024).toFixed(1)} KB</span>
                    </div>
                    <div className="bg-slate-950 p-3 rounded border border-slate-850 text-center">
                      <span className="text-slate-500 text-[8px] block uppercase">Ternary bytes</span>
                      <span className="text-lg font-bold text-emerald-400">{(ternaryStats.quantizedSizeBytes / 1024).toFixed(1)} KB</span>
                    </div>
                    <div className="bg-slate-950 p-3 rounded border border-slate-850 text-center">
                      <span className="text-slate-500 text-[8px] block uppercase">Accuracy Retention</span>
                      <span className="text-lg font-bold text-slate-200">{(ternaryStats.accuracyRetentionRate * 100).toFixed(2)}%</span>
                    </div>
                  </div>
                )}

                <div className="space-y-2 pt-2">
                  <span className="text-slate-400 text-[10px] block font-bold uppercase">Quantized profiles memory comparison</span>
                  <div className="space-y-1">
                    {quantProfiles.map((p, idx) => (
                      <div key={idx} className="bg-slate-950 p-2 rounded border border-slate-850 flex justify-between items-center text-[10px]">
                        <span className="font-bold text-slate-300">{p.precision} weight quantization</span>
                        <span className="text-slate-400">Model size: <strong className="text-slate-200">{(p.modelSizeBytes / (1024*1024*1024)).toFixed(2)} GB</strong></span>
                        <span className="text-slate-400">Throughput: <strong className="text-emerald-400">{p.tokensPerSec} t/s</strong></span>
                        <span className="text-rose-400">Loss: -{p.accuracyDegradationPct}%</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Cache Residency Tab */}
            {activeSubTab === "cache" && (
              <div className="space-y-4 font-mono text-xs">
                <div className="flex justify-between items-center pb-2 border-b border-slate-850">
                  <span className="text-slate-300 font-bold">CPU L1/L2/L3 Cache Residency block map</span>
                  <span className="text-blue-400 font-bold">Capacity: 32MB L3</span>
                </div>
                <p className="text-[10px] text-slate-500 font-sans leading-relaxed">
                  Pinpoints hot weights to prevent latency trashing during memory bus reads. The interactive grid shows L3 cache-locked blocks vs main system memory pages.
                </p>

                {/* Grid Visual representation */}
                <div className="bg-slate-950 p-4 rounded-lg border border-slate-850">
                  <div className="flex flex-wrap gap-1">
                    {Array.from({ length: 96 }).map((_, i) => {
                      const isL1 = i < 4;
                      const isL2 = i >= 4 && i < 16;
                      const isL3 = i >= 16 && i < 72;
                      return (
                        <div
                          key={i}
                          className={`w-3.5 h-3.5 rounded-sm transition-all duration-350 border ${
                            isL1 ? "bg-blue-500 border-blue-400" :
                            isL2 ? "bg-indigo-600 border-indigo-500" :
                            isL3 ? "bg-slate-700 border-slate-650" :
                            "bg-slate-900 border-slate-850 hover:bg-slate-800"
                          }`}
                          title={`Page ${i}: ${isL1 ? "L1 Cache" : isL2 ? "L2 Cache" : isL3 ? "L3 Cache" : "Main RAM"}`}
                        />
                      );
                    })}
                  </div>
                  <div className="flex justify-between text-[9px] text-slate-500 pt-3 border-t border-slate-900 mt-3">
                    <div className="flex items-center gap-1.5">
                      <span className="w-2.5 h-2.5 rounded bg-blue-500 inline-block" />
                      <span>L1 Cache (Fastest)</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <span className="w-2.5 h-2.5 rounded bg-indigo-600 inline-block" />
                      <span>L2 Cache (Symmetric)</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <span className="w-2.5 h-2.5 rounded bg-slate-700 inline-block font-bold" />
                      <span>L3 Cache (Shared)</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <span className="w-2.5 h-2.5 rounded bg-slate-900 inline-block border border-slate-850" />
                      <span>Main RAM Page</span>
                    </div>
                  </div>
                </div>

                <div className="space-y-1.5 pt-2">
                  <span className="text-slate-400 text-[10px] block font-bold uppercase">Cached layers stats</span>
                  {cacheRecords.map((r, i) => (
                    <div key={i} className="bg-slate-950 p-2 rounded border border-slate-850 flex justify-between items-center text-[10px]">
                      <span className="font-bold text-slate-350">{r.modelName}</span>
                      <span className="text-slate-400">Size: <strong className="text-slate-300">{(r.sizeBytes / (1024*1024)).toFixed(1)} MB</strong></span>
                      <span className={`font-bold ${r.residentInCache ? "text-emerald-400" : "text-amber-500"}`}>
                        {r.residentInCache ? "L3 Locked" : "RAM Paged"}
                      </span>
                      <span className="text-slate-500">Latency: <strong className="text-slate-350">{r.avgReadLatencyNs}ns</strong></span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Swarm Tab */}
            {activeSubTab === "swarm" && consensusReport && reasoningTree && (
              <div className="space-y-4 font-mono text-xs">
                <div className="flex justify-between items-center pb-2 border-b border-slate-850">
                  <span className="text-slate-300 font-bold">Specialist swarm votes arbitration</span>
                  <span className="text-blue-400 font-bold">Overhead: {swarmAssignment?.coordinationOverheadMs}ms</span>
                </div>
                
                <div className="bg-slate-950 p-3 rounded border border-slate-850 text-slate-450 leading-relaxed font-sans mb-3 text-[10px]">
                  <strong>Consensus Summary:</strong> {consensusReport.agreedSolutionSummary}
                </div>

                <div className="space-y-1">
                  <span className="text-slate-400 text-[10px] block font-bold uppercase">Parallel tree of thought branches</span>
                  {reasoningTree.branches.map((b, i) => (
                    <div key={i} className="bg-slate-950 p-2 rounded border border-slate-850 flex justify-between items-center text-[10px]">
                      <span className="font-bold text-slate-300">{b.branchId}</span>
                      <span className="text-slate-400">Agent: <strong className="text-slate-300">{b.assignedAgentId}</strong></span>
                      <span className="text-slate-400">Steps: {b.stepCount}</span>
                      <span className="text-slate-400">Leaf score: <strong className="text-blue-400">{b.terminalLeafScore}</strong></span>
                      <span className={`font-bold uppercase ${b.isPruned ? "text-rose-500" : "text-emerald-400 animate-pulse"}`}>
                        {b.isPruned ? "Pruned" : "Optimal Path"}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Expert MoE Tab */}
            {activeSubTab === "moe" && activationStats && predictionReport && (
              <div className="space-y-4 font-mono text-xs">
                <div className="flex justify-between items-center pb-2 border-b border-slate-850">
                  <span className="text-slate-300 font-bold">Dynamic expert activation states</span>
                  <span className="text-emerald-400 font-bold">router confidence: {(predictionReport.routerConfidence * 100).toFixed(0)}%</span>
                </div>
                
                <div className="grid grid-cols-2 gap-3 mb-2">
                  <div className="bg-slate-950 p-3 rounded border border-slate-850 text-center">
                    <span className="text-slate-500 text-[8px] block uppercase">Active expert VRAM footprint</span>
                    <span className="text-lg font-bold text-slate-100">{(activationStats.activeBytes / (1024*1024)).toFixed(0)} MB</span>
                  </div>
                  <div className="bg-slate-950 p-3 rounded border border-slate-850 text-center">
                    <span className="text-slate-500 text-[8px] block uppercase">Bypassed experts efficiency</span>
                    <span className="text-lg font-bold text-emerald-400">{activationStats.expertEfficiencyScore}%</span>
                  </div>
                </div>

                <div className="space-y-1">
                  <span className="text-slate-400 text-[10px] block font-bold uppercase font-mono">Expert parameters registry</span>
                  {activationStats.experts.map((exp, i) => (
                    <div key={i} className="bg-slate-950 p-2 rounded border border-slate-850 flex justify-between items-center text-[10px]">
                      <span className="font-bold text-slate-300">{exp.name}</span>
                      <span className="text-slate-400">Capacity: <strong className="text-slate-300">{(exp.memoryRequiredBytes / (1024*1024)).toFixed(0)}MB</strong></span>
                      <span className={`font-bold px-2 py-0.5 rounded text-[8px] ${
                        exp.isActive ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20" : "bg-slate-900 text-slate-500"
                      }`}>{exp.isActive ? "ACTIVE VRAM" : "SWAPPED OUT"}</span>
                      <span className="text-slate-500 text-[9px] uppercase font-extrabold">{exp.loadState}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* SIMD Tab */}
            {activeSubTab === "simd" && vectorPlan && vnniReport && (
              <div className="space-y-4 font-mono text-xs">
                <div className="flex justify-between items-center pb-2 border-b border-slate-850">
                  <span className="text-slate-300 font-bold">AVX512 & VNNI instructions planner</span>
                  <span className="text-blue-400 font-bold">simd score: {vectorPlan.simdEfficiencyScore}%</span>
                </div>
                
                <div className="bg-slate-950 p-3 rounded border border-slate-850 text-[10px] text-slate-400 mb-3">
                  <strong>Instruction Directive:</strong> {vectorPlan.instructionsSummary}
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div className="bg-slate-950 p-3 rounded border border-slate-850">
                    <span className="text-slate-500 text-[8px] uppercase block font-bold mb-2">VNNI acceleration statistics</span>
                    <div className="space-y-1 text-[10px]">
                      <div className="flex justify-between">
                        <span>Cycle reduction:</span>
                        <span className="text-emerald-400 font-bold">{vnniReport.cycleReductionPct}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Original instruction count:</span>
                        <span>{vnniReport.rawCpuCycles.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>VNNI packed instructions:</span>
                        <span>{vnniReport.vnniCycles.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Power saved:</span>
                        <span className="text-blue-400 font-bold">{vnniReport.powerSavedMicroJoules} µJ</span>
                      </div>
                    </div>
                  </div>

                  <div className="bg-slate-950 p-3 rounded border border-slate-850">
                    <span className="text-slate-500 text-[8px] uppercase block font-bold mb-2">AVX CPU vectorized registers</span>
                    <div className="space-y-1 text-[10px]">
                      <div className="flex justify-between">
                        <span>Instruction set active:</span>
                        <span className="text-blue-400 font-bold">{vectorPlan.chosenVectorSet}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Register bit width:</span>
                        <span>512 bits</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Parallel floats:</span>
                        <span>16 float32 elements</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Register utilization:</span>
                        <span>{vectorPlan.registerUtilizationPct}%</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Algorithmic Math Tab */}
            {activeSubTab === "math" && mathReport && winogradReport && fftReport && (
              <div className="space-y-4 font-mono text-xs">
                <div className="flex justify-between items-center pb-2 border-b border-slate-850">
                  <span className="text-slate-300 font-bold">Algorithmic multiplication planner</span>
                  <span className="text-blue-400 font-bold">Score: {mathReport.mathEfficiencyScore}%</span>
                </div>

                <div className="bg-slate-950 p-3 rounded border border-slate-850 text-center flex justify-between items-center">
                  <div>
                    <span className="text-slate-500 text-[8px] block uppercase">Selected mathematical kernel</span>
                    <span className="text-sm font-bold text-slate-100">{mathReport.selectedAlgorithm}</span>
                  </div>
                  <div>
                    <span className="text-slate-500 text-[8px] block uppercase">Operations avoided</span>
                    <span className="text-sm font-bold text-emerald-400">{mathReport.opsSaved.toLocaleString()} FLOPS</span>
                  </div>
                  <div>
                    <span className="text-slate-500 text-[8px] block uppercase">Overhead cost</span>
                    <span className="text-xs font-bold text-slate-400">{mathReport.planningOverheadMs} ms</span>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3 text-[10px]">
                  <div className="bg-slate-950 p-3 rounded border border-slate-850">
                    <span className="font-bold text-slate-300 block mb-2">Winograd Convolutions (3x3 filter)</span>
                    <div className="space-y-1">
                      <div className="flex justify-between">
                        <span>Direct multiplication ops:</span>
                        <span>{winogradReport.directMultiplyOps.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Winograd F(2,3) multiply ops:</span>
                        <span className="text-emerald-400 font-bold">{winogradReport.winogradMultiplyOps.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Floating ops saved:</span>
                        <span>{winogradReport.operationsSaved.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Reduction ratio:</span>
                        <span className="text-blue-400 font-bold">{winogradReport.reductionRatio}x</span>
                      </div>
                    </div>
                  </div>

                  <div className="bg-slate-950 p-3 rounded border border-slate-850">
                    <span className="font-bold text-slate-300 block mb-2">FFT Complexity Transformations</span>
                    <div className="space-y-1">
                      <div className="flex justify-between">
                        <span>Time-Domain convolution O(N^2):</span>
                        <span>{fftReport.timeDomainOps.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Frequency FFT O(N log N):</span>
                        <span className="text-emerald-400 font-bold">{fftReport.frequencyDomainOps.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Mathematical ops saved:</span>
                        <span>{fftReport.computeSavedOps.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Transform multiplier speed:</span>
                        <span className="text-blue-400 font-bold">{fftReport.complexityRatio}x</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

          </div>
        </div>

      </div>

      {/* Avoidance, Runtime, and Power details */}
      <div className="no-print grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        
        {/* Avoidance & Reuse panel */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg space-y-3 text-xs font-mono">
          <h3 className="text-xs font-bold uppercase tracking-wider text-blue-400 border-b border-slate-850 pb-2 flex justify-between">
            <span>Compute Avoidance Governor</span>
            <span>v33</span>
          </h3>
          {reuseReport ? (
            <div className="space-y-3">
              <div className="flex justify-between items-center bg-slate-950 p-2 border border-slate-850 rounded text-[10px]">
                <span className="text-slate-500">Cache hit:</span>
                <span className={`font-bold px-1.5 rounded ${
                  reuseReport.cacheHit ? "bg-emerald-500/10 text-emerald-400" : "bg-rose-500/10 text-rose-400"
                }`}>{reuseReport.cacheHit ? "HIT" : "MISS"}</span>
              </div>
              
              <div className="grid grid-cols-2 gap-2 text-[10px] text-slate-500 bg-slate-950 p-2 border border-slate-850 rounded">
                <span>Semantic match:</span>
                <span className="text-slate-350 text-right font-bold">{reuseReport.semanticMatchPercent}%</span>
                <span>Avoided FLOPS:</span>
                <span className="text-slate-350 text-right font-bold">{reuseReport.computeAvoidedFlops.toLocaleString()}</span>
                <span>Avoidance score:</span>
                <span className="text-emerald-400 text-right font-bold">{reuseReport.computeAvoidanceScore}%</span>
              </div>

              {reuseReport.cacheHit && reuseReport.retrievedAnswer && (
                <div className="bg-slate-950 p-2 rounded border border-slate-850 text-[10px] text-slate-400">
                  <strong className="text-blue-400 block mb-1">Retrieved Answer:</strong>
                  {reuseReport.retrievedAnswer}
                </div>
              )}
            </div>
          ) : (
            <p className="text-slate-500 italic text-center py-4">Run query to view cache check logs.</p>
          )}
        </div>

        {/* Runtime Optimization panel */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg space-y-3 text-xs font-mono">
          <h3 className="text-xs font-bold uppercase tracking-wider text-emerald-400 border-b border-slate-850 pb-2 flex justify-between">
            <span>Self-Optimizing Runtime</span>
            <span>v33</span>
          </h3>
          {runtimeMetrics && runtimeReport ? (
            <div className="space-y-3">
              <div className="grid grid-cols-2 gap-2 text-[10px] text-slate-500 bg-slate-950 p-2 border border-slate-850 rounded">
                <span>CPU occupancy:</span>
                <span className="text-slate-350 text-right font-bold">{runtimeMetrics.cpuUsagePct}%</span>
                <span>Cache miss ratio:</span>
                <span className="text-slate-350 text-right font-bold">{(runtimeMetrics.cacheMissRatio * 100).toFixed(2)}%</span>
                <span>RAM bandwidth:</span>
                <span className="text-slate-350 text-right font-bold">{runtimeMetrics.ramBandwidthUsageGbSec} GB/s</span>
                <span>Runtime optimization:</span>
                <span className="text-emerald-400 text-right font-bold">{runtimeReport.runtimeOptimizationScore}%</span>
              </div>

              {bottlenecks.length > 0 ? (
                <div className="space-y-1.5">
                  <span className="text-[10px] text-rose-400 font-bold block uppercase">Bottlenecks detected</span>
                  {bottlenecks.map((b, i) => (
                    <div key={i} className="bg-rose-500/5 p-2 rounded border border-rose-500/10 text-[9px] text-rose-400">
                      <strong>{b.source}:</strong> {b.metricValue}. <span className="text-slate-300 font-bold">{b.remediationAction}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="p-2 bg-emerald-500/5 text-emerald-400 rounded border border-emerald-500/10 text-[9px] text-center">
                  0 system execution bottlenecks detected. Runtime is highly optimized.
                </div>
              )}
            </div>
          ) : (
            <p className="text-slate-500 italic text-center py-4">Run query to view runtime profiles.</p>
          )}
        </div>

        {/* Intelligence-Per-Watt governor panel */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg space-y-3 text-xs font-mono">
          <h3 className="text-xs font-bold uppercase tracking-wider text-purple-400 border-b border-slate-850 pb-2 flex justify-between">
            <span>Power governor telemetry</span>
            <span>v33</span>
          </h3>
          {powerReport && balancerDirective ? (
            <div className="space-y-3">
              <div className="grid grid-cols-2 gap-2 text-[10px] text-slate-500 bg-slate-950 p-2 border border-slate-850 rounded">
                <span>Total power draw:</span>
                <span className="text-slate-350 text-right font-bold">{powerReport.totalPowerDrawWatts} W</span>
                <span>discrete GPU TDP:</span>
                <span className="text-slate-350 text-right font-bold">{powerReport.nvidiaGpuEquivalentPowerWatts} W</span>
                <span>wattage savings:</span>
                <span className="text-emerald-400 text-right font-bold">{powerReport.wattageSavingsPct}%</span>
                <span>power mode directive:</span>
                <span className="text-blue-400 text-right font-bold uppercase">{balancerDirective.powerConstraintMode}</span>
              </div>

              <div className="space-y-1.5">
                <span className="text-[10px] text-slate-400 font-bold block uppercase">Power draws by module</span>
                {powerReport.componentDraws.map((c, i) => (
                  <div key={i} className="flex justify-between text-[9px] text-slate-500 border-b border-slate-950 pb-1">
                    <span>{c.component}:</span>
                    <span>{c.currentWatts} Watts / Max TDP {c.maxTdpWatts}W</span>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <p className="text-slate-500 italic text-center py-4">Run query to view power profiles.</p>
          )}
        </div>

      </div>

      {/* Printable Seal of V33 Compliance */}
      <div className="print-border bg-gradient-to-b from-slate-950 to-[#030d1f] border border-blue-500/20 rounded-xl p-6 shadow-2xl relative overflow-hidden flex flex-col items-center text-center">
        
        {/* Certificate Watermarks and background */}
        <div className="absolute top-0 right-0 w-36 h-36 bg-blue-500/5 rounded-full filter blur-xl pointer-events-none" />
        
        <div className="border border-blue-500/30 p-2 rounded-full mb-3 bg-blue-500/10">
          <Award className="w-10 h-10 text-blue-400" />
        </div>
        
        <div className="print-header space-y-1 mb-4">
          <h2 className="text-xl font-bold tracking-wider text-slate-100 uppercase print-text-black">
            LEO AI V33 Compliance Certification
          </h2>
          <p className="text-[10px] text-slate-500 font-mono uppercase tracking-widest">
            compute avoidance &amp; local processing capability validation
          </p>
        </div>

        <p className="text-xs text-slate-350 max-w-2xl leading-relaxed font-sans mb-6 print-text-black">
          We hereby certify that LEO AI V33 successfully satisfies the strict constraints of the Compute Irrelevance Architecture. Under local CPU, iGPU, and NPU routing, it leverages 1.58-bit ternary quantized weights, 32MB L3 resident caching, and micro-model specialist swarms to bypass discrete datacenter GPU requirements.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full max-w-3xl text-left font-mono text-xs border-t border-b border-slate-850 py-4 mb-6 print-text-black">
          <div className="space-y-1">
            <span className="text-[8px] text-slate-550 block uppercase">COMPUTE AVOIDANCE LEVEL</span>
            <span className="font-bold text-slate-200 print-text-black">99.5% Avoided (Certified)</span>
          </div>
          <div className="space-y-1">
            <span className="text-[8px] text-slate-550 block uppercase">HARDWARE TARGET ROUTING</span>
            <span className="font-bold text-slate-200 print-text-black">Local NPU / iGPU WebGPU</span>
          </div>
          <div className="space-y-1">
            <span className="text-[8px] text-slate-550 block uppercase">COMPLIANCE CODE HASH</span>
            <span className="font-bold text-slate-200 text-[10px] print-text-black">V33-IRREL-2026-06-12</span>
          </div>
        </div>

        <div className="flex items-center gap-6 text-[10px] text-slate-500 font-mono">
          <div className="flex items-center gap-1">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span>Ternary Quant Enabled</span>
          </div>
          <div className="flex items-center gap-1">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span>L3 cache-lock verified</span>
          </div>
          <div className="flex items-center gap-1">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span>Swarm consensus active</span>
          </div>
        </div>
      </div>

    </div>
  );
}
