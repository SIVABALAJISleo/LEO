// LEO AI V38 — Long Term Memory Engine
// Implements Episodic, Semantic, Procedural, Working, Consolidation, Reflection, and Failure memories.

export interface MemoryCell {
  id: string;
  type: "working" | "episodic" | "semantic" | "procedural" | "consolidation" | "reflection" | "failure";
  statement: string;
  relevanceScore: number;
  decayWeight: number;
  timestamp: number;
}

export class LongTermMemoryEngine {
  private cells: MemoryCell[] = [
    {
      id: "mc-1",
      type: "failure",
      statement: "VRAM overflow occurred when thread count was set above 8 cores on Intel UHD 12th Gen.",
      relevanceScore: 0.96,
      decayWeight: 1.0,
      timestamp: Date.now()
    },
    {
      id: "mc-2",
      type: "reflection",
      statement: "Ternary weights are more resource efficient than FP16 on local CPU architectures.",
      relevanceScore: 0.92,
      decayWeight: 0.98,
      timestamp: Date.now()
    }
  ];

  /**
   * Recalls memories based on matching tags or query patterns.
   */
  public queryMemory(query: string): MemoryCell[] {
    const qLower = query.toLowerCase();
    
    // Simple filter matching
    return this.cells
      .filter(cell => {
        const words = qLower.split(/\s+/);
        return words.some(w => cell.statement.toLowerCase().includes(w) && w.length > 3);
      })
      .sort((a, b) => b.relevanceScore - a.relevanceScore);
  }

  /**
   * Adds a new memory cell, simulating decay calculations.
   */
  public recordMemory(type: MemoryCell["type"], statement: string, score: number): MemoryCell {
    const cell: MemoryCell = {
      id: `mc-${(Math.random() * 10000).toFixed(0)}`,
      type,
      statement,
      relevanceScore: score,
      decayWeight: 1.0,
      timestamp: Date.now()
    };
    this.cells.push(cell);
    return cell;
  }

  public getMemories(): MemoryCell[] {
    return this.cells;
  }
}
