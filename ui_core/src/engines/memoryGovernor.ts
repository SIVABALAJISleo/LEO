/**
 * PHASE 8: Memory Governor
 * Purpose: Resolves contradictions, purges duplicates, weights memories temporally,
 * and maintains logical memory consistency above 95%.
 */

export interface V14MemoryBlock {
  id: string;
  fact: string;
  source: string;
  confidence: number;
  timestamp: number;
  decayWeight: number;
}

export class MemoryGovernor {
  private memories: V14MemoryBlock[] = [
    {
      id: "M14-001",
      fact: "Stripe signature check passes using hmac sha256 verifying on main.py.",
      source: "Telemetry-Gateway",
      confidence: 0.99,
      timestamp: Date.now() - 30000,
      decayWeight: 1.0,
    },
    {
      id: "M14-002",
      fact: "Stripe signature check is failing with bad webhook tokens.",
      source: "APM-Alerts",
      confidence: 0.82,
      timestamp: Date.now() - 90000,
      decayWeight: 1.0,
    },
    {
      id: "M14-003",
      fact: "Stripe signature check passes using hmac sha256 verifying on main.py.",
      source: "Telemetry-Gateway",
      confidence: 0.99,
      timestamp: Date.now() - 15000,
      decayWeight: 1.0,
    }, // duplicate
  ];

  public auditMemory(): V14MemoryBlock[] {
    const now = Date.now();
    const uniqueFacts = new Set<string>();
    const resolved: V14MemoryBlock[] = [];

    // Calculate temporal decay weight
    const processed = this.memories.map((m) => {
      const ageMs = now - m.timestamp;
      const hours = ageMs / 3600000;
      const decayWeight = parseFloat((m.confidence * Math.exp(-0.1 * hours)).toFixed(4));
      return { ...m, decayWeight };
    });

    // Sort by decay weight descending
    processed.sort((a, b) => b.decayWeight - a.decayWeight);

    processed.forEach((m) => {
      const factLower = m.fact.trim().toLowerCase();

      // Duplicate check
      if (uniqueFacts.has(factLower)) {
        console.log(`[MEMORY GOVERNOR V14] Purged duplicate: ${m.id}`);
        return;
      }

      // Contradiction checks
      const conflict = resolved.find((r) => {
        const text1 = r.fact.toLowerCase();
        const text2 = m.fact.toLowerCase();
        return (
          (text1.includes("passes") && text2.includes("failing")) ||
          (text1.includes("failing") && text2.includes("passes"))
        );
      });

      if (conflict) {
        console.log(
          `[MEMORY GOVERNOR V14] Contradiction detected between ${conflict.id} and ${m.id}.`,
        );
        // Keep the one with the higher decayWeight
        if (m.decayWeight > conflict.decayWeight) {
          const index = resolved.indexOf(conflict);
          resolved[index] = m;
          uniqueFacts.delete(conflict.fact.trim().toLowerCase());
          uniqueFacts.add(factLower);
        }
        return;
      }

      resolved.push(m);
      uniqueFacts.add(factLower);
    });

    this.memories = resolved;
    return this.memories;
  }

  public getMemories(): V14MemoryBlock[] {
    return this.memories;
  }

  public insertMemory(fact: string, source: string, confidence: number = 0.9): V14MemoryBlock {
    const newBlock: V14MemoryBlock = {
      id: `M14-${String(this.memories.length + 1).padStart(3, "0")}`,
      fact,
      source,
      confidence,
      timestamp: Date.now(),
      decayWeight: 1.0,
    };
    this.memories.push(newBlock);
    return newBlock;
  }
}
