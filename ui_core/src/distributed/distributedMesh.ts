/**
 * Phase 14: Federated Intelligence Mesh
 * Path: ui_core/src/distributed/distributedMesh.ts
 * Purpose: Upgrades distributed mesh operations, tracking node trust ratings, coordinating consensus rounds, and resolving peer conflicts.
 */

export interface MeshNode {
  nodeId: string;
  trustRating: number; // 0 to 1
  latencyMs: number;
  status: "active" | "offline" | "restricted";
  agreedCrystalsCount: number;
}

export interface ConflictResolutionReport {
  conflictResolved: boolean;
  resolutionWinnerId: string;
  majorityConsensusValue: string;
  nodesAgreedPercentage: number;
}

export class DistributedMesh {
  private nodes: MeshNode[] = [
    {
      nodeId: "node-alpha-403",
      trustRating: 0.98,
      latencyMs: 14,
      status: "active",
      agreedCrystalsCount: 245,
    },
    {
      nodeId: "node-beta-201",
      trustRating: 0.95,
      latencyMs: 28,
      status: "active",
      agreedCrystalsCount: 182,
    },
    {
      nodeId: "node-gamma-612",
      trustRating: 0.88,
      latencyMs: 45,
      status: "active",
      agreedCrystalsCount: 94,
    },
    {
      nodeId: "node-malicious-99",
      trustRating: 0.15,
      latencyMs: 350,
      status: "restricted",
      agreedCrystalsCount: 2,
    },
  ];

  /**
   * Register or audit node connections.
   */
  public registerNode(nodeId: string, latencyMs: number, initialTrust: number): MeshNode {
    const existing = this.nodes.find((n) => n.nodeId === nodeId);
    if (existing) {
      existing.latencyMs = latencyMs;
      existing.status = "active";
      return existing;
    }

    const newNode: MeshNode = {
      nodeId,
      trustRating: initialTrust,
      latencyMs,
      status: initialTrust < 0.3 ? "restricted" : "active",
      agreedCrystalsCount: 0,
    };

    this.nodes.push(newNode);
    return newNode;
  }

  /**
   * Run distributed consensus validation for a crystal transaction.
   */
  public validateAcrossMesh(crystalId: string): {
    consensusReached: boolean;
    trustRatio: number;
    votingNodesCount: number;
  } {
    const activeNodes = this.nodes.filter((n) => n.status === "active");
    const votingCount = activeNodes.length;

    // Sum trust scores of active nodes
    const totalTrust = activeNodes.reduce((sum, n) => sum + n.trustRating, 0);
    const avgTrust = votingCount === 0 ? 0 : totalTrust / votingCount;

    // Consensus requires majority (>=2 nodes) and average trust rating > 0.80
    const consensusReached = votingCount >= 2 && avgTrust > 0.8;

    if (consensusReached) {
      activeNodes.forEach((n) => n.agreedCrystalsCount++);
    }

    return {
      consensusReached,
      trustRatio: parseFloat(avgTrust.toFixed(4)),
      votingNodesCount: votingCount,
    };
  }

  /**
   * Resolves conflicts when two nodes report contradicting knowledge crystal properties.
   */
  public resolveConflict(
    nodeAId: string,
    valueA: string,
    nodeBId: string,
    valueB: string,
  ): ConflictResolutionReport {
    const nodeA = this.nodes.find((n) => n.nodeId === nodeAId) || { trustRating: 0.5 };
    const nodeB = this.nodes.find((n) => n.nodeId === nodeBId) || { trustRating: 0.5 };

    let resolutionWinnerId = "";
    let majorityConsensusValue = "";

    // Conflict resolution rule: Highest node trust rating wins
    if (nodeA.trustRating >= nodeB.trustRating) {
      resolutionWinnerId = nodeAId;
      majorityConsensusValue = valueA;
    } else {
      resolutionWinnerId = nodeBId;
      majorityConsensusValue = valueB;
    }

    // Nodes agreed percentage: simple metric simulating peer confirmations
    const totalMeshTrust = this.nodes.reduce((sum, n) => sum + n.trustRating, 0);
    const winnerTrust =
      nodeA.trustRating >= nodeB.trustRating ? nodeA.trustRating : nodeB.trustRating;
    const nodesAgreedPercentage = parseFloat(((winnerTrust / totalMeshTrust) * 100).toFixed(2));

    return {
      conflictResolved: true,
      resolutionWinnerId,
      majorityConsensusValue,
      nodesAgreedPercentage,
    };
  }

  public getNodes(): MeshNode[] {
    return this.nodes;
  }
}
