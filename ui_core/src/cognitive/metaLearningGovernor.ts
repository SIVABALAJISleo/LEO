/**
 * PHASE 5: Meta Learning System
 * Identifies and selects the best reasoning, planning, memory, and retrieval pathways
 * to continuously improve intelligence execution over time.
 */

export interface PathMetric {
  pathId: string;
  name: string;
  category: "agent" | "retrieval" | "memory" | "planning";
  successCount: number;
  failureCount: number;
  avgResponseTimeMs: number;
  rewardScore: number;
}

export class MetaLearningGovernor {
  private pathways: PathMetric[] = [
    { pathId: "A1", name: "6-Agent Round-Robin Debate", category: "agent", successCount: 142, failureCount: 4, avgResponseTimeMs: 1400, rewardScore: 0.96 },
    { pathId: "A2", name: "Direct Single-Agent Critique", category: "agent", successCount: 98, failureCount: 12, avgResponseTimeMs: 320, rewardScore: 0.88 },
    { pathId: "R1", name: "GraphRAG Causal Context Mapping", category: "retrieval", successCount: 204, failureCount: 5, avgResponseTimeMs: 450, rewardScore: 0.97 },
    { pathId: "R2", name: "Direct Semantic Vector Cache Lookup", category: "retrieval", successCount: 450, failureCount: 22, avgResponseTimeMs: 5, rewardScore: 0.94 },
    { pathId: "M1", name: "Temporal Decay Memory Store", category: "memory", successCount: 110, failureCount: 2, avgResponseTimeMs: 12, rewardScore: 0.98 },
    { pathId: "P1", name: "Critical Path Decomposition Planner", category: "planning", successCount: 85, failureCount: 6, avgResponseTimeMs: 650, rewardScore: 0.92 },
  ];

  /**
   * Logs execution outcomes and computes the pathway rewards.
   */
  public logPathResult(pathId: string, isSuccess: boolean, latencyMs: number): void {
    const path = this.pathways.find(p => p.pathId === pathId);
    if (!path) return;

    if (isSuccess) {
      path.successCount += 1;
    } else {
      path.failureCount += 1;
    }

    // Running average of response times
    path.avgResponseTimeMs = Math.round((path.avgResponseTimeMs * 0.9) + (latencyMs * 0.1));

    // Update reward: higher success rate and lower latency increases reward
    const successRate = path.successCount / (path.successCount + path.failureCount);
    const latencyPenalty = Math.max(0.1, 1 - (path.avgResponseTimeMs / 5000));
    path.rewardScore = (successRate * 0.7) + (latencyPenalty * 0.3);
  }

  /**
   * Recommends the optimal pathway configuration for a given query type.
   */
  public recommendPathways(queryCategory: "logic" | "speed" | "safety"): Record<string, string> {
    const getBest = (cat: "agent" | "retrieval" | "memory" | "planning") => {
      const candidates = this.pathways.filter(p => p.category === cat);
      if (queryCategory === "speed") {
        // Prioritize low latency
        return candidates.sort((a, b) => a.avgResponseTimeMs - b.avgResponseTimeMs)[0];
      }
      // Prioritize reward score
      return candidates.sort((a, b) => b.rewardScore - a.rewardScore)[0];
    };

    return {
      agentPath: getBest("agent").name,
      retrievalPath: getBest("retrieval").name,
      memoryPath: getBest("memory").name,
      planningPath: getBest("planning").name,
    };
  }

  public getPathways(): PathMetric[] {
    return this.pathways;
  }
}
