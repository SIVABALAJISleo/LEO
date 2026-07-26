// LEO AI V33 — Federated Inference Engine
// Capabilities: Coordinate edge node cluster inference tasks, run split-layer routing, and compile capacities.

export interface EdgeNode {
  nodeId: string;
  deviceType: "desktop" | "laptop" | "mobile" | "edge";
  availableMemoryMB: number;
  computePowerIndex: number; // 1 to 10
  latencyMs: number;
  isActive: boolean;
}

export interface SplitInferenceJob {
  jobId: string;
  layerStart: number;
  layerEnd: number;
  assignedNodeId: string;
  status: "pending" | "processing" | "completed" | "failed";
}

export class FederatedInferenceEngine {
  private nodes: EdgeNode[] = [
    {
      nodeId: "node-desktop-intel",
      deviceType: "desktop",
      availableMemoryMB: 16384,
      computePowerIndex: 9.2,
      latencyMs: 15,
      isActive: true,
    },
    {
      nodeId: "node-laptop-ryzen",
      deviceType: "laptop",
      availableMemoryMB: 8192,
      computePowerIndex: 6.5,
      latencyMs: 35,
      isActive: true,
    },
    {
      nodeId: "node-mobile-snapdragon",
      deviceType: "mobile",
      availableMemoryMB: 3072,
      computePowerIndex: 3.1,
      latencyMs: 85,
      isActive: true,
    },
    {
      nodeId: "node-edge-raspberry",
      deviceType: "edge",
      availableMemoryMB: 1024,
      computePowerIndex: 1.2,
      latencyMs: 120,
      isActive: false,
    },
  ];

  assignLayers(modelLayersCount = 32): SplitInferenceJob[] {
    const activeNodes = this.nodes.filter((n) => n.isActive);
    if (activeNodes.length === 0) return [];

    const totalComputeIndex = activeNodes.reduce((a, b) => a + b.computePowerIndex, 0);
    const jobs: SplitInferenceJob[] = [];
    let layerCursor = 0;

    activeNodes.forEach((node, idx) => {
      // Allocate portion of layers based on compute power share
      const share = node.computePowerIndex / totalComputeIndex;
      const layersAllocated =
        idx === activeNodes.length - 1
          ? modelLayersCount - layerCursor // cover any rounding remainder
          : Math.round(modelLayersCount * share);

      if (layersAllocated > 0) {
        jobs.push({
          jobId: `job-layer-split-${idx}-${Date.now().toString().slice(-4)}`,
          layerStart: layerCursor,
          layerEnd: layerCursor + layersAllocated - 1,
          assignedNodeId: node.nodeId,
          status: "completed",
        });
        layerCursor += layersAllocated;
      }
    });

    return jobs;
  }

  getActiveNodes(): EdgeNode[] {
    return this.nodes;
  }
}
