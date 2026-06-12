// LEO AI V31 — Phase 15 Distributed Intelligence Mesh
// Purpose: Distribute rare expensive workloads.
// Rules: Local First → Peer Second → Cloud Last
// Goal: Minimize centralized/cloud compute overhead.

export type ExecutionNode = "Local_iGPU" | "Peer_Node" | "Cloud_HyperCluster";

export interface MeshNodeStatus {
  nodeId: string;
  type: ExecutionNode;
  availableFlopsGiga: number;
  latencyMs: number;
  costPerQueryDollar: number;
  online: boolean;
}

export interface WorkloadDistribution {
  query: string;
  assignedNodeId: string;
  nodeType: ExecutionNode;
  networkLatencyMs: number;
  processingLatencyMs: number;
  totalLatencyMs: number;
  costDollar: number;
  routingDecisions: string[];
}

export class DistributedIntelligenceMesh {
  private meshNodes: MeshNodeStatus[] = [
    { nodeId: "node-local-0", type: "Local_iGPU", availableFlopsGiga: 80, latencyMs: 5, costPerQueryDollar: 0.0, online: true },
    { nodeId: "node-peer-1", type: "Peer_Node", availableFlopsGiga: 250, latencyMs: 42, costPerQueryDollar: 0.002, online: true },
    { nodeId: "node-peer-2", type: "Peer_Node", availableFlopsGiga: 180, latencyMs: 65, costPerQueryDollar: 0.002, online: false },
    { nodeId: "node-cloud-3", type: "Cloud_HyperCluster", availableFlopsGiga: 8500, latencyMs: 185, costPerQueryDollar: 0.065, online: true }
  ];

  distribute(query: string, localLoadFactor: number = 0.5): WorkloadDistribution {
    const decisions: string[] = [];
    let selectedNode = this.meshNodes[0]; // default local
    let networkLatencyMs = 0;
    
    decisions.push("Evaluating local iGPU capacity...");

    // Heuristics for routing:
    // If local load is high or query is extremely heavy, evaluate peers first, then fallback to cloud
    const isHeavyReasoning = query.toLowerCase().includes("proof") || query.toLowerCase().includes("scientific");
    
    if (localLoadFactor < 0.8 && !isHeavyReasoning) {
      selectedNode = this.meshNodes[0];
      decisions.push("Local capacity confirmed. Routing to Local iGPU.");
      networkLatencyMs = selectedNode.latencyMs;
    } else {
      decisions.push("Local node saturated or query requires heavy floating point capacity. Evaluating Peer Mesh...");
      
      const onlinePeer = this.meshNodes.find(n => n.type === "Peer_Node" && n.online);
      if (onlinePeer) {
        selectedNode = onlinePeer;
        decisions.push(`Peer node ${selectedNode.nodeId} available. Routing to Peer.`);
        networkLatencyMs = selectedNode.latencyMs;
      } else {
        decisions.push("All cooperative peer nodes offline or overloaded. Routing to Cloud HyperCluster...");
        selectedNode = this.meshNodes.find(n => n.type === "Cloud_HyperCluster")!;
        networkLatencyMs = selectedNode.latencyMs;
      }
    }

    const processingLatencyMs = selectedNode.type === "Local_iGPU" ? 110 :
                              selectedNode.type === "Peer_Node" ? 95 : 22; // Cloud has superior hardware speed but network cost

    const totalLatencyMs = networkLatencyMs + processingLatencyMs;

    return {
      query,
      assignedNodeId: selectedNode.nodeId,
      nodeType: selectedNode.type,
      networkLatencyMs,
      processingLatencyMs,
      totalLatencyMs,
      costDollar: selectedNode.costPerQueryDollar,
      routingDecisions: decisions
    };
  }

  getMeshNodes(): MeshNodeStatus[] {
    return this.meshNodes;
  }
}
