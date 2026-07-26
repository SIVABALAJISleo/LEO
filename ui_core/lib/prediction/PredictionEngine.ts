import { LazyExecutor } from "../optimization/LazyExecutor";

// eslint-disable-next-line @typescript-eslint/no-unused-vars
interface ActionCount {
  action: string;
  count: number;
  lastSeen: number;
}

interface Transition {
  from: string;
  to: string;
  count: number;
}

export class PredictionEngine {
  private static instance: PredictionEngine;
  private actionHistory: string[] = [];
  private transitions: Map<string, Transition[]> = new Map();
  private lazy: LazyExecutor;
  private readonly HISTORY_SIZE = 100;

  private constructor() {
    this.lazy = LazyExecutor.getInstance();
  }

  static getInstance(): PredictionEngine {
    if (!PredictionEngine.instance) {
      PredictionEngine.instance = new PredictionEngine();
    }
    return PredictionEngine.instance;
  }

  recordAction(action: string) {
    if (this.actionHistory.length > 0) {
      const previous = this.actionHistory[this.actionHistory.length - 1];
      this.recordTransition(previous, action);
    }

    this.actionHistory.push(action);
    if (this.actionHistory.length > this.HISTORY_SIZE) {
      this.actionHistory.shift();
    }
  }

  predictNext(currentAction: string): string[] {
    const transitions = this.transitions.get(currentAction) || [];
    const sorted = transitions.sort((a, b) => b.count - a.count);
    return sorted.slice(0, 3).map((t) => t.to);
  }

  prefetch(currentAction: string, prefetchHandler: (action: string) => Promise<void>) {
    const predictions = this.predictNext(currentAction);

    // Schedule prefetching in background
    predictions.forEach((predicted, index) => {
      this.lazy.defer(async () => {
        console.log(`[PredictionEngine] Prefetching: ${predicted}`);
        await prefetchHandler(predicted);
      }, index); // Lower priority for later predictions
    });
  }

  private recordTransition(from: string, to: string) {
    const existing = this.transitions.get(from) || [];
    const transition = existing.find((t) => t.to === to);

    if (transition) {
      transition.count++;
    } else {
      existing.push({ from, to, count: 1 });
    }

    this.transitions.set(from, existing);
  }

  getHeatmap(): Record<string, number> {
    const heatmap: Record<string, number> = {};

    for (const action of this.actionHistory) {
      heatmap[action] = (heatmap[action] || 0) + 1;
    }

    return heatmap;
  }
}
