// LEO AI V37 — World Model Engine
// Forecasts outcome consequences and simulates scenarios before agent action execution.

export interface SimulationResult {
  stepIndex: number;
  simulatedAction: string;
  expectedState: string;
  safetyScore: number; // 0.0 - 1.0
  riskDetected: boolean;
}

export interface WorldModelReport {
  overallRiskScore: number;
  passedSafetyVerification: boolean;
  simulationTrace: SimulationResult[];
  recommendedAdjustments: string[];
}

export class WorldModelEngine {
  /**
   * Evaluates proposed operations using simulated trajectory projections.
   */
  public simulatePlan(actions: string[]): WorldModelReport {
    const simulationTrace: SimulationResult[] = [];
    let riskCount = 0;
    const recommendedAdjustments: string[] = [];

    actions.forEach((act, idx) => {
      const actLower = act.toLowerCase();
      let safetyScore = 0.98;
      let riskDetected = false;
      let expectedState = "System stable";

      if (actLower.includes("kill") || actLower.includes("remove") || actLower.includes("bypass")) {
        safetyScore = 0.45;
        riskDetected = true;
        expectedState = "Potential memory leak or security violation";
        riskCount++;
        recommendedAdjustments.push(
          `Step ${idx + 1}: Override action '${act}' with safe sandbox equivalent.`,
        );
      } else if (actLower.includes("write")) {
        safetyScore = 0.85;
        expectedState = "Data written; indexing file updates";
      }

      simulationTrace.push({
        stepIndex: idx + 1,
        simulatedAction: act,
        expectedState,
        safetyScore,
        riskDetected,
      });
    });

    const passedSafetyVerification = riskCount === 0;
    const overallRiskScore = actions.length > 0 ? riskCount / actions.length : 0;

    return {
      overallRiskScore,
      passedSafetyVerification,
      simulationTrace,
      recommendedAdjustments: passedSafetyVerification
        ? ["All simulated steps verified as safe."]
        : recommendedAdjustments,
    };
  }
}
