// LEO AI V33 — Peer Coordinator
// Capabilities: Run peer latency pinging, manage connection limits, and resolve nodes connection drops.

export interface ConnectionHeartbeat {
  nodeId: string;
  pingMs: number;
  packetLossRate: number; // 0.0 to 1.0
  connectionStatus: "stable" | "degraded" | "disconnected";
  failoverBackupNodeId?: string;
}

export class PeerCoordinator {
  pingPeer(nodeId: string, customLatency?: number): ConnectionHeartbeat {
    const pingMs = customLatency ?? Math.round(Math.random() * 95 + 10);
    const loss = Math.random() > 0.95 ? 0.08 : 0.0; // occasional packets drop

    let connectionStatus: "stable" | "degraded" | "disconnected" = "stable";
    if (pingMs > 150 || loss > 0.05) {
      connectionStatus = "degraded";
    }
    if (pingMs > 1000) {
      connectionStatus = "disconnected";
    }

    return {
      nodeId,
      pingMs,
      packetLossRate: loss,
      connectionStatus,
      failoverBackupNodeId: connectionStatus !== "stable" ? "node-desktop-intel" : undefined,
    };
  }
}
