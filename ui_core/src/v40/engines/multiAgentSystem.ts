export interface AgentAction { agentName: string; contribution: string; confidenceScore: number; }
export interface AgentDebateReport { transcript: AgentAction[]; consensusScore: number; finalVerdict: string; }
export class MultiAgentSystem {
  public async executeAgentWorkflow(question: string): Promise<AgentDebateReport> {
    const res = await fetch("http://localhost:8000/api/v1/v40/engines/agents", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question })
    });
    return res.json();
  }
}
