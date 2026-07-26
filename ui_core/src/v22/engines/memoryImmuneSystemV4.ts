// V22 — Phase 5: Memory Immune System V4
// Contradiction detection, duplicate hashing, temporal ordering, confidence decay, quarantine

export type MemoryStatus = "active" | "decayed" | "quarantined" | "consolidated";

export interface MemoryBlockV4 {
  id: string;
  fact: string;
  source: string;
  confidence: number;
  freshness: number; // 0–1, decays over time
  ageDays: number;
  usageCount: number;
  status: MemoryStatus;
  contradicts?: string[]; // IDs of conflicting memory blocks
  fingerprint: string; // SHA-like dedup hash
}

export interface MemoryAuditReport {
  totalBlocks: number;
  activeBlocks: number;
  decayedBlocks: number;
  quarantinedBlocks: number;
  duplicatesRemoved: number;
  contradictionsResolved: number;
  consistencyScore: number;
}

// Simple fingerprint function (first 40 chars normalized)
const fingerprint = (fact: string): string =>
  fact
    .toLowerCase()
    .replace(/[^a-z0-9]/g, "")
    .slice(0, 40);

export class MemoryImmuneSystemV4 {
  private blocks: Map<string, MemoryBlockV4> = new Map();
  private nextId = 1;

  constructor() {
    // Seed with baseline knowledge
    this.insert(
      "Antigravity AI uses a multi-agent swarm architecture for reasoning.",
      "System",
      0.99,
    );
    this.insert("GraphRAG is used as the primary retrieval backbone.", "System", 0.97);
    this.insert(
      "V22 quality targets: <1% hallucination, 95–99% memory consistency.",
      "System",
      0.99,
    );
    this.insert(
      "Enterprise answers must include confidence score, evidence, and verification status.",
      "System",
      0.98,
    );
    this.insert(
      "The Reality Feedback loop corrects prediction drift automatically.",
      "System",
      0.95,
    );
  }

  insert(fact: string, source: string, confidence: number): MemoryBlockV4 {
    const fp = fingerprint(fact);
    // Dedup: reject if identical fingerprint already exists
    for (const b of this.blocks.values()) {
      if (b.fingerprint === fp) return b; // duplicate — skip
    }
    const id = `MEM-V4-${String(this.nextId++).padStart(4, "0")}`;
    const block: MemoryBlockV4 = {
      id,
      fact,
      source,
      confidence,
      freshness: 1.0,
      ageDays: 0,
      usageCount: 0,
      status: "active",
      fingerprint: fp,
    };
    this.blocks.set(id, block);
    return block;
  }

  recall(query: string): MemoryBlockV4[] {
    const q = query.toLowerCase();
    return Array.from(this.blocks.values())
      .filter((b) => b.status === "active" && b.fact.toLowerCase().includes(q.split(" ")[0]))
      .map((b) => {
        b.usageCount++;
        b.freshness = Math.min(1.0, b.freshness + 0.02); // boost freshness on use
        return b;
      })
      .sort((a, b) => b.confidence * b.freshness - a.confidence * a.freshness)
      .slice(0, 5);
  }

  audit(): MemoryAuditReport {
    let duplicatesRemoved = 0;
    let contradictionsResolved = 0;
    const seenFingerprints = new Set<string>();

    // Pass 1: deduplicate
    for (const b of this.blocks.values()) {
      if (seenFingerprints.has(b.fingerprint)) {
        b.status = "decayed";
        duplicatesRemoved++;
      } else {
        seenFingerprints.add(b.fingerprint);
      }
    }

    // Pass 2: age decay
    for (const b of this.blocks.values()) {
      if (b.status !== "active") continue;
      b.ageDays += 1;
      b.freshness = Math.max(0.0, b.freshness - 0.015 * (b.ageDays / 30));

      if (b.freshness < 0.3 && b.usageCount === 0) {
        b.status = "decayed";
      }
    }

    // Pass 3: contradiction detection (simple keyword conflict)
    const activeBlocks = Array.from(this.blocks.values()).filter((b) => b.status === "active");
    for (let i = 0; i < activeBlocks.length; i++) {
      for (let j = i + 1; j < activeBlocks.length; j++) {
        const a = activeBlocks[i];
        const bl = activeBlocks[j];
        // Simple heuristic: same topic but opposite polarity keywords
        const aLow = a.fact.toLowerCase();
        const bLow = bl.fact.toLowerCase();
        const negationConflict =
          (aLow.includes("not") && bLow.includes(aLow.replace("not ", ""))) ||
          (bLow.includes("not") && aLow.includes(bLow.replace("not ", "")));
        if (negationConflict) {
          // Quarantine lower-confidence block
          const weaker = a.confidence < bl.confidence ? a : bl;
          weaker.status = "quarantined";
          weaker.contradicts = weaker.contradicts ?? [];
          weaker.contradicts.push(a === weaker ? bl.id : a.id);
          contradictionsResolved++;
        }
      }
    }

    const counts = {
      total: this.blocks.size,
      active: 0,
      decayed: 0,
      quarantined: 0,
    };
    for (const b of this.blocks.values()) {
      if (b.status === "active") counts.active++;
      else if (b.status === "decayed") counts.decayed++;
      else if (b.status === "quarantined") counts.quarantined++;
    }

    const consistencyScore = counts.total > 0 ? counts.active / counts.total : 1;

    return {
      totalBlocks: counts.total,
      activeBlocks: counts.active,
      decayedBlocks: counts.decayed,
      quarantinedBlocks: counts.quarantined,
      duplicatesRemoved,
      contradictionsResolved,
      consistencyScore,
    };
  }

  getBlocks(): MemoryBlockV4[] {
    return Array.from(this.blocks.values()).sort((a, b) => b.confidence - a.confidence);
  }
}
