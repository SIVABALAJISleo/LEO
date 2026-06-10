// V22 — Phase 7: Knowledge Quality Governor
// Lifecycle management: Trust, Freshness, Evidence, Usage, Verification → crystallize or decay

export type KnowledgeItemStatus = 'crystallized' | 'active' | 'decaying' | 'evicted';

export interface KnowledgeItemV22 {
  id: string;
  topic: string;
  content: string;
  trustScore: number;      // 0–1
  freshnessScore: number;  // 0–1 (decays over time)
  evidenceCount: number;   // number of supporting sources
  usageCount: number;
  verificationStatus: 'verified' | 'unverified' | 'contested';
  qualityScore: number;    // composite
  status: KnowledgeItemStatus;
  lastAccessedCycle: number;
}

export interface KnowledgeGovernanceReport {
  totalItems: number;
  crystallized: number;
  active: number;
  decaying: number;
  evicted: number;
  averageQualityScore: number;
  governanceCycle: number;
}

const qualityScore = (item: KnowledgeItemV22): number =>
  item.trustScore * 0.30 +
  item.freshnessScore * 0.25 +
  Math.min(1.0, item.evidenceCount / 5) * 0.20 +
  Math.min(1.0, item.usageCount / 20) * 0.10 +
  (item.verificationStatus === 'verified' ? 0.15 : item.verificationStatus === 'contested' ? 0.05 : 0.08);

export class KnowledgeQualityGovernor {
  private items: Map<string, KnowledgeItemV22> = new Map();
  private nextId = 1;
  private cycle = 0;

  constructor() {
    // Seed with core knowledge items
    const seeds: { topic: string; content: string; trust: number; evidence: number }[] = [
      { topic: 'Multi-Path Reasoning', content: 'V22 ReasoningAmplifierV2 runs 3 independent chains and selects the highest-evidence consensus.', trust: 0.99, evidence: 5 },
      { topic: 'Hallucination Elimination', content: 'Every claim is verified against GraphRAG, Memory, Search, Database, Calculator, and Tool before commitment.', trust: 0.98, evidence: 6 },
      { topic: 'Memory Immune System V4', content: 'Memory blocks are deduplicated by fingerprint, aged by decay factor, and quarantined on contradiction.', trust: 0.97, evidence: 4 },
      { topic: 'Agent Priority Queue', content: 'Agents are ranked by composite score (Accuracy 35%, Reliability 25%, Latency 20%, Verification 20%).', trust: 0.96, evidence: 3 },
      { topic: 'Enterprise Trust Layer', content: 'All enterprise answers include Confidence, Evidence citations, and Verification Status badge.', trust: 0.99, evidence: 5 },
      { topic: 'Reality Feedback Loop', content: 'Prediction-vs-Reality deltas drive continuous calibration weight adjustments.', trust: 0.95, evidence: 4 },
      { topic: 'Autonomous Improvement', content: 'Measure → Find Weakness → Improve → Retest → Deploy cycle runs perpetually.', trust: 0.97, evidence: 4 },
    ];
    seeds.forEach(s => this.addItem(s.topic, s.content, s.trust, s.evidence));
  }

  addItem(topic: string, content: string, trust: number, evidenceCount: number): KnowledgeItemV22 {
    const id = `KNW-${String(this.nextId++).padStart(4, '0')}`;
    const item: KnowledgeItemV22 = {
      id,
      topic,
      content,
      trustScore: trust,
      freshnessScore: 1.0,
      evidenceCount,
      usageCount: 0,
      verificationStatus: trust >= 0.95 ? 'verified' : trust >= 0.75 ? 'unverified' : 'contested',
      qualityScore: 0,
      status: 'active',
      lastAccessedCycle: this.cycle,
    };
    item.qualityScore = qualityScore(item);
    item.status = item.qualityScore >= 0.85 ? 'crystallized' : 'active';
    this.items.set(id, item);
    return item;
  }

  govern(): KnowledgeGovernanceReport {
    this.cycle++;
    for (const item of this.items.values()) {
      if (item.status === 'evicted') continue;

      // Age freshness
      const cycleSinceAccess = this.cycle - item.lastAccessedCycle;
      item.freshnessScore = Math.max(0, item.freshnessScore - cycleSinceAccess * 0.01);

      // Recompute quality
      item.qualityScore = qualityScore(item);

      // Status transitions
      if (item.qualityScore >= 0.85 && item.freshnessScore >= 0.6) {
        item.status = 'crystallized';
      } else if (item.qualityScore >= 0.55) {
        item.status = 'active';
      } else if (item.qualityScore >= 0.30) {
        item.status = 'decaying';
      } else {
        item.status = 'evicted';
      }
    }

    const counts = { crystallized: 0, active: 0, decaying: 0, evicted: 0 };
    let qSum = 0;
    for (const item of this.items.values()) {
      counts[item.status]++;
      qSum += item.qualityScore;
    }

    return {
      totalItems: this.items.size,
      ...counts,
      averageQualityScore: this.items.size > 0 ? qSum / this.items.size : 0,
      governanceCycle: this.cycle,
    };
  }

  getItems(): KnowledgeItemV22[] {
    return Array.from(this.items.values())
      .filter(i => i.status !== 'evicted')
      .sort((a, b) => b.qualityScore - a.qualityScore);
  }

  recall(query: string): KnowledgeItemV22[] {
    const q = query.toLowerCase();
    return this.getItems()
      .filter(i => i.topic.toLowerCase().includes(q) || i.content.toLowerCase().includes(q.split(' ')[0]))
      .slice(0, 3)
      .map(i => {
        i.usageCount++;
        i.freshnessScore = Math.min(1.0, i.freshnessScore + 0.02);
        i.lastAccessedCycle = this.cycle;
        return i;
      });
  }
}
