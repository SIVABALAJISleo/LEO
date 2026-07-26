// V23 — Phase 7 Knowledge Quality Matrix
// Measures knowledge assets by Trust, Freshness, Evidence, and Outcomes, decaying weak knowledge

export interface KnowledgeItemV23 {
  key: string;
  topic: string;
  trustScore: number; // 0 to 1
  freshnessScore: number; // 0 to 1 (decaying over time)
  evidenceCount: number;
  verificationLevel: "Unverified" | "Partial" | "Fully-Crystallized";
  usageCount: number;
  outcomeSuccessRate: number; // 0 to 1
  strength: number; // 0 to 1, computed metric
}

export class KnowledgeQualityMatrix {
  private matrix: KnowledgeItemV23[] = [];

  constructor() {
    this.seedMatrix();
  }

  private seedMatrix() {
    this.matrix = [
      {
        key: "K-RAG-001",
        topic: "iGPU hardware acceleration boundaries for WebGPU compute cores",
        trustScore: 0.98,
        freshnessScore: 0.95,
        evidenceCount: 12,
        verificationLevel: "Fully-Crystallized",
        usageCount: 450,
        outcomeSuccessRate: 0.99,
        strength: 0.97,
      },
      {
        key: "K-SEC-042",
        topic: "Stripe Webhook Signature Verification Secret Key rules",
        trustScore: 0.99,
        freshnessScore: 0.9,
        evidenceCount: 8,
        verificationLevel: "Fully-Crystallized",
        usageCount: 120,
        outcomeSuccessRate: 0.98,
        strength: 0.96,
      },
      {
        key: "K-TAM-081",
        topic: "Tamil-English semantic translation dictionaries for query canonicalizers",
        trustScore: 0.92,
        freshnessScore: 0.88,
        evidenceCount: 5,
        verificationLevel: "Partial",
        usageCount: 78,
        outcomeSuccessRate: 0.93,
        strength: 0.91,
      },
      {
        key: "K-BAD-009",
        topic: "Unverified API Key mock fallbacks (from old 0763f03 commit)",
        trustScore: 0.4,
        freshnessScore: 0.2,
        evidenceCount: 0,
        verificationLevel: "Unverified",
        usageCount: 2,
        outcomeSuccessRate: 0.25,
        strength: 0.28,
      },
    ];
  }

  govern(): { items: KnowledgeItemV23[]; averageMatrixQuality: number; evictedCount: number } {
    let evictedCount = 0;

    // Apply governance formula: compute strength & apply decay
    this.matrix = this.matrix.map((item) => {
      // Freshness decays by 2% on every governance tick if usage is low
      if (item.usageCount < 50) {
        item.freshnessScore = parseFloat(Math.max(0.1, item.freshnessScore - 0.02).toFixed(3));
      }

      // Compute Strength metric: weight trust (30%), freshness (20%), evidence count scaled (20%), outcome success (30%)
      const scaledEvidence = Math.min(1.0, item.evidenceCount / 10);
      const computedStrength =
        item.trustScore * 0.3 +
        item.freshnessScore * 0.2 +
        scaledEvidence * 0.2 +
        item.outcomeSuccessRate * 0.3;
      item.strength = parseFloat(Math.min(1.0, computedStrength).toFixed(3));

      // Crystallization status
      if (item.strength > 0.95 && item.evidenceCount >= 8) {
        item.verificationLevel = "Fully-Crystallized";
      } else if (item.strength < 0.6) {
        item.verificationLevel = "Unverified";
      }

      return item;
    });

    // Evict items below 0.30 strength
    const initialCount = this.matrix.length;
    this.matrix = this.matrix.filter((item) => {
      if (item.strength < 0.3) {
        evictedCount++;
        return false;
      }
      return true;
    });

    const sumStrength = this.matrix.reduce((sum, item) => sum + item.strength, 0);
    const averageMatrixQuality = this.matrix.length > 0 ? sumStrength / this.matrix.length : 0.95;

    return {
      items: this.matrix,
      averageMatrixQuality: parseFloat(averageMatrixQuality.toFixed(3)),
      evictedCount,
    };
  }

  getMatrix(): KnowledgeItemV23[] {
    return this.matrix;
  }

  insertItem(topic: string, trustScore: number, outcomeSuccessRate: number) {
    const key = `K-NEW-${Date.now().toString().slice(-4)}`;
    this.matrix.push({
      key,
      topic,
      trustScore,
      freshnessScore: 1.0,
      evidenceCount: 1,
      verificationLevel: "Partial",
      usageCount: 1,
      outcomeSuccessRate,
      strength: 0.85,
    });
  }
}
