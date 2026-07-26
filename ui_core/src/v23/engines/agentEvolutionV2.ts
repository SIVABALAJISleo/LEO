// V23 — Phase 6 Agent Evolution V2
// Tracks agent accuracy, latency, verification, and success rates, promoting/retiring dynamically

export interface AgentV23 {
  name: string;
  role: string;
  accuracy: number; // 0 to 1
  latencyMs: number;
  verificationRate: number; // 0 to 1
  successRate: number; // 0 to 1
  tier: "Elite" | "Standard" | "Quarantined" | "Retired";
}

export class AgentEvolutionV2 {
  private agents: AgentV23[] = [];

  constructor() {
    this.seedAgents();
  }

  private seedAgents() {
    this.agents = [
      {
        name: "OmniPlanner-V23",
        role: "Hierarchical Query Planning",
        accuracy: 0.985,
        latencyMs: 140,
        verificationRate: 0.99,
        successRate: 0.98,
        tier: "Elite",
      },
      {
        name: "FactSentinel-V23",
        role: "RAG Fact Checker",
        accuracy: 0.992,
        latencyMs: 90,
        verificationRate: 0.995,
        successRate: 0.99,
        tier: "Elite",
      },
      {
        name: "TamilLinguist-V23",
        role: "Tamil-English Slang Normalizer",
        accuracy: 0.965,
        latencyMs: 180,
        verificationRate: 0.95,
        successRate: 0.96,
        tier: "Standard",
      },
      {
        name: "LegacyResolver-V11",
        role: "Raw Text Query Parsing",
        accuracy: 0.812,
        latencyMs: 340,
        verificationRate: 0.72,
        successRate: 0.74,
        tier: "Standard", // Candidate for retirement
      },
      {
        name: "MathProver-V18",
        role: "Propositional Solver",
        accuracy: 0.941,
        latencyMs: 290,
        verificationRate: 0.92,
        successRate: 0.93,
        tier: "Standard",
      },
    ];
  }

  evolve(): { agents: AgentV23[]; auditSummary: string } {
    let auditSummary = "";
    const promoted: string[] = [];
    const retired: string[] = [];

    this.agents = this.agents.map((agent) => {
      const score = agent.accuracy * 0.4 + agent.successRate * 0.3 + agent.verificationRate * 0.3;

      if (score > 0.97 && agent.tier !== "Elite") {
        agent.tier = "Elite";
        promoted.push(agent.name);
      } else if (score < 0.85 && agent.tier !== "Retired" && agent.tier !== "Quarantined") {
        agent.tier = "Retired";
        retired.push(agent.name);
      }

      return agent;
    });

    if (promoted.length > 0) {
      auditSummary += `Promoted ${promoted.join(", ")} to Elite. `;
    }
    if (retired.length > 0) {
      auditSummary += `Retired sub-performing agents: ${retired.join(", ")}. `;
    }

    if (!auditSummary) {
      auditSummary =
        "All agents performing within expected calibration envelopes. No routing swaps required.";
    }

    return {
      agents: this.agents,
      auditSummary,
    };
  }

  getAgents(): AgentV23[] {
    return this.agents.sort((a, b) => {
      const scoreA = (a.accuracy + a.successRate + a.verificationRate) / 3;
      const scoreB = (b.accuracy + b.successRate + b.verificationRate) / 3;
      return scoreB - scoreA;
    });
  }

  registerAgentResult(name: string, success: boolean, latencyMs: number) {
    const agent = this.agents.find((a) => a.name === name);
    if (agent) {
      // Smooth average updates
      agent.latencyMs = Math.round(agent.latencyMs * 0.9 + latencyMs * 0.1);
      const outcome = success ? 1.0 : 0.0;
      agent.successRate = parseFloat((agent.successRate * 0.95 + outcome * 0.05).toFixed(3));
      agent.accuracy = parseFloat(
        (agent.accuracy * 0.98 + (success ? 1.0 : 0.8) * 0.02).toFixed(3),
      );
    }
  }
}
