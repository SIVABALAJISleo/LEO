// LEO AI V36 — Edge Case Library
// Catalogs rare anomalies and reproduction scenario permutations.

export interface EdgeCaseRecord {
  id: string;
  errorHash: string;
  reproducibleSteps: string[];
}

export class EdgeCaseLibrary {
  private library: EdgeCaseRecord[] = [];

  public registerCase(hash: string, steps: string[]): void {
    this.library.push({
      id: `ec-${(100 + Math.random() * 900).toFixed(0)}`,
      errorHash: hash,
      reproducibleSteps: steps,
    });
  }

  public getLibrary(): EdgeCaseRecord[] {
    return this.library;
  }
}
