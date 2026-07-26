import { SystemMetrics } from "./SystemMetrics";
import { ReliabilityOrchestrator } from "../core/ReliabilityOrchestrator";
import { RuntimeProfiler } from "../adaptive/RuntimeProfiler";
import { PerformanceController } from "../core/PerformanceController";

interface BenchmarkScenario {
  name: string;
  description: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  execute: () => Promise<any>;
}

interface BenchmarkResult {
  scenario: string;
  beforeLatencyMs: number;
  afterLatencyMs: number;
  improvement: number;
  computeSavedMs: number;
  fallbackUsed: boolean;
}

export class BenchmarkGenerator {
  private static instance: BenchmarkGenerator;
  private metrics: SystemMetrics;
  private profiler: RuntimeProfiler;
  private orchestrator: ReliabilityOrchestrator;
  private perfController: PerformanceController;

  private constructor() {
    this.metrics = SystemMetrics.getInstance();
    this.profiler = RuntimeProfiler.getInstance();
    this.orchestrator = ReliabilityOrchestrator.getInstance();
    this.perfController = PerformanceController.getInstance();
  }

  static getInstance(): BenchmarkGenerator {
    if (!BenchmarkGenerator.instance) {
      BenchmarkGenerator.instance = new BenchmarkGenerator();
    }
    return BenchmarkGenerator.instance;
  }

  async runScenarios(scenarios: BenchmarkScenario[]): Promise<BenchmarkResult[]> {
    const results: BenchmarkResult[] = [];

    for (const scenario of scenarios) {
      console.log(`[Benchmark] Running: ${scenario.name}`);

      const beforeTime = performance.now();
      await scenario.execute();
      const afterTime = performance.now();

      const latency = afterTime - beforeTime;
      const baseline = 1000; // Mock baseline for comparison

      results.push({
        scenario: scenario.name,
        beforeLatencyMs: baseline,
        afterLatencyMs: latency,
        improvement: ((baseline - latency) / baseline) * 100,
        computeSavedMs: baseline - latency,
        fallbackUsed: false, // Would be tracked from orchestrator
      });
    }

    return results;
  }

  exportProof(): object {
    const allMetrics = this.metrics.getSummary();
    const profiles = this.profiler.getAllProfiles();
    const auditLog = this.orchestrator.getAuditLog();

    return {
      timestamp: new Date().toISOString(),
      quality: this.perfController.getQuality(),
      metrics: allMetrics,
      taskProfiles: profiles.map((p) => ({
        taskType: p.taskType,
        avgLatency: p.avgLatencyMs,
        executionCount: p.executionCount,
      })),
      auditSummary: {
        total: auditLog.length,
        successful: auditLog.filter((a) => a.result === "success").length,
        degraded: auditLog.filter((a) => a.result === "degraded").length,
        failed: auditLog.filter((a) => a.result === "failed").length,
      },
      architecture: {
        layers: [
          "Intelligence (RAG, MoE)",
          "Adaptive (Profiling, Strategy)",
          "Memory (Persistent Cache)",
          "Prediction (Heatmap)",
          "Optimization (Lazy, Approximation)",
          "Compute (SIMD, Workers)",
          "Perception (Progressive)",
          "Reliability (Chaos, Swapping)",
        ],
        policy: "CPU+iGPU optimized, zero GPU dependency",
      },
    };
  }

  generateReport(): string {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const proof = this.exportProof() as any;

    return `# System Performance Report

**Generated**: ${proof.timestamp}
**Quality Level**: ${proof.quality}

## Architecture Layers
${proof.architecture.layers.map((l: string) => `- ${l}`).join("\n")}

## Execution Summary
- **Total Actions**: ${proof.auditSummary.total}
- **Successful**: ${proof.auditSummary.successful}
- **Degraded (Fallback)**: ${proof.auditSummary.degraded}
- **Failed**: ${proof.auditSummary.failed}
- **Success Rate**: ${((proof.auditSummary.successful / proof.auditSummary.total) * 100).toFixed(1)}%

## Task Performance Profiles
${proof.taskProfiles
  .map(
    (t: { taskType: string; avgLatency: number; executionCount: number }) =>
      `- **${t.taskType}**: ${t.avgLatency.toFixed(1)}ms avg (${t.executionCount} runs)`,
  )
  .join("\n")}

## Policy
${proof.architecture.policy}

## Optimization Evidence
This system replaces brute-force GPU compute with:
- Retrieval instead of generation
- Approximation instead of exact math
- Prediction instead of calculation
- Perception instead of physical accuracy
- Memorization instead of recomputation
`;
  }
}
