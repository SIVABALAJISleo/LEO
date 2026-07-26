export interface ScientificHypothesis {
  claim: string;
  causalFactors: string[];
  evidenceWeight: number;
  contradictions: string[];
}
export interface ScienceEvaluation {
  hypotheses: ScientificHypothesis[];
  proposedExperiment: string;
  reproducibilityConfidence: number;
}
export class ScientificReasoningEngine {
  public async evaluateResearchClaim(claimText: string): Promise<ScienceEvaluation> {
    const res = await fetch("http://localhost:8000/api/v1/v40/engines/scientific", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ claimText }),
    });
    return res.json();
  }
}
