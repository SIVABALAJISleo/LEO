// LEO AI V32 — Phase 8 Agent Consensus System V2
// Agents: Agent A, Agent B, Agent C, Agent D, Agent E.
// Evaluate: correctness, evidence, confidence, latency.
// Consensus Methods: weighted voting, trust-weight voting, evidence-weight voting.

export interface AgentResponse {
  agentId: "Agent_A" | "Agent_B" | "Agent_C" | "Agent_D" | "Agent_E";
  proposedAnswer: string;
  correctnessConfidence: number; // 0 to 1.0
  evidenceQuality: number; // 0 to 10
  latencySec: number;
  trustFactor: number; // 0 to 10
}

export interface ConsensusVerdictV2 {
  responses: AgentResponse[];
  methodUsed: "WeightedVoting" | "TrustWeightVoting" | "EvidenceWeightVoting";
  finalConsensusAnswer: string;
  consensusScore: number;
}

export class AgentConsensusSystemV2 {
  coordinateConsensus(
    responses: AgentResponse[],
    method: "WeightedVoting" | "TrustWeightVoting" | "EvidenceWeightVoting",
  ): ConsensusVerdictV2 {
    let bestResponse = responses[0];
    let maxScore = -1;

    responses.forEach((r) => {
      let score = 0;

      if (method === "WeightedVoting") {
        // Average weight of confidence and latency
        const latencyPenalty = Math.max(0.1, r.latencySec);
        score = r.correctnessConfidence * 7.0 + (5.0 / latencyPenalty) * 3.0;
      } else if (method === "TrustWeightVoting") {
        // Rely heavily on long-term trust factor
        score = r.trustFactor * 0.7 + r.correctnessConfidence * 3.0;
      } else {
        // Evidence weight voting
        score = r.evidenceQuality * 0.8 + r.correctnessConfidence * 2.0;
      }

      if (score > maxScore) {
        maxScore = score;
        bestResponse = r;
      }
    });

    return {
      responses,
      methodUsed: method,
      finalConsensusAnswer: `[Consensus Chosen Response: ${bestResponse.agentId}] ${bestResponse.proposedAnswer}`,
      consensusScore: parseFloat(Math.min(10.0, maxScore).toFixed(2)),
    };
  }
}
