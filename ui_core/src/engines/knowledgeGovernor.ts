/**
 * PHASE 7: Knowledge Governor
 * Purpose: Evaluates crystal assets based on accuracy, freshness, trust, verification,
 * and reuse scores, and prunes or reinforces them.
 */

export interface KnowledgeItem {
  id: string;
  topic: string;
  accuracy: number;
  freshness: number;
  trust: number;
  verification: number;
  reuse: number;
  status: "active" | "decayed" | "strengthened";
}

export class KnowledgeGovernor {
  private items: KnowledgeItem[] = [
    { id: "V14-K01", topic: "V14 Cognitive Reconstruction Map", accuracy: 0.98, freshness: 0.95, trust: 0.97, verification: 0.99, reuse: 0.82, status: "active" },
    { id: "V14-K02", topic: "Z3 Solver Proof Bounds", accuracy: 0.96, freshness: 0.92, trust: 0.94, verification: 0.98, reuse: 0.70, status: "active" },
    { id: "V14-K03", topic: "Legacy Policy Contradiction Maps", accuracy: 0.40, freshness: 0.25, trust: 0.35, verification: 0.20, reuse: 0.05, status: "active" },
  ];

  public auditAssets(): KnowledgeItem[] {
    const decayThreshold = 0.55;
    const reinforceThreshold = 0.92;

    this.items = this.items.map((item) => {
      const compositeScore = 
        (item.accuracy * 0.35) + 
        (item.freshness * 0.15) + 
        (item.trust * 0.20) + 
        (item.verification * 0.20) + 
        (item.reuse * 0.10);

      let status = item.status;
      if (compositeScore < decayThreshold) {
        status = "decayed";
      } else if (compositeScore > reinforceThreshold) {
        status = "strengthened";
      }

      return { ...item, status };
    });

    return this.items;
  }

  public getItems(): KnowledgeItem[] {
    return this.items;
  }

  public addCrystal(topic: string, acc: number, trust: number): KnowledgeItem {
    const newItem: KnowledgeItem = {
      id: `V14-K${String(this.items.length + 1).padStart(2, "0")}`,
      topic,
      accuracy: acc,
      freshness: 1.0,
      trust,
      verification: 0.85,
      reuse: 0.10,
      status: "active",
    };
    this.items.push(newItem);
    return newItem;
  }
}
