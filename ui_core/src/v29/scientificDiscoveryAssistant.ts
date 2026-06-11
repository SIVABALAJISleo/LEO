// V29 — Phase 6 Scientific Discovery Assistant
// Generates, tracks, and ranks hypotheses based on evidence counts

export interface HypothesisNode {
  id: string;
  observation: string;
  hypothesisText: string;
  evidenceCitationsCount: number;
  verificationRate: number; // 0 to 1
  rank: number;
}

export class ScientificDiscoveryAssistant {
  private hypotheses: HypothesisNode[] = [];

  constructor() {
    this.seedHypotheses();
  }

  private seedHypotheses() {
    this.hypotheses = [
      {
        id: "H-2901",
        observation: "pLDDT structural structures are highly disordered in AlphaFold predictions for Q9BY12",
        hypothesisText: "Target ligand binding stabilizes the domain boundaries under normal room temperatures.",
        evidenceCitationsCount: 14,
        verificationRate: 0.942,
        rank: 1
      },
      {
        id: "H-2902",
        observation: "INT8 quantization spikes latency on dynamic iGPU routes",
        hypothesisText: "Dynamic scheduling thread collisions dilute offload vector allocations.",
        evidenceCitationsCount: 8,
        verificationRate: 0.815,
        rank: 2
      }
    ];
  }

  proposeHypothesis(observation: string, text: string, citations: number, rate: number): HypothesisNode {
    const newNode: HypothesisNode = {
      id: `H-29${String(this.hypotheses.length + 1).padStart(2, "0")}`,
      observation,
      hypothesisText: text,
      evidenceCitationsCount: citations,
      verificationRate: rate,
      rank: this.hypotheses.length + 1
    };

    this.hypotheses.push(newNode);
    this.reRank();
    return newNode;
  }

  private reRank() {
    // Rank by verification rate desc, then citations desc
    this.hypotheses.sort((a, b) => {
      if (b.verificationRate !== a.verificationRate) {
        return b.verificationRate - a.verificationRate;
      }
      return b.evidenceCitationsCount - a.evidenceCitationsCount;
    });

    this.hypotheses.forEach((h, idx) => h.rank = idx + 1);
  }

  getHypotheses(): HypothesisNode[] {
    return this.hypotheses;
  }
}
// V29 Scientific Discovery
