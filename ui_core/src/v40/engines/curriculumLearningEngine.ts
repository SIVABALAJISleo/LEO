export interface CurriculumStep { stepId: string; label: string; difficulty: "Easy" | "Medium" | "Hard"; dependencyIds: string[]; acquired: boolean; }
export interface CurriculumReport { stages: CurriculumStep[]; overallProgress: number; activeTargetStep?: string; }
export class CurriculumLearningEngine {
  public async evaluateCurriculumProgress(): Promise<CurriculumReport> {
    const res = await fetch("http://localhost:8000/api/v1/v40/engines/curriculum");
    return res.json();
  }
  public async completeStep(stepId: string): Promise<void> {
    await fetch("http://localhost:8000/api/v1/v40/engines/curriculum/complete", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ stepId })
    });
  }
}
