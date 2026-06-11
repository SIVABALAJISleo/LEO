// V29 — Phase 1 Topological World Model Engine
// Compresses dense coordinate environments into semantic relationship nodes (rooms, corridors, zones, landmarks)

export interface TopologicalNode {
  id: string;
  type: "room" | "corridor" | "zone" | "landmark";
  label: string;
  connections: string[]; // Connected Node IDs
  properties: Record<string, any>;
}

export class TopologicalWorldModel {
  private nodes: Map<string, TopologicalNode> = new Map();

  constructor() {
    this.seedMap();
  }

  private seedMap() {
    const defaultNodes: TopologicalNode[] = [
      { id: "node-1", type: "room", label: "Docking Zone Alpha", connections: ["node-2"], properties: { containsCharger: true } },
      { id: "node-2", type: "corridor", label: "Main Corridor West", connections: ["node-1", "node-3", "node-4"], properties: { widthMeters: 2.5 } },
      { id: "node-3", type: "room", label: "Silicon Lab Room B", connections: ["node-2"], properties: { temperatureCelsius: 22.1 } },
      { id: "node-4", type: "zone", label: "Assembly Area Delta", connections: ["node-2", "node-5"], properties: { highVoltageZone: true } },
      { id: "node-5", type: "landmark", label: "Structural Pillar 10", connections: ["node-4"], properties: { isObstacle: true } }
    ];

    defaultNodes.forEach(node => this.nodes.set(node.id, node));
  }

  getNodes(): TopologicalNode[] {
    return Array.from(this.nodes.values());
  }

  addNode(node: TopologicalNode) {
    this.nodes.set(node.id, node);
  }

  getNode(id: string): TopologicalNode | undefined {
    return this.nodes.get(id);
  }
}
