import { Node, Edge } from "reactflow";

export interface UOD_NodeData {
  type: "dataset" | "filter" | "aggregate" | "join" | "output";
  value?: any;
  config?: any;
}

export class SQLCompiler {
  static compile(nodes: Node<UOD_NodeData>[], edges: Edge[]): string {
    // 1. Build adjacency list/DAG
    // For simplicity, we assume a single path ending at an 'output' node
    const outputNode = nodes.find((n) => n.data.type === "output");
    if (!outputNode) return "-- No output node found";

    return this.buildQuery(outputNode, nodes, edges);
  }

  private static buildQuery(
    node: Node<UOD_NodeData>,
    nodes: Node<UOD_NodeData>[],
    edges: Edge[],
  ): string {
    const incomingEdges = edges.filter((e) => e.target === node.id);
    const parents = incomingEdges.map((e) => nodes.find((n) => n.id === e.source)!);

    switch (node.data.type) {
      case "dataset":
        return `SELECT * FROM ${node.data.value}`;

      case "filter": {
        const parentQuery = this.buildQuery(parents[0], nodes, edges);
        return `SELECT * FROM (${parentQuery}) AS sub WHERE ${node.data.config.condition}`;
      }

      case "aggregate": {
        const parentQuery = this.buildQuery(parents[0], nodes, edges);
        const { groupBy, aggs } = node.data.config;
        const selectCols = [
          ...groupBy,
          ...aggs.map((a: any) => `${a.fn}(${a.col}) AS ${a.alias}`),
        ].join(", ");
        return `SELECT ${selectCols} FROM (${parentQuery}) AS sub GROUP BY ${groupBy.join(", ")}`;
      }

      case "output": {
        return parents.length > 0 ? this.buildQuery(parents[0], nodes, edges) : "SELECT 1";
      }

      default:
        return "SELECT 1";
    }
  }
}
