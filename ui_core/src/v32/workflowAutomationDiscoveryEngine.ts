// LEO AI V32 — Phase 6 Workflow Automation Discovery Engine
// Find: repetitive tasks, predictable tasks, high-frequency tasks.
// Rank: ROI, Impact, Complexity.
// Output: automationPriorityQueue.

export interface AutomationOpportunity {
  taskName: string;
  frequencyPerHour: number;
  impactScore: number; // 0 to 10
  complexityScore: number; // 0 to 10 (lower is easier)
  estimatedRoi: number; // calculated composite score
}

export class WorkflowAutomationDiscoveryEngine {
  rankOpportunities(
    tasks: { name: string; frequency: number; impact: number; complexity: number }[],
  ): AutomationOpportunity[] {
    return tasks
      .map((t) => {
        // ROI is proportional to frequency and impact, inversely proportional to complexity
        const calculatedRoi = parseFloat(
          ((t.frequency * t.impact) / (t.complexity || 1.0)).toFixed(2),
        );

        return {
          taskName: t.name,
          frequencyPerHour: t.frequency,
          impactScore: t.impact,
          complexityScore: t.complexity,
          estimatedRoi: calculatedRoi,
        };
      })
      .sort((a, b) => b.estimatedRoi - a.estimatedRoi);
  }
}
