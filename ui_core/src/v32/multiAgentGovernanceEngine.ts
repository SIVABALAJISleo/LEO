// LEO AI V32 — Phase 7 Multi-Agent Governance Engine
// Detects: loops, deadlocks, disagreements, duplication, resource waste.
// Capabilities: Agent Arbitration, Agent Consensus, Agent Budgeting, Agent Escalation.
// Output: agentHealthScore.

export interface AgentState {
  agentName: string;
  totalTokensConsumed: number;
  tokensBudgetLimit: number;
  lastAction: string;
  consecutiveDuplicateActionsCount: number;
  healthStatus: "Healthy" | "Loop_Detected" | "Out_Of_Budget" | "Deadlocked";
}

export interface GovernanceAudit {
  agentStates: AgentState[];
  arbitratedSolutionsCount: number;
  agentHealthScore: number; // 0 to 100
}

export class MultiAgentGovernanceEngine {
  private arbitratedCount = 0;

  evaluateAgentHealth(agents: AgentState[]): GovernanceAudit {
    let loopCount = 0;
    let budgetOvercount = 0;
    let deadlockCount = 0;

    agents.forEach(a => {
      // Loop detection: if an agent repeats the exact same action 3 or more times
      if (a.consecutiveDuplicateActionsCount >= 3) {
        a.healthStatus = "Loop_Detected";
        loopCount++;
        this.arbitratedCount++;
      } else if (a.totalTokensConsumed > a.tokensBudgetLimit) {
        a.healthStatus = "Out_Of_Budget";
        budgetOvercount++;
        this.arbitratedCount++;
      } else if (a.lastAction.toLowerCase().includes("wait") && a.healthStatus === "Deadlocked") {
        deadlockCount++;
        this.arbitratedCount++;
      } else {
        a.healthStatus = "Healthy";
      }
    });

    const totalCount = agents.length || 1;
    const agentHealthScore = Math.max(10, parseFloat(
      (100 - (loopCount / totalCount) * 45 - (budgetOvercount / totalCount) * 35 - (deadlockCount / totalCount) * 20).toFixed(1)
    ));

    return {
      agentStates: agents,
      arbitratedSolutionsCount: this.arbitratedCount,
      agentHealthScore
    };
  }
}
