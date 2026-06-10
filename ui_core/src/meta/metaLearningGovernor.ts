/**
 * Phase 8: Meta Learning Governor
 * Path: ui_core/src/meta/metaLearningGovernor.ts
 * Purpose: V16 Upgraded Meta Learning Governor. Automatically tracks and promotes high-performing strategies across retrieval, reasoning, agents, planners, and verifiers.
 */

export interface StrategyMetric {
  id: string;
  name: string;
  category: "reasoning" | "retrieval" | "agent" | "planner" | "verifier";
  accuracyRate: number;
  avgLatencyMs: number;
  rewards: number;
  promoted: boolean;
}

export class MetaLearningGovernor {
  private strategies: StrategyMetric[] = [
    // Reasoning
    { id: "S-REAS-01", name: "Systems Thinking Pipeline", category: "reasoning", accuracyRate: 0.96, avgLatencyMs: 220, rewards: 0.94, promoted: true },
    { id: "S-REAS-02", name: "Deductive Proof Validator", category: "reasoning", accuracyRate: 0.98, avgLatencyMs: 140, rewards: 0.97, promoted: false },
    { id: "S-REAS-03", name: "Counterfactual Analogy Resolver", category: "reasoning", accuracyRate: 0.89, avgLatencyMs: 290, rewards: 0.82, promoted: false },
    // Retrieval
    { id: "S-RETR-01", name: "Gossip Mesh CRDT Cache", category: "retrieval", accuracyRate: 0.95, avgLatencyMs: 9, rewards: 0.96, promoted: true },
    { id: "S-RETR-02", name: "GraphRAG Deep Traversal", category: "retrieval", accuracyRate: 0.97, avgLatencyMs: 340, rewards: 0.93, promoted: false },
    // Agent
    { id: "S-AGEN-01", name: "7-Agent Consensus Debate", category: "agent", accuracyRate: 0.98, avgLatencyMs: 1250, rewards: 0.97, promoted: true },
    { id: "S-AGEN-02", name: "Single Critic Audit Step", category: "agent", accuracyRate: 0.91, avgLatencyMs: 150, rewards: 0.88, promoted: false },
    // Planner
    { id: "S-PLAN-01", name: "Linear Milestone Decomposition", category: "planner", accuracyRate: 0.93, avgLatencyMs: 280, rewards: 0.91, promoted: false },
    { id: "S-PLAN-02", name: "Dependency-Graph Scheduler V2", category: "planner", accuracyRate: 0.97, avgLatencyMs: 380, rewards: 0.95, promoted: true },
    // Verifier
    { id: "S-VERI-01", name: "Calculated Proof & Verification", category: "verifier", accuracyRate: 0.99, avgLatencyMs: 110, rewards: 0.98, promoted: true },
    { id: "S-VERI-02", name: "Direct Regex Syntax Check", category: "verifier", accuracyRate: 0.85, avgLatencyMs: 15, rewards: 0.78, promoted: false }
  ];

  /**
   * Evaluates pathways, updating rewards and auto-promoting high-performing strategies.
   */
  public logExecutionReward(strategyId: string, success: boolean, latencyMs: number): void {
    const strategy = this.strategies.find(s => s.id === strategyId);
    if (!strategy) return;

    // Dampened updates
    const currentAcc = strategy.accuracyRate;
    const nextAcc = success ? Math.min(0.99, currentAcc * 0.95 + 0.05) : Math.max(0.5, currentAcc * 0.95);
    strategy.accuracyRate = parseFloat(nextAcc.toFixed(4));
    strategy.avgLatencyMs = Math.round((strategy.avgLatencyMs * 0.9) + (latencyMs * 0.1));

    // Re-calculate rewards
    const latencyFactor = Math.max(0.01, 1 - (strategy.avgLatencyMs / 3000));
    strategy.rewards = parseFloat(((strategy.accuracyRate * 0.7) + (latencyFactor * 0.3)).toFixed(4));

    // Dynamic promotion swap: Promote the highest rewarded strategy in this category
    const categoryStrategies = this.strategies.filter(s => s.category === strategy.category);
    const bestReward = Math.max(...categoryStrategies.map(s => s.rewards));

    categoryStrategies.forEach(s => {
      s.promoted = (s.rewards === bestReward);
    });
  }

  public recommendStrategies(): Record<string, StrategyMetric> {
    const getPromoted = (cat: "reasoning" | "retrieval" | "agent" | "planner" | "verifier"): StrategyMetric => {
      return this.strategies.find(s => s.category === cat && s.promoted) || 
             this.strategies.filter(s => s.category === cat).sort((a,b) => b.rewards - a.rewards)[0];
    };

    return {
      reasoning: getPromoted("reasoning"),
      retrieval: getPromoted("retrieval"),
      agent: getPromoted("agent"),
      planner: getPromoted("planner"),
      verifier: getPromoted("verifier")
    };
  }

  public getStrategies(): StrategyMetric[] {
    return this.strategies;
  }
}
