// LEO AI V36 — Open World Reasoner
// Adapts route scheduling when encountering unmapped entities or sensor drifting.

export class OpenWorldReasoner {
  public reasonUnexpectedObstacle(
    obstacleLabel: string,
    confidence: number
  ): { actionPlan: string; recalculationNeeded: boolean } {
    if (confidence < 0.4) {
      return {
        actionPlan: "Uncertain sensor match. Maintain current speed while increasing camera frequency.",
        recalculationNeeded: false
      };
    }
    
    if (obstacleLabel.toLowerCase().includes("construction") || obstacleLabel.toLowerCase().includes("debris")) {
      return {
        actionPlan: "Halt trajectory. Trigger alternate route planning.",
        recalculationNeeded: true
      };
    }

    return {
      actionPlan: "Slow down. Proceed with adaptive steering checks.",
      recalculationNeeded: true
    };
  }
}
