export interface SparsityDirectives { activeHeadsCount: number; sparsityRatio: number; conditionalComputeGate: boolean; flopsSaved: number; }
export class SparseComputationEngine {
  public async prescribeSparsity(attentionHeadsCount: number, ramLimitGb: number): Promise<SparsityDirectives> {
    const res = await fetch("http://localhost:8000/api/v1/v40/engines/sparse", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ attentionHeadsCount, ramLimitGb })
    });
    return res.json();
  }
}
