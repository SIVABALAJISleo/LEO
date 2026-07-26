// eslint-disable-next-line @typescript-eslint/no-unused-vars
import { RuntimeProfiler, TaskProfile } from "./RuntimeProfiler";
import { PerformanceController } from "../core/PerformanceController";

export type ExecutionStrategy = "retrieve" | "approximate" | "simulate" | "compute";

export interface StrategyDecision {
  strategy: ExecutionStrategy;
  confidence: number;
  reasoning: string;
}

export class StrategySelector {
  private static instance: StrategySelector;
  private profiler: RuntimeProfiler;
  private perfController: PerformanceController;

  private constructor() {
    this.profiler = RuntimeProfiler.getInstance();
    this.perfController = PerformanceController.getInstance();
  }

  static getInstance(): StrategySelector {
    if (!StrategySelector.instance) {
      StrategySelector.instance = new StrategySelector();
    }
    return StrategySelector.instance;
  }

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  selectStrategy(taskType: string, payloadSize: number = 1): StrategyDecision {
    const profile = this.profiler.getProfile(taskType);
    const quality = this.perfController.getQuality();

    // Strategy selection logic
    if (!profile || profile.executionCount < 3) {
      return {
        strategy: "compute",
        confidence: 0.5,
        reasoning: "Not enough profiling data, defaulting to compute",
      };
    }

    // If system is under load, prefer lighter strategies
    if (quality === "LOW") {
      if (profile.avgLatencyMs < 50) {
        return {
          strategy: "retrieve",
          confidence: 0.9,
          reasoning: "System under load, task is fast - using retrieval/cache",
        };
      }
      return {
        strategy: "approximate",
        confidence: 0.85,
        reasoning: "System under load, using approximation",
      };
    }

    // If task is historically expensive, consider alternatives
    if (profile.avgLatencyMs > 500) {
      return {
        strategy: "simulate",
        confidence: 0.8,
        reasoning: "Task is expensive, using simulation/precomputed results",
      };
    }

    // If task is fast, just compute
    if (profile.avgLatencyMs < 100) {
      return {
        strategy: "compute",
        confidence: 0.95,
        reasoning: "Task is fast enough to compute directly",
      };
    }

    // Medium complexity - check cache first
    return {
      strategy: "retrieve",
      confidence: 0.7,
      reasoning: "Medium complexity, attempting retrieval first",
    };
  }
}
