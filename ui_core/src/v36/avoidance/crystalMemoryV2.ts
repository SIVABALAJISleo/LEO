// LEO AI V36 — Crystal Memory V2 (Avoidance Subsystem)
// Caches crystallized facts to support high reuse rates.

export interface CrystallizedConcept {
  id: string;
  conceptKey: string;
  responseBody: string;
  frequency: number;
}

export class CrystalMemoryV2 {
  private memoryCache: CrystallizedConcept[] = [
    {
      id: "c-10",
      conceptKey: "vnni offset cycles",
      responseBody: "AVX-VNNI reduces integer steps to 1 instruction cycle.",
      frequency: 12,
    },
  ];

  public lookupMemory(key: string): CrystallizedConcept | null {
    const kNorm = key.toLowerCase();
    const match = this.memoryCache.find(
      (c) => kNorm.includes(c.conceptKey) || c.conceptKey.includes(kNorm),
    );

    if (match) {
      match.frequency++;
      return match;
    }
    return null;
  }
}
