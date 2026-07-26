/**
 * Layer 0: Knowledge Crystallization Engine (V13 Upgraded)
 * Purpose: Store solutions, reasoning traces, workflows, and discoveries.
 * Integrates automatic expiration for decaying or untrusted knowledge crystals.
 */

export interface CrystalAsset {
  id: string;
  content: any;
  type: "solution" | "trace" | "workflow" | "discovery";
  confidenceScore: number;
  temporalDecay: number; // calculated age multiplier
  trustScore: number;
  lastUsed: number;
}

export class KnowledgeCrystallizationEngine {
  private crystalStore: Map<string, CrystalAsset> = new Map();

  public storeCrystal(asset: CrystalAsset): void {
    this.crystalStore.set(asset.id, asset);
    console.log(
      `[CRYSTALLIZATION L0] New ${asset.type} crystal stored. Confidence: ${asset.confidenceScore}`,
    );
  }

  public retrieveCrystal(id: string): CrystalAsset | undefined {
    const asset = this.crystalStore.get(id);
    if (!asset) return undefined;

    // Perform trust and decay auditing on retrieve
    const now = Date.now();
    const ageHours = (now - asset.lastUsed) / 3600000;

    // Calculate decay multiplier
    const temporalDecay = Math.max(0.1, 1 - ageHours * 0.05);
    const activeTrust = asset.trustScore * temporalDecay;

    // If trust falls below threshold (0.50), expire the crystal automatically
    if (activeTrust < 0.5) {
      console.log(
        `[CRYSTALLIZATION L0] Crystal ${id} expired automatically due to trust decay (${activeTrust.toFixed(2)}).`,
      );
      this.crystalStore.delete(id);
      return undefined;
    }

    // Update last used timestamp
    asset.lastUsed = now;
    return {
      ...asset,
      temporalDecay,
      trustScore: parseFloat(activeTrust.toFixed(4)),
    };
  }

  public getAllCrystals(): CrystalAsset[] {
    // Filter out expired on list
    const list: CrystalAsset[] = [];
    for (const [id, asset] of this.crystalStore.entries()) {
      const retrieved = this.retrieveCrystal(id);
      if (retrieved) list.push(retrieved);
    }
    return list;
  }
}
