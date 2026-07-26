// V22 — Phase 6: Agent Performance Evolution
// Dynamic priority queue: best agents gain priority, weak agents lose priority

export type AgentDomain =
  | "Reasoning"
  | "RAG"
  | "Language"
  | "Code"
  | "Search"
  | "Security"
  | "Memory"
  | "Planning"
  | "Enterprise"
  | "Verification";

export interface AgentRecord {
  agentId: string;
  name: string;
  domain: AgentDomain;
  accuracyScore: number; // 0–1
  latencyScore: number; // 0–1 (1 = fastest)
  reliabilityScore: number; // 0–1
  verificationScore: number; // 0–1
  compositeScore: number; // weighted average
  priority: number; // 1 = highest priority
  tasksCompleted: number;
  tasksSucceeded: number;
  isActive: boolean;
}

export interface AgentLeaderboard {
  agents: AgentRecord[];
  promoted: string[];
  demoted: string[];
  cycleNumber: number;
}

const AGENT_DEFS: { name: string; domain: AgentDomain }[] = [
  { name: "ReasonCore", domain: "Reasoning" },
  { name: "RAGMaster", domain: "RAG" },
  { name: "LinguaAgent", domain: "Language" },
  { name: "CodeSentinel", domain: "Code" },
  { name: "SearchVector", domain: "Search" },
  { name: "SecureGuard", domain: "Security" },
  { name: "MemoryKeeper", domain: "Memory" },
  { name: "PlannerPrime", domain: "Planning" },
  { name: "EnterpriseCog", domain: "Enterprise" },
  { name: "VerifyBot", domain: "Verification" },
];

const compositeScore = (a: AgentRecord): number =>
  a.accuracyScore * 0.35 +
  a.latencyScore * 0.2 +
  a.reliabilityScore * 0.25 +
  a.verificationScore * 0.2;

export class AgentPerformanceEvolution {
  private agents: Map<string, AgentRecord>;
  private cycle = 0;

  constructor() {
    this.agents = new Map();
    AGENT_DEFS.forEach((def, idx) => {
      const id = `AGT-${String(idx + 1).padStart(3, "0")}`;
      const acc = 0.88 + Math.random() * 0.11;
      const lat = 0.8 + Math.random() * 0.18;
      const rel = 0.85 + Math.random() * 0.13;
      const ver = 0.87 + Math.random() * 0.11;
      const rec: AgentRecord = {
        agentId: id,
        name: def.name,
        domain: def.domain,
        accuracyScore: acc,
        latencyScore: lat,
        reliabilityScore: rel,
        verificationScore: ver,
        compositeScore: 0,
        priority: idx + 1,
        tasksCompleted: Math.floor(Math.random() * 500) + 100,
        tasksSucceeded: 0,
        isActive: true,
      };
      rec.tasksSucceeded = Math.floor(rec.tasksCompleted * acc);
      rec.compositeScore = compositeScore(rec);
      this.agents.set(id, rec);
    });
  }

  evolve(): AgentLeaderboard {
    this.cycle++;
    const promoted: string[] = [];
    const demoted: string[] = [];

    // Simulate task outcomes and update scores
    for (const agent of this.agents.values()) {
      const delta = (Math.random() - 0.48) * 0.03; // slight positive bias
      agent.accuracyScore = Math.min(0.99, Math.max(0.6, agent.accuracyScore + delta));
      agent.latencyScore = Math.min(
        0.99,
        Math.max(0.55, agent.latencyScore + (Math.random() - 0.5) * 0.02),
      );
      agent.reliabilityScore = Math.min(
        0.99,
        Math.max(0.65, agent.reliabilityScore + (Math.random() - 0.45) * 0.02),
      );
      agent.verificationScore = Math.min(
        0.99,
        Math.max(0.65, agent.verificationScore + (Math.random() - 0.48) * 0.02),
      );

      const oldComposite = agent.compositeScore;
      agent.compositeScore = compositeScore(agent);
      agent.tasksCompleted += Math.floor(Math.random() * 20) + 5;
      agent.tasksSucceeded += Math.floor((Math.random() * 20 + 5) * agent.accuracyScore);

      if (agent.compositeScore > oldComposite + 0.005) promoted.push(agent.name);
      else if (agent.compositeScore < oldComposite - 0.005) demoted.push(agent.name);
    }

    // Re-rank by composite score
    const sorted = Array.from(this.agents.values()).sort(
      (a, b) => b.compositeScore - a.compositeScore,
    );
    sorted.forEach((agent, idx) => {
      agent.priority = idx + 1;
    });

    return {
      agents: sorted,
      promoted,
      demoted,
      cycleNumber: this.cycle,
    };
  }

  getAgents(): AgentRecord[] {
    return Array.from(this.agents.values()).sort((a, b) => a.priority - b.priority);
  }

  routeTask(domain: AgentDomain): AgentRecord | undefined {
    return Array.from(this.agents.values())
      .filter((a) => a.domain === domain && a.isActive)
      .sort((a, b) => b.compositeScore - a.compositeScore)[0];
  }
}
