export interface ExpertGateReport {
  selectedExperts: string[];
  activeWeights: number[];
  gateConfidence: number;
  unactivatedExpertsCount: number;
  reason: string;
}
export class MixtureOfExpertsEngine {
  public async routeToExperts(prompt: string): Promise<ExpertGateReport> {
    const res = await fetch("http://localhost:8000/api/v1/v40/engines/moe", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt }),
    });
    return res.json();
  }
}
