export interface NetworkNode { id: string; name: string; category: string; }
export interface NetworkEdge { sourceId: string; targetId: string; predicate: string; relevance: number; }
export interface GraphTraceReport { traversedNodes: string[]; causalChain: string; hopsResolved: number; dependencyDiscovered: boolean; }
export class GraphIntelligenceEngine {
  public async traceCausality(startName: string, endName: string): Promise<GraphTraceReport> {
    const res = await fetch("http://localhost:8000/api/v1/v40/engines/graph/trace", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ startName, endName })
    });
    return res.json();
  }
}
