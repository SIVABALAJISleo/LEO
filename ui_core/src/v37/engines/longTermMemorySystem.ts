// LEO AI V37 — Long Term Memory System
// Manages episodic, semantic, procedural, user, project, and failure memory blocks to ensure continuous intelligence evolution.

export interface MemoryBlock {
  id: string;
  type: "episodic" | "semantic" | "procedural" | "user" | "project" | "failure";
  content: string;
  tags: string[];
  importance: number;
  timestamp: number;
}

export class LongTermMemorySystem {
  private memoryStores: MemoryBlock[] = [
    {
      id: "mem-101",
      type: "failure",
      content: "Avoid multi-agent loop locks when both verification agent and optimizer agent have equal vote weight; resolve via constitution clause 3.",
      tags: ["arbitration", "swarm", "deadlocks"],
      importance: 0.95,
      timestamp: Date.now() - 3600000
    },
    {
      id: "mem-102",
      type: "semantic",
      content: "Intel Core i5 12th Gen physical threads should use CPU affinity bindings to avoid context switching latency.",
      tags: ["hardware", "intel", "ipex"],
      importance: 0.88,
      timestamp: Date.now() - 7200000
    }
  ];

  /**
   * Searches the memory stores for relevant contexts to prevent repeating past mistakes or to reuse insights.
   */
  public recallRelevantMemories(queryTags: string[]): MemoryBlock[] {
    return this.memoryStores
      .filter(mem => mem.tags.some(t => queryTags.includes(t)))
      .sort((a, b) => b.importance - a.importance);
  }

  /**
   * Registers a new memory instance.
   */
  public crystallizeMemory(
    type: MemoryBlock["type"],
    content: string,
    tags: string[],
    importance: number
  ): MemoryBlock {
    const newBlock: MemoryBlock = {
      id: `mem-${(Math.random() * 10000).toFixed(0)}`,
      type,
      content,
      tags,
      importance,
      timestamp: Date.now()
    };
    this.memoryStores.push(newBlock);
    return newBlock;
  }

  public getMemoryCount(): number {
    return this.memoryStores.length;
  }

  public getAllMemories(): MemoryBlock[] {
    return this.memoryStores;
  }
}
