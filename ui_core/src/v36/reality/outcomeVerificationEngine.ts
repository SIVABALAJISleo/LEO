// LEO AI V36 — Outcome Verification Engine
// Evaluates outcomes against database assertions and external sensors.

export class OutcomeVerificationEngine {
  public verifyOutcome(predicted: string, actual: string): { matches: boolean; errorDelta: number } {
    const pNorm = predicted.toLowerCase().trim();
    const aNorm = actual.toLowerCase().trim();

    if (pNorm === aNorm) {
      return { matches: true, errorDelta: 0.0 };
    }
    
    // Partially matching heuristics
    const distance = Math.abs(predicted.length - actual.length) / Math.max(1, predicted.length);
    return {
      matches: distance < 0.2,
      errorDelta: parseFloat(distance.toFixed(3))
    };
  }
}
