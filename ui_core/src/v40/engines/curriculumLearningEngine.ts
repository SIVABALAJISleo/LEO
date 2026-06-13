// LEO AI V40 — Curriculum Learning Engine
// Implements Easy -> Medium -> Hard progression, Knowledge dependency mapping, and Skill acquisition tracking.

export interface CurriculumStep {
  stepId: string;
  label: string;
  difficulty: "Easy" | "Medium" | "Hard";
  dependencyIds: string[];
  acquired: boolean;
}

export interface CurriculumReport {
  stages: CurriculumStep[];
  overallProgress: number; // 0.0 - 1.0
  activeTargetStep?: string;
}

export class CurriculumLearningEngine {
  private stages: CurriculumStep[] = [
    {
      stepId: "c-01",
      label: "Basic Semantic Caching (L1/L2)",
      difficulty: "Easy",
      dependencyIds: [],
      acquired: true
    },
    {
      stepId: "c-02",
      label: "Multi-Hop graph causal discoveries",
      difficulty: "Medium",
      dependencyIds: ["c-01"],
      acquired: true
    },
    {
      stepId: "c-03",
      label: "Mamba Recurrent Linear state projections",
      difficulty: "Hard",
      dependencyIds: ["c-02"],
      acquired: false
    }
  ];

  /**
   * Tracks skill progress and identifies the next pending curriculum stage.
   */
  public evaluateCurriculumProgress(): CurriculumReport {
    const completed = this.stages.filter(s => s.acquired).length;
    const overallProgress = completed / this.stages.length;

    // Next target is the first step not yet acquired
    const activeTargetStep = this.stages.find(s => !s.acquired)?.label;

    return {
      stages: this.stages,
      overallProgress: parseFloat(overallProgress.toFixed(2)),
      activeTargetStep
    };
  }

  public completeStep(stepId: string) {
    const step = this.stages.find(s => s.stepId === stepId);
    if (step) {
      step.acquired = true;
    }
  }
}
