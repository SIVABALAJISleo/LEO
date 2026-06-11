// V24 — Phase 6 Agent Effectiveness Optimizer
// Measures and optimizes agent routing, promoting high-performance models and evicting sub-performing routes

export interface AgentV24 {
  name: string;
  role: string;
  accuracy: number;
  latencyMs: number;
  reliability: number;
  verificationRate: number;
  status: "Active-Promoted" | "Active-Standard" | "Quarantined" | "Retired";
}

export class AgentEffectivenessOptimizer {
  private agents: AgentV24[] = [];

  constructor() {
    this.seedAgents();
  }

  private seedAgents() {
    this.agents = [
      {
        name: "ConvergencePlanner-V24",
        role: "Hierarchical Task Deconstruction",
        accuracy: 0.991,
        latencyMs: 125,
        reliability: 0.995,
        verificationRate: 0.99,
        status: "Active-Promoted"
      },
      {
        name: "FactSentinel-V24",
        role: "RAG Fact Checker",
        accuracy: 0.994,
        latencyMs: 85,
        reliability: 0.998,
        verificationRate: 0.995,
        status: "Active-Promoted"
      },
      {
        name: "ColloquialTranslator-V24",
        role: "Tamil-English Dialect Normalizer",
        accuracy: 0.972,
        latencyMs: 160,
        reliability: 0.965,
        verificationRate: 0.96,
        status: "Active-Standard"
      },
      {
        name: "LegacyTokenizer-V10",
        role: "Basic Query Parsing",
        accuracy: 0.782,
        latencyMs: 380,
        reliability: 0.702,
        verificationRate: 0.65,
        status: "Active-Standard" // candidate for retirement
      },
      {
        name: "MathSMTProver-V20",
        role: "Theorem Prover & SAT Solver",
        accuracy: 0.954,
        latencyMs: 250,
        reliability: 0.941,
        verificationRate: 0.95,
        status: "Active-Standard"
      }
    ];
  }

  optimize(): { agents: AgentV24[]; log: string } {
    let log = "";
    const promoted: string[] = [];
    const retired: string[] = [];

    this.agents = this.agents.map(a => {
      const compositeScore = (a.accuracy * 0.4) + (a.reliability * 0.3) + (a.verificationRate * 0.3);

      if (compositeScore > 0.985 && a.status !== "Active-Promoted") {
        a.status = "Active-Promoted";
        promoted.push(a.name);
      } else if (compositeScore < 0.82 && a.status !== "Retired") {
        a.status = "Retired";
        retired.push(a.name);
      }

      return a;
    });

    if (promoted.length > 0) {
      log += `Promoted agents to Active-Promoted: ${promoted.join(", ")}. `;
    }
    if (retired.length > 0) {
      log += `Retired sub-performing agents: ${retired.join(", ")}. `;
    }

    if (!log) {
      log = "All routing slots operate at optimal latency and safety levels.";
    }

    return {
      agents: this.agents,
      log
    };
  }

  getAgents(): AgentV24[] {
    return this.agents.sort((a, b) => {
      const scoreA = (a.accuracy + a.reliability + a.verificationRate) / 3;
      const scoreB = (b.accuracy + b.reliability + b.verificationRate) / 3;
      return scoreB - scoreA;
    });
  }

  registerMetric(name: string, success: boolean, latencyMs: number) {
    const a = this.agents.find(ag => ag.name === name);
    if (a) {
      a.latencyMs = Math.round(a.latencyMs * 0.9 + latencyMs * 0.1);
      const outputVal = success ? 1.0 : 0.0;
      a.reliability = parseFloat((a.reliability * 0.95 + outputVal * 0.05).toFixed(3));
      a.accuracy = parseFloat((a.accuracy * 0.98 + (success ? 1.0 : 0.78) * 0.02).toFixed(3));
    }
  }
}
