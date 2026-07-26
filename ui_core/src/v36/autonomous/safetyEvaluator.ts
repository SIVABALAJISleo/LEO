// LEO AI V36 — Safety Evaluator
// Enforces deceleration targets and collision avoidance parameters.

export class SafetyEvaluator {
  public checkDecelerationSafe(
    velocityKmh: number,
    obstacleDistanceMeters: number,
  ): { safe: boolean; decelerationRequired: number } {
    // Basic braking distance formula: d = v^2 / (2 * a)
    // a = v^2 / (2 * d)
    const velocityMs = velocityKmh / 3.6;
    if (obstacleDistanceMeters <= 2) return { safe: false, decelerationRequired: 9.8 };

    const decelerationRequired = parseFloat(
      ((velocityMs * velocityMs) / (2 * obstacleDistanceMeters)).toFixed(2),
    );
    return {
      safe: decelerationRequired < 6.5, // 6.5 m/s^2 is maximum comfortable deceleration
      decelerationRequired,
    };
  }
}
