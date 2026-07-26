// LEO AI V36 — Consensus Layer
// Orchestrates voting mechanisms across swarm agents to align reasoning outputs.

export class ConsensusLayer {
  public evaluateVotes(votes: Array<{ agentId: string; choice: string }>): {
    consensusChoice: string;
    consensusRate: number;
  } {
    if (votes.length === 0) return { consensusChoice: "none", consensusRate: 0 };

    const counts: Record<string, number> = {};
    votes.forEach((v) => {
      counts[v.choice] = (counts[v.choice] || 0) + 1;
    });

    let consensusChoice = "";
    let maxVotes = 0;

    for (const key in counts) {
      if (counts[key] > maxVotes) {
        maxVotes = counts[key];
        consensusChoice = key;
      }
    }

    const consensusRate = parseFloat((maxVotes / votes.length).toFixed(3));
    return {
      consensusChoice,
      consensusRate,
    };
  }
}
