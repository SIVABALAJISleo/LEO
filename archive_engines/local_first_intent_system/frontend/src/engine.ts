/**
 * DETERMINISTIC INTENT ENGINE (V5)
 * "Zero Reasoning. Pure Traversal."
 */

export type NodeType = "ENTITY" | "METRIC" | "TIME" | "CONDITION";

export interface Node {
  id: string;
  type: NodeType;
  name: string;
  metadata?: Record<string, any>;
}

export interface Edge {
  from: string;
  to: string;
}

export class LocalIntentEngine {
  private nodes: Map<string, Node> = new Map();
  private edges: Map<string, string[]> = new Map();

  constructor() {
    this.initializeGraph();
  }

  private initializeGraph() {
    // Mock Nodes (In production, these come from Local SQLite/CRDT)
    const rawNodes: Node[] = [
      { id: "e1", type: "ENTITY", name: "ALPHA_NODE" },
      { id: "e2", type: "ENTITY", name: "BETA_NODE" },
      { id: "m1", type: "METRIC", name: "CPU_LOAD" },
      { id: "m2", type: "METRIC", name: "MEMORY" },
      { id: "t1", type: "TIME", name: "LAST_5M" },
      { id: "t2", type: "TIME", name: "REALTIME" },
      { id: "c1", type: "CONDITION", name: "ABOVE_90" },
      { id: "c2", type: "CONDITION", name: "NOMINAL" },
    ];

    rawNodes.forEach((n) => this.nodes.set(n.id, n));

    // Valid Paths (Edges)
    this.addEdge("e1", "m1");
    this.addEdge("e1", "m2");
    this.addEdge("e2", "m1");
    this.addEdge("m1", "t1");
    this.addEdge("m1", "t2");
    this.addEdge("m2", "t1");
    this.addEdge("t1", "c1");
    this.addEdge("t1", "c2");
    this.addEdge("t2", "c1");
  }

  private addEdge(from: string, to: string) {
    const list = this.edges.get(from) || [];
    list.push(to);
    this.edges.set(from, list);
  }

  public getNodesByType(type: NodeType, previousId?: string): Node[] {
    if (!previousId) {
      return Array.from(this.nodes.values()).filter((n) => n.type === type);
    }

    const possibleNextIds = this.edges.get(previousId) || [];
    return possibleNextIds.map((id) => this.nodes.get(id)!).filter((n) => n.type === type);
  }

  /**
   * LAYER 4: EXECUTION
   * Pure Graph Traversal Validation
   */
  public execute(intentIds: string[]): {
    status: string;
    result?: any;
    error?: string;
    details?: string;
  } {
    if (intentIds.length === 0) return { status: "ERROR", error: "EMPTY_INTENT" };

    // Validate chain
    for (let i = 0; i < intentIds.length - 1; i++) {
      const current = intentIds[i];
      const next = intentIds[i + 1];
      const validNexts = this.edges.get(current) || [];
      if (!validNexts.includes(next)) {
        return {
          status: "REJECTED",
          error: "INVALID_PATH",
          details: `Sequence ${this.nodes.get(current)?.name} -> ${this.nodes.get(next)?.name} is logically impossible.`,
        };
      }
    }

    // Deterministic Result Fetch
    const lastNode = this.nodes.get(intentIds[intentIds.length - 1])!;
    return {
      status: "SUCCESS",
      result: {
        trace: intentIds.map((id) => this.nodes.get(id)!.name),
        outcome: `DETERMINISTIC_VAL: Resolution for intent chain completed locally.`,
        data: lastNode.type === "CONDITION" ? "ACK_CONFIG_ALIGNED" : "DATA_STREAM_ACTIVE",
      },
    };
  }
}
