// V24 — Phase 8 Knowledge Governance Engine
// Tracks semantic assets by Trust, Freshness, Evidence, and Usage, evicting decayed items

export interface KnowledgeItemV24 {
  key: string;
  topic: string;
  trustScore: number;
  freshnessScore: number;
  evidenceCount: number;
  usageCount: number;
  verificationLevel: "Unverified" | "Partial" | "Fully-Crystallized";
  overallScore: number;
}

export class KnowledgeGovernanceEngine {
  private index: KnowledgeItemV24[] = [];

  constructor() {
    this.seedIndex();
  }

  private seedIndex() {
    this.index = [
      {
        key: "K-RAG-001",
        topic: "iGPU WebGPU local execution routing rules for low latency models",
        trustScore: 0.98,
        freshnessScore: 0.95,
        evidenceCount: 15,
        usageCount: 420,
        verificationLevel: "Fully-Crystallized",
        overallScore: 0.97
      },
      {
        key: "K-SEC-042",
        topic: "Stripe signature webhook token verification rules",
        trustScore: 0.99,
        freshnessScore: 0.91,
        evidenceCount: 10,
        usageCount: 150,
        verificationLevel: "Fully-Crystallized",
        overallScore: 0.98
      },
      {
        key: "K-TAM-081",
        topic: " Tamil-English intent maps and semantic token translations",
        trustScore: 0.93,
        freshnessScore: 0.89,
        evidenceCount: 6,
        usageCount: 88,
        verificationLevel: "Partial",
        overallScore: 0.91
      },
      {
        key: "K-BAD-009",
        topic: "Unverified API Key mocking parameters (historical 0763f03 commit)",
        trustScore: 0.35,
        freshnessScore: 0.15,
        evidenceCount: 0,
        usageCount: 1,
        verificationLevel: "Unverified",
        overallScore: 0.25
      }
    ];
  }

  govern(): { items: KnowledgeItemV24[]; evictedCount: number; averageQuality: number } {
    let evictedCount = 0;

    this.index = this.index.map(item => {
      // Apply decay
      if (item.usageCount < 50) {
        item.freshnessScore = parseFloat(Math.max(0.1, item.freshnessScore - 0.03).toFixed(3));
      }

      // Compute overall quality score: trust (40%), freshness (20%), evidence count scaled (20%), usage scaled (20%)
      const scaledEvidence = Math.min(1.0, item.evidenceCount / 10);
      const scaledUsage = Math.min(1.0, item.usageCount / 200);
      
      const score = (item.trustScore * 0.4) + (item.freshnessScore * 0.2) + (scaledEvidence * 0.2) + (scaledUsage * 0.2);
      item.overallScore = parseFloat(Math.min(1.0, score).toFixed(3));

      // Re-evaluate verification level
      if (item.overallScore > 0.95 && item.evidenceCount >= 8) {
        item.verificationLevel = "Fully-Crystallized";
      } else if (item.overallScore < 0.60) {
        item.verificationLevel = "Unverified";
      } else {
        item.verificationLevel = "Partial";
      }

      return item;
    });

    // Evict items below 0.30 overall score
    this.index = this.index.filter(item => {
      if (item.overallScore < 0.30) {
        evictedCount++;
        return false;
      }
      return true;
    });

    const sum = this.index.reduce((s, it) => s + it.overallScore, 0);
    const averageQuality = this.index.length > 0 ? sum / this.index.length : 0.95;

    return {
      items: this.index,
      evictedCount,
      averageQuality: parseFloat(averageQuality.toFixed(3))
    };
  }

  getItems(): KnowledgeItemV24[] {
    return this.index;
  }

  addItem(topic: string, trustScore: number) {
    const key = `K-NEW-${Date.now().toString().slice(-4)}`;
    this.index.push({
      key,
      topic,
      trustScore,
      freshnessScore: 1.0,
      evidenceCount: 1,
      usageCount: 1,
      verificationLevel: "Partial",
      overallScore: 0.85
    });
  }
}
