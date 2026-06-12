// LEO AI V36 — Evidence Graph Builder
// Builds parent-child citation graphs for dynamic context traversals.

export interface EvidenceNode {
  nodeId: string;
  sourceLabel: string;
  referencedNodes: string[];
}

export class EvidenceGraphBuilder {
  private nodes: Record<string, EvidenceNode> = {};

  public addNode(id: string, label: string, references: string[]): void {
    this.nodes[id] = {
      nodeId: id,
      sourceLabel: label,
      referencedNodes: references
    };
  }

  public getGraph(): Record<string, EvidenceNode> {
    return this.nodes;
  }
}
