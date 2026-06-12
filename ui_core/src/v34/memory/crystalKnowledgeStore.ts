// LEO AI V34 — Crystal Knowledge Store
// Capabilities: Store concept labels, factual assertions, and relational graphs.

export interface CrystalConcept {
  conceptId: string;
  label: string;
  assertions: string[];
  lastAccessedTime: number;
}

export class CrystalKnowledgeStore {
  private store = new Map<string, CrystalConcept>();

  storeConcept(label: string, assertions: string[]): CrystalConcept {
    const conceptId = `concept-${label.toLowerCase().replace(/[^a-z0-9]/g, "-")}`;
    const concept: CrystalConcept = {
      conceptId,
      label,
      assertions,
      lastAccessedTime: Date.now()
    };
    this.store.set(conceptId, concept);
    return concept;
  }

  getConcept(conceptId: string): CrystalConcept | null {
    const concept = this.store.get(conceptId);
    if (concept) {
      concept.lastAccessedTime = Date.now();
      this.store.set(conceptId, concept);
    }
    return concept || null;
  }

  getStoreSize(): number {
    return this.store.size;
  }
}
