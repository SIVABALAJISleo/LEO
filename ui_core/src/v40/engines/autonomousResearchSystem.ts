export interface LiteraturePaper {
  id: string;
  title: string;
  coreInsight: string;
}
export interface ResearchGapReport {
  analyzedPapers: LiteraturePaper[];
  detectedGaps: string[];
  proposedHypotheses: string[];
  experimentPlan: string;
}
export class AutonomousResearchSystem {
  public async analyzeLiterature(queryField: string): Promise<ResearchGapReport> {
    const res = await fetch("http://localhost:8000/api/v1/v40/engines/research", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ queryField }),
    });
    return res.json();
  }
}
