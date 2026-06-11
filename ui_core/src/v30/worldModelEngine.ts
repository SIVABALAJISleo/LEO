// LEO AI V30 — Phase 1 World Model Engine
// Encapsulates semantic world representation, environmental abstraction, and dynamic events.

export interface WorldNode {
  id: string;
  type: "room" | "zone" | "landmark";
  label: string;
  connections: string[]; // Neighbor node IDs
  properties: Record<string, any>;
}

export interface WorldEvent {
  eventId: string;
  nodeId: string;
  eventType: string;
  description: string;
  timestamp: number;
}

export class WorldModelEngine {
  private nodes: Map<string, WorldNode> = new Map();
  private events: WorldEvent[] = [];

  constructor() {
    this.initializeDefaultMap();
  }

  private initializeDefaultMap() {
    const defaultNodes: WorldNode[] = [
      { id: "v30-node-1", type: "room", label: "Cleanroom Alpha", connections: ["v30-node-2"], properties: { classISO: 5, tempC: 21.5 } },
      { id: "v30-node-2", type: "zone", label: "Gantry Crane Pathway", connections: ["v30-node-1", "v30-node-3"], properties: { payloadLimitKg: 500 } },
      { id: "v30-node-3", type: "landmark", label: "Calibration Target 04", connections: ["v30-node-2"], properties: { opticalAccuracyMm: 0.05 } }
    ];

    defaultNodes.forEach(n => this.nodes.set(n.id, n));
    this.addEvent("v30-node-1", "CalibrationReset", "Initial environmental scan completed successfully");
  }

  getNodes(): WorldNode[] {
    return Array.from(this.nodes.values());
  }

  getNode(id: string): WorldNode | undefined {
    return this.nodes.get(id);
  }

  addNode(node: WorldNode) {
    this.nodes.set(node.id, node);
  }

  addEvent(nodeId: string, eventType: string, description: string) {
    const event: WorldEvent = {
      eventId: `event-${Math.random().toString(36).substring(2, 9)}`,
      nodeId,
      eventType,
      description,
      timestamp: Date.now()
    };
    this.events.push(event);
  }

  getEvents(): WorldEvent[] {
    return this.events;
  }

  // GraphRAG & Memory Integration placeholder helper
  queryStatePrediction(query: string): { simulatedPath: string[]; confidence: number } {
    // Determine path based on topological nodes
    const paths = Array.from(this.nodes.keys());
    return {
      simulatedPath: paths,
      confidence: query.includes("optimal") ? 0.995 : 0.942
    };
  }
}
