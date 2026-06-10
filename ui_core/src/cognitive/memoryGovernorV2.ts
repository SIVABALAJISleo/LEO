/**
 * PHASE 7: Memory Governance V2
 * Upgrades episodic/semantic memory consistency checks, handles contradictions,
 * temporal weighting, and duplicate purging.
 * Target Memory Consistency Score: 95%+
 */

export interface MemoryBlock {
  id: string;
  content: string;
  source: string;
  timestamp: number;
  confidence: number;
  weight: number; // calculated based on temporal decay
  category: "episodic" | "semantic";
}

export class MemoryGovernorV2 {
  private blocks: MemoryBlock[] = [
    {
      id: "MEM-001",
      content: "Stripe verification is complete and authenticated on backend main.py.",
      source: "Webhook-System",
      timestamp: Date.now() - 60000, // 1 min ago
      confidence: 1.0,
      weight: 1.0,
      category: "episodic",
    },
    {
      id: "MEM-002",
      content: "Stripe signature check is currently failing on invalid keys.",
      source: "DevOps-Alerts",
      timestamp: Date.now() - 120000, // 2 mins ago
      confidence: 0.85,
      weight: 0.95,
      category: "episodic",
    },
    {
      id: "MEM-003",
      content: "Stripe verification is complete and authenticated on backend main.py.", // duplicate
      source: "Webhook-System",
      timestamp: Date.now() - 30000,
      confidence: 1.0,
      weight: 1.0,
      category: "episodic",
    },
  ];

  /**
   * Cleans duplicates and resolves contradiction blocks based on confidence and timestamps.
   */
  public governMemory(): MemoryBlock[] {
    const uniqueContent = new Set<string>();
    const cleanedBlocks: MemoryBlock[] = [];

    // 1. Purge Duplicates & Compute Temporal Weight
    const now = Date.now();
    const halfLife = 86400000; // 24 hours in ms

    const processed = this.blocks.map((block) => {
      // Calculate temporal exponential decay: weight = confidence * e^(-decay_rate * time)
      const age = now - block.timestamp;
      const weight = parseFloat((block.confidence * Math.exp(-0.693 * (age / halfLife))).toFixed(4));
      return { ...block, weight };
    });

    // 2. Sort by weight descending
    processed.sort((a, b) => b.weight - a.weight);

    // 3. Keep highest weight block for duplicates, detect contradictions
    processed.forEach((block) => {
      const cleanText = block.content.trim().toLowerCase();

      // Duplicate check
      if (uniqueContent.has(cleanText)) {
        console.log(`[MEMORY GOVERNOR V2] Purging duplicate block ${block.id}.`);
        return; // Skip duplicate
      }

      // Contradiction detection
      const contradicting = cleanedBlocks.find((b) => {
        const t1 = b.content.toLowerCase();
        const t2 = block.content.toLowerCase();
        // Simple contradiction heuristic (e.g. one says complete, other says failing)
        return (t1.includes("complete") && t2.includes("failing")) || (t1.includes("failing") && t2.includes("complete"));
      });

      if (contradicting) {
        console.log(`[MEMORY GOVERNOR V2] Contradiction found between ${contradicting.id} and ${block.id}.`);
        // Resolve contradiction by keeping the one with higher weight/confidence
        if (block.weight > contradicting.weight) {
          // Replace contradicting block
          const index = cleanedBlocks.indexOf(contradicting);
          cleanedBlocks[index] = block;
          uniqueContent.delete(contradicting.content.trim().toLowerCase());
          uniqueContent.add(cleanText);
        }
        return; // Resolve conflict
      }

      cleanedBlocks.push(block);
      uniqueContent.add(cleanText);
    });

    this.blocks = cleanedBlocks;
    return this.blocks;
  }

  public getBlocks(): MemoryBlock[] {
    return this.blocks;
  }

  public insertMemory(content: string, source: string, category: "episodic" | "semantic"): MemoryBlock {
    const newBlock: MemoryBlock = {
      id: `MEM-${String(this.blocks.length + 1).padStart(3, "0")}`,
      content,
      source,
      timestamp: Date.now(),
      confidence: 1.0,
      weight: 1.0,
      category,
    };
    this.blocks.push(newBlock);
    return newBlock;
  }
}
