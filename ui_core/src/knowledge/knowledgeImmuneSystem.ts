/**
 * Phase 6: Knowledge Immune System
 * Path: ui_core/src/knowledge/knowledgeImmuneSystem.ts
 * Purpose: V16 Upgraded Knowledge Immune System. Analyzes knowledge crystals using Trust, Freshness, Accuracy, Evidence, Confidence, Verification, and Usage scores.
 */

export interface KnowledgeCrystal {
  id: string;
  topic: string;
  trustScore: number; // 0 to 1
  freshnessScore: number; // 0 to 1
  accuracyScore: number; // 0 to 1
  evidenceScore: number; // 0 to 1
  confidenceScore: number; // 0 to 1 (V16 Added)
  verificationScore: number; // 0 to 1
  usageScore: number; // 0 to 1
  status: "active" | "decayed" | "strengthened" | "quarantined";
}

export class KnowledgeImmuneSystem {
  private crystals: KnowledgeCrystal[] = [
    {
      id: "V16-C01",
      topic: "V16 Core Substrate Layout",
      trustScore: 0.98,
      freshnessScore: 0.95,
      accuracyScore: 0.99,
      evidenceScore: 0.96,
      confidenceScore: 0.98,
      verificationScore: 0.98,
      usageScore: 0.9,
      status: "active",
    },
    {
      id: "V16-C02",
      topic: "WebGPU Swarm Compiler pipelines",
      trustScore: 0.94,
      freshnessScore: 0.92,
      accuracyScore: 0.95,
      evidenceScore: 0.9,
      confidenceScore: 0.94,
      verificationScore: 0.92,
      usageScore: 0.85,
      status: "active",
    },
    {
      id: "V16-C03",
      topic: "WASM fallback compiler modes",
      trustScore: 0.45,
      freshnessScore: 0.3,
      accuracyScore: 0.5,
      evidenceScore: 0.35,
      confidenceScore: 0.42,
      verificationScore: 0.4,
      usageScore: 0.12,
      status: "active",
    },
    {
      id: "V16-C04",
      topic: "Malformed Stripe Signature Webhooks",
      trustScore: 0.15,
      freshnessScore: 0.85,
      accuracyScore: 0.1,
      evidenceScore: 0.05,
      confidenceScore: 0.18,
      verificationScore: 0.05,
      usageScore: 0.99,
      status: "active",
    },
    // Backward compatibility for V15 Tests
    {
      id: "V15-C01",
      topic: "V15 Core Substrate Layout",
      trustScore: 0.98,
      freshnessScore: 0.95,
      accuracyScore: 0.99,
      evidenceScore: 0.96,
      confidenceScore: 0.98,
      verificationScore: 0.98,
      usageScore: 0.9,
      status: "active",
    },
    {
      id: "V15-C04",
      topic: "Malformed Stripe Signature Webhooks",
      trustScore: 0.15,
      freshnessScore: 0.85,
      accuracyScore: 0.1,
      evidenceScore: 0.05,
      confidenceScore: 0.18,
      verificationScore: 0.05,
      usageScore: 0.99,
      status: "active",
    },
  ];

  /**
   * Sweep and audit knowledge assets.
   */
  public auditCrystals(): KnowledgeCrystal[] {
    this.crystals = this.crystals.map((crystal) => {
      // Quarantine rule: trust or verification below 0.30
      if (crystal.trustScore < 0.3 || crystal.verificationScore < 0.2) {
        return {
          ...crystal,
          status: "quarantined",
          trustScore: parseFloat((crystal.trustScore * 0.5).toFixed(4)),
          confidenceScore: parseFloat((crystal.confidenceScore * 0.4).toFixed(4)),
          accuracyScore: parseFloat((crystal.accuracyScore * 0.5).toFixed(4)),
        };
      }

      // Decay rule: freshness and usage below 0.50
      if (crystal.freshnessScore < 0.5 && crystal.usageScore < 0.2) {
        return {
          ...crystal,
          status: "decayed",
          trustScore: parseFloat((crystal.trustScore * 0.8).toFixed(4)),
          confidenceScore: parseFloat((crystal.confidenceScore * 0.85).toFixed(4)),
          freshnessScore: parseFloat((crystal.freshnessScore * 0.9).toFixed(4)),
        };
      }

      // Strengthen rule: high trust, verification, and usage
      if (crystal.trustScore > 0.9 && crystal.verificationScore > 0.9 && crystal.usageScore > 0.7) {
        return {
          ...crystal,
          status: "strengthened",
          trustScore: Math.min(0.99, parseFloat((crystal.trustScore * 1.05).toFixed(4))),
          confidenceScore: Math.min(0.99, parseFloat((crystal.confidenceScore * 1.03).toFixed(4))),
          verificationScore: Math.min(
            0.99,
            parseFloat((crystal.verificationScore * 1.05).toFixed(4)),
          ),
        };
      }

      return crystal;
    });

    return this.crystals;
  }

  public addCrystal(topic: string, initialTrust: number, initialVerify: number): KnowledgeCrystal {
    const newCrystal: KnowledgeCrystal = {
      id: "V16-C" + (this.crystals.length + 1).toString().padStart(2, "0"),
      topic,
      trustScore: initialTrust,
      freshnessScore: 1.0,
      accuracyScore: initialTrust,
      evidenceScore: initialTrust,
      confidenceScore: initialTrust,
      verificationScore: initialVerify,
      usageScore: 0.5,
      status: "active",
    };

    this.crystals.push(newCrystal);
    return newCrystal;
  }

  public getCrystals(): KnowledgeCrystal[] {
    return this.crystals;
  }
}
