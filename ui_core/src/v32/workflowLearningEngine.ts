// LEO AI V32 — Phase 5 Enterprise Workflow Learning Engine
// Purpose: Learn how users work to identify bottlenecks and manual effort.
// Output: workflowEfficiencyScore.

export interface UserWorkflowStep {
  stepIndex: number;
  actionName: string;
  toolUsed: string;
  delayMs: number;
  failed: boolean;
}

export interface OptimizationSuggestion {
  targetStepsRange: number[];
  problemDescription: string;
  proposedAutomationFix: string;
  estimatedTimeSavedMinutes: number;
}

export class WorkflowLearningEngine {
  private activeSequence: UserWorkflowStep[] = [];

  recordStep(action: string, tool: string, delay: number, failed: boolean): void {
    this.activeSequence.push({
      stepIndex: this.activeSequence.length + 1,
      actionName: action,
      toolUsed: tool,
      delayMs: delay,
      failed,
    });
  }

  evaluateEfficiency(): { suggestions: OptimizationSuggestion[]; workflowEfficiencyScore: number } {
    const suggestions: OptimizationSuggestion[] = [];
    let bottleneckCount = 0;
    let failureCount = 0;

    this.activeSequence.forEach((s) => {
      if (s.delayMs > 4000) bottleneckCount++;
      if (s.failed) failureCount++;
    });

    // Heuristics: search for repeating action sequences (manual copy-paste triggers)
    const consecutiveGittable = this.activeSequence.filter((s) =>
      s.toolUsed.includes("git"),
    ).length;
    if (consecutiveGittable > 3) {
      suggestions.push({
        targetStepsRange: [1, this.activeSequence.length],
        problemDescription:
          "Frequent, repetitive Git commit and checkout command iterations detected.",
        proposedAutomationFix:
          "Consolidate into an automated Git staging and backup macro function.",
        estimatedTimeSavedMinutes: 12.0,
      });
    }

    const testFailures = this.activeSequence.filter(
      (s) => s.actionName.includes("test") && s.failed,
    ).length;
    if (testFailures > 2) {
      suggestions.push({
        targetStepsRange: [1, this.activeSequence.length],
        problemDescription: "High frequency of consecutive test verification failures.",
        proposedAutomationFix:
          "Integrate V32 Autonomous Failure Hunter V2 to pre-test code changes in the background.",
        estimatedTimeSavedMinutes: 25.0,
      });
    }

    // Baseline index is 100, drops with delay bottlenecks and failures
    const stepsCount = this.activeSequence.length || 1;
    const workflowEfficiencyScore = Math.max(
      10,
      parseFloat(
        (100 - (bottleneckCount / stepsCount) * 40 - (failureCount / stepsCount) * 35).toFixed(1),
      ),
    );

    return {
      suggestions,
      workflowEfficiencyScore,
    };
  }

  getStepsCount(): number {
    return this.activeSequence.length;
  }
}
